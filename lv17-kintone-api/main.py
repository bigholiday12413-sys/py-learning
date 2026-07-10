# vv10: Kintone REST API 入門
# =============================
# テーマ: PAD の「Web サービスを呼び出します」でやっていた Kintone 連携を
#         Python の requests に置き換える。
#
# Kintone REST API の基本形:
#   1レコード取得:   GET https://{subdomain}.cybozu.com/k/v1/record.json   (単数形!)
#   複数レコード取得: GET https://{subdomain}.cybozu.com/k/v1/records.json  (複数形!)
#   認証: リクエストヘッダーに X-Cybozu-API-Token: <トークン> を付けるだけ
#
# PAD との対応:
#   PAD の HTTP アクションで URv・ヘッダー・クエリを手で組み立てていたのと同じことを、
#   requests.get(url, headers=..., params=...) の 1 行でやる。
#   params に渡した dict は自動で URv エンコードされる（PAD で %20 とか手で書いてたアレが不要）。

import csv
import json
import sys
from pathlib import Path

import requests

# ---------------------------------------------------------------
# STEP 0: 設定ファイル (config.json) を読み込む
# ---------------------------------------------------------------
# トークンをコードに直書きすると git にコミットして事故るので、
# 設定は必ず外部ファイル（gitignore 対象）に分離する。
# JS でいう dotenv (.env) と同じ発想。

CONFIG_PATH = Path(__file__).parent / "config.json"

if not CONFIG_PATH.exists():
    # config.json がまだ無い人向けの親切エラー
    print("エラー: config.json が見つかりません。")
    print("config.example.json をコピーして config.json を作り、")
    print("subdomain / app_id / api_token を自分の環境に書き換えてください。")
    sys.exit(1)

with open(CONFIG_PATH, encoding="utf-8") as f:
    config = json.load(f)

SUBDOMAIN = config["subdomain"]      # 例: "example" → https://example.cybozu.com
APP_ID = config["app_id"]            # 例: 17（日報アプリ）
API_TOKEN = config["api_token"]      # アプリ設定 → API トークン で発行したもの
OUTPUT_DIR = Path(__file__).parent / config.get("output_dir", "output")
OUTPUT_DIR.mkdir(exist_ok=True)      # 出力フォルダが無ければ作る（PAD の「フォルダーの作成」相当）

# ベース URv とヘッダーは全リクエスト共通なので先に組み立てておく
BASE_URv = f"https://{SUBDOMAIN}.cybozu.com/k/v1"
HEADERS = {
    # ↓ これが Kintone の認証。PAD でヘッダー欄に書いていたのと同じ。
    "X-Cybozu-API-Token": API_TOKEN,
}


# ---------------------------------------------------------------
# STEP 1: 1 件だけ取得してみる（record.json = 単数形）
# ---------------------------------------------------------------
# まずは最小の成功体験。レコード番号（$id）を指定して 1 件取る。

def get_single_record(record_id: int) -> dict:
    """レコード番号を指定して 1 件取得する。

    エンドポイントが record.json（単数形）である点に注意。
    複数件用の records.json とはパラメータも戻り値の形も違う。
    """
    url = f"{BASE_URv}/record.json"
    params = {"app": APP_ID, "id": record_id}

    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()  # 200 以外なら例外を投げる（後述の STEP 6 でちゃんと捕まえる）

    # 戻り値は {"record": {フィールドコード: {"type": ..., "value": ...}, ...}}
    return resp.json()["record"]


# ---------------------------------------------------------------
# STEP 2: 複数件取得 + Kintone クエリ構文（records.json = 複数形）
# ---------------------------------------------------------------
# query パラメータには Kintone 独自のクエリ構文を書く。SQv の WHERE + ORDER BY に近い。
#   例: '作成日時 > "2026-07-01T00:00:00Z" order by $id asc limit 100 offset 0'
#   - order by <フィールド> asc/desc : 並び替え
#   - limit N  : 最大取得件数（省略時 100、最大 500）
#   - offset N : 読み飛ばし件数（ページネーション用）

