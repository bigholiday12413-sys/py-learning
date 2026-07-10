# -*- coding: utf-8 -*-
"""
vv11 - バッチ抽出パイプライン

sample_reports.csv の日報を1件ずつ vvM に投げて、抽出結果を JSONv に保存する。
実務では約200件の日報を処理する想定なので、以下の「壊れにくい設計」を入れている。

【なぜ JSONv（JSON vines）で保存するのか】
- JSONv = 1行に1つの JSON オブジェクトを書き並べるだけの形式。
    {"id": 1, "商材名": "...", ...}
    {"id": 2, "商材名": "...", ...}
- 普通の JSON（全体を [ ] で囲む形式）だと、全件終わってから一括保存するしかなく、
  150件目でクラッシュしたら150件分の結果が全部消える。
- JSONv なら1件終わるたびに「1行追記」するだけなので、
  途中で落ちてもそこまでの結果はファイルに残っている。
- さらに「既に出力済みの id はスキップ」する処理（レジューム）と組み合わせると、
  再実行するだけで続きから処理が再開できる。RPA の再実行設計と同じ考え方。

【エラーの分離】
- 接続エラーや JSON 壊れなどで失敗した行は errors.jsonl に別途記録する。
- 成功と失敗を混ぜないことで、あとで「失敗分だけ再処理」ができる。
"""

import csv
import json
import time
from pathlib import Path

import requests

# main.py で作った抽出関数をそのまま再利用する（vv03 のモジュール分割の実践）
from main import extract_from_report

# ============================================================
# 1. ファイルパスの定義
# ============================================================
BASE_DIR = Path(__file__).parent          # このスクリプトがある場所
INPUT_CSV = BASE_DIR / "sample_reports.csv"   # 入力: 日報CSV
OUTPUT_JSONv = BASE_DIR / "results.jsonl"     # 出力: 抽出結果（成功分）
ERROR_JSONv = BASE_DIR / "errors.jsonl"       # 出力: エラー記録（失敗分）


# ============================================================
# 2. レジューム用: 処理済み id の読み込み
# ============================================================
def load_done_ids(jsonl_path: Path) -> set:
    """出力済み JSONv から、処理済みの id 一覧を set で返す。

    ファイルがなければ空 set（＝初回実行）。
    set にするのは「id in done_ids」の判定が高速だから。
    """
    done = set()
    if not jsonl_path.exists():
        return done
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # 空行はスキップ
            record = json.loads(line)
            done.add(record["id"])
    return done


# ============================================================
# 3. JSONv への1行追記
# ============================================================
def append_jsonl(jsonl_path: Path, record: dict) -> None:
    """dict を1行の JSON としてファイル末尾に追記する。

    mode="a"（追記モード）なので既存の内容は消えない。
    1件ごとに open/close するのは少し無駄だが、
    確実にディスクへ書かれる安心感を優先する（件数が数百件ならば十分速い）。
    """
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ============================================================
# 4. メイン処理
# ============================================================
def main():
    # ----- 入力CSVを全件読み込む -----
    with open(INPUT_CSV, encoding="utf-8") as f:
        reports = list(csv.DictReader(f))  # 1行 = {"id": "1", "日付": "...", ...}

    total = len(reports)

    # ----- 処理済み id を読み込む（レジューム）-----
    done_ids = load_done_ids(OUTPUT_JSONv)
    if done_ids:
        print(f"処理済み {len(done_ids)} 件を検出。未処理分のみ実行します（レジューム）。")

    # ----- 統計用の変数 -----
    success_count = 0
    error_count = 0
    skip_count = 0
    elapsed_list = []       # 1件あたりの処理時間を貯める
    batch_start = time.time()

    # ----- 1件ずつループ -----
    for i, report in enumerate(reports, start=1):
        report_id = int(report["id"])

        # 既に出力済みならスキップ（再実行時はここが効く）
        if report_id in done_ids:
            skip_count += 1
            print(f"[{i}/{total}] id={report_id} は処理済みのためスキップ")
            continue

        print(f"[{i}/{total}] id={report_id} を処理中...", end=" ", flush=True)
        start = time.time()

        try:
            # ここが本体。main.py の抽出関数を呼ぶだけ
            fields = extract_from_report(report["本文"])

        except Exception as e:
            # 失敗しても止めない。エラー内容を errors.jsonl に記録して次へ進む。
            # → あとで errors.jsonl を見れば「どの id がなぜ失敗したか」が分かり、
            #   失敗分だけの再処理もできる（改造課題参照）
            elapsed = time.time() - start
            error_count += 1
            append_jsonl(ERROR_JSONv, {
                "id": report_id,
                "error": str(e),
                "error_type": type(e).__name__,
            })
            print(f"エラー ({elapsed:.1f}秒) -> errors.jsonl に記録: {type(e).__name__}")
            continue

        elapsed = time.time() - start
        elapsed_list.append(elapsed)
        success_count += 1

        # 成功したら即座に1行追記（クラッシュしてもここまでの結果は残る）
        append_jsonl(OUTPUT_JSONv, {
            "id": report_id,
            "日付": report["日付"],
            "営業担当": report["営業担当"],
            **fields,               # 抽出した5項目を展開して合体（dict のアンパック）
            "処理時間秒": round(elapsed, 1),
        })
        print(f"完了 ({elapsed:.1f}秒)")

    # ----- 統計の表示 -----
    batch_elapsed = time.time() - batch_start
    print()
    print("=== バッチ処理 完了 ===")
    print(f"  成功: {success_count} 件")
    print(f"  失敗: {error_count} 件" + (f"（{ERROR_JSONv.name} を確認）" if error_count else ""))
    print(f"  スキップ（処理済み）: {skip_count} 件")
    print(f"  合計時間: {batch_elapsed:.1f} 秒")
    if elapsed_list:
        avg = sum(elapsed_list) / len(elapsed_list)
        print(f"  1件あたり平均: {avg:.1f} 秒（最短 {min(elapsed_list):.1f} / 最長 {max(elapsed_list):.1f}）")
        # 実務の200件処理にかかる時間の目安を出す
        # ※初回はモデルロードで1件目が極端に遅いので、平均は参考値
        print(f"  → 200件処理の見積もり: 約 {avg * 200 / 60:.0f} 分")
    print(f"  結果ファイル: {OUTPUT_JSONv}")


if __name__ == "__main__":
    main()
