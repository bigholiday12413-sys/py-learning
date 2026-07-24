# pandas講座 Lv08 - ピボットテーブル（pivot_table）

## テーマ

Excelでマウスをドラッグ&ドロップして作る「ピボットテーブル」を、コードで再現する。
`groupby`（Lv05）の「2軸バージョン」と捉えると理解しやすい。

## 動かし方

```bash
cd pandas-course/lv08-pivot-table
python main.py
```

`output/pivot_report.xlsx` にピボット結果がExcelとして出力される。

## Excelのピボットテーブルとの対応

Excelでピボットテーブルを作るとき、4つの枠にフィールドをドラッグする:

| Excelの操作 | `pivot_table()` の引数 |
|-------------|------------------------|
| 「行」の枠にドラッグ | `index=` |
| 「列」の枠にドラッグ | `columns=` |
| 「値」の枠にドラッグ | `values=` |
| 集計方法（合計/平均/個数） | `aggfunc=` |

```python
pd.pivot_table(df, index="category", columns="region", values="subtotal", aggfunc="sum")
```

これは「カテゴリを行に、地域を列に、売上の合計をセルに表示する」ピボットテーブルと同じ。

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `pd.pivot_table(index=, columns=, values=, aggfunc=)` | 基本形 |
| `fill_value=0` | 組み合わせが無いセルを0で埋める（NaNのままだと見づらい） |
| `margins=True` / `margins_name=` | 総計行・総計列を追加（Excelの「総計」チェック相当） |
| `aggfunc=["sum","mean","count"]` | 複数の集計方法を同時に指定 |
| `pd.crosstab(列1, 列2)` | 件数だけのクロス集計（pivot_tableより簡潔） |
| `crosstab(..., normalize="index")` | 行ごとの構成比(%) |
| `to_excel()` | ピボット結果もただのDataFrame。そのままExcel出力できる |

## groupby と pivot_table の関係

```python
# groupby: 1軸の集計（縦に並ぶ）
df.groupby("category")["subtotal"].sum()

# pivot_table: 2軸の集計（表の形に展開）
pd.pivot_table(df, index="category", columns="region", values="subtotal", aggfunc="sum")
```

`pivot_table` は内部的に `groupby(["category", "region"])` をした結果を、
「region の値を列として横に展開した表」に変形しているだけ。
groupbyが分かっていれば、pivot_tableは「見た目を変える機能」として理解できる。

## 読む順番

1. この README
2. `main.py` を上から実行結果と見比べながら読む
3. 生成された `output/pivot_report.xlsx` をExcelで開いて確認
4. 改造課題へ

## 改造課題

- [ ] `index` と `columns` を入れ替えて（`index="region"`, `columns="category"`）、見え方の違いを確認しよう
- [ ] `aggfunc="mean"` に変えて、平均注文額のピボットを作ってみよう
- [ ] `values="quantity"` に変えて、数量ベースのピボットを作ってみよう
- [ ] `membership_level`（会員ランク）を列に使ったピボットを作ってみよう
- [ ] `crosstab` の `normalize="columns"` を試し、`normalize="index"` との違いを確認しよう
