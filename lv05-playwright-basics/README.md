# Lv05 - Playwright基礎：ブラウザを Python で動かす

## テーマ

Python の Playwright ライブラリを使って、ブラウザを自動操作する基礎を学ぶ。
これがこのリポジトリの **本丸** -- ここからが本番。
「ページを開く・要素を取得する・クリックする・入力する・スクリーンショットを撮る」
という自動操作の基本要素を一通り体験する。

## 動かし方

```powershell
cd py-learning/lv05-playwright-basics

# 1. 仮想環境を作成（初回のみ）
python -m venv venv

# 2. 仮想環境を有効化
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Windows (cmd)
.\venv\Scripts\activate.bat
# macOS / Linux
source venv/bin/activate

# 3. 依存パッケージをインストール（初回のみ）
pip install -r requirements.txt

# 4. Playwright 用のブラウザをインストール（初回のみ）
#    Playwright は自動操作専用のブラウザバイナリを自分で管理する
#    chromium だけ入れれば十分（firefox, webkit も選べる）
playwright install chromium

# 5. 同期版を実行（初心者はこちらから）
python main_sync.py

# 6. 非同期版を実行（asyncio を理解してから）
python main_async.py
```

## 学べること

| Python Playwright | ひとことで言うと |
|-------------------|----------------|
| `sync_playwright()` | Playwright を起動する入口 |
| `p.chromium.launch()` | ブラウザを立ち上げる |
| `page.goto(url)` | URL に移動する |
| `page.locator(selector)` | CSS セレクタで要素を指定する |
| `locator.click()` | 要素をクリックする |
| `locator.fill(text)` | テキストフィールドに入力する |
| `locator.text_content()` | 要素内のテキストを取得する |
| `locator.get_attribute(name)` | 要素の属性値を取得する |
| `locator.all()` | 一致する全要素をリストで取得する |
| `page.wait_for_selector()` | 要素が現れるまで待つ |
| `page.screenshot()` | スクリーンショットを撮る |
| `headless=False` | ブラウザ画面を表示して実行する |

## Playwrightとは

Playwright はマイクロソフトが開発したブラウザ自動操作ライブラリ。
Chromium / Firefox / WebKit の3種類のブラウザに対応している。

### Lv04 のスクレイピングとの違い

| 項目 | requests + BeautifulSoup (Lv04) | Playwright (Lv05〜) |
|------|--------------------------------|---------------------|
| 仕組み | HTML を文字列として取得して解析 | 本物のブラウザを起動して操作 |
| JavaScript 実行 | されない（静的HTMLのみ） | される（動的サイトもOK） |
| ログイン・クリック・入力 | 苦手（手動でHTTPを組む必要） | 得意（人間の操作を再現） |
| 速度・軽さ | 速い・軽い | 遅い・重い |
| 使い分け | 静的なページの一括取得 | 動的なページ・操作が必要な業務 |

### Playwright の強み: 自動待機

`page.locator()` で取得した要素は、操作時に
「要素が画面に現れるまで自動で待って」くれる。
このおかげで「まだ表示されていない要素をクリックして失敗」が起きにくい。

## sync vs async API

Python Playwright は **2つのAPI** を提供している。

### sync API（同期）-- 初心者はこちら

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()
```

- 上から順に1行ずつ実行される。素直に読める
- 各操作が完了するまで次の行に進まない
- **スクリプトや業務自動化ツールにはこれで十分**

### async API（非同期）

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com")
        print(await page.title())
        await browser.close()

asyncio.run(main())
```

- `async def` / `await` を使って書く（詳しくは `main_async.py` の解説を参照）
- FastAPI や aiohttp など非同期フレームワークと組み合わせる場合に使う
- 複数ブラウザの並列操作が可能

**結論：業務自動化ツールを作るなら sync API で十分。**

## 読む順番

1. この README を読む
2. **`main_sync.py`** を上から順に読む（まずはこちら）
3. `python main_sync.py` で実行し、**ブラウザが動くのを目で確認する**
4. **`main_async.py`** を読んで async 版との違いを理解する
5. `python main_async.py` で実行する
6. 改造課題に挑戦する

## 改造課題

- [ ] 別のサイト（例: Wikipedia）を開いてタイトルとh1テキストを取得してみよう
- [ ] スクリーンショットのファイル名に日時を含めてみよう（`datetime` モジュール）
- [ ] 本のタイトルだけでなく、価格も一緒に取得してみよう
- [ ] 3ページ目まで自動でページ遷移して、全ページの本タイトルを集めてみよう
- [ ] 取得した本の情報を CSV ファイルに保存してみよう（Lv02 の知識を活用）
- [ ] `headless=True` に変えて実行し、見えない状態でも動くことを確認してみよう
- [ ] `page.locator()` の代わりに `page.query_selector()` を使ってみて、違いを比較しよう
