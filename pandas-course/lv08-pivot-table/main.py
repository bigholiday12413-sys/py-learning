"""
pandas講座 Lv08 - ピボットテーブル（pivot_table）
===================================================
Excelでマウスをドラッグ&ドロップして作る「ピボットテーブル」を、
コードで再現する。groupby の「2軸バージョン」と捉えると理解しやすい。

実行方法:
    python main.py
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


orders = pd.read_csv(DATA_DIR / "orders.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")
orders["subtotal"] = orders["quantity"] * orders["unit_price"]
orders["month"] = orders["order_date"].str[:7]  # "2026-04-15" → "2026-04"（Lv09で詳しく扱う）

df = orders.merge(customers, on="customer_id")  # Lv07で学んだmerge

section("0. 結合済みデータ（region付き）")
print(df[["order_date", "month", "region", "category", "subtotal"]].head())


# ============================================================
# 1. Excelのピボットテーブルとの対応関係
# ============================================================
# Excelでピボットテーブルを作るとき、4つの枠にフィールドをドラッグする:
#   行フィールド → index
#   列フィールド → columns
#   値フィールド → values
#   集計方法     → aggfunc
# pivot_table() はこの4つを引数として指定するだけ。

section("1. pivot_table の基本形")

print("""
  Excelのピボットテーブル        pivot_table() の引数
  ─────────────────────────────  ─────────────────────
  「行」の枠にドラッグ           index=
  「列」の枠にドラッグ           columns=
  「値」の枠にドラッグ           values=
  集計方法（合計/平均/個数）     aggfunc=
""")

pivot1 = pd.pivot_table(
    df,
    index="category",       # 行: カテゴリ
    columns="region",       # 列: 地域
    values="subtotal",      # 値: 売上
    aggfunc="sum",          # 集計方法: 合計
    fill_value=0,           # 組み合わせが無いセルは0で埋める（NaNのままだと見にくい）
)
print(pivot1)


# ============================================================
# 2. 月次 × カテゴリ のピボット ─ 実務で一番よく作る形
# ============================================================

section("2. 月次売上のピボット（月 × カテゴリ）")

pivot2 = pd.pivot_table(
    df,
    index="month",
    columns="category",
    values="subtotal",
    aggfunc="sum",
    fill_value=0,
)
print(pivot2)

# --- margins=True: 縦横の合計（総計行・総計列）を追加する ---
# Excelのピボットテーブルで「総計」にチェックを入れるのと同じ
section("2b. margins=True: 総計行・総計列を追加")

pivot2_with_total = pd.pivot_table(
    df,
    index="month",
    columns="category",
    values="subtotal",
    aggfunc="sum",
    fill_value=0,
    margins=True,           # 総計を追加
    margins_name="合計",     # 総計行・列の名前
)
print(pivot2_with_total)


# ============================================================
# 3. 集計方法を複数同時に指定する
# ============================================================

section("3. aggfunc にリストを渡す")

pivot3 = pd.pivot_table(
    df,
    index="category",
    values="subtotal",
    aggfunc=["sum", "mean", "count"],
)
print(pivot3.round(0))


# ============================================================
# 4. crosstab ─ 「件数」だけのクロス集計
# ============================================================
# 「売上」のような数値ではなく「件数」だけを知りたい場合、
# pivot_table(aggfunc="count") でも書けるが、crosstab の方が簡潔。

section("4. crosstab(): 件数のクロス集計")

ct = pd.crosstab(df["category"], df["region"])
print(ct)

print("\n--- normalize='index' で行ごとの構成比(%)にする ---")
ct_pct = (pd.crosstab(df["category"], df["region"], normalize="index") * 100).round(1)
print(ct_pct)


# ============================================================
# 5. ピボット結果をExcelに出す
# ============================================================
# ピボット結果はただのDataFrameなので、Lv14/メインコースLv10と同じ書き出しができる

section("5. Excelへの書き出し")

output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True)
output_path = output_dir / "pivot_report.xlsx"

with pd.ExcelWriter(output_path) as writer:
    pivot1.to_excel(writer, sheet_name="カテゴリ×地域")
    pivot2_with_total.to_excel(writer, sheet_name="月次×カテゴリ")

print(f"保存完了: {output_path}")


# ============================================================
# まとめ
# ============================================================
section("まとめ")

print("""
  Excelのピボットテーブル        pandas
  ─────────────────────────────  ─────────────────────────────────────────
  行・列・値・集計方法をドラッグ pd.pivot_table(df, index=, columns=, values=, aggfunc=)
  空欄セルを0にする              fill_value=0
  総計行・総計列を追加           margins=True
  件数だけのクロス集計           pd.crosstab(df["列1"], df["列2"])
  構成比(%)                      crosstab(..., normalize="index")

  ★ groupby は「1軸の集計」、pivot_table は「2軸の集計を表の形に
    並べたもの」。中身はどちらもgroupbyの考え方の応用。
""")
