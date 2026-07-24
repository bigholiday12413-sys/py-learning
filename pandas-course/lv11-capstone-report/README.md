# pandas講座 Lv11 - 総合演習：月次売上レポートの自動生成【Capstone】

## テーマ

Lv01〜Lv10で学んだことをすべて組み合わせ、**「汚れた生データ → クレンジング →
結合 → 集計 → グラフ → Excelレポート」**という実務の一連の流れを1本のスクリプトにする。

これが完走できれば、「Excelで手作業でやっていた月次レポート作成」を
自動化するための材料は揃ったと言える。

## 動かし方

```bash
cd pandas-course/lv11-capstone-report
python main.py
```

`output/monthly_report.xlsx` に、複数シート＋グラフ画像入りのレポートが生成される。
実行後、Excelで開いて確認する。

## 処理の流れとレベル対応

| ステップ | 内容 | 対応レベル |
|---------|------|-----------|
| 1 | データ読み込みと品質チェック（欠損・重複・表記ゆれの確認） | Lv01, Lv04 |
| 2 | クレンジング（`.str.strip()`、`fillna`、`drop_duplicates`） | Lv03, Lv04 |
| 3 | 顧客マスタとの結合（`merge`、結合前後の行数チェック） | Lv07 |
| 4 | 日付処理・月列の追加・小計列の追加 | Lv09, Lv03 |
| 5 | カテゴリ別・地域別の集計とランキング | Lv05, Lv06 |
| 6 | 月次×カテゴリのピボットテーブル | Lv08 |
| 7 | 月次推移グラフの作成 | Lv10 |
| 8 | 複数シート＋グラフ埋め込みのExcelレポート出力 | （新規: openpyxl連携） |

## 使用データ: あえて汚れた生データ

`data/orders_raw.csv` は、これまでのレベルで個別に扱ってきた問題を
**まとめて仕込んだ「本番想定」のデータ**:

- カテゴリ名に前後の空白（全角・半角混在）
- 数量・単価の欠損
- 重複した注文行

これを`main.py`のセクション1〜2で、実際に検出して直す様子を確認できる。

## 新しく学ぶこと: Excelへのグラフ埋め込み

```python
with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="データ")               # pandasで普通に書き出し
    ...
    sheet = writer.book.create_sheet("概要", 0)             # openpyxlで直接シート操作
    sheet.add_image(XLImage(chart_path), "B9")              # matplotlibで作った画像を貼る
```

`pd.ExcelWriter(engine="openpyxl")` を使うと、`writer.book` で
**openpyxlのWorkbookオブジェクトに直接アクセス**できる。
pandasの `to_excel()` で機械的にシートを作りつつ、同じファイルの中に
openpyxlの機能（画像埋め込み、書式設定）を組み合わせられる。

これはメインコースの `lv10-excel-report`（openpyxl単体でのレポート生成）と
今回のpandas集計を橋渡しする技術。

## 読む順番

1. この README
2. `main.py` を上から実行結果と見比べながら読む（各セクション番号がLvと対応）
3. 生成された `output/monthly_report.xlsx` を実際にExcelで開く
4. 改造課題へ

## 改造課題

- [ ] 「地域別集計」シートに、Lv06の`rank()`を使って地域ランキング列を追加してみよう
- [ ] グラフをもう1つ追加しよう（カテゴリ別売上の棒グラフ。Lv10参照）
- [ ] 概要シートに「前月比」（Lv09の`pct_change()`）の数値も追加してみよう
- [ ] `customers.csv` の `membership_level` 別の集計シートを追加してみよう
- [ ] このスクリプトを関数に分割し、`clean_data(df)` / `build_pivot(df)` のように
      再利用しやすい形にリファクタリングしてみよう（メインコースLv03の関数化の実践）
- [ ] メインコースの `lv12-scheduler-notify` と組み合わせ、「毎月1日にこのレポートを自動生成してSlackに通知する」仕組みを考えてみよう

## お疲れさまでした

ここまでで、pandasを使って「Excelでの手作業」の大半を自動化する土台ができている。
この先さらに深めたくなったら:

- **メインコースの `lv19-pandas-plotly`**（インタラクティブなグラフ、plotly）
- **メインコースの `lv15-streamlit`**（この集計結果をWeb画面にする）
- **メインコースの `lv12-scheduler-notify`**（レポートを定期実行して自動送信する）

に進むと、今回作った分析パイプラインがそのまま活きる。
