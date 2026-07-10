# kintone_client.py
# =============================
# main.py で学んだ処理を「再利用できるクラス」にまとめたもの。
# Lv03 で学んだクラス・モジュール分割の実践編。
#
# 使い方の例:
#
#   import json
#   from kintone_client import KintoneClient
#
#   with open("config.json", encoding="utf-8") as f:
#       cfg = json.load(f)
#
#   client = KintoneClient(cfg["subdomain"], cfg["app_id"], cfg["api_token"])
#   records = client.get_all_records()               # 全件
#   today = client.get_records('作成日時 > TODAY()')  # 条件付き
#
# JS でいうと「fetch を毎回手書きせず、APIClient クラスに包む」のと同じ発想。
# PAD でいうと「共通処理をサブフローに切り出す」のと同じ発想。

import logging

import requests

# このモジュール専用のロガー。使う側で logging.basicConfig(level=logging.INFO)
# を呼べば進捗ログが表示される（print と違って本番では黙らせられるのが利点）。
logger = logging.getLogger(__name__)


class KintoneClient:
    """Kintone REST API のシンプルなクライアント。

    レコード取得（GET）専用。1 リクエスト 500 件制限と offset 10,000 制限を
    意識せずに済むよう、内部で seek 法（$id カーソル方式）による
    自動ページネーションを行う。

    Attributes:
        base_url: API のベース URL（https://{subdomain}.cybozu.com/k/v1）
        app_id: 対象アプリの ID
    """

    # 1 リクエストで取得できる最大件数（Kintone の仕様）
    MAX_LIMIT = 500

    def __init__(self, subdomain: str, app_id: int, api_token: str) -> None:
        """クライアントを初期化する。

        Args:
            subdomain: Kintone のサブドメイン（https://XXX.cybozu.com の XXX 部分）
            app_id: アプリ ID（アプリの URL /k/17/ の数字部分）
            api_token: アプリ設定 → API トークン で発行したトークン
        """
        self.base_url = f"https://{subdomain}.cybozu.com/k/v1"
        self.app_id = app_id
        # requests.Session を使うと接続を使い回せて連続リクエストが速くなる。
        # 共通ヘッダー（認証トークン）も一度セットすれば毎回書かなくて済む。
        self._session = requests.Session()
        self._session.headers.update({"X-Cybozu-API-Token": api_token})

    def get_record(self, record_id: int) -> dict:
        """レコード番号を指定して 1 件取得する。

        Args:
            record_id: レコード番号（$id）

        Returns:
            {フィールドコード: {"type": ..., "value": ...}} 形式の dict
        """
        resp = self._session.get(
            f"{self.base_url}/record.json",  # 単数形エンドポイント
            params={"app": self.app_id, "id": record_id},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["record"]

    def get_records(self, query: str = "") -> list[dict]:
        """条件に一致するレコードを全件取得する（自動ページネーション）。

        seek 法（$id カーソル方式）を使うため、offset 10,000 制限に
        引っかからず何件でも取得できる。

        Args:
            query: Kintone クエリ構文の絞り込み条件。
                   例: '作成日時 > "2026-07-01T00:00:00Z"'
                   空文字なら全件。
                   ※ order by / limit / offset は内部で付与するので含めないこと。

        Returns:
            レコードの list（Kintone の生の入れ子構造のまま）

        Raises:
            ValueError: query に order by / limit / offset が含まれている場合
            requests.exceptions.HTTPError: 認証エラー等で API がエラーを返した場合
        """
        # seek 法と両立できないキーワードが混ざっていたら早めに教えてあげる
        lowered = query.lower()
        for forbidden in ("order by", "limit", "offset"):
            if forbidden in lowered:
                raise ValueError(
                    f"query に '{forbidden}' は指定できません"
                    "（ページネーションのためクライアント側で自動付与します）"
                )

        all_records: list[dict] = []
        last_id = 0  # カーソル: 前回取得した最後のレコードの $id

        while True:
            # $id > last_id を条件に足して「続きから」取得する
            condition = f"$id > {last_id}"
            if query:
                condition = f"({query}) and {condition}"
            full_query = f"{condition} order by $id asc limit {self.MAX_LIMIT}"

            resp = self._session.get(
                f"{self.base_url}/records.json",  # 複数形エンドポイント
                params={"app": self.app_id, "query": full_query},
                timeout=30,
            )
            resp.raise_for_status()

            records = resp.json()["records"]
            if not records:
                break  # 1 件も返ってこなければ取り切った

            all_records.extend(records)
            last_id = int(records[-1]["$id"]["value"])
            logger.info("累計 %d 件取得（最後の $id=%d）", len(all_records), last_id)

            if len(records) < self.MAX_LIMIT:
                break  # 最終ページ

        return all_records

    def get_all_records(self) -> list[dict]:
        """アプリの全レコードを取得する（get_records の条件なし版）。

        Returns:
            全レコードの list
        """
        return self.get_records()

    @staticmethod
    def flatten(record: dict) -> dict:
        """Kintone の入れ子構造レコードを {フィールドコード: 値} に平ら化する。

        - ユーザー系フィールド（dict）は表示名（name）に変換
        - 複数選択系フィールド（list）は "、" 区切りの文字列に変換

        Args:
            record: get_record / get_records が返すレコード 1 件

        Returns:
            シンプルな dict（CSV 出力や LLM 分析に使いやすい形）
        """
        flat = {}
        for field_code, field in record.items():
            value = field["value"]
            if isinstance(value, dict) and "name" in value:
                value = value["name"]
            elif isinstance(value, list):
                value = "、".join(
                    v["name"] if isinstance(v, dict) and "name" in v else str(v)
                    for v in value
                )
            flat[field_code] = value
        return flat


# このファイルを直接実行したときの簡易動作確認
# （import されたときは動かない。Lv03 で学んだ if __name__ == "__main__" パターン）
if __name__ == "__main__":
    import json
    from pathlib import Path

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    config_path = Path(__file__).parent / "config.json"
    with open(config_path, encoding="utf-8") as f:
        cfg = json.load(f)

    client = KintoneClient(cfg["subdomain"], cfg["app_id"], cfg["api_token"])
    records = client.get_all_records()
    print(f"全 {len(records)} 件取得できました")
    if records:
        print("1 件目（平ら化後）:")
        print(json.dumps(client.flatten(records[0]), ensure_ascii=False, indent=2))
