"""
pandas講座 Lv06 - 並べ替えとランキング
========================================
「売上トップ5」「成績の悪い順」のような、実務で頻出の
「並べ替え」と「順位付け」を扱う。groupby(Lv05)の結果に対して
使うことも多いので、セットで身につける。

実行方法:
    python main.py
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


orders = pd.read_csv(DATA_DIR / "orders.csv")
orders["subtotal"] = orders["quantity"] * orders["unit_price"]

section("0. データ確認")
print(orders.head())


# ============================================================
# 1. sort_values ─ 基本の並べ替え
# ============================================================

section("1. sort_values(): 基本の並べ替え")

# --- 降順（高い順） ---
print("--- 注文額の高い順 トップ5 ---")
top5 = orders.sort_values("subtotal", ascending=False).head(5)
print(top5[["order_id", "product", "quantity", "unit_price", "subtotal"]])

# --- 昇順（低い順。ascendingのデフォルトはTrue） ---
print("\n--- 注文額の低い順 トップ5 ---")
bottom5 = orders.sort_values("subtotal").head(5)
print(bottom5[["order_id", "product", "subtotal"]])


# ============================================================
# 2. 複数キーでの並べ替え
# ============================================================
# 「カテゴリで大きくまとめつつ、その中では価格が高い順」のような
# 複合的な並べ替えは、列のリストと ascending のリストを対応させて渡す

section("2. 複数キーでの並べ替え")

multi_sort = orders.sort_values(["category", "subtotal"], ascending=[True, False])
print("--- カテゴリ順（昇順）、同じカテゴリ内は注文額の高い順 ---")
print(multi_sort[["category", "product", "subtotal"]].head(10))


# ============================================================
# 3. nlargest / nsmallest ─ トップNの近道
# ============================================================
# sort_values().head(N) と同じ結果を、より意図が伝わる書き方で得られる

section("3. nlargest() / nsmallest(): トップNの近道")

print("--- nlargest(3, 'subtotal'): 注文額トップ3 ---")
print(orders.nlargest(3, "subtotal")[["product", "subtotal"]])

print("\n--- nsmallest(3, 'subtotal'): 注文額ワースト3 ---")
print(orders.nsmallest(3, "subtotal")[["product", "subtotal"]])


# ============================================================
# 4. groupby と組み合わせる ─ 「カテゴリ別売上ランキング」
# ============================================================
# Lv05のgroupbyの結果（Series）にもsort_valuesが使える。
# 実務で最頻出の組み合わせパターン。

section("4. groupby + sort_values: カテゴリ別売上ランキング")

ranking = (
    orders.groupby("category")["subtotal"]
    .sum()
    .sort_values(ascending=False)
)
print(ranking)

print("\n--- 順位も付けたい場合: reset_index() で表に戻してから連番を振る ---")
ranking_df = ranking.reset_index()  # Series → DataFrame に戻し、indexを連番に戻す
ranking_df.index = ranking_df.index + 1  # 1位から始まるように調整
ranking_df.index.name = "順位"
print(ranking_df)


# ============================================================
# 5. rank() ─ 各行に順位を付ける
# ============================================================
# 並べ替えではなく「元の順序を保ったまま、順位という列を追加したい」ときに使う

section("5. rank(): 順位を列として追加する")

orders["subtotal_rank"] = orders["subtotal"].rank(ascending=False, method="min").astype(int)
# method="min": 同額の場合は同じ順位を付け、次の順位を飛ばす（1,1,3,4...のような振り方）
top_ranked = orders.sort_values("subtotal_rank").head(5)
print(top_ranked[["order_id", "product", "subtotal", "subtotal_rank"]])


# ============================================================
# 6. reset_index() ─ groupby・sort後の「index を整える」定番操作
# ============================================================
# groupbyやsort_valuesの後は、indexが元の行番号のまま(飛び飛び)になっていることが多い。
# reset_index() で 0,1,2... の連番に戻すと、後続処理やExcel出力がきれいになる。

section("6. reset_index(): indexを連番に戻す")

sorted_orders = orders.sort_values("subtotal", ascending=False).head(5)
print("--- reset_index前（indexが元の行番号のまま）---")
print(sorted_orders.index.tolist())

sorted_orders_clean = sorted_orders.reset_index(drop=True)
# drop=True: 古いindexを列として残さず、そのまま捨てる
print("\n--- reset_index後（0始まりの連番）---")
print(sorted_orders_clean.index.tolist())


# ============================================================
# まとめ
# ============================================================
section("まとめ")

print("""
  やりたいこと                          書き方
  ─────────────────────────────────────  ─────────────────────────────────
  高い順に並べ替え                      df.sort_values("列", ascending=False)
  複数キーで並べ替え                    df.sort_values(["列1","列2"], ascending=[True,False])
  トップN（近道）                       df.nlargest(N, "列")  /  df.nsmallest(N, "列")
  グループ別ランキング                  df.groupby("列").sum().sort_values(...)
  各行に順位を振る                      df["列"].rank(ascending=False)
  indexを連番に戻す                     df.reset_index(drop=True)

  ★ groupby → sort_values → reset_index はセットで使うことが多い
    「集計してランキングを作る」の定番パターン。
""")
