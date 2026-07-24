"""
pandas講座 Lv05 - グループ集計（groupby）
===========================================
「カテゴリ別の売上」「地域ごとの平均」のような
Excelの SUMIFS / COUNTIFS / AVERAGEIFS に相当する処理を、
groupby という1つの仕組みで統一的に扱う。

実行方法:
    python main.py
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


orders = pd.read_csv(DATA_DIR / "orders.csv")
orders["subtotal"] = orders["quantity"] * orders["unit_price"]  # Lv03で学んだ列追加

section("0. データ確認（Zakka Store 注文データ 全81件）")
print(f"件数: {len(orders)} 件 / 期間: {orders['order_date'].min()} 〜 {orders['order_date'].max()}")
print(orders.head())


# ============================================================
# 1. groupby の基本形 ─ 「〜ごとに」を宣言する
# ============================================================
# df.groupby("グループ化する列")["集計したい列"].集計方法()
# という3ステップの組み立てで読む。

section("1. groupby の基本形")

print("--- カテゴリごとの売上合計 ---")
by_category = orders.groupby("category")["subtotal"].sum()
print(by_category)

print(f"\n型を確認: {type(by_category)}")  # groupbyの結果もSeriesになる
print(f"型を確認（sort_values前）: index = {list(by_category.index)}")

# 見やすく並べ替える（Lv06で本格的に扱うが、ここでも軽く使う）
print("\n--- 売上の高い順に並べ替え ---")
print(by_category.sort_values(ascending=False))


# ============================================================
# 2. 複数の集計を同時に ─ agg()
# ============================================================
# 「合計だけ」でなく「件数・平均・最大」も同時に見たいときは agg() にリストを渡す

section("2. agg(): 複数の集計方法を同時に")

summary = orders.groupby("category")["subtotal"].agg(["count", "sum", "mean", "max"]).round(0)
print(summary.sort_values("sum", ascending=False))


# ============================================================
# 3. 集計後の列に日本語名を付ける（named aggregation）
# ============================================================
# agg(新しい列名=("元の列", "集計方法")) の形で書くと、
# 結果の列名を自分で指定できる。レポートにそのまま使える形になる。

section("3. named aggregation: 列名を指定して集計")

report = orders.groupby("category").agg(
    件数=("order_id", "count"),
    売上合計=("subtotal", "sum"),
    平均注文額=("subtotal", "mean"),
).round(0)
print(report.sort_values("売上合計", ascending=False))


# ============================================================
# 4. 複数キーでのグループ化
# ============================================================
# groupby(["列1", "列2"]) のようにリストを渡すと、
# 「列1 × 列2 の組み合わせごと」に集計できる（Excelピボットの2軸に相当。Lv08で発展）

section("4. 複数キーでのグループ化")

# customers.csv と結合していないので、ここでは注文データだけで完結する例:
# カテゴリ × 商品 で集計
by_cat_product = orders.groupby(["category", "product"])["subtotal"].sum()
print(by_cat_product.head(10))


# ============================================================
# 5. value_counts() ─ 「件数を数える」の最短ルート
# ============================================================
# 「グループごとの合計」ではなく「グループごとの件数」だけでよいなら、
# groupby(...).size() より value_counts() の方が短く書ける

section("5. value_counts(): 件数だけのショートカット")

print("--- カテゴリ別の注文件数 ---")
print(orders["category"].value_counts())

print("\n--- 正規化オプション: 割合(%)で見る ---")
print((orders["category"].value_counts(normalize=True) * 100).round(1))


# ============================================================
# 6. groupby の結果をそのままグラフに（先取り）
# ============================================================
# groupby の結果は Series/DataFrame なので、そのまま .plot() できる。
# グラフの本格的な扱いは Lv10 で行うので、ここでは「できる」ことだけ紹介する。

section("6. （先取り）groupbyの結果はそのままグラフ化できる")
print("例: orders.groupby('category')['subtotal'].sum().plot(kind='bar')")
print("→ 詳しくは pandas-course/lv10-visualization で扱う")


# ============================================================
# まとめ
# ============================================================
section("まとめ")

print("""
  やりたいこと                        書き方
  ───────────────────────────────────  ─────────────────────────────────────────
  カテゴリごとの合計                  df.groupby("category")["列"].sum()
  複数の集計を同時に                  df.groupby("category")["列"].agg(["count","sum","mean"])
  集計結果に日本語名を付ける          df.groupby("category").agg(件数=("列","count"), ...)
  2軸でグループ化                     df.groupby(["列1","列2"])["列3"].sum()
  件数だけ数える（最短）              df["列"].value_counts()
  割合(%)で見る                       df["列"].value_counts(normalize=True)

  ★ groupby は「グループ化する列」→「集計したい列」→「集計方法」の
    3ステップで組み立てると迷わない。
""")
