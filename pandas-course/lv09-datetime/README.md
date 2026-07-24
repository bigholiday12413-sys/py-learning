# pandas講座 Lv09 - 日付データの扱い（datetime）

## テーマ

「月次売上」「前月比」「曜日別の傾向」は経理・営業レポートの定番。
これらはすべて「日付を正しく扱う力」が土台になっている。

## 動かし方

```bash
cd pandas-course/lv09-datetime
python main.py
```

`data/daily_sales.csv` はZakka Storeの2026年4〜6月の日別売上（91日分）。

## 最初の落とし穴: CSVの日付は「ただの文字列」

CSVから読み込んだ日付列は、そのままだと `"2026-04-01"` という**文字列**でしかない
（`dtypes` で確認すると `object` になっている）。年や月を取り出したり、月末で集計したりするには、
まず日付型に変換する必要がある。

```python
df["date"] = pd.to_datetime(df["date"])
```

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `pd.to_datetime(df["列"])` | 文字列 → 日付型への変換（最初の一手） |
| `.dt.year` / `.dt.month` / `.dt.day` | 日付から年月日を取り出す |
| `.dt.day_name()` | 曜日名を取り出す（英語） |
| `.map(辞書)` | 辞書で値を1対1変換（曜日の日本語化などに） |
| `.between("開始","終了")` | 日付の範囲で絞り込む |
| `set_index("日付列")` | 時系列データはindexに日付を置くのが作法 |
| `.resample("ME").sum()` | 日次 → 月次への集約（"ME"=月末、"W"=週） |
| `.pct_change()` | 前期比（%）を計算 |

## resample の考え方

```python
df_indexed = df.set_index("date")
monthly = df_indexed["revenue"].resample("ME").sum()
```

`resample` は「日付をindexにした状態」でないと使えない。
「日ごとの売上」を「月ごとの売上」にまとめ直す処理で、
Excelで「日付をグループ化して月単位にする」操作に相当する。

主なresampleの単位:

| 記号 | 意味 |
|------|------|
| `"D"` | 日次 |
| `"W"` | 週次 |
| `"ME"` | 月末（Month End） |
| `"QE"` | 四半期末 |
| `"YE"` | 年末 |

## pct_change() の読み方

```python
monthly.pct_change() * 100
```

「1つ前の値と比べて何%増減したか」を計算する。最初の期間は「比べる相手がない」ため
`NaN` になる（これは正常な挙動で、バグではない）。

## 読む順番

1. この README
2. `main.py` を上から実行結果と見比べながら読む
3. 改造課題へ

## 改造課題

- [ ] `resample("W")`（週次）で週ごとの売上合計と前週比を出してみよう
- [ ] 曜日別だけでなく「月初(1〜10日)/月中(11〜20日)/月末(21日〜)」の3区分で平均売上を比較してみよう
- [ ] `df["date"].dt.is_month_end` を調べて、月末フラグの列を作ってみよう
- [ ] Lv05のgroupbyと組み合わせ、`df.groupby(df["date"].dt.month)["revenue"].sum()` のように月ごとの合計を別の書き方でも出してみよう
- [ ] Lv07のorders.csv（注文単位データ）に`to_datetime`を適用し、月別のカテゴリ別売上をpivot_table（Lv08）で作ってみよう（月次×カテゴリの応用）
