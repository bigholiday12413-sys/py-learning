# Lv19 - pandas 集計と plotly 可視化

## テーマ

LLM で日報から抽出したデータ（CSV）を pandas で集計し、plotly でグラフ化する。

想定シナリオは「営業日報 約200件から LLM で抽出した項目
（商材名・競合社名・商談結果・極性など）を集計して、
提案資料に貼れるグラフを 2〜3 枚作る」という実務そのもの。

- pandas … Excel のピボットテーブルをコードでやるためのライブラリ
- plotly … マウスオーバーで値が見えるインタラクティブなグラフライブラリ

Lv18 (Ollama/LLM) で「抽出」を学んだ人は、この Lv19 が「集計・可視化」の続きになる。

## 動かし方

```bash
cd py-learning/lv19-pandas-plotly

# 仮想環境を作って有効化（作成済みならスキップ）
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

python main.py        # pandas の基本と集計（コンソール出力 + output/ に CSV）
python visualize.py   # plotly でグラフ生成（output/ に HTML と PNG）
```

※ PNG 出力には `kaleido` が必要（requirements.txt に入っている）。
　 HTML だけでよければ kaleido なしでも動くが、その場合は
　 `visualize.py` の `write_image()` の行をコメントアウトすること。
※ 実行すると `output/` フォルダにグラフと集計 CSV が生成される。

## 学べること

| # | トピック | JS/Excel との対応 |
|---|---------|------------------|
| 1 | `pd.read_csv()` と `parse_dates` / `dtype` | Excel で CSV を開く + 列の書式設定 |
| 2 | DataFrame / Series の基本 (`head`, `info`, `describe`, `shape`) | DataFrame ≒ Excel シート、Series ≒ 1列 |
| 3 | 列の選択・ブールインデックス (`df[df["列"] == 値]`) | JS の `array.filter()` / Excel のフィルタ |
| 4 | 欠損値処理 (`isna`, `fillna`, `dropna`) | Excel の空セル対応 |
| 5 | 日付から「月」列を作る (`dt.to_period("M")`) | Excel の `TEXT(A1,"yyyy-mm")` |
| 6 | `groupby` + `agg`（商材別件数・担当者別受注率） | Excel の SUMIF / COUNTIF |
| 7 | `pivot_table`（商材×月クロス集計） | Excel のピボットテーブルそのもの |
| 8 | `value_counts` / `pd.crosstab`（競合×勝敗） | ピボットの「行×列で件数」 |
| 9 | plotly でグループ棒・積み上げ棒・折れ線 | Excel グラフ / Chart.js |
| 10 | `write_html()`（対話的） vs `write_image()`（PNG・資料貼り付け用） | ― |

## csv モジュールと pandas の違い（いつどちらを使うか）

Lv02 では標準ライブラリの `csv` モジュールを使った。使い分けの目安：

| 観点 | `csv` モジュール (Lv02) | `pandas` (この Lv) |
|------|------------------------|---------------------|
| 追加インストール | 不要（標準ライブラリ） | `pip install pandas` が必要 |
| 得意なこと | 1行ずつ読む・書く（変換、転記） | 表全体の集計・結合・ピボット |
| データの持ち方 | list / dict（自分でループを書く） | DataFrame（ループをほぼ書かない） |
| 集計 | 自分で dict にカウントしていく | `groupby` / `pivot_table` 一発 |
| 向いている場面 | EXE 化する軽量ツール、行単位の整形 | 分析・レポート・クロス集計 |

目安：**「行を右から左へ流す」なら csv、「表を集計・分析する」なら pandas**。
PAD で言うと、csv は「Excel の起動→1行ずつ処理」に近く、
pandas は「Excel のピボットテーブルを一瞬で作る」に近い。

## 読む順番

1. この README を読む
2. `sample_extracted.csv` を開いて、どんな列があるか確認する
   （LLM が日報から抽出した結果、という想定のデータ）
3. `main.py` を上から順に読む → `python main.py` で動かす
4. `output/` に出た集計 CSV を Excel で開いて答え合わせする
5. `visualize.py` を読む → `python visualize.py` で動かす
6. `output/` の HTML をブラウザで開いてマウスオーバーしてみる（plotly の醍醐味）
7. PNG をパワポに貼ってみる → これがそのまま提案資料の素材になる

## 改造課題

- [ ] 自分の実データ（LLM 抽出結果）の列名に合わせて `main.py` を書き換えてみよう
- [ ] `pivot_table` の集計対象を「件数」から「受注のみの件数」に変えてみよう
- [ ] 担当者別の受注率を棒グラフにする `visualize.py` の 4 枚目を追加してみよう
- [ ] 極性の折れ線を「件数」と「割合(%)」で切り替えられるようにしてみよう
- [ ] グラフの配色を会社のコーポレートカラーに変えてみよう（`color_discrete_map`）
- [ ] Lv18 の LLM 抽出スクリプトの出力 CSV をそのままこの Lv の入力につないでみよう
      （抽出 → 集計 → 可視化 のパイプライン完成）
