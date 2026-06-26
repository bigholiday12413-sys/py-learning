"""
Lv05 - Playwright 基礎（非同期 API）
=====================================
Python Playwright の async API を使ってブラウザを自動操作する。
main_sync.py と同じ処理を非同期で書いた版。

★ いつ async を使うべきか？
  - FastAPI / aiohttp など非同期フレームワークと組み合わせるとき
  - 複数ブラウザを並列で操作したいとき
  - 既存の asyncio ベースのプロジェクトに組み込むとき

★ 業務自動化ツールを1つ作るだけなら sync API で十分。
  async は「知っておく」レベルでOK。

JS/TS 開発者向けポイント：
  - JS/TS の async/await とほぼ同じ感覚で書ける
  - ただし Python では asyncio.run() で明示的にイベントループを起動する必要がある

実行方法：
    python main_async.py
"""

# ============================================================
# インポート
# ============================================================

# asyncio: Python の非同期処理ライブラリ
# JS/TS では async/await は言語に組み込まれているが、
# Python では asyncio モジュールを使ってイベントループを管理する
import asyncio

# async_playwright をインポート（sync 版と異なるモジュール）
# JS/TS: const { chromium } = require('playwright')
# Python sync: from playwright.sync_api import sync_playwright
# Python async: from playwright.async_api import async_playwright  ← こちら
from playwright.async_api import async_playwright

# 待機用（デモ用途）
import time


