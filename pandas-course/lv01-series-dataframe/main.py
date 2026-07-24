"""
pandas講座 Lv01 - Series と DataFrame 入門
============================================
pandas は「表」を丸ごと1つの変数として扱うライブラリ。
リストや辞書でデータを持つのではなく、Excelのシートのような
「行×列」の構造そのものをオブジェクトとして操作する。

実行方法:
    python main.py
"""

from pathlib import Path

import pandas as pd  # 慣習として pd という別名で import する

DATA_CSV = Path(__file__).parent / "data" / "sales_mini.csv"


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


# ============================================================
# 1. DataFrame とは何か ─ 辞書のリストの進化形
# ============================================================
# 「1件のデータ = 1つの辞書」「複数件 = 辞書のリスト」という形は
# 普通の Python でもよく使う（CSVの各行を辞書にする、など）。
# pandas はこれを「表」として扱えるようにしたもの。

section("1. 辞書のリスト → DataFrame")

books = [
    {"title": "Sharp Objects", "category": "Mystery", "price": 47.82},
    {"title": "Sapiens", "category": "History", "price": 54.23},
    {"title": "Starving Hearts", "category": "Fiction", "price": 13.99},
]

df = pd.DataFrame(books)
print(df)

# --- 表の見方 ---
# 横1行 = 1件のデータ（元の辞書1個に相当）
# 縦1列 = 1つの項目。列を1本だけ取り出したものを Series と呼ぶ
# 左端の 0, 1, 2 は行番号（index）。指定しなければ pandas が自動で振る

print(f"\n型を確認: {type(df)}")
print(f"1列だけ取り出すと: {type(df['title'])}")  # DataFrame ではなく Series になる


# ============================================================
# 2. CSVを読み込む ─ read_csv 一発
# ============================================================
section("2. CSVの読み込み")

# CSVモジュール + DictReader + for ループ（メインコースLv02）でやっていたことが
# この1行に相当する。数値の列（quantity, unit_price）は自動で数値型として読まれる
df = pd.read_csv(DATA_CSV)

print(f"読み込み完了: {len(df)} 行 × {len(df.columns)} 列")
print(f"列名: {list(df.columns)}")


# ============================================================
# 3. まず中身を眺める ─ 実務で最初にやる3点セット
# ============================================================
# 集計やグラフを作る前に、まず「このデータは何者か」を確認する癖を付ける。
# これを飛ばして加工を始めると、後で「型が違う」「欠損がある」に気づかず事故る。

section("3. head() / dtypes / describe()")

# --- head(n): 先頭n行を表示（省略時は5行） ---
print("--- head(): 先頭の中身を見る ---")
print(df.head())

# --- dtypes: 各列の型 ---
# quantity が int64、unit_price が int64 になっているかを必ず確認する。
# もし文字列(object)になっていたら「数値のはずが文字列で読まれた」サインで、
# どこかに変な値（空欄や単位付き文字列）が混ざっている可能性が高い
print("\n--- dtypes: 列の型 ---")
print(df.dtypes)

# --- shape: 行数と列数 ---
print(f"\n--- shape: {df.shape} ← (行数, 列数) ---")

# --- describe(): 数値列の統計量を一発で出す ---
# count(件数)・mean(平均)・min・max・std(標準偏差) などが並ぶ
print("\n--- describe(): 数値列の統計 ---")
print(df.describe())


# ============================================================
# 4. 列と行、それぞれの選び方
# ============================================================
section("4. 列の選択と行の指定")

# --- 列を1本だけ選ぶ: df["列名"] → Series が返る ---
print("--- df['product'] （1列だけ）---")
print(df["product"].head())

# --- 複数列を選ぶ: df[["列1", "列2"]] → 角括弧が二重になる ---
# 外側の [] は「df から取り出す」、内側の [] は「列名のリスト」
print("\n--- df[['product', 'unit_price']] （2列）---")
print(df[["product", "unit_price"]].head())

# --- 行を指定する: loc（ラベルで指定）/ iloc（番号で指定） ---
# 今回の index は 0,1,2... という自動採番なので、loc と iloc は同じ結果になる。
# 違いが出るのは「index を並べ替えた後」など（Lv06で扱う）
print("\n--- df.loc[0] （0行目。ラベル基準）---")
print(df.loc[0])

print("\n--- df.iloc[0:3] （先頭3行。番号基準のスライス）---")
print(df.iloc[0:3])


# ============================================================
# まとめ
# ============================================================
section("まとめ")

print("""
  やりたいこと         書き方
  ───────────────────  ─────────────────────────
  CSVを読み込む         pd.read_csv(path)
  先頭を確認            df.head()
  列の型を確認          df.dtypes
  統計量を確認          df.describe()
  行数・列数を確認      df.shape
  1列選ぶ               df["列名"]      → Series
  複数列選ぶ            df[["列1","列2"]]
  行を選ぶ（番号）      df.iloc[番号]

  ★ 何か処理する前に、まず head/dtypes/describe で「中身を見る」。
    これが実務でも一番大事な最初の一歩。
""")
