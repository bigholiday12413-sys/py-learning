# Lv09 - 実践：業務自動化ツール（総合プロジェクト）

## テーマ

Lv01〜Lv08 で学んだすべてを組み合わせて、実際に業務で使えるブラウザ自動化ツールを作る。
設定ファイルで動作を切り替え、ブラウザ操作→データ取得→CSV/JSON出力→ログ記録まで一気通貫で動く「本物のツール」を完成させる。

## このレベルのゴール

- 設定ファイル（config.json）で動作を制御する設計を理解する
- ログ出力（ファイル＋コンソール）の実装を学ぶ
- ブラウザ管理をクラスで行い、エラー時にスクリーンショットを保存する
- Webスクレイピング（ページ遷移・データ抽出・ページネーション）を実装する
- フォーム入力・ボタンクリックなどのブラウザ操作を自動化する
- 取得データをCSV/JSONに出力する
- PyInstaller で exe 化して配布可能な形にする

## 動かし方

### 1. 仮想環境の作成と有効化

```bash
cd lv09-gyomu-tool
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 2. パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. Playwright のブラウザインストール

```bash
playwright install chromium
```

### 4. 設定ファイルの確認

`config.json` を開いて、必要に応じて設定を変更する。
デフォルトではデモサイト（books.toscrape.com）を対象にしている。

### 5. 実行

```bash
python main.py
```

`output/` フォルダに CSV・JSON・サマリーが出力される。

## 全体の処理フロー

```
┌─────────────┐
│ main.py     │  エントリポイント
│ 設定読み込み │  config.json → dict
│ ログ設定     │  ファイル＋コンソール
└──────┬──────┘
       ▼
┌─────────────┐
│ browser.py  │  ブラウザ起動
│ BrowserManager │  with文で安全管理
└──────┬──────┘
       ▼
┌─────────────┐
│ actions.py  │  （任意）ログイン操作
│ ログイン処理 │  フォーム入力→送信
└──────┬──────┘
       ▼
┌─────────────┐
│ scraper.py  │  データ取得
│ PageScraper │  ページ巡回＋抽出
└──────┬──────┘
       ▼
┌─────────────┐
│ actions.py  │  （任意）クリック操作
│ カート追加等 │  ボタン操作＋検証
└──────┬──────┘
       ▼
┌─────────────┐
│ export.py   │  データ出力
│ CSV/JSON    │  ファイル書き出し
│ サマリー     │  レポート生成
└─────────────┘
```

## ファイル構成

```
lv09-gyomu-tool/
├── README.md           ← このファイル
├── main.py             ← エントリポイント（設定読み込み・ログ・全体制御）
├── config.json         ← 設定ファイル（URL・セレクタ・出力先など）
├── browser.py          ← ブラウザ管理クラス（起動・終了・スクリーンショット）
├── scraper.py          ← スクレイピングロジック（データ抽出・ページネーション）
├── actions.py          ← ブラウザ操作（ログイン・クリック・フォーム入力）
├── export.py           ← データ出力（CSV・JSON・サマリー）
├── requirements.txt    ← 依存パッケージ一覧
├── build.bat           ← exe化ビルドスクリプト
└── output/             ← 出力先（実行時に自動生成）
```

## 読む順番

1. **config.json** - まず設定の構造を把握する。JS の設定ファイルと同じ感覚。
2. **main.py** - エントリポイント。処理の全体像がここで分かる。
3. **browser.py** - `with` 文でリソースを管理する Python らしいパターン。JS の `try/finally` に相当。
4. **scraper.py** - Playwright のロケータ API でデータを抽出する。`querySelectorAll` + `map` のイメージ。
5. **actions.py** - フォーム入力やクリック。Puppeteer/Cypress の経験があれば馴染みやすい。
6. **export.py** - CSV/JSON出力。`fs.writeFileSync` 相当の処理。
7. **build.bat** - exe化の手順。Electron の `electron-builder` に近い概念。

## 改造課題

### 初級
- 出力ファイル名に日付を自動で付ける（`books_20240101.csv` のような形式）
- スクレイピング対象のセレクタを config.json で自由に変更できるようにする

### 中級
- 複数サイトを順番にスクレイピングする（config.json に sites 配列を追加）
- Excel(.xlsx) への出力機能を追加する（openpyxl を使用）
- ChatWork や Slack に完了通知を送る

### 上級
- GUI画面を追加する（tkinter で設定画面を作る）
- スケジューラ（schedule ライブラリ）で定期実行する
- データベース（SQLite）に結果を保存して差分検知する

## exe化の手順

### 1. PyInstaller のインストール

```bash
pip install pyinstaller
```

### 2. ビルド実行

```bash
# build.bat をダブルクリック、または手動で実行
python -m PyInstaller --onefile --name gyomu-tool main.py
```

### 3. 配布物の準備

```
dist/
├── gyomu-tool.exe    ← 実行ファイル
└── config.json       ← 設定ファイル（手動でコピー）
```

### 注意事項
- Playwright はブラウザバイナリが必要なため、exe化しても配布先で `playwright install chromium` が必要
- 社内配布の場合は、ブラウザバイナリも一緒に配布するか、インストールスクリプトを同梱する
- config.json は exe と同じフォルダに置く
