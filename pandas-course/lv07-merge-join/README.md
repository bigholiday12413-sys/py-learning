# pandas講座 Lv07 - テーブルの結合（merge / concat）

## テーマ

Excelで「VLOOKUP / XLOOKUP で他のシートから情報を持ってくる」作業を、
pandasでは **`merge()`** という1つの関数で行う。

VLOOKUPは1セルずつ検索するが、`merge()` は**表全体を一括で**結合する。

## 動かし方

```bash
cd pandas-course/lv07-merge-join
python main.py
```

## merge の基本形

```python
merged = orders.merge(customers, on="customer_id")
```

「`orders`（注文）に、`customers`（顧客マスタ）から `customer_id` が一致する行の
情報を横につなげる」という意味。VLOOKUPで1件ずつやっていた検索を、全行に対して一度に行う。

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `df1.merge(df2, on="列")` | 共通の列で2つの表を結合 |
| `how="inner"`（既定） | 両方に存在するキーだけ残す |
| `how="left"` | 左側は全部残す（VLOOKUP風。無ければNaN） |
| `how="left"` 後の `isna()` | マスタの抜け漏れを見つける定番テクニック |
| `validate="many_to_one"` 等 | 意図しない重複結合をエラーとして検出 |
| `left_on` / `right_on` | 結合キーの列名が左右で違う場合 |
| `pd.concat([df1, df2])` | 同じ形の表を縦に積む（月次ファイルの統合等） |

## ⚠ 最重要の罠: 結合キーの重複で行が増える

merge で一番ハマりやすい事故がこれ。**結合相手のキーが重複していると、
一致した組み合わせの数だけ行が増える**（`main.py` セクション3で実際に再現している）。

```python
merged = orders.merge(customers, on="customer_id")
print(f"結合前: {len(orders)} 行 / 結合後: {len(merged)} 行")   # ★ 必ず確認する
```

**結合前後で行数を確認する**、これだけでこの事故のほとんどは検知できる。
不安なら `validate="many_to_one"`（多対1のはず、と宣言する）を付けると、
想定外の重複があった時点でエラーにしてくれる。

## how の選び方フローチャート

```
両方に存在するデータだけでよい？        → how="inner"（デフォルト）
片方（基準にしたい表）は全部残したい？   → how="left" または "right"
抜け漏れがないか全体を調査したい？       → how="outer"
```

## 読む順番

1. この README
2. `main.py` を上から実行結果と見比べながら読む（特にセクション3の「行が増える罠」）
3. 改造課題へ

## 改造課題

- [ ] `merged` に対して Lv05 のgroupbyを使い、`region`（地域）別の売上合計を出してみよう
- [ ] `merged` に対して `membership_level` 別の平均注文額を出してみよう
- [ ] `how="outer"` を試して、`orders` にも `customers` にも無いはずのデータが混ざっていないか確認する使い方をやってみよう
- [ ] `validate="one_to_many"` など他のオプションも試して、エラーの出方を比べよう
- [ ] `data/orders.csv` を月ごとに3つのDataFrameに分割し、`concat` で1つに戻してみよう（元と行数が一致するか確認）
