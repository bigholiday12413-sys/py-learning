"""
pandas講座 Lv02 - 抽出とフィルタリング（絞り込み）
====================================================
「条件に合う行だけを取り出す」は、pandas を使う理由の半分を占める操作。
Excel の「フィルタ」機能をコードで再現する、というイメージで読み進める。

実行方法:
    python main.py
"""

from pathlib import Path

import pandas as pd

DATA_CSV = Path(__file__).parent / "data" / "orders.csv"


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


df = pd.read_csv(DATA_CSV)

section("0. 読み込んだデータ（Zakka Store注文データ 先頭20件）")
print(df.head())
print(f"\n列: {list(df.columns)}")


# ============================================================
# 1. ブールインデックス ─ pandas最大の発想転換
# ============================================================
# df["列"] >= 値 と書くと、「各行が条件を満たすか」の True/False が
# 並んだ Series が返る。これを df[...] に渡すと、True の行だけが残る。

section("1. ブールインデックス（絞り込みの基本）")

# --- まず条件だけを見てみる ---
condition = df["quantity"] >= 2
print("--- df['quantity'] >= 2 の中身（先頭5件）---")
print(condition.head())
print(f"（True: {condition.sum()} 件 / 全 {len(df)} 件）")
# ↑ True は 1、False は 0 として扱われるので sum() で件数を数えられる

# --- 条件を df[] に渡すと、絞り込まれた表になる ---
print("\n--- df[df['quantity'] >= 2] （数量2個以上の注文）---")
result = df[df["quantity"] >= 2]
print(result)


# ============================================================
# 2. 複数条件 ─ & (かつ) と | (または)
# ============================================================
# Python の and / or ではなく、必ず & と | を使う。
# さらに各条件を () で囲むのが文法上の約束（忘れるとエラーになる最頻出ミス）。

section("2. 複数条件の絞り込み")

# --- かつ (&) ---
print("--- 数量2個以上 かつ 単価2000円以上 ---")
both = df[(df["quantity"] >= 2) & (df["unit_price"] >= 2000)]
print(both)

# --- または (|) ---
print("\n--- カテゴリが文房具 または インテリア ---")
either = df[(df["category"] == "文房具") | (df["category"] == "インテリア")]
print(either[["order_id", "category", "product"]])

# --- 否定 (~) ---
print("\n--- カテゴリが文房具『以外』 ---")
not_stationery = df[~(df["category"] == "文房具")]
print(f"件数: {len(not_stationery)} 件（元は {len(df)} 件）")


# ============================================================
# 3. isin() ─ 「複数の候補のどれか」を簡潔に書く
# ============================================================
# category == "A" | category == "B" | category == "C" ... を何度も書くより、
# isin() でリストを渡す方が読みやすい

section("3. isin(): 複数候補のいずれかに一致")

target_categories = ["文房具", "インテリア", "アウトドア"]
matched = df[df["category"].isin(target_categories)]
print(f"対象カテゴリ {target_categories} に一致: {len(matched)} 件")
print(matched["category"].value_counts())
# value_counts(): 各値が何回出現するかを数える。集計の入り口（Lv05で本格的に扱う）


# ============================================================
# 4. loc[] ─ 「行の条件」と「列の指定」を同時に書く
# ============================================================
# df[条件][["列1","列2"]] と書くこともできるが、
# df.loc[条件, ["列1","列2"]] の方が「行の絞り込みと列の選択を1回で書く」意図が伝わる

section("4. loc[]: 行条件と列指定を同時に")

print("--- 単価3000円以上の order_id と product だけ ---")
high_price = df.loc[df["unit_price"] >= 3000, ["order_id", "product", "unit_price"]]
print(high_price)


# ============================================================
# 5. query() ─ Excelのフィルタに近い書き方
# ============================================================
# 文字列で条件を書けるので、df["列"] の繰り返しがなく読みやすくなることが多い。
# 列名にスペースなどが無ければ、変数のように書ける。

section("5. query(): 文字列で条件を書く")

print("--- query('quantity >= 2 and unit_price >= 2000') ---")
print(df.query("quantity >= 2 and unit_price >= 2000"))

# 外部の変数を条件に使いたいときは @ を付ける
min_qty = 3
print(f"\n--- query('quantity >= @min_qty')  (min_qty={min_qty}) ---")
print(df.query("quantity >= @min_qty"))


# ============================================================
# まとめ
# ============================================================
section("まとめ")

print("""
  やりたいこと                    書き方
  ───────────────────────────────  ─────────────────────────────────────
  条件で絞り込む                  df[df["列"] >= 値]
  かつ / または                   df[(条件1) & (条件2)]  /  (条件1) | (条件2)
  否定                             df[~条件]
  複数候補のどれか                df[df["列"].isin([...])]
  行の条件 + 列の指定を同時に     df.loc[条件, ["列1","列2"]]
  文字列で条件を書く（読みやすい）df.query("列 >= 値 and 列2 == 'X'")

  ★ &・| を使うときは各条件を () で必ず囲む。これが最頻出のエラー原因。
""")
