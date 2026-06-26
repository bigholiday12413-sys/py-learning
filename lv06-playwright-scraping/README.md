# Lv06 - Playwrightスクレイピング実践

## テーマ

ブラウザ自動化ライブラリ **Playwright** を使って、JavaScriptで動的に描画されるWebページからデータを取得する方法を学ぶ。

Lv04（requests + BeautifulSoup）では取得できなかった **SPA（シングルページアプリケーション）** や **動的ロードコンテンツ** にも対応できるスクレイピング技術を身につける。

## 動かし方

```bash
# 仮想環境の作成と有効化
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# パッケージのインストール
pip install -r requirements.txt

# Playwrightのブラウザをインストール（初回のみ）
playwright install

# メインスクリプトの実行
python main.py

# 再利用可能なスクレイパークラスの実行
python scraper.py
```

## 学べること

- Playwrightの基本（Sync API）
- ページの待機戦略（wait_for_load_state, wait_for_selector, expect_response など）
- 動的コンテンツからのデータ抽出
- ページネーション（「次へ」ボタンのクリックと新コンテンツの待機）
- スクリーンショットの取得とPDF保存
- ネットワークリクエストのインターセプト（画像・広告ブロックで高速化）
- ブラウザコンテキストオプション（viewport, user_agent, locale）
- CSVファイルへのデータ保存
- クラス設計とコンテキストマネージャ（`__enter__` / `__exit__`）
- loggingモジュールによるログ出力

## Lv04（requests + BeautifulSoup）との違い

| 項目 | Lv04: requests + BS4 | Lv06: Playwright |
|------|----------------------|------------------|
| JSレンダリング | 不可（HTMLのみ取得） | 可能（実ブラウザで実行） |
| SPA対応 | 不可 | 可能 |
| ボタンクリック | 不可 | 可能 |
| スクリーンショット | 不可 | 可能 |
| PDF保存 | 不可 | 可能（Chromiumのみ） |
| 速度 | 速い | 遅い（ブラウザ起動のため） |
| メモリ使用量 | 少ない | 多い |
| 向いている用途 | 静的HTML、API | 動的サイト、操作が必要なサイト |

**使い分けの指針**: まず requests で試し、JSレンダリングが必要な場合のみ Playwright を使う。

## 読む順番

1. **この README** - 全体像を把握
2. **main.py** - Playwrightの各機能を順番に学ぶ（待機戦略、ページネーション、スクショ、PDF、ネットワークインターセプト）
3. **scraper.py** - 実務で使える再利用可能なクラス設計を学ぶ

## 改造課題

1. **別サイトのスクレイピング**: `quotes.toscrape.com/js/` をスクレイピングしてみよう（JS描画版）
2. **ログイン付きスクレイピング**: `books.toscrape.com` のログインページからログインしてからスクレイピング
3. **無限スクロール対応**: 無限スクロールのサイト（例: Twitterライク）をスクレイピングする関数を追加
4. **並列スクレイピング**: 複数ページを同時にスクレイピングする処理を実装（`browser.new_page()` を複数作る）
5. **データベース保存**: CSVの代わりにSQLiteにデータを保存するように改造
6. **エラーリトライ**: タイムアウトエラー時に自動リトライする仕組みを追加
