"""
pandas講座 Lv07 - テーブルの結合（merge / concat）
====================================================
Excelで「VLOOKUP / XLOOKUP で他のシートから情報を持ってくる」作業を、
pandas では merge() という1つの関数で行う。

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

section("0. 結合する2つの表")
print("--- orders（注文）: customer_id で顧客に紐づく ---")
print(orders[["order_id", "customer_id", "product", "subtotal"]].head())
print(f"\n--- customers（顧客マスタ）: {len(customers)} 名 ---")
print(customers)


# ============================================================
# 1. merge の基本形 ─ VLOOKUP の発想を思い出す
# ============================================================
# VLOOKUP は「注文データの customer_id を検索キーにして、
#            顧客マスタから customer_name 等を持ってくる」処理。
# merge() は「2つの表を、共通の列（キー）で横につなげる」処理として、
# これを一度に・全行に対して行う。

section("1. merge(): 顧客名・地域を注文データに付ける")

merged = orders.merge(customers, on="customer_id")
# on="customer_id": 両方の表に共通する列名を「結合キー」として指定する
print(merged[["order_id", "customer_id", "customer_name", "region", "product", "subtotal"]].head())

print(f"\n結合前 orders: {len(orders)} 行 / 結合後: {len(merged)} 行")
# ★ 行数が変わっていないかを必ず確認する。増減していたら結合キーの重複を疑う（3章で解説）


# ============================================================
# 2. how= ─ 結合の種類（inner / left / right / outer）
# ============================================================
# VLOOKUPと違い、merge()は「一致しない行をどうするか」を選べる。
# これがExcelのVLOOKUPよりmergeが優れている点の1つ。

section("2. how=: 結合の種類")

print("""
  how の種類    意味                                    使う場面
  ────────────  ──────────────────────────────────────  ────────────────────────
  "inner"（既定）両方に存在するキーだけ残す              通常の結合。デフォルト
  "left"        左側(orders)は全部残す。無ければNaN     「注文は全部見たい」とき
  "right"       右側(customers)は全部残す                「顧客は全部見たい」とき
  "outer"       どちらか一方にあれば残す（完全外部結合） 抜け漏れの調査
""")

# --- left: 顧客マスタに無い customer_id があっても、注文行は残す ---
left_merged = orders.merge(customers, on="customer_id", how="left")
print(f"--- how='left' の結果件数: {len(left_merged)} 行（orders件数と一致するはず）---")

# --- 顧客マスタに存在しないIDが混ざっていたケースを再現して確認する ---
orders_with_bad_id = pd.concat([
    orders,
    pd.DataFrame([{"order_id": "O9999", "order_date": "2026-07-01",
                    "customer_id": "C999", "category": "文房具",
                    "product": "テスト商品", "quantity": 1, "unit_price": 100,
                    "subtotal": 100}]),
], ignore_index=True)

left_check = orders_with_bad_id.merge(customers, on="customer_id", how="left")
unmatched = left_check[left_check["customer_name"].isna()]
print(f"\n--- 顧客マスタに存在しない customer_id の注文: {len(unmatched)} 件 ---")
print(unmatched[["order_id", "customer_id", "product"]])
print("→ how='left' + isna() チェックは「マスタの抜け漏れ」を見つける定番テクニック")


# ============================================================
# 3. 結合キーの重複に注意 ─ 「行が増える」事故
# ============================================================
# merge で最もハマりやすい罠: 結合キーが「相手側で重複」していると、
# 一致した組み合わせの数だけ行が増える（1対多、多対多になる）。

section("3. 注意: キーの重複で行が増える罠")

# customers に同じ customer_id が2行あるケースを再現
customers_dup = pd.concat([customers, customers.iloc[[0]]], ignore_index=True)
print(f"customers_dup の行数: {len(customers_dup)}（本来12名のはずが13行）")

merged_exploded = orders.merge(customers_dup, on="customer_id")
print(f"結合後の行数: {len(merged_exploded)}（orders は {len(orders)} 行だったのに増えている！）")
print("→ 結合前後で行数を必ず確認する習慣が、この事故を防ぐ")

# --- validate引数で「意図しない重複」をエラーとして検出する（安全策） ---
print("\n--- validate='many_to_one' で重複を検出する ---")
try:
    orders.merge(customers_dup, on="customer_id", validate="many_to_one")
except pd.errors.MergeError as e:
    print(f"MergeError が発生（想定通り）: {str(e)[:80]}...")


# ============================================================
# 4. 列名が違うときの結合 ─ left_on / right_on
# ============================================================
# 実務では「注文側は customer_id」「マスタ側は id」のように
# 列名が食い違っていることがよくある。その場合の書き方。

section("4. left_on / right_on: 列名が違う場合")

customers_renamed = customers.rename(columns={"customer_id": "id"})
merged_diff_name = orders.merge(customers_renamed, left_on="customer_id", right_on="id")
print(merged_diff_name[["order_id", "customer_id", "id", "customer_name"]].head(3))


# ============================================================
# 5. concat ─ 同じ形の表を縦に積む
# ============================================================
# merge が「横に列を増やす」のに対し、concat は「縦に行を増やす」。
# 「4月分.csv」「5月分.csv」のような月ごとのファイルを1つにまとめる場面で使う。

section("5. concat(): 同じ形の表を縦に積む")

april = orders[orders["order_date"].str.startswith("2026-04")]
may = orders[orders["order_date"].str.startswith("2026-05")]

combined = pd.concat([april, may], ignore_index=True)
# ignore_index=True: 積んだ後にindexを振り直す（付けないと重複したindexが残る）
print(f"4月: {len(april)} 件 + 5月: {len(may)} 件 → concat後: {len(combined)} 件")


# ============================================================
# まとめ
# ============================================================
section("まとめ")

print("""
  やりたいこと                          書き方
  ─────────────────────────────────────  ─────────────────────────────────
  共通の列で2つの表を横に結合           df1.merge(df2, on="共通列")
  片方は全部残したい（VLOOKUP風）       df1.merge(df2, on="列", how="left")
  マスタの抜け漏れを見つける            how="left" 後に isna() でチェック
  意図しない行数増加を防ぐ              merge(..., validate="many_to_one" 等)
  列名が違う場合                        merge(left_on="列A", right_on="列B")
  同じ形の表を縦に積む                  pd.concat([df1, df2], ignore_index=True)

  ★ merge の後は必ず「結合前後で行数がどう変わったか」を確認する。
    これがVLOOKUPよりmergeが危険にも安全にもなりうる最大のポイント。
""")
