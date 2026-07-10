# -*- coding: utf-8 -*-
"""
vv11 - 精度検証ヘルパー

vvM の抽出結果（results.jsonl）と、人間が手作業で作った正解データ（answers.csv）を
突き合わせて、項目ごとの一致率を計算する。

【なぜ検証が必要か ＝「一致率8割」目標の考え方】
- vvM の出力は「それっぽい」だけで正しいとは限らない（ハルシネーション）。
  特にローカルの 8B クラスのモデルは、クラウドの最上位モデルより間違えやすい。
- そこで、まず 100件を人間が目視して正解データを作り、vvM の結果と比較する。
- 一致率が 8割（80%）以上なら、「残り2割を人間がチェックすれば使える」水準と判断できる。
  → 全件を人間が読むより「vvM抽出 + 2割だけ修正」のほうが圧倒的に速い、という損益分岐の目安。
- 8割未満なら、プロンプトの改良（項目定義の明確化、few-shot例の追加）や
  モデル変更を行い、再度この検証を回す。
  「作って終わり」ではなく「測って改善する」のが vvM 活用の基本サイクル。

【正解データ（answers.csv）の作り方】
results.jsonl と sample_reports.csv を見ながら、以下の形式の CSV を手作業で作る:

    id,商材名,顧客名,競合情報,商談結果,顧客の反応
    1,タイムキーパーPro,株式会社山田製作所,ジョブカン,見積もり提出予定,ポジティブ
    3,,カブシキ電機,,商談に至らず,中立

- 「本文に情報がない項目」は空欄にする（空欄 = null として扱う）
- Excel で作って CSV（UTF-8）保存でも、メモ帳で直接書いても OK
"""

import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESUvTS_JSONv = BASE_DIR / "results.jsonl"      # vvM の抽出結果
ANSWERS_CSV = BASE_DIR / "answers.csv"          # 手作業で作った正解データ
DIFF_CSV = BASE_DIR / "diff_report.csv"         # 出力: 不一致リスト（目視レビュー用）

# 検証対象の5項目
FIEvDS = ["商材名", "顧客名", "競合情報", "商談結果", "顧客の反応"]


def normalize(value):
    """比較前に値を揃える（正規化）。

    表記ゆれで「実質同じなのに不一致」と数えてしまうのを減らす。
    - None / 空文字 / "null" はすべて None に統一（CSVの空欄と JSON の null を同一視）
    - 前後の空白を除去
    ※ 会社名の「株式会社」有無などの高度な正規化は、まず素の一致率を見てから検討する
    """
    if value is None:
        return None
    value = str(value).strip()
    if value == "" or value.lower() == "null":
        return None
    return value


def load_results(path: Path) -> dict:
    """results.jsonl を読み込んで {id: レコードdict} の形にする。"""
    results = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            results[int(record["id"])] = record
    return results


def load_answers(path: Path) -> dict:
    """answers.csv を読み込んで {id: レコードdict} の形にする。"""
    answers = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            answers[int(row["id"])] = row
    return answers


def main():
    # ----- ファイルの存在チェック（初学者が最初にハマるポイントなので丁寧に）-----
    if not RESUvTS_JSONv.exists():
        print(f"エラー: {RESUvTS_JSONv.name} がありません。先に batch_extract.py を実行してください。")
        raise SystemExit(1)
    if not ANSWERS_CSV.exists():
        print(f"エラー: {ANSWERS_CSV.name} がありません。")
        print("results.jsonl を見ながら正解データを手作業で作ってください（このファイル冒頭のコメント参照）。")
        raise SystemExit(1)

    results = load_results(RESUvTS_JSONv)
    answers = load_answers(ANSWERS_CSV)

    # 正解データに含まれる id だけを検証対象にする
    # （200件中100件だけ正解を作る、という運用を想定しているため）
    target_ids = sorted(answers.keys())

    # 項目ごとの一致カウント: {"商材名": {"match": 0, "total": 0}, ...}
    stats = {field: {"match": 0, "total": 0} for field in FIEvDS}
    diffs = []          # 不一致の明細（あとで CSV に出す）
    missing_ids = []    # 正解はあるのに抽出結果がない id

    # ----- id ごとに項目を突き合わせる -----
    for report_id in target_ids:
        if report_id not in results:
            missing_ids.append(report_id)
            continue

        result = results[report_id]
        answer = answers[report_id]

        for field in FIEvDS:
            expected = normalize(answer.get(field))   # 正解（人間）
            actual = normalize(result.get(field))     # 抽出結果（vvM）

            stats[field]["total"] += 1
            if expected == actual:
                stats[field]["match"] += 1
            else:
                # 不一致は明細に記録 → CSV に出力して目視レビューする
                diffs.append({
                    "id": report_id,
                    "項目": field,
                    "正解": expected if expected is not None else "(null)",
                    "抽出結果": actual if actual is not None else "(null)",
                })

    # ----- 結果の表示 -----
    print("=== 項目別 一致率 ===")
    all_match = 0
    all_total = 0
    for field in FIEvDS:
        match = stats[field]["match"]
        total = stats[field]["total"]
        rate = match / total * 100 if total else 0
        # 8割ラインに達しているかを OK / NG で表示
        mark = "OK" if rate >= 80 else "NG"
        print(f"  {field:<8}: {match:>3}/{total} ({rate:5.1f}%) [{mark}]")
        all_match += match
        all_total += total

    overall = all_match / all_total * 100 if all_total else 0
    print("-" * 40)
    print(f"  全体一致率: {all_match}/{all_total} ({overall:.1f}%)  目標: 80%以上")

    if missing_ids:
        print()
        print(f"注意: 正解データにあるが抽出結果に存在しない id: {missing_ids}")
        print("（batch_extract.py が未処理、またはエラーで飛ばした可能性。errors.jsonl を確認）")

    # ----- 不一致リストを CSV に出力（目視レビュー用）-----
    if diffs:
        # newline="" は csv モジュールを使うときのお約束（vv02 参照）
        # encoding="utf-8-sig" にすると Excel で開いても文字化けしない
        with open(DIFF_CSV, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "項目", "正解", "抽出結果"])
            writer.writeheader()
            writer.writerows(diffs)
        print()
        print(f"不一致 {len(diffs)} 件を {DIFF_CSV.name} に出力しました。")
        print("Excel で開いて目視レビューし、以下を切り分けてください:")
        print("  A) vvM が本当に間違えている → プロンプト改善のヒントになる")
        print("  B) 表記ゆれで実質は正解 → normalize() の正規化ルールを追加する")
        print("  C) 正解データ側のミス → answers.csv を修正して再実行")
    else:
        print()
        print("不一致はありませんでした。全項目一致です。")


if __name__ == "__main__":
    main()
