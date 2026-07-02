"""
Lv14 - pandas入門：データ処理の王道フレームワーク
===================================================
pandas は表形式データ（CSVやExcelのようなデータ）を扱う事実上の標準ライブラリ。
データ分析・レポート作成・前処理の現場で圧倒的に使われている。

Lv02 では CSV を「forループと辞書」で集計した。
pandas を使うと同じ処理が数行になり、しかも高速に動く。
「自力でループを書ける」→「王道の道具で楽をする」がこのレベルのテーマ。

中心となる考え方:
  DataFrame = 行と列を持つ「表」そのものを表すオブジェクト。
  表全体に対して「絞り込む」「列を足す」「グループ集計する」を
  1行ずつのループなしで宣言的に書ける。

実行方法:
    pip install -r requirements.txt
    python main.py
"""

from pathlib import Path

import pandas as pd  # 慣習として pd という別名で import する

DATA_CSV = Path(__file__).parent / "data" / "books.csv"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


# ============================================================
# 1. CSV を読み込む ─ read_csv 一発
# ============================================================
section("1. CSVの読み込み（DataFrameを作る）")

# Lv02 では open() + csv.DictReader + ループで読んだが、pandas なら1行。
# 型（数値/文字列）も自動で推定してくれる
df = pd.read_csv(DATA_CSV)

print(f"読み込み完了: {len(df)} 行 × {len(df.columns)} 列")
print(f"列名: {list(df.columns)}")


# ============================================================
# 2. まず中身を眺める ─ head / dtypes / describe
# ============================================================
section("2. データの概観")

# head(n): 先頭 n 行を表示（デフォルト5行）。まず必ずこれで中身を確認する癖を付ける
print("--- head(3): 先頭3行 ---")
print(df.head(3))

# dtypes: 各列の型。price が float、rating が int と自動判定されている
print("\n--- dtypes: 列の型 ---")
print(df.dtypes)

# describe(): 数値列の統計量（件数・平均・最小・最大など）を一発で出す
print("\n--- describe(): 数値列の統計 ---")
print(df[["price", "rating", "stock"]].describe().round(2))


# ============================================================
# 3. 列の選択と行の絞り込み
# ============================================================
section("3. 列の選択と行の絞り込み")

# --- 列の選択: df["列名"] で1列、df[["列1", "列2"]] で複数列 ---
print("--- タイトルと価格だけ（先頭3行）---")
print(df[["title", "price"]].head(3))

# --- 行の絞り込み（ブールインデックス） ---
# df["rating"] >= 4 は「各行が条件を満たすか」の True/False の列になる。
# それを df[...] に渡すと True の行だけが残る。
# Lv01 の「if で絞り込むループ」を、表全体への1つの式で書いている
high_rated = df[df["rating"] >= 4]
print(f"\n--- 星4以上: {len(high_rated)} 冊 ---")
print(high_rated[["title", "rating", "price"]])

# --- 複数条件: & (かつ) / | (または)。各条件を () で囲むのが文法上の約束 ---
cheap_and_good = df[(df["rating"] >= 4) & (df["price"] < 30)]
print(f"\n--- 星4以上 かつ 30ポンド未満: {len(cheap_and_good)} 冊 ---")
print(cheap_and_good[["title", "rating", "price"]])


# ============================================================
# 4. 列の追加 ─ 全行への一括計算
# ============================================================
section("4. 列の追加（円換算・お買い得フラグ）")

# 列全体 × 数値 のように書くと、全行に一括で計算される（ループ不要）
GBP_TO_JPY = 190
df["price_jpy"] = (df["price"] * GBP_TO_JPY).round(0).astype(int)

# 条件から True/False の列を作ることもできる
df["is_bargain"] = (df["rating"] >= 4) & (df["price"] < 30)

print(df[["title", "price", "price_jpy", "is_bargain"]].head(5))


# ============================================================
# 5. グループ集計 ─ Lv02 の手書き集計が1行になる
# ============================================================
section("5. groupby: カテゴリ別の集計")

# Lv02 では「辞書に部署ごとのリストを貯めて sum/len で計算」した。
# pandas では groupby(グループ列)[集計列].agg(集計方法) の1文で書ける
summary = (
    df.groupby("category")["price"]
    .agg(["count", "mean", "min", "max"])   # 件数・平均・最小・最大を同時に
    .round(2)
    .sort_values("count", ascending=False)  # 冊数の多い順に並べる
)
print(summary)

# 複数列・複数集計の組み合わせも同じ形で書ける
print("\n--- 星評価別: 平均価格と合計在庫 ---")
by_rating = df.groupby("rating").agg(
    冊数=("title", "count"),
    平均価格=("price", "mean"),
    合計在庫=("stock", "sum"),
).round(2)
print(by_rating)


# ============================================================
# 6. 並べ替えと上位抽出
# ============================================================
section("6. sort_values: 高い本トップ5")

top5 = df.sort_values("price", ascending=False).head(5)
print(top5[["title", "category", "price"]])


# ============================================================
# 7. 結果の書き出し ─ CSV も Excel も1行
# ============================================================
section("7. 結果の書き出し")

# CSV 出力（Excel対応の BOM 付き UTF-8。Lv02 で学んだ知識がそのまま活きる）
csv_path = OUTPUT_DIR / "bargain_books.csv"
df[df["is_bargain"]].to_csv(csv_path, index=False, encoding="utf-8-sig")
print(f"お買い得本CSV: {csv_path}")

# Excel 出力（内部で Lv10 の openpyxl が使われている）
# ExcelWriter を使うと複数シートも書ける
excel_path = OUTPUT_DIR / "summary.xlsx"
with pd.ExcelWriter(excel_path) as writer:
    df.to_excel(writer, sheet_name="全データ", index=False)
    summary.to_excel(writer, sheet_name="カテゴリ別集計")
print(f"集計Excel:     {excel_path}")


# ============================================================
# まとめ
# ============================================================
section("まとめ: 手書きループ vs pandas")

print("""
  やりたいこと           Lv02の書き方              pandas
  ────────────────────  ───────────────────────  ─────────────────────────
  CSVを読む             open + DictReader + for   pd.read_csv(path)
  条件で絞る            for + if + append         df[df["rating"] >= 4]
  列を計算して足す      for の中で計算            df["新列"] = df["列"] * 190
  グループ集計          辞書に貯めて sum/len      df.groupby("列").agg(...)
  並べ替え              sorted(key=...)           df.sort_values("列")
  CSV/Excelに書く       csv.writer / openpyxl     df.to_csv / df.to_excel

  ★ ループを手書きできる力があるからこそ、pandas が
    「何をやってくれているか」を理解して使える。
""")