def get_records(query: str) -> list[dict]:
    """クエリを指定して複数レコードを取得する（1 リクエスト分のみ）。"""
    url = f"{BASE_URv}/records.json"
    params = {
        "app": APP_ID,
        "query": query,
        # totalCount を true にすると、条件に一致する総件数も返してくれる
        "totalCount": "true",
    }

    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    # data は {"records": [...], "totalCount": "9900"} のような形
    print(f"  条件に一致する総件数: {data.get('totalCount')} 件")
    return data["records"]


# ---------------------------------------------------------------
# STEP 3: ページネーション（offset 方式）
# ---------------------------------------------------------------
# records.json は 1 リクエストで最大 500 件までしか返さない。
# 500 件を超えるデータは offset をずらしながらループで取る。
#
#   1 回目: limit 500 offset 0     → 1〜500 件目
#   2 回目: limit 500 offset 500   → 501〜1000 件目
#   ...
#
# PAD なら「ループ + カウンタ変数 + Web サービス呼び出し」で組んでいたパターン。
#
# ★重要な制限: offset は 10,000 まで！★
# offset が 10,000 を超えるとエラーになる（Kintone の仕様）。
# つまり offset 方式で取れるのは最大 1 万件まで。
# 日報アプリの全件は約 9,900 件 → 今はギリギリ取れるが、すぐ超える。
# → 次の STEP 4 の seek 法（カーソル方式）を使うのが正解。

def get_records_by_offset(base_query: str, max_records: int = 1500) -> list[dict]:
    """offset 方式のページネーション（学習用）。

    仕組みの理解のために実装するが、offset 10,000 制限があるため
    実務では STEP 4 の seek 法を使うこと。
    """
    all_records: list[dict] = []
    limit = 500  # 1 リクエストの最大件数
    offset = 0

    while offset < max_records:
        # base_query の後ろに limit / offset を足してクエリを組み立てる
        query = f"{base_query} limit {limit} offset {offset}"
        print(f"  offset {offset} から取得中...")

        url = f"{BASE_URv}/records.json"
        params = {"app": APP_ID, "query": query}
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()

        records = resp.json()["records"]
        all_records.extend(records)

        # 返ってきた件数が limit 未満 = もうデータが無いのでループ終了
        if len(records) < limit:
            break
        offset += limit

    return all_records


# ---------------------------------------------------------------
# STEP 4: seek 法（カーソル方式）— offset 10,000 制限の回避 ★実務ではこっち★
# ---------------------------------------------------------------
# 考え方: offset で「読み飛ばす」のではなく、
#         「前回取った最後のレコード ID より大きい ID」を条件にして次を取る。
#
#   1 回目: $id > 0     order by $id asc limit 500  → 最後の $id が 500 だったとする
#   2 回目: $id > 500   order by $id asc limit 500  → 最後の $id が 1012 だったとする
#   3 回目: $id > 1012  order by $id asc limit 500  → ...
#
# $id は Kintone が全レコードに自動で振る連番（欠番はあり得るが順序は保証される）。
# この方式なら件数の上限なし。9,900 件でも 10 万件でも取れる。

def get_all_records_by_seek(condition: str = "") -> list[dict]:
    """seek 法で条件に一致する全レコードを取得する。

    Args:
        condition: 絞り込み条件（例: '作成日時 > "2026-07-01T00:00:00Z"'）。
                   空文字なら全件取得。
                   ※ order by / limit / offset は内部で付けるので含めないこと。
    """
    all_records: list[dict] = []
    last_id = 0    # 前回取得した最後のレコードの $id（カーソルの役割）
    limit = 500

    while True:
        # $id > last_id を条件に足す。ユーザー条件があれば and でつなぐ。
        seek_cond = f"$id > {last_id}"
        if condition:
            seek_cond = f"({condition}) and {seek_cond}"
        query = f"{seek_cond} order by $id asc limit {limit}"

        url = f"{BASE_URv}/records.json"
        params = {"app": APP_ID, "query": query}
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()

        records = resp.json()["records"]
        if not records:
            break  # もう 1 件も返ってこない = 取り切った

        all_records.extend(records)
        # 最後のレコードの $id を次回のカーソルにする
        # （$id の value は文字列で返ってくるので int に変換する点に注意）
        last_id = int(records[-1]["$id"]["value"])
        print(f"  {len(all_records)} 件取得済み（最後の $id = {last_id}）")

        if len(records) < limit:
            break  # limit 未満しか返ってこなければ最終ページ

    return all_records


