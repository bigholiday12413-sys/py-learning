# Lv14 - pandas入門：データ処理の王道【フレームワーク編】

## テーマ

**pandas** は表形式データを扱う Python の事実上の標準ライブラリ。
Lv02 で「forループと辞書」で書いた CSV 集計が、pandas なら数行で書ける。

このコースであえて先に手書きループを学んだのは、
pandas が「何をやってくれているか」を理解して使えるようになるため。
ここからは王道の道具で楽をする。

## 動かし方

```bash
cd lv14-pandas
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows / macOSは source venv/bin/activate
pip install -r requirements.txt
python main.py
```

`output/` に絞り込みCSVと集計Excelが生成される。

## 中心概念: DataFrame

DataFrame = 行と列を持つ「表」を丸ごと表すオブジェクト。

```python
import pandas as pd

df = pd.read_csv("data/books.csv")   # CSV → DataFrame（1行！）
df[df["rating"] >= 4]                # 絞り込み（ループ不要）
df.groupby("category")["price"].mean()  # グループ集計（1行！）
```

「1行ずつ処理する」発想から「**表全体に操作を宣言する**」発想への転換が pandas の肝。

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `pd.read_csv()` | CSV読み込み（型も自動推定） |
| `head()` / `dtypes` / `describe()` | まずデータを眺める3点セット |
| `df[["列1", "列2"]]` | 列の選択 |
| `df[条件]`（ブールインデックス） | 行の絞り込み。`&`(かつ) `\|`(または) |
| `df["新列"] = 式` | 全行への一括計算で列を追加 |
| `groupby().agg()` | グループ集計（Lv02の手書き集計の正体） |
| `sort_values()` | 並べ替えと上位抽出 |
| `to_csv()` / `to_excel()` | 結果の書き出し（utf-8-sig / 複数シート） |

## Lv02 との対応表（main.py 末尾にも掲載）

| やりたいこと | Lv02の書き方 | pandas |
|-------------|-------------|--------|
| CSVを読む | `open` + `DictReader` + `for` | `pd.read_csv(path)` |
| 条件で絞る | `for` + `if` + `append` | `df[df["rating"] >= 4]` |
| グループ集計 | 辞書に貯めて `sum`/`len` | `df.groupby("列").agg(...)` |
| Excelに書く | openpyxl でセル操作 | `df.to_excel(...)` |

## 読む順番

1. この README
2. `data/books.csv` を開いてデータを確認
3. `main.py` を上から実行結果と見比べながら読む
4. 改造課題へ

## 改造課題

- [ ] 「在庫金額（price × stock）」列を追加して、カテゴリ別の合計在庫金額を集計しよう
- [ ] `df["title"].str.contains("The")` でタイトル絞り込みを試そう（文字列メソッドの列版）
- [ ] Lv04/Lv09 のスクレイピング結果（list[dict]）を `pd.DataFrame(データ)` で直接 DataFrame にしよう
- [ ] Lv11 の SQLite から `pd.read_sql_query()` で読み込んでみよう（DBとpandasの連携）
- [ ] 2つのCSVを `pd.merge()` で結合してみよう（Excel の VLOOKUP に相当）

## 補足: pandas を使うべきとき・使わなくていいとき

- **使うべき**: 集計・結合・ピボットなど「表の変形」が主役の処理、数万行以上のデータ
- **不要なことも**: 数十行のデータを1回なめるだけなら Lv02 の標準ライブラリで十分。
  依存を増やさない選択も実務では正しい
