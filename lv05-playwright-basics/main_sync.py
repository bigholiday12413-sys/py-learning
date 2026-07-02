"""
Lv05 - Playwright 基礎（同期 API）
===================================
Python Playwright の sync API を使ってブラウザを自動操作する。
初心者はまずこちらから始める。

ポイント：
- sync API は上から順に1行ずつ実行されるので読みやすい
- 各操作は完了するまで次の行に進まない（await などの記述は不要）
- with 文で playwright のリソースを管理する（Lv02 のファイルと同じ考え方）

実行方法：
    python main_sync.py
"""

# ============================================================
# インポート
# ============================================================

# playwright.sync_api から sync_playwright をインポート
# sync = 同期 → 各操作の完了を待ちながら順番に実行される API
from playwright.sync_api import sync_playwright

# time モジュール -- 動作確認用の待機に使う（実務では不要なことが多い）
import time


def main():
    """
    メイン処理：ブラウザを起動して Web サイトを操作する。

    sync_playwright() は with 文で使う。
    with ブロックを抜けると自動的にリソースが解放される
    （ファイルの with open(...) と同じ仕組み）。
    """

    # ================================================================
    # 1. Playwright の起動とブラウザの立ち上げ
    # ================================================================

    # with sync_playwright() as p: で Playwright を起動する
    # p を通じてブラウザ (chromium / firefox / webkit) を立ち上げられる
    with sync_playwright() as p:

        # --- ブラウザを起動する ---
        # headless=False → ブラウザの画面が表示される（学習中はこれが重要！）
        # headless=True（デフォルト）にすると画面なしで実行される
        # slow_mo=500 → 各操作の間に 500ms の遅延を入れる（デモ用）
        #                実務では外すか小さくする
        print("=" * 60)
        print("ブラウザを起動します...")
        print("headless=False なので、ブラウザの画面が見えます")
        print("=" * 60)

        browser = p.chromium.launch(
            headless=False,  # ★ ブラウザを表示する（学習のため必ず False にする）
            slow_mo=500,     # 各操作に 500ms の遅延を入れる（動きが見やすい）
        )

        # --- 新しいページ（タブ）を開く ---
        page = browser.new_page()

        # ================================================================
        # 2. ページへのナビゲーション（遷移）
        # ================================================================

        # --- URL に遷移する ---
        # goto() はページの読み込みが完了するまで待ってから次に進む
        target_url = "https://books.toscrape.com/"
        print(f"\n{target_url} に遷移します...")
        page.goto(target_url)

        # --- ページタイトルを取得する ---
        title = page.title()
        print(f"ページタイトル: {title}")

        # --- 現在の URL を取得する ---
        # page.url はプロパティなので () を付けない
        current_url = page.url
        print(f"現在のURL: {current_url}")

        # ================================================================
        # 3. 要素の取得 -- page.locator()
        # ================================================================
        # locator() は Playwright の推奨する要素取得方法。
        # Lv04 の BeautifulSoup と同じく CSS セレクタで要素を指定するが、
        # 大きな違いとして「自動待機機能」がある
        # → 要素が表示されるまで自動で待ってくれる（明示的な待機が不要なことが多い）

        print("\n" + "=" * 60)
        print("3. 要素の取得と操作")
        print("=" * 60)

        # --- 単一要素のテキストを取得する ---
        # text_content() は要素内のテキストを返す
        h1_text = page.locator("h1").text_content()
        print(f"h1 のテキスト: {h1_text}")

        # --- 要素の属性を取得する ---
        # get_attribute() で HTML 属性の値を取る
        # .first は「一致した要素のうち最初の1つ」を指す
        # 例: サイドバーのリンクの href を取得
        first_link = page.locator("aside .side_categories a").first
        link_href = first_link.get_attribute("href")
        link_text = first_link.text_content()
        print(f"最初のサイドバーリンク: {link_text} → {link_href}")

        # ================================================================
        # 4. 複数要素の取得 -- locator().all()
        # ================================================================
        # locator はセレクタに一致する「全要素」を表せる。
        # all() を呼ぶと、その時点の一致要素をリストで受け取れる。

        print("\n" + "=" * 60)
        print("4. 複数要素の取得（本のタイトル一覧）")
        print("=" * 60)

        # 本のタイトルを全件取得する
        # books.toscrape.com では、h3 > a に本のタイトルが入っている
        book_titles = page.locator("article.product_pod h3 a")

        # count() で要素数を取得する
        book_count = book_titles.count()
        print(f"このページの本の数: {book_count}冊\n")

        # all() で全要素をリストとして取得する → list[Locator]
        for i, book in enumerate(book_titles.all(), start=1):
            # title 属性に完全なタイトルが入っている
            # （テキスト表示は省略されることがあるため）
            full_title = book.get_attribute("title")
            # テキストとしても取得してみる（省略版）
            short_title = book.text_content()
            print(f"  {i:>2}. {full_title}")

        # ================================================================
        # 5. 要素の待機 -- wait_for_selector()
        # ================================================================
        # wait_for_selector() は指定セレクタの要素が現れるまで待機する。
        # Playwright の locator は自動待機するが、明示的に待ちたい場合に使う。

        print("\n" + "=" * 60)
        print("5. 要素の待機")
        print("=" * 60)

        # wait_for_selector でサイドバーが表示されるのを確認する
        # state="visible" → 要素が見える状態になるまで待つ
        # timeout=5000    → 最大 5000ms（5秒）待つ（デフォルトは30秒）
        page.wait_for_selector(
            "aside .side_categories",  # サイドバーのカテゴリ
            state="visible",           # 表示状態になるまで待つ
            timeout=5000,              # 最大5秒待つ
        )
        print("サイドバーのカテゴリが表示されました")

        # ================================================================
        # 6. クリック操作 -- locator.click()
        # ================================================================
        # click() は要素をクリックする。
        # 人間がマウスでクリックするのと同じことをコードで実行できる。

        print("\n" + "=" * 60)
        print("6. クリックでページ遷移")
        print("=" * 60)

        # "next" ボタンをクリックして2ページ目に遷移する
        # books.toscrape.com では .next > a が「次のページ」ボタン
        next_button = page.locator("li.next a")

        # クリック前の URL を記録
        url_before = page.url
        print(f"遷移前のURL: {url_before}")

        # クリックする
        next_button.click()
        print("「next」ボタンをクリックしました")

        # ページ遷移後の URL を確認
        # click() 後に自動的にナビゲーションを待ってくれることが多いが、
        # 念のため wait_for_load_state() で完了を待つ
        page.wait_for_load_state("networkidle")  # ネットワークが静かになるまで待つ
        url_after = page.url
        print(f"遷移後のURL: {url_after}")

        # 2ページ目の本も取得してみる
        books_page2 = page.locator("article.product_pod h3 a").all()
        print(f"\n2ページ目の本（{len(books_page2)}冊）:")
        for i, book in enumerate(books_page2, start=1):
            print(f"  {i:>2}. {book.get_attribute('title')}")

        # ================================================================
        # 7. テキスト入力 -- locator.fill()
        # ================================================================
        # fill() はテキストフィールドに文字を入力する。
        #
        # ※ fill() は既存の値をクリアしてから入力する
        # ※ 1文字ずつ入力する type() もあるが、fill() の方が高速で推奨されている

        print("\n" + "=" * 60)
        print("7. テキスト入力（fill の例）")
        print("=" * 60)

        # books.toscrape.com にはフォームがないので、
        # ここでは使い方の紹介のみ（フォーム操作は Lv07 でたっぷり練習する）
        print("fill() の使い方:")
        print('  page.locator("input[name=q]").fill("Python Playwright")')
        print("  → テキストフィールドに「Python Playwright」と入力する")
        print("  ※ fill() は既存テキストをクリアしてから入力する")

        # ================================================================
        # 8. スクリーンショット -- page.screenshot()
        # ================================================================
        # screenshot() は現在のページのスクリーンショットを撮る。
        # 自動化処理の途中経過を記録したり、エラー時の状況確認に便利。

        print("\n" + "=" * 60)
        print("8. スクリーンショット")
        print("=" * 60)

        # ページ全体のスクリーンショットを保存
        screenshot_path = "screenshot_page2.png"
        page.screenshot(path=screenshot_path)
        print(f"スクリーンショットを保存しました: {screenshot_path}")

        # full_page=True で、スクロールが必要なページも全体を撮れる
        full_screenshot_path = "screenshot_full.png"
        page.screenshot(path=full_screenshot_path, full_page=True)
        print(f"フルページスクリーンショットを保存しました: {full_screenshot_path}")

        # 特定の要素だけのスクリーンショットも撮れる
        element_screenshot_path = "screenshot_header.png"
        page.locator("header").screenshot(path=element_screenshot_path)
        print(f"ヘッダーのスクリーンショットを保存しました: {element_screenshot_path}")

        # ================================================================
        # 9. ブラウザを閉じる
        # ================================================================
        # with 文で管理しているので、ブロック終了時に自動で閉じられるが、
        # 明示的に閉じることもできる

        # 結果が見えるように少し待つ（学習用）
        print("\n3秒後にブラウザを閉じます...")
        time.sleep(3)

        browser.close()
        print("ブラウザを閉じました")

    # with ブロックを抜けると sync_playwright のリソースも解放される

    # ================================================================
    # まとめ
    # ================================================================
    print("\n" + "=" * 60)
    print("まとめ: Playwright sync API の基本操作")
    print("=" * 60)
    print("""
    1. sync_playwright() を with 文で起動する
    2. p.chromium.launch(headless=False) でブラウザを起動（目で見える）
    3. browser.new_page() で新しいタブを開く
    4. page.goto(url) でページに遷移する
    5. page.locator(selector) で要素を取得する
       - .text_content()    → テキストを取得
       - .get_attribute()   → 属性を取得
       - .click()           → クリック
       - .fill()            → テキスト入力
       - .all()             → 複数要素をリストで取得
    6. page.wait_for_selector() で要素の出現を待つ
    7. page.screenshot() でスクリーンショットを撮る
    8. browser.close() でブラウザを閉じる

    ★ locator は要素が現れるまで自動で待ってくれるのが Playwright の強み！
    """)


# ============================================================
# エントリーポイント
# ============================================================
# __name__ == "__main__" ガード（Lv03 で学んだ慣習）。
# このファイルが直接実行されたときだけ main() を呼ぶ。
# import されたときは main() が実行されない。
if __name__ == "__main__":
    main()
