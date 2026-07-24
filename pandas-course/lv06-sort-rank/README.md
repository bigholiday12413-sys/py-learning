# pandas講座 Lv06 - 並べ替えとランキング

## テーマ

「売上トップ5」「成績の悪い順」のような、実務で頻出の並べ替えと順位付けを扱う。
Lv05のgroupbyの結果に対して使うことが非常に多いので、セットで身につける。

## 動かし方

```bash
cd pandas-course/lv06-sort-rank
python main.py
```

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `sort_values("列", ascending=False)` | 高い順に並べ替え |
| `sort_values(["列1","列2"], ascending=[...])` | 複数キーでの並べ替え |
| `nlargest(N, "列")` / `nsmallest(N, "列")` | トップN/ワーストNの近道 |
| `groupby(...).sum().sort_values(...)` | グループ別ランキング（最頻出パターン） |
| `rank(ascending=False)` | 元の順序を保ったまま順位を列として追加 |
| `reset_index(drop=True)` | indexを0始まりの連番に戻す |

## 最頻出パターン: groupby → sort_values → reset_index

```python
ranking = (
    orders.groupby("category")["subtotal"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)
```

「集計する → 並べ替える → きれいな表に戻す」の3点セットは、
レポート作成でほぼ毎回登場する。この形を覚えると応用が効く。

## sort_values(head) vs nlargest の違い

```python
df.sort_values("subtotal", ascending=False).head(3)   # 全部並べ替えてから先頭を取る
df.nlargest(3, "subtotal")                             # 「上位3件だけ」を意図した書き方
```

結果は同じだが、`nlargest`/`nsmallest` の方が「トップNが欲しい」という意図がコードから伝わる。

## 読む順番

1. この README
2. `main.py` を上から実行結果と見比べながら読む
3. 改造課題へ

## 改造課題

- [ ] 商品別（`product`）の売上ランキングを作り、トップ3を表示しよう
- [ ] `quantity`（数量）でソートし、一番多く買われた注文を探そう
- [ ] `rank(method="dense")` を試し、`method="min"` との違いを確認しよう（同率順位の後の番号の振り方が変わる）
- [ ] カテゴリ別の「平均注文額」ランキングを作ってみよう（合計ではなく平均で順位が変わることを確認）
- [ ] `data/customers.csv` の `membership_level` ごとに `orders` を集計し、会員ランク別の売上ランキングを作ろう（Lv07のmergeが先取りで必要になることに気づけたら理解が進んでいる証拠）
