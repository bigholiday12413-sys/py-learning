# Lv05 - Playwright基礎：ブラウザを Python で動かす

## テーマ

Python の Playwright ライブラリを使って、ブラウザを自動操作する基礎を学ぶ。
これがこのリポジトリの **本丸** -- ここからが本番。
JS/TS の Puppeteer や Playwright (Node版) を知っている人向けに、
Python 版 Playwright の使い方を解説する。

## 動かし方

```powershell
cd py-learning/lv05-playwright-basics

# 1. 仮想環境を作成（初回のみ）
#    JS/TS の node_modules に相当する隔離環境
python -m venv venv

# 2. 仮想環境を有効化
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Windows (cmd)
.\venv\Scripts\activate.bat
# macOS / Linux
source venv/bin/activate

# 3. 依存パッケージをインストール（初回のみ）
#    JS/TS の npm install に相当
pip install -r requirements.txt

# 4. Playwright 用のブラウザをインストール（初回のみ）
#    Node版と違い、Playwright が専用ブラウザバイナリを管理する
#    chromium だけ入れれば十分（firefox, webkit も選べる）
playwright install chromium

# 5. 同期版を実行（初心者はこちらから）
python main_sync.py

# 6. 非同期版を実行（asyncio を理解してから）
python main_async.py
```

## 学べること

| Python Playwright | JS/TS 対応概念 |
|-------------------|---------------|
| `sync_playwright()` | `puppeteer.launch()` / `chromium.launch()` |
| `page.goto(url)` | `page.goto(url)` / `await page.goto(url)` |
| `page.locator(selector)` | `page.$(selector)` / `page.locator(selector)` |
| `locator.click()` | `element.click()` |
| `locator.fill(text)` | `element.type(text)` |
| `locator.text_content()` | `element.textContent` |
| `locator.get_attribute(name)` | `element.getAttribute(name)` |
| `locator.all()` | `page.$$(selector)` / `locator.all()` |
| `page.wait_for_selector()` | `page.waitForSelector()` |
| `page.screenshot()` | `page.screenshot()` |
| `headless=False` | `{ headless: false }` |

## Playwrightとは

Playwright はマイクロソフトが開発したブラウザ自動操作ライブラリ。
Node.js 版が先に登場し、後から Python 版が追加された。

### JS/TS の Puppeteer との比較

| 項目 | Puppeteer (JS) | Playwright (Python) |
|------|---------------|-------------------|
| 開発元 | Google | Microsoft |
| 対応ブラウザ | Chromium 中心 | Chromium, Firefox, WebKit |
| API スタイル | `await page.$()` | `page.locator()` |
| 自動待機 | 手動で waitFor が多い | locator が自動で待機してくれる |
| セレクタ | CSS / XPath | CSS / XPath / text= / role= など豊富 |
| Python対応 | なし | 公式サポート |

### JS Playwright と Python Playwright の違い

```javascript
// JS/TS版（おなじみの書き方）
const { chromium } = require('playwright');
const browser = await chromium.launch({ headless: false });
const page = await browser.newPage();
await page.goto('https://example.com');
await page.locator('h1').textContent();
await browser.close();
```

```python
# Python版（sync API）-- await が不要でシンプル
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://example.com")
    page.locator("h1").text_content()
    browser.close()
```

ほぼ同じだが、Python版は **snake_case**（`new_page` vs `newPage`）になる。

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

- `await` が不要でコードが読みやすい
- 上から順に1行ずつ実行される（JS でいう同期処理）
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

- `async/await` が必要（JS/TS の感覚に近い）
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
