# pandas講座 Lv03 - 列の操作と文字列処理

## テーマ

実務のデータは「前後に余計な空白がある」「表記ゆれがある」ことが非常に多い
（Excel出力・手入力・システム間連携でよく起きる）。
このレベルでは、列の追加・計算方法と、文字列データの整形方法を学ぶ。

## 動かし方

```bash
cd pandas-course/lv03-columns-strings
python main.py
```

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `df["新列"] = df["列"] * 数` | 全行への一括計算で列を追加 |
| `df["列"].apply(関数)` | 行ごとに条件分岐を含む変換を適用 |
| `apply(lambda x: ...)` | 名前のない1行関数をその場で使う |
| `.str.strip()` | 前後の空白を除去（列全体に一括） |
| `.str.contains("文字")` | 部分一致での絞り込み |
| `.str.replace("旧","新")` | 文字列の置換 |
| `.str.len()` | 文字数を数える |
| `astype(型)` | 列全体の型変換 |
| `rename(columns={...})` | 列名の変更 |
| `drop(columns=[...])` | 列の削除 |

## apply と直接計算の使い分け

```python
df["subtotal"] = df["quantity"] * df["unit_price"]          # 単純計算 → 直接書く

def price_tier(price):                                       # if分岐を含む変換
    if price >= 3000: return "高価格帯"
    ...
df["price_tier"] = df["unit_price"].apply(price_tier)        # → apply + 関数
```

「掛け算・足し算だけ」なら直接書く方が速くて読みやすい。
「条件によって処理が変わる」ときだけ `apply()` を使う、が判断基準。

## .str アクセサ ─ 表記ゆれ対策の主戦場

```python
df["customer_name"] = df["customer_name_raw"].str.strip()
```

`data/orders_with_names.csv` の `customer_name_raw` 列には、わざと前後の空白や
全角スペースを混ぜてある。`repr()` で表示するとその汚れが目に見える
（`main.py` のセクション3参照）。**「なんとなく変」と思ったらまず `.str.strip()` を疑う**のが実務の定石。

## 読む順番

1. この README
2. `main.py` を上から実行結果と見比べながら読む（特にセクション3の repr 表示に注目）
3. 改造課題へ

## 改造課題

- [ ] `df["category"].str.upper()` を試して、日本語には効果がないことを確認しよう（英語表記の列で試すとよい）
- [ ] `price_tier` 関数に「1500円未満は"エントリー価格帯"」の分岐を追加してみよう
- [ ] `df["product"].str.len()` で商品名の文字数ランキングを作ってみよう（Lv06のsort_valuesを先取り）
- [ ] `.str.strip()` を通した後の `customer_name` で、`value_counts()` を使い「誰が何回注文したか」を集計してみよう
- [ ] `rename()` で全列名を英語→日本語に変換する辞書を作ってみよう
