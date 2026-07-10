# =============================================================
# vv12 - pandas 基礎: vvM 抽出データの集計
# =============================================================
# 想定シナリオ:
#   営業日報 約200件を vvM に読ませて、
#   「商材名・競合社名・商談結果・極性」などを抽出した CSV がある。
#   それを pandas で集計して、提案資料の数字の裏付けを作る。
#
# pandas の頭の中のイメージ:
#   - DataFrame ≒ Excel の1枚のシート（行×列の表）
#   - Series    ≒ シートの1列（またはフィルタ結果の1列）
#   Excel でピボットテーブルを作る操作を、コードで再現できると思えばよい。
#
# 実行: python main.py
# =============================================================

from pathlib import Path

import pandas as pd

# --- 出力先フォルダを用意（vv02 でやった pathlib の復習） ---
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================
# 1. CSV を読み込む: read_csv
# =============================================================
print("=" * 60)
print("1. read_csv でデータを読み込む")
print("=" * 60)

# parse_dates=["日付"] を付けると「日付」列が文字列ではなく
# datetime 型で読み込まれる（Excel の「セルの書式設定→日付」に相当）。
# datetime 型にしておくと、後で「月」を取り出すのが一発でできる。
#
# dtype={"id": "int64"} のように列の型を明示することもできる。
# vvM の抽出結果は型が揺れがち（"1" と 1 が混ざる等）なので、
# 実データでは dtype を指定して読み込み時に揃えておくと事故が減る。
df = pd.read_csv(
    BASE_DIR / "sample_extracted.csv",
    parse_dates=["日付"],       # この列を datetime 型として解釈する
    dtype={"id": "int64"},      # id は整数と明示（型揺れ対策）
)

# =============================================================
# 2. DataFrame の基本: まず全体像を眺める
# =============================================================
print()
print("=" * 60)
print("2. DataFrame の基本 (head / info / describe / shape)")
print("=" * 60)

# head(): 先頭5行を表示。Excel でシートを開いて上の方を眺めるのと同じ。
print("--- head(): 先頭5行 ---")
print(df.head())

# shape: (行数, 列数) のタプル。JS で言う array.length の表バージョン。
print(f"\n--- shape: {df.shape} → {df.shape[0]}行 × {df.shape[1]}列 ---")

# info(): 各列の型と欠損の有無。読み込み直後に必ず見るクセをつける。
#   「日付」が datetime64 になっているか、
#   「競合社名」に欠損（non-null が行数より少ない）があるか、をここで確認。
print("\n--- info(): 列の型と欠損チェック ---")
df.info()

# describe(): 数値列の統計量（件数・平均・最小・最大など）。
# このデータは数値列が id だけなのであまり意味はないが、
# 売上金額などの列があるデータでは真っ先に見る。
print("\n--- describe(): 数値列の統計量 ---")
print(df.describe())

# =============================================================
# 3. 列の選択とフィルタ（ブールインデックス）
# =============================================================
print()
print("=" * 60)
print("3. 列の選択とフィルタ")
print("=" * 60)

# df["列名"] で1列だけ取り出す → これが Series（Excel の1列に相当）
tanto = df["営業担当"]
print(f"--- df['営業担当'] は Series 型: {type(tanto).__name__} ---")
print(tanto.head(3))

# 行のフィルタは「ブールインデックス」と呼ばれる書き方をする。
#   df[df["商談結果"] == "受注"]
# JS で書くなら rows.filter(r => r.商談結果 === "受注") に相当。
# 内側の df["商談結果"] == "受注" が True/False の Series を作り、
# それを df[...] に渡すと True の行だけが残る、という仕組み。
juchu = df[df["商談結果"] == "受注"]
print(f"\n--- 受注の行だけ抽出: {len(juchu)}件 ---")
print(juchu[["日付", "営業担当", "商材名", "顧客名"]].head())

# 条件を組み合わせるときは & (AND) / | (OR) を使い、各条件を () で囲む。
# ※ Python の and/or ではなく & | なので注意（ここは JS と違うハマりどころ）
sato_juchu = df[(df["営業担当"] == "佐藤") & (df["商談結果"] == "受注")]
print(f"\n--- 佐藤さんの受注: {len(sato_juchu)}件 ---")

# =============================================================
# 4. 欠損値の処理: isna / fillna / dropna
# =============================================================
print()
print("=" * 60)
print("4. 欠損値の処理")
print("=" * 60)

# vvM 抽出データでは「日報に競合の記載がない」→ 競合社名が空、が普通に起きる。
# pandas は空セルを NaN (Not a Number) として読み込む。

# isna(): 各セルが欠損かどうかの True/False。sum() と組み合わせて欠損数を数える。
print("--- 各列の欠損数 (isna().sum()) ---")
print(df.isna().sum())

# fillna(): 欠損を指定の値で埋める。
# ここでは「競合の記載なし = 競合なし案件」とみなして「競合なし」で埋める。
# ※ 元の df を直接書き換えず、埋めた結果を新しい列/変数に入れるのが安全。
df["競合社名"] = df["競合社名"].fillna("競合なし")
print("\n--- fillna 後の競合社名の内訳 ---")
print(df["競合社名"].value_counts())

# dropna(): 欠損がある行を削除する。
# 「必須項目が抜けている行は集計から外す」ときに使う。
# 今回は fillna で埋めたので実際には減らないが、書き方だけ確認。
df_no_missing = df.dropna(subset=["商談結果", "極性"])
print(f"\n--- dropna 後の行数: {len(df_no_missing)}件（元: {len(df)}件） ---")

