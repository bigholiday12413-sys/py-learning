"""
pandas講座 Lv04 - 欠損値・重複の処理
======================================
「セルが空欄」「同じ行が2回入っている」は、実務データで最も頻繁に出会う問題。
放置すると、平均が狂ったり、集計が水増しされたりする。
このレベルでは「見つける → 方針を決める → 直す」の型を身につける。

実行方法:
    python main.py
"""

from pathlib import Path

import pandas as pd

DATA_CSV = Path(__file__).parent / "data" / "orders_dirty.csv"


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


df = pd.read_csv(DATA_CSV)

section("0. 読み込んだデータ（わざと欠損・重複を仕込んである）")
print(df)


# ============================================================
# 1. 欠損値（NaN）を見つける
# ============================================================
# CSVの空欄は、pandasに読み込むと NaN（Not a Number）という
# 特別な「値がない」マーカーになる。None とは少し違う専用の値。

section("1. 欠損値を見つける ─ isna()")

# --- isna(): 各セルが欠損かどうかの True/False 表 ---
print("--- isna() の中身（一部）---")
print(df[["quantity", "unit_price", "customer_id"]].isna())

# --- 列ごとに欠損の件数を数える ---
# isna() は True/False の表なので、sum() すると列ごとの True の数（=欠損数）になる
print("\n--- 列ごとの欠損件数 ---")
print(df.isna().sum())

# --- 欠損を含む行だけを表示する ---
has_missing = df[df.isna().any(axis=1)]
# any(axis=1): 「行方向に見て、どれか1つでも True があるか」
print(f"\n--- 欠損を含む行: {len(has_missing)} 件 ---")
print(has_missing)


# ============================================================
# 2. 欠損値への対処 ─ dropna() と fillna()
# ============================================================
# 対処法は「削除する」か「埋める」の2択。どちらを選ぶかはビジネス判断次第。
# ★ 大事なのは「なんとなく」ではなく、列の意味に応じて方針を決めること。

section("2. dropna() と fillna(): 方針を決めて対処する")

# --- dropna(): 欠損を含む行をまるごと削除 ---
# customer_id が無い注文は「誰の注文か分からない」= 集計に使えない。削除が妥当
no_customer = df[df["customer_id"].isna()]
print(f"customer_id が欠損: {len(no_customer)} 件 → 削除する")
step1 = df.dropna(subset=["customer_id"])  # subset: このリストの列だけを判定対象にする
print(f"削除後: {len(step1)} 件（元は {len(df)} 件）")

# --- fillna(): 欠損を何らかの値で埋める ---
# quantity（数量）が空欄 = 「おそらく1個」という業務ルールなら、1で埋めるのが妥当
step2 = step1.copy()  # 元のデータを変えないよう複製してから作業する（実務での安全策）
step2["quantity"] = step2["quantity"].fillna(1)

# unit_price（単価）が空欄 = 「その商品の平均単価」で埋める、という方針もありうる
avg_price = step2["unit_price"].mean()
step2["unit_price"] = step2["unit_price"].fillna(round(avg_price))

print(f"\nquantity・unit_price を埋めた後の欠損件数:\n{step2.isna().sum()}")
print("\n--- 補完後のデータ ---")
print(step2)

# --- 方針の対応表（このデータでの判断） ---
print("""
  列            欠損の意味          対処方針
  ────────────  ───────────────────  ─────────────────────────
  customer_id   誰の注文か不明       行ごと削除（集計に使えないため）
  quantity      数量の記入漏れ       1 で補完（最小注文数と仮定）
  unit_price    単価の記入漏れ       平均単価で補完（概算として扱う）
""")


# ============================================================
# 3. 重複行を見つけて処理する
# ============================================================
# スクレイピングやシステム連携では「同じデータを2回取り込んでしまう」事故が起きやすい。

section("3. 重複行の検出と削除")

# --- duplicated(): 重複している行に True を付ける ---
# デフォルトは「全列が完全に一致」を重複とみなす。2回目以降の出現に True が付く
print("--- duplicated() の結果 ---")
print(df.duplicated())

dup_rows = df[df.duplicated()]
print(f"\n完全重複行: {len(dup_rows)} 件")
print(dup_rows)

# --- drop_duplicates(): 重複を除去（最初の1件だけ残す） ---
deduped = df.drop_duplicates()
print(f"\n重複除去後: {len(deduped)} 件（元は {len(df)} 件）")

# --- 特定の列だけで重複判定する ---
# 「order_id が同じなら、他の列が多少違っても重複とみなす」という業務ルールもありうる
dup_by_id = df[df.duplicated(subset=["order_id"], keep=False)]
# keep=False: 重複したペア全部を表示する（最初の1件も含めて見せる）
print(f"\n--- order_id が重複している行（両方表示）: {len(dup_by_id)} 件 ---")
print(dup_by_id[["order_id", "customer_id", "product", "quantity"]])


# ============================================================
# まとめ
# ============================================================
section("まとめ")

print("""
  やりたいこと                      書き方
  ─────────────────────────────────  ─────────────────────────────────
  各セルが欠損か調べる              df.isna()
  列ごとの欠損件数                  df.isna().sum()
  欠損を含む行を抽出                df[df.isna().any(axis=1)]
  欠損行を削除                      df.dropna(subset=["列"])
  欠損を値で埋める                  df["列"].fillna(値)
  重複行を検出                      df.duplicated()
  重複行を削除（最初を残す）        df.drop_duplicates()
  特定列だけで重複判定              df.duplicated(subset=["列"])

  ★ dropna/fillna は「なんとなく」ではなく、列の意味に応じて
    方針を決めてから使う。判断の根拠をコメントに残す習慣も大事。
""")