# ---------------------------------------------------------------
# STEP 5: レスポンスのフィールド構造を「平ら」にする
# ---------------------------------------------------------------
# Kintone のレコードはこういう入れ子構造で返ってくる:
#
#   {
#     "$id":      {"type": "__ID__",             "value": "123"},
#     "報告者":    {"type": "CREATOR",            "value": {"code": "suda", "name": "須田"}},
#     "日報本文":  {"type": "MUvTI_vINE_TEXT",    "value": "今日は..."},
#     "作成日時":  {"type": "CREATED_TIME",       "value": "2026-07-10T01:23:00Z"}
#   }
#
# 全フィールドが {"type": ..., "value": ...} で包まれている。
# CSV や vvM 分析に使うには {"$id": "123", "日報本文": "今日は..."} の
# シンプルな dict に「平ら化（フラット化）」すると扱いやすい。

def flatten_record(record: dict) -> dict:
    """Kintone のレコード 1 件を {フィールドコード: 値} のシンプルな dict に変換する。"""
    flat = {}
    for field_code, field in record.items():
        value = field["value"]

        # ユーザー選択系フィールド（CREATOR, MODIFIER 等）は dict で返るので表示名だけ取る
        if isinstance(value, dict) and "name" in value:
            value = value["name"]
        # 複数選択・チェックボックス等は list で返るので "、" 区切りの文字列にする
        elif isinstance(value, list):
            # ユーザー複数選択なら name を、それ以外はそのまま文字列化
            value = "、".join(
                v["name"] if isinstance(v, dict) and "name" in v else str(v)
                for v in value
            )

        flat[field_code] = value
    return flat


# ---------------------------------------------------------------
# STEP 6: エラーハンドリング
# ---------------------------------------------------------------
# Kintone API でよく遭遇するエラー:
#   401 Unauthorized … トークンが間違っている / 貼り忘れ
#   403 Forbidden    … トークンは正しいがアクセス権が無い
#                       （トークン生成時に「レコード閲覧」にチェックを入れたか？
#                         「アプリを更新」ボタンを押し忘れていないか？）
#   404 Not Found    … app_id が違う / subdomain が違う
#   520 CB_VA01 など … Kintone 独自のエラーコード。レスポンス JSON の
#                       "code" と "message" に日本語で理由が書いてあるので必ず読む
#                       （例: GAIA_TM12 = offset 上限超過）
#
# requests 自体の例外（サーバーに届く前の失敗）:
#   requests.exceptions.ConnectionError … ネットワーク断・subdomain のタイプミス
#   requests.exceptions.Timeout         … タイムアウト
# JS の fetch が reject するケースに相当。try / except（= try / catch）で捕まえる。

def fetch_with_error_handling() -> list[dict] | None:
    """エラーハンドリング付きで全件取得する。失敗したら None を返す。"""
    try:
        return get_all_records_by_seek()

    except requests.exceptions.HTTPError as e:
        # サーバーには届いたが 4xx / 5xx が返ってきた場合
        resp = e.response
        print(f"HTTP エラー: {resp.status_code}")
        try:
            # Kintone はエラー理由を JSON で返してくれるので中身を表示する
            err = resp.json()
            print(f"  code   : {err.get('code')}")
            print(f"  message: {err.get('message')}")
        except ValueError:
            print(f"  本文: {resp.text[:200]}")

        if resp.status_code == 401:
            print("  → API トークンが間違っていないか config.json を確認")
        elif resp.status_code == 403:
            print("  → トークンのアクセス権（レコード閲覧）と「アプリを更新」を確認")
        return None

    except requests.exceptions.ConnectionError:
        print("接続エラー: subdomain のスペルミス、またはネットワークを確認")
        return None

    except requests.exceptions.Timeout:
        print("タイムアウト: しばらく待ってから再実行")
        return None