async def main():
    """
    メイン処理（非同期版）。

    sync 版との違い：
    1. 関数定義が async def になる
    2. with が async with になる
    3. ほぼ全てのメソッド呼び出しに await が付く
    4. asyncio.run(main()) で実行する

    JS/TS 開発者へ：
    JS/TS の async/await と同じ感覚で読めるはず。
    ただし Python では await を忘れると Coroutine オブジェクトが返るだけで、
    実行されないので注意（JS でも await 忘れると Promise が返るのと同じ）。
    """

    # ================================================================
    # 1. Playwright の起動とブラウザの立ち上げ（async版）
    # ================================================================

    # async with で Playwright を起動する
    # sync版:  with sync_playwright() as p:
    # async版: async with async_playwright() as p:  ← async が付く
    async with async_playwright() as p:

        # --- ブラウザを起動する ---
        # sync版:  browser = p.chromium.launch(headless=False)
        # async版: browser = await p.chromium.launch(headless=False)  ← await が付く
        print("=" * 60)
        print("【async版】ブラウザを起動します...")
        print("headless=False なので、ブラウザの画面が見えます")
        print("=" * 60)

        browser = await p.chromium.launch(
            headless=False,  # ★ ブラウザを表示する（学習のため必ず False にする）
            slow_mo=500,     # 各操作に 500ms の遅延を入れる（動きが見やすい）
        )

        # --- 新しいページ（タブ）を開く ---
        # sync版:  page = browser.new_page()
        # async版: page = await browser.new_page()  ← await が付く
        page = await browser.new_page()

        # ================================================================
        # 2. ページへのナビゲーション（async版）
        # ================================================================

        # --- URL に遷移する ---
        # sync版:  page.goto(url)
        # async版: await page.goto(url)  ← await が付く
        target_url = "https://books.toscrape.com/"
        print(f"\n{target_url} に遷移します...")
        await page.goto(target_url)

        # --- ページタイトルを取得する ---
        # sync版:  title = page.title()
        # async版: title = await page.title()  ← await が付く
        title = await page.title()
        print(f"ページタイトル: {title}")

        # --- 現在の URL を取得する ---
        # page.url はプロパティなので await 不要（sync と同じ）
        # ★ プロパティアクセスには await は付けない（JS と同じルール）
        current_url = page.url
        print(f"現在のURL: {current_url}")

        # ================================================================
        # 3. 要素の取得（async版）
        # ================================================================

        print("\n" + "=" * 60)
        print("3. 要素の取得と操作（async版）")
        print("=" * 60)

        # --- 単一要素のテキストを取得する ---
        # sync版:  page.locator("h1").text_content()
        # async版: await page.locator("h1").text_content()
        # ★ locator() 自体は await 不要。その後のメソッドに await が必要
        h1_text = await page.locator("h1").text_content()
        print(f"h1 のテキスト: {h1_text}")

        # --- 要素の属性を取得する ---
        # sync版:  locator.get_attribute("href")
        # async版: await locator.get_attribute("href")
        first_link = page.locator("aside .side_categories a").first
        link_href = await first_link.get_attribute("href")
        link_text = await first_link.text_content()
        print(f"最初のサイドバーリンク: {link_text} → {link_href}")

        # ================================================================
        # 4. 複数要素の取得（async版）
        # ================================================================

        print("\n" + "=" * 60)
        print("4. 複数要素の取得（本のタイトル一覧）")
        print("=" * 60)

        # locator() 自体は await 不要
        book_titles = page.locator("article.product_pod h3 a")

        # count() には await が必要
        # sync版:  book_titles.count()
        # async版: await book_titles.count()
        book_count = await book_titles.count()
        print(f"このページの本の数: {book_count}冊\n")

        # all() にも await が必要
        # sync版:  book_titles.all()
        # async版: await book_titles.all()
        all_books = await book_titles.all()
        for i, book in enumerate(all_books, start=1):
            full_title = await book.get_attribute("title")
            print(f"  {i:>2}. {full_title}")

        # ================================================================
        # 5. 要素の待機（async版）
        # ================================================================

        print("\n" + "=" * 60)
        print("5. 要素の待機（async版）")
        print("=" * 60)

        # sync版:  page.wait_for_selector("selector")
        # async版: await page.wait_for_selector("selector")
        await page.wait_for_selector(
            "aside .side_categories",
            state="visible",
            timeout=5000,
        )
        print("サイドバーのカテゴリが表示されました")

        # ================================================================
        # 6. クリック操作（async版）
        # ================================================================

        print("\n" + "=" * 60)
        print("6. クリックでページ遷移（async版）")
        print("=" * 60)

        next_button = page.locator("li.next a")

        url_before = page.url
        print(f"遷移前のURL: {url_before}")

        # click() に await が必要
        # sync版:  next_button.click()
        # async版: await next_button.click()
        await next_button.click()
        print("「next」ボタンをクリックしました")

        # wait_for_load_state() にも await が必要
        await page.wait_for_load_state("networkidle")
        url_after = page.url
        print(f"遷移後のURL: {url_after}")

        # 2ページ目の本を取得
        books_page2 = await page.locator("article.product_pod h3 a").all()
        print(f"\n2ページ目の本（{len(books_page2)}冊）:")
        for i, book in enumerate(books_page2, start=1):
            title = await book.get_attribute("title")
            print(f"  {i:>2}. {title}")

        # ================================================================
        # 7. テキスト入力（async版）
        # ================================================================

        print("\n" + "=" * 60)
        print("7. テキスト入力（async版の fill の例）")
        print("=" * 60)

        # fill() の async 版
        # sync版:  page.locator("input").fill("text")
        # async版: await page.locator("input").fill("text")
        print("async fill() の使い方:")
        print('  await page.locator("input[name=q]").fill("Python Playwright")')
        print("  → sync 版と同じだが、先頭に await が付くだけ")

        # ================================================================
        # 8. スクリーンショット（async版）
        # ================================================================

        print("\n" + "=" * 60)
        print("8. スクリーンショット（async版）")
        print("=" * 60)

        # screenshot() に await が必要
        # sync版:  page.screenshot(path="screenshot.png")
        # async版: await page.screenshot(path="screenshot.png")
        screenshot_path = "screenshot_async_page2.png"
        await page.screenshot(path=screenshot_path)
        print(f"スクリーンショットを保存しました: {screenshot_path}")

        # フルページスクリーンショット
        full_screenshot_path = "screenshot_async_full.png"
        await page.screenshot(path=full_screenshot_path, full_page=True)
        print(f"フルページスクリーンショットを保存しました: {full_screenshot_path}")

        # ================================================================
        # 9. ★ async ならではの機能：並列処理
        # ================================================================
        # async API の最大のメリット = 複数の処理を同時に実行できる
        # JS/TS の Promise.all() と同じ概念

        print("\n" + "=" * 60)
        print("9. ★ async ならでは：並列処理（asyncio.gather）")
        print("=" * 60)

        # 複数の情報を同時に取得する例
        # JS/TS: const [title, url] = await Promise.all([...])
        # Python: results = await asyncio.gather(coroutine1, coroutine2, ...)
        page_title, page_content_text = await asyncio.gather(
            page.title(),                                   # タイトルを取得
            page.locator("article.product_pod").first.text_content(),  # 最初の本の情報
        )
        print(f"並列取得 - タイトル: {page_title}")
        print(f"並列取得 - 最初の本の情報: {page_content_text[:80]}...")
        print("\n※ sync API ではこの並列処理はできない")
        print("※ 業務自動化で1つのブラウザを操作するだけなら sync で十分")

        # ================================================================
        # 10. ブラウザを閉じる
        # ================================================================

        # sync版:  browser.close()
        # async版: await browser.close()
        print("\n3秒後にブラウザを閉じます...")
        await asyncio.sleep(3)  # async では asyncio.sleep() を使う（time.sleep はブロッキング）

        await browser.close()
        print("ブラウザを閉じました")

    # ================================================================
    # まとめ：sync vs async の違い
    # ================================================================
    print("\n" + "=" * 60)
    print("まとめ: sync vs async の違い")
    print("=" * 60)
    print("""
    sync API:
      from playwright.sync_api import sync_playwright
      with sync_playwright() as p:
          browser = p.chromium.launch()
          page = browser.new_page()
          page.goto("https://example.com")

    async API:
      from playwright.async_api import async_playwright
      async with async_playwright() as p:
          browser = await p.chromium.launch()
          page = await browser.new_page()
          await page.goto("https://example.com")

    違いのまとめ：
      1. import 元が sync_api → async_api に変わる
      2. with → async with に変わる
      3. メソッド呼び出しに await が付く
      4. 関数定義が def → async def に変わる
      5. asyncio.run() でイベントループを起動する
      6. time.sleep() → asyncio.sleep() を使う
      7. asyncio.gather() で並列処理ができる

    ★ JS/TS 開発者にとっては async 版の方が馴染みやすいかもしれない。
    ★ しかし Python では sync 版の方がシンプルで、業務ツールには十分。
    ★ どちらを選んでも Playwright の機能は同じ。書き方が違うだけ。
    """)


# ============================================================
# エントリーポイント
# ============================================================
# asyncio.run() で非同期関数を実行する
# JS/TS ではトップレベル await が使えるが、
# Python では明示的にイベントループを起動する必要がある
#
# JS/TS:  await main()  （トップレベル await）
# Python: asyncio.run(main())  ← これが必要
if __name__ == "__main__":
    asyncio.run(main())
