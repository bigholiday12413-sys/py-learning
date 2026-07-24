# pandas講座 Lv05 - グループ集計（groupby）

## テーマ

「カテゴリ別の売上」「地域ごとの平均」のような、Excelの
**SUMIFS / COUNTIFS / AVERAGEIFS に相当する処理**を、`groupby` という1つの仕組みで統一的に扱う。

ここからLv08（ピボットテーブル）まで、Zakka Storeの本編データ
（`data/orders.csv` 81件、`data/customers.csv` 12件）を通して使う。

## 動かし方

```bash
cd pandas-course/lv05-groupby
python main.py
```

## groupby の組み立て方

```python
df.groupby("グループ化する列")["集計したい列"].集計方法()
```

の3ステップで読む。

```python
orders.groupby("category")["subtotal"].sum()
```

「categoryで**グループに分け**、subtotal列に**sumをかける**」と読む。

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `groupby("列")["列2"].sum()` | 基本形。〜ごとの合計 |
| `.agg(["count","sum","mean"])` | 複数の集計を同時に出す |
| `.agg(新名=("元列","方法"))` | 集計結果に自分で列名を付ける（named aggregation） |
| `groupby(["列1","列2"])` | 2軸でのグループ化 |
| `.value_counts()` | 件数だけを数える最短ルート |
| `.value_counts(normalize=True)` | 割合(%)で見る |

## value_counts() vs groupby().size()

「件数だけ知りたい」なら `value_counts()` が最短:

```python
orders["category"].value_counts()          # ← これでOK
orders.groupby("category").size()          # ← 同じ結果だが少し長い
```

「合計・平均も一緒に知りたい」なら `groupby().agg()` を使う。

## 読む順番

1. この README
2. `main.py` を上から実行結果と見比べながら読む
3. 改造課題へ

## 改造課題

- [ ] `groupby("product")["subtotal"].sum()` で商品別売上を出し、一番売れている商品を探そう
- [ ] 件数（count）ではなく `nunique()` を使って「カテゴリごとに何種類の商品があるか」を数えてみよう
- [ ] `orders.groupby("category")["quantity"].agg(["sum","mean","max"])` で数量の集計も試そう
- [ ] `data/customers.csv` を読み込み、`membership_level`（会員ランク）ごとの人数を `value_counts()` で数えよう（結合はLv07で本格的に扱う）
- [ ] named aggregation で「最大注文額」「最小注文額」も含めたレポートを作ってみよう
