# pandas講座 Lv01 - Series と DataFrame 入門

## テーマ

pandas は「表」を丸ごと1つの変数として扱うライブラリ。
リストや辞書のように1件ずつ処理するのではなく、Excelのシートのような
「行×列」の構造そのものをオブジェクト（**DataFrame**）として操作する。

## 動かし方

```bash
cd pandas-course/lv01-series-dataframe
python main.py
```

（venvと依存パッケージは `pandas-course` フォルダの README を参照）

## 中心概念: DataFrame は「辞書のリスト」の進化形

```python
books = [
    {"title": "Sharp Objects", "category": "Mystery", "price": 47.82},
    {"title": "Sapiens", "category": "History", "price": 54.23},
]
df = pd.DataFrame(books)
```

- 横1行 = 1件のデータ（元の辞書1個に相当）
- 縦1列 = 1つの項目。1列だけ取り出したものは **Series** と呼ばれる
- 左端の連番（0, 1, 2...）は **index**。指定しなければ自動で振られる

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `pd.DataFrame(辞書のリスト)` | 手持ちのデータを表に変換 |
| `pd.read_csv(path)` | CSVをそのまま表として読み込む |
| `df.head()` | 先頭数行を見る（まず必ずこれ） |
| `df.dtypes` | 各列の型を確認（数値のはずが文字列になっていないか） |
| `df.describe()` | 数値列の統計量を一発表示 |
| `df.shape` | (行数, 列数) |
| `df["列名"]` | 1列選択（Seriesが返る） |
| `df[["列1","列2"]]` | 複数列選択（角括弧が二重になる） |
| `df.loc[]` / `df.iloc[]` | 行の選択（ラベル基準 / 番号基準） |

## 実務でまず確認する3点セット

```python
df.head()       # 中身の雰囲気
df.dtypes       # 型が想定通りか
df.describe()   # 数値の範囲がおかしくないか
```

これを飛ばしていきなり集計・グラフ化に進むと、「価格が文字列で読まれていて計算できない」
「日付が数値のままだった」のような事故に**後から**気づくことになる。読み込んだら必ず眺める。

## Zakka Store データセット

このコース全体で、架空のネットショップ「Zakka Store」の売上データを扱う。
Lv01では最初の10件だけを抜き出した `data/sales_mini.csv` を使う
（列: product, category, quantity, unit_price）。

## 改造課題

- [ ] `df["category"]` を実行して、Series として表示されることを確認しよう
- [ ] `df.iloc[-1]`（最後の行）を表示してみよう
- [ ] `df["unit_price"].mean()` で平均単価を計算してみよう（Series にも統計メソッドがある）
- [ ] `pd.DataFrame({"a": [1,2,3], "b": [4,5,6]})` のように、辞書から直接DataFrameを作ってみよう
- [ ] `df.info()` を実行し、`describe()` との違いを比べてみよう