# =============================================================
# 5. 日付から「月」列を作る: dt.to_period("M")
# =============================================================
print()
print("=" * 60)
print("5. 日付 → 月 の変換")
print("=" * 60)

# datetime 型の列には .dt というアクセサが生えていて、
# .dt.year / .dt.month / .dt.to_period("M") などが使える。
# to_period("M") は「2026-03-15 → 2026-03」のように月単位に丸める。
# Excel で言えば TEXT(A1,"yyyy-mm") で月キーを作る操作。
df["月"] = df["日付"].dt.to_period("M").astype(str)  # 文字列にしておくと扱いやすい
print("--- 月列を追加した ---")
print(df[["日付", "月"]].head())
print(f"\n対象期間: {df['月'].min()} 〜 {df['月'].max()}")

# =============================================================
# 6. groupby + agg: グループごとの集計
# =============================================================
print()
print("=" * 60)
print("6. groupby + agg")
print("=" * 60)

# groupby は Excel の「ピボットで行にドラッグ」に相当。
# SQv を知っていれば GROUP BY そのもの。

# --- 6-1. 商材別の件数 ---
# size() は「グループの行数」。COUNTIF を全商材分いっぺんにやるイメージ。
syozai_count = df.groupby("商材名").size().sort_values(ascending=False)
print("--- 商材別 商談件数 ---")
print(syozai_count)

# --- 6-2. 担当者別の受注率 ---
# 「受注かどうか」の True/False 列を作り、mean() を取ると受注率になる。
#   True=1, False=0 として平均される → 受注率（これは常套手段なので覚える価値あり）
df["受注フラグ"] = df["商談結果"] == "受注"
juchu_rate = (
    df.groupby("営業担当")
    .agg(
        商談件数=("id", "count"),        # agg(新列名=(元の列, 集計方法)) の形
        受注件数=("受注フラグ", "sum"),
        受注率=("受注フラグ", "mean"),
    )
    .sort_values("受注率", ascending=False)
)
juchu_rate["受注率"] = (juchu_rate["受注率"] * 100).round(1)  # % 表記に
print("\n--- 担当者別 受注率 (%) ---")
print(juchu_rate)

# =============================================================
# 7. pivot_table: 商材×月のクロス集計（★実務の本命★）
# =============================================================
print()
print("=" * 60)
print("7. pivot_table: 商材×月 クロス集計")
print("=" * 60)

# Excel のピボットテーブルで
#   行 = 商材名, 列 = 月, 値 = 件数
# とドラッグする操作が、この1行に対応する。
pivot = pd.pivot_table(
    df,
    index="商材名",       # 行に置く列
    columns="月",         # 列に置く列
    values="id",          # 集計対象（件数を数えるだけなので何の列でもよい）
    aggfunc="count",      # 集計方法: count / sum / mean など
    fill_value=0,         # 該当がないセルは 0 で埋める（NaN のままにしない）
)
print(pivot)

# 集計結果を CSV に保存。encoding="utf-8-sig" にしておくと
# Excel でダブルクリックしても文字化けしない（BOM 付き UTF-8。vv02 の復習）。
pivot.to_csv(OUTPUT_DIR / "pivot_商材x月.csv", encoding="utf-8-sig")
print(f"\n→ {OUTPUT_DIR / 'pivot_商材x月.csv'} に保存した（Excel で開いて確認してみよう）")

# =============================================================
# 8. value_counts / crosstab: 競合×勝敗
# =============================================================
print()
print("=" * 60)
print("8. value_counts と crosstab")
print("=" * 60)

# value_counts(): 1列の値の内訳を数える。一番手軽な集計。
print("--- 商談結果の内訳 (value_counts) ---")
print(df["商談結果"].value_counts())

# normalize=True で割合になる
print("\n--- 極性の割合 ---")
print((df["極性"].value_counts(normalize=True) * 100).round(1))

# pd.crosstab(): 2つの列で「行×列の件数表」を作る。
# pivot_table(aggfunc="count") の簡易版で、件数のクロス集計ならこちらが短い。
# 「競合がいた案件で、どの競合に勝ってどの競合に負けたか」= 提案資料の鉄板ネタ。
kyogo_df = df[df["競合社名"] != "競合なし"]  # 競合がいた案件だけに絞る
kyogo_cross = pd.crosstab(kyogo_df["競合社名"], kyogo_df["商談結果"])
print("\n--- 競合×勝敗 (crosstab) ---")
print(kyogo_cross)

kyogo_cross.to_csv(OUTPUT_DIR / "crosstab_競合x勝敗.csv", encoding="utf-8-sig")

# =============================================================
# 9. ソートと出力: sort_values / to_csv
# =============================================================
print()
print("=" * 60)
print("9. ソートと CSV 出力")
print("=" * 60)

# sort_values: 指定列で並べ替え。ascending=False で降順。
# JS の array.sort((a, b) => ...) に相当するが、列名を書くだけでよい。
df_sorted = df.sort_values(["月", "商材名"], ascending=[True, True])
print("--- 月→商材名 の順でソート（先頭5行） ---")
print(df_sorted[["月", "商材名", "営業担当", "商談結果", "極性"]].head())

# 加工済みデータ（月列・受注フラグ付き）を保存。
# index=False にしないと行番号が余計な列として出力されるので注意。
out_path = OUTPUT_DIR / "cleaned_data.csv"
df_sorted.to_csv(out_path, index=False, encoding="utf-8-sig")
print(f"\n→ {out_path} に保存した")

print()
print("=" * 60)
print("完了！ 次は visualize.py でこの集計をグラフにする")
print("=" * 60)
