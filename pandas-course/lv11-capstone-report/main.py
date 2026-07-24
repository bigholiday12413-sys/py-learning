"""
pandas講座 Lv11 - 総合演習：月次売上レポートの自動生成
========================================================
Lv01〜Lv10で学んだことをすべて組み合わせ、
「汚れた生データ → クレンジング → 結合 → 集計 → グラフ → Excelレポート」
という実務の一連の流れを1本のスクリプトにする。

処理の流れ（カッコ内は対応するレベル）:
  1. データの読み込みと品質チェック（Lv01）
  2. クレンジング: 表記ゆれ・欠損値・重複の処理（Lv03, Lv04）
  3. 顧客マスタとの結合（Lv07）
  4. 日付処理と月次列の追加（Lv09）
  5. カテゴリ別・月次・地域別の集計とランキング（Lv05, Lv06）
  6. ピボットテーブルの作成（Lv08）
  7. グラフの作成（Lv10）
  8. 複数シート・グラフ付きExcelレポートの出力

実行方法:
    python main.py
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from openpyxl.drawing.image import Image as XLImage

matplotlib.use("Agg")

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 日本語フォント設定（Lv10と同じ）
available_fonts = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
for font_name in ["IPAexGothic", "Noto Sans CJK JP", "Meiryo", "Hiragino Sans", "Yu Gothic"]:
    if font_name in available_fonts:
        plt.rcParams["font.family"] = font_name
        break
plt.rcParams["axes.unicode_minus"] = False


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


# ============================================================
# 1. データの読み込みと品質チェック（Lv01・Lv04の復習）
# ============================================================

section("1. データ読み込みと品質チェック")

raw = pd.read_csv(DATA_DIR / "orders_raw.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")

print(f"読み込み件数: {len(raw)} 件")
print(f"\n--- 欠損件数（列ごと）---")
print(raw.isna().sum())
print(f"\n--- 完全重複行: {raw.duplicated().sum()} 件 ---")
print(f"\n--- category 列のユニーク値（表記ゆれの確認）---")
for cat in raw["category"].unique():
    print(f"  {cat!r}")  # repr() で前後の空白を可視化（Lv03の手法）


# ============================================================
# 2. クレンジング（Lv03・Lv04の復習）
# ============================================================

section("2. クレンジング")

df = raw.copy()  # 元データは変更せず複製してから作業する

# --- 表記ゆれの除去: category の前後の空白を除去 ---
df["category"] = df["category"].str.strip()
print("--- strip後の category ユニーク値 ---")
print(sorted(df["category"].unique()))

# --- 重複行を削除 ---
before = len(df)
df = df.drop_duplicates()
print(f"\n重複削除: {before} 件 → {len(df)} 件")

# --- 欠損値の補完（列の意味に応じて方針を決める。Lv04参照） ---
# quantity（数量）の欠損 → 1 で補完（最小注文数と仮定）
df["quantity"] = df["quantity"].fillna(1)

# unit_price（単価）の欠損 → 同じカテゴリの平均単価で補完
# transform("mean"): グループごとの平均を「元の行数のまま」返す（fillnaにそのまま使える）
category_avg_price = df.groupby("category")["unit_price"].transform("mean")
df["unit_price"] = df["unit_price"].fillna(category_avg_price.round(0))

print(f"\n補完後の欠損件数:\n{df.isna().sum()}")


# ============================================================
# 3. 顧客マスタとの結合（Lv07の復習）
# ============================================================

section("3. 顧客マスタとの結合")

merged = df.merge(customers, on="customer_id", how="left", validate="many_to_one")
print(f"結合前: {len(df)} 行 / 結合後: {len(merged)} 行（一致するはず）")

unmatched = merged[merged["customer_name"].isna()]
if len(unmatched) > 0:
    print(f"⚠ 顧客マスタに見つからない注文: {len(unmatched)} 件")
else:
    print("✔ 全注文が顧客マスタと正しく紐づいた")


# ============================================================
# 4. 日付処理（Lv09の復習）
# ============================================================

section("4. 日付処理")

merged["order_date"] = pd.to_datetime(merged["order_date"])
merged["month"] = merged["order_date"].dt.strftime("%Y-%m")
merged["subtotal"] = merged["quantity"] * merged["unit_price"]  # Lv03の復習

print(merged[["order_date", "month", "category", "quantity", "unit_price", "subtotal"]].head())


# ============================================================
# 5. 集計とランキング（Lv05・Lv06の復習）
# ============================================================

section("5. 集計とランキング")

category_ranking = (
    merged.groupby("category")["subtotal"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
category_ranking.columns = ["カテゴリ", "売上合計"]
print("--- カテゴリ別売上ランキング ---")
print(category_ranking)

region_summary = (
    merged.groupby("region")
    .agg(件数=("order_id", "count"), 売上合計=("subtotal", "sum"), 平均単価=("unit_price", "mean"))
    .round(0)
    .sort_values("売上合計", ascending=False)
)
print("\n--- 地域別集計 ---")
print(region_summary)


# ============================================================
# 6. ピボットテーブル（Lv08の復習）
# ============================================================

section("6. 月次×カテゴリ ピボットテーブル")

monthly_category_pivot = pd.pivot_table(
    merged, index="month", columns="category", values="subtotal",
    aggfunc="sum", fill_value=0, margins=True, margins_name="合計",
)
print(monthly_category_pivot)


# ============================================================
# 7. グラフ作成（Lv10の復習）
# ============================================================

section("7. グラフ作成")

monthly_total = merged.groupby("month")["subtotal"].sum()

fig, ax = plt.subplots(figsize=(7, 4))
monthly_total.plot(kind="line", marker="o", ax=ax, title="月次売上推移")
ax.set_ylabel("売上（円）")
plt.tight_layout()

chart_path = OUTPUT_DIR / "_monthly_trend.png"
plt.savefig(chart_path)
plt.close()
print(f"グラフ保存: {chart_path}")


# ============================================================
# 8. Excelレポートの出力（複数シート + グラフ埋め込み）
# ============================================================

section("8. Excelレポートの出力")

report_path = OUTPUT_DIR / "monthly_report.xlsx"

with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
    # --- シート1: クレンジング後の生データ ---
    merged[
        ["order_id", "order_date", "month", "customer_name", "region",
         "category", "product", "quantity", "unit_price", "subtotal"]
    ].to_excel(writer, sheet_name="クレンジング後データ", index=False)

    # --- シート2: カテゴリ別ランキング ---
    category_ranking.to_excel(writer, sheet_name="カテゴリ別ランキング", index=False)

    # --- シート3: 地域別集計 ---
    region_summary.to_excel(writer, sheet_name="地域別集計")

    # --- シート4: 月次×カテゴリ ピボット ---
    monthly_category_pivot.to_excel(writer, sheet_name="月次×カテゴリ")

    # --- シート5: 概要（グラフ画像を埋め込む） ---
    # pd.ExcelWriter(engine="openpyxl") の場合、writer.book は openpyxl の Workbook。
    # pandasのto_excel()を使わず、openpyxlの機能で直接シートを作って画像を貼れる。
    summary_sheet = writer.book.create_sheet("概要", 0)  # index=0 で先頭に挿入
    summary_sheet["B2"] = "Zakka Store 月次売上レポート"
    summary_sheet["B4"] = "対象期間:"
    summary_sheet["C4"] = f"{merged['order_date'].min().date()} 〜 {merged['order_date'].max().date()}"
    summary_sheet["B5"] = "総売上:"
    summary_sheet["C5"] = f"{merged['subtotal'].sum():,.0f} 円"
    summary_sheet["B6"] = "対象件数:"
    summary_sheet["C6"] = f"{len(merged)} 件"

    img = XLImage(str(chart_path))
    summary_sheet.add_image(img, "B9")  # B9セルを起点にグラフ画像を配置

print(f"レポート保存完了: {report_path}")


# ============================================================
# まとめ
# ============================================================
section("まとめ: このスクリプトが行った全ステップ")

print(f"""
  1. 読み込み・品質チェック   Lv01, Lv04
  2. 表記ゆれ・欠損値・重複   Lv03, Lv04
  3. 顧客マスタとの結合       Lv07
  4. 日付処理・列追加         Lv09, Lv03
  5. 集計とランキング         Lv05, Lv06
  6. ピボットテーブル         Lv08
  7. グラフ作成               Lv10
  8. Excelレポート出力        （openpyxl埋め込み。メインコース lv10-excel-report と同じ技術）

  生成物:
    {report_path}
    {chart_path}

  ★ これが「生データ→分析→レポート」の実務パイプラインの最小構成。
    Lv1〜10で学んだ部品を、順番に組み合わせているだけ。
""")
