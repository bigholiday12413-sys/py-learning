# Lv10 - Excelレポート出力（openpyxl）【発展編】

## テーマ

CSVではなく「そのまま提出できるExcelレポート」を Python で自動生成する。
複数シート・書式設定・集計・Excel数式の埋め込みまでを一通り学ぶ。

実務では「CSVで渡しても、結局誰かが Excel で開いて整形している」ことが非常に多い。
**その整形作業ごと自動化する**のがこのレベルのゴール。

## なぜ CSV だけでは足りないか

| | CSV (Lv02〜) | Excel (Lv10) |
|--|-------------|--------------|
| シート | 1つだけ | 複数（生データ＋集計＋表紙） |
| 書式 | なし | 色・罫線・列幅・数値フォーマット |
| フィルタ/固定行 | なし | オートフィルタ・ウィンドウ枠固定 |
| 数式 | なし | `=SUM(...)` などを埋め込める |
| 向き | プログラム間のデータ受け渡し | 人間が見る最終成果物 |

## 動かし方

```bash
cd lv10-excel-report
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows / macOSは source venv/bin/activate
pip install -r requirements.txt
python main.py
```

`output/report_日時.xlsx` が生成されるので、Excel（またはLibreOffice等）で開いて確認する。

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `Workbook` / `create_sheet` | Excelファイルとシートの作成 |
| `ws.cell(row, column, value)` | セル単位の書き込み（1始まり） |
| `ws.append(list)` | 1行まとめて追加 |
| `Font` / `PatternFill` / `Border` | 文字色・背景色・罫線 |
| `number_format` | 小数桁数などの表示形式 |
| `column_dimensions[...].width` | 列幅の調整 |
| `auto_filter` / `freeze_panes` | フィルタとヘッダー行固定 |
| `value="=SUM(...)"` | Excel数式の埋め込み |
| `setdefault()` | 辞書グループ化の便利メソッド（Lv02の発展） |

## 読む順番

1. この README
2. `main.py` を上から読む（スタイル定義 → 生データ → 集計 → 表紙）
3. 実行して、生成された xlsx を **実際に Excel で開く**
4. 改造課題へ

## 改造課題

- [ ] 在庫数が 20 未満の行の背景を黄色にしてみよう（`PatternFill`）
- [ ] 「価格帯別集計」シート（〜20 / 20〜40 / 40〜）を追加してみよう
- [ ] Lv09 のツールに `export_excel.py` として組み込み、CSV と Excel を両方出力してみよう
- [ ] 既存の Excel ファイルを読み込んで加工してみよう（`load_workbook()`）
- [ ] グラフ（棒グラフ）を集計シートに追加してみよう（`openpyxl.chart.BarChart`）

## 補足: pandas という選択肢

データ量が多い・集計が複雑な場合は、データ分析ライブラリ **pandas** の
`df.to_excel()` を使う方法もある。まず openpyxl で「Excelの構造」を理解しておくと、
pandas に進んだときも何が起きているか分かる。
