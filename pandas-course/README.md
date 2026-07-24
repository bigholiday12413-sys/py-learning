# pandas集中講座（Lv1〜Lv11）— ビジネス実務で使う範囲まで

## これは何か

**pandas だけ**に絞った、独立した学習コースです。
メインコース（`lv01-hello-python` 以降）の「Lv1: 変数・リスト・辞書・for/if」さえ知っていれば、
メインコースを完走していなくてもこのコースだけで進められます。

架空のネットショップ「**Zakka Store**」の売上データを教材にして、
Lv1〜Lv11 を通して1つのストーリーとして扱います。

## 学べる範囲（スコープ）

**ビジネスの現場で pandas を使う場面**、つまり「Excelでやっていた集計・並べ替え・
VLOOKUP・ピボットテーブル・グラフ作成を、コードで自動化する」ところまでを扱います。

含まないもの（この先が必要になったら別の学習リソースへ）:
- 機械学習・統計モデリング（scikit-learn 等）
- 大規模データのパフォーマンスチューニング（Dask、並列処理等）
- MultiIndex の高度な操作
- 時系列の高度な統計分析（ARIMA等の予測モデル）

## 学習マップ

| Lv | フォルダ | テーマ | 学べること |
|----|---------|--------|-----------|
| 1 | `lv01-series-dataframe` | Series と DataFrame 入門 | 表の読み込み・眺め方（head/dtypes/describe） |
| 2 | `lv02-select-filter` | 抽出とフィルタリング | 列選択・絞り込み・loc/iloc・query() |
| 3 | `lv03-columns-strings` | 列の操作と文字列処理 | 列追加・apply/lambda・.str・型変換 |
| 4 | `lv04-missing-duplicates` | 欠損値・重複の処理 | isna/dropna/fillna・drop_duplicates |
| 5 | `lv05-groupby` | グループ集計 | groupby・agg・value_counts |
| 6 | `lv06-sort-rank` | 並べ替えとランキング | sort_values・nlargest・rank |
| 7 | `lv07-merge-join` | テーブルの結合 | merge（VLOOKUP相当）・concat |
| 8 | `lv08-pivot-table` | ピボットテーブル | pivot_table・crosstab |
| 9 | `lv09-datetime` | 日付データの扱い | to_datetime・resample・月次推移 |
| 10 | `lv10-visualization` | グラフ化の基本 | pandas.plot()・matplotlib基本 |
| 11 | `lv11-capstone-report` | 総合演習 | 生データ→クレンジング→集計→Excelレポート自動生成 |

## 動かし方

```bash
cd pandas-course
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows / macOSは source venv/bin/activate
pip install -r requirements.txt

cd lv01-series-dataframe
python main.py
```

`requirements.txt` はこの `pandas-course` フォルダに1つだけ置いてあり、
Lv1〜Lv11 共通で使う（pandas, openpyxl, matplotlib）。
venv は最初に1回作れば、以降は `cd lvXX... && python main.py` で進められる。

## 教材データ: Zakka Store（架空のネットショップ）

- **商品**: 5カテゴリ × 3商品（キッチン雑貨・文房具・インテリア・ファッション小物・アウトドア）
- **顧客**: 12名（関東・関西・中部・九州の4地域、ブロンズ/シルバー/ゴールドの会員ランク）
- **注文データ**: 2026年4〜6月の3ヶ月分、81件

Lv5以降で使う `orders.csv` / `customers.csv` はこの1セットのデータを指しており、
「同じデータを別の角度から見る」感覚でLv5〜Lv8を進められるようにしてある。

## 読み方

各レベルは独立したフォルダで、`README.md`（解説）と `main.py`（実行して読むコード）のペア。
`python main.py` で上から実行され、各セクションの結果が画面に出る。
出力を見ながら `main.py` のコメントを読み、最後に各READMEの改造課題に挑戦する。

## メインコースとの関係

このコースは独立して進められるが、以下と関連がある:

- `lv02-file-csv`（メインコース）… CSVの読み書きの基礎。本コースの前提
- `lv14-pandas`（メインコース）… pandasの最初の触りだけを扱うミニ導入。本コースはその本編にあたる
- `lv10-excel-report`（メインコース）… openpyxl での手動Excel生成。本コースLv11の集計後にこちらへ進むと理解が深まる
- `lv19-pandas-plotly`（日報分析編）… 本コースの集計スキルを前提に、plotlyでの可視化に発展させたもの