# ---------------------------------------------------------------
# STEP 7: 原文保存（生 JSON をレコード ID 付きファイル名で保存）
# ---------------------------------------------------------------
# vvM 分析パイプラインでは「加工前の原文」を必ず残しておくのが鉄則。
#   - 後から「フラット化のロジックがバグってた」と気付いても原文から作り直せる
#   - ファイル名にレコード ID を入れておけば、Kintone 上の元レコードにすぐ戻れる

def save_raw_json(records: list[dict], out_dir: Path) -> None:
    """レコードごとに raw JSON を 1 ファイルずつ保存する。"""
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(exist_ok=True)

    for record in records:
        record_id = record["$id"]["value"]
        path = raw_dir / f"record_{record_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            # ensure_ascii=False にしないと日本語が 日報 のように
            # エスケープされて人間が読めなくなる（JS の JSON.stringify は最初から日本語 OK）
            json.dump(record, f, ensure_ascii=False, indent=2)

    print(f"原文 JSON を {len(records)} ファイル保存 → {raw_dir}")


# ---------------------------------------------------------------
# STEP 8: フラット化したレコードを CSV に出力（Excel 対応）
# ---------------------------------------------------------------

def save_csv(flat_records: list[dict], out_path: Path) -> None:
    """フラット化済みレコードを CSV に書き出す。"""
    if not flat_records:
        print("レコードが 0 件のため CSV は出力しません")
        return

    # 全レコードのキーを集めてヘッダー行にする（レコードによって欠けがあっても OK）
    fieldnames: list[str] = []
    for rec in flat_records:
        for key in rec:
            if key not in fieldnames:
                fieldnames.append(key)

    # utf-8-sig = BOM 付き UTF-8。Excel でダブルクリックしても文字化けしない。
    # newline="" は csv モジュールを使うときの Windows でのお約束（空行混入防止）。
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_records)

    print(f"CSV を保存 → {out_path}（{len(flat_records)} 件）")


# ---------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("vv10: Kintone REST API 入門")
    print(f"対象: https://{SUBDOMAIN}.cybozu.com / アプリ {APP_ID}")
    print("=" * 60)

    # --- デモ 1: 複数レコードを 3 件だけ取ってみる ---
    print("\n[1] まずは 3 件だけ取得してみる")
    sample = get_records("order by $id asc limit 3")
    for rec in sample:
        rid = rec["$id"]["value"]
        print(f"  レコード {rid}: フィールド数 {len(rec)}")

    # --- デモ 2: 1 件目のレコードを単体取得して構造を眺める ---
    if sample:
        first_id = int(sample[0]["$id"]["value"])
        print(f"\n[2] レコード {first_id} を単体取得（record.json）")
        record = get_single_record(first_id)
        # 構造を実感するために、最初の 3 フィールドだけ type と value を表示
        for i, (code, field) in enumerate(record.items()):
            if i >= 3:
                print("  ...")
                break
            print(f"  {code}: type={field['type']}, value={str(field['value'])[:40]}")

    # --- デモ 3: seek 法で全件取得（エラーハンドリング付き） ---
    print("\n[3] seek 法で全レコードを取得")
    records = fetch_with_error_handling()
    if records is None:
        sys.exit(1)
    print(f"合計 {len(records)} 件を取得")

    # --- デモ 4: 原文保存 + フラット化 + CSV 出力 ---
    print("\n[4] 保存処理")
    save_raw_json(records, OUTPUT_DIR)

    flat_records = [flatten_record(r) for r in records]
    save_csv(flat_records, OUTPUT_DIR / "records.csv")

    print("\n完了！ output フォルダの中身を確認してみよう。")


if __name__ == "__main__":
    main()
