"""
pandas講座 Lv03 - 列の操作と文字列処理
========================================
実務のデータは、Excelから吐き出したCSVのように
「前後に余計な空白がある」「表記ゆれがある」ことが非常に多い。
このレベルでは、列を追加・計算する方法と、文字列データを整える方法を学ぶ。

実行方法:
    python main.py
"""

from pathlib import Path

import pandas as pd

DATA_CSV = Path(__file__).parent / "data" / "orders_with_names.csv"


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


df = pd.read_csv(DATA_CSV)

section("0. 読み込んだデータ")
print(df[["order_id", "product", "quantity", "unit_price", "customer_name_raw"]].head())


# ============================================================
# 1. 列の追加 ─ 全行への一括計算
# ============================================================
# 「列 × 数」「列 と 列 の計算」と書くだけで、pandasが全行に対して
# まとめて計算する。for ループで1行ずつ計算する必要はない。

section("1. 列の追加（小計を計算する）")

df["subtotal"] = df["quantity"] * df["unit_price"]
print(df[["product", "quantity", "unit_price", "subtotal"]].head())

# 条件から True/False の列を作ることもできる
df["is_high_value"] = df["subtotal"] >= 5000
print(f"\n高額注文（5000円以上）: {df['is_high_value'].sum()} 件")


# ============================================================
# 2. apply + lambda ─ 単純計算では書けない変換
# ============================================================
# 「列 × 数」のような単純な計算は直接書けるが、
# 「もっと複雑な変換（if分岐を含む等）」は関数を作って apply() に渡す。
#
# lambda は「名前のない1行関数」。apply(lambda x: 式) の形でよく使われる。
# 複雑な処理は def で普通の関数を作った方が読みやすい（後半で比較する）。

section("2. apply() と lambda: 行ごとの変換")


def price_tier(price: int) -> str:
    """単価から価格帯ラベルを作る（if分岐を含む変換の例）"""
    if price >= 3000:
        return "高価格帯"
    elif price >= 1500:
        return "中価格帯"
    else:
        return "低価格帯"


# 列全体に関数を適用する: Series.apply(関数)
df["price_tier"] = df["unit_price"].apply(price_tier)
print(df[["product", "unit_price", "price_tier"]].head(8))

# lambda 版（1行で済む単純な変換ならこちらでもよい）
df["quantity_label"] = df["quantity"].apply(lambda q: "まとめ買い" if q >= 3 else "通常")
print("\n--- lambda版の例 ---")
print(df[["product", "quantity", "quantity_label"]].head(8))


# ============================================================
# 3. .str アクセサ ─ 列全体への文字列処理
# ============================================================
# df["列"].str.メソッド() で、文字列の列すべてに一括で
# 文字列メソッド（strip, upper, replace など）を適用できる。
# 「1件ずつ .strip() する for ループ」が要らなくなる。

section("3. .str アクセサ: 表記ゆれを直す")

# --- 生データの汚れ具合を確認 ---
print("--- customer_name_raw の生データ（repr()でクォート・空白を可視化）---")
for name in df["customer_name_raw"].head(5):
    print(f"  {name!r}")

# --- strip(): 前後の空白を除去 ---
df["customer_name"] = df["customer_name_raw"].str.strip()

print("\n--- strip() 後 ---")
for name in df["customer_name"].head(5):
    print(f"  {name!r}")

# --- その他よく使う .str メソッド ---
print("\n--- len(): 文字数を数える ---")
print(df["customer_name"].str.len().head())

print("\n--- contains(): 部分一致で絞り込む ---")
tanaka_orders = df[df["customer_name"].str.contains("田中")]
print(tanaka_orders[["customer_name", "product"]])

print("\n--- replace(): 文字列の置換 ---")
print(df["category"].str.replace("雑貨", "グッズ").head(3))


# ============================================================
# 4. 型変換（astype）と列名の変更（rename）
# ============================================================

section("4. astype() と rename()")

# --- astype(): 列全体の型を変換する ---
# 例: quantity を文字列にしたい場合（実務では逆に「文字列→数値」の変換で多用する）
df["quantity_str"] = df["quantity"].astype(str)
print(f"変換前の型: {df['quantity'].dtype} / 変換後の型: {df['quantity_str'].dtype}")

# --- rename(): 列名を変更する ---
# columns={"旧名": "新名"} の辞書で指定する
renamed = df.rename(columns={"unit_price": "price", "quantity": "qty"})
print("\n--- rename後の列名 ---")
print(list(renamed.columns))


# ============================================================
# 5. 不要な列を落とす（drop）
# ============================================================

section("5. drop(): 列を削除する")

cleaned = df.drop(columns=["customer_name_raw", "quantity_str", "is_high_value"])
print(f"drop前: {list(df.columns)}")
print(f"drop後: {list(cleaned.columns)}")


# ============================================================
# まとめ
# ============================================================
section("まとめ")

print("""
  やりたいこと                  書き方
  ─────────────────────────────  ─────────────────────────────────
  計算した新しい列を追加        df["新列"] = df["列"] * 2
  行ごとに条件分岐して変換      df["新列"] = df["列"].apply(関数)
  文字列の前後空白を除去        df["列"] = df["列"].str.strip()
  文字列の部分一致で絞り込む    df[df["列"].str.contains("文字")]
  文字列の置換                  df["列"].str.replace("旧", "新")
  型を変換する                  df["列"].astype(str / int / float)
  列名を変更する                df.rename(columns={"旧": "新"})
  列を削除する                  df.drop(columns=["列名"])

  ★ 実務データの前処理は「まず .str.strip() で空白を疑う」が定石。
""")
