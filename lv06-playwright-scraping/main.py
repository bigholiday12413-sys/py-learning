"""
Lv06 - Playwrightスクレイピング実践
====================================

このファイルでは Playwright の Sync API を使って、
動的なWebサイトからデータをスクレイピングする方法を学ぶ。

Lv05 の基礎に加えて、実務で必要になる
「待機戦略」「ページネーション」「PDF保存」「ネットワーク制御」を扱う。

対象サイト: https://books.toscrape.com（スクレイピング練習用サイト）
"""

import csv
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


# ============================================================
# 1. なぜ Playwright を使うのか？（requests + BS4 との違い）
# ============================================================
#
# requests + BeautifulSoup の限界:
#   - サーバーから返される「生のHTML」しか取得できない
#   - JavaScriptで描画されるコンテンツは取れない
#   - ボタンをクリックしてページ遷移することができない
#   - SPAサイト（React, Vue, Angularなど）のデータが取れない
#
# Playwright の強み:
#   - 実際のブラウザ（Chromium, Firefox, WebKit）を操作する
#   - JavaScriptが実行された後の最終的なDOMを取得できる
#   - クリック、入力、スクロールなどのユーザー操作を自動化できる
#   - スクリーンショットやPDF保存ができる
#   - ネットワークリクエストを監視・操作できる


# ============================================================
# 2. 出力ディレクトリの準備
# ============================================================

# スクリーンショットやCSVの保存先
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
# os.makedirs: ディレクトリを再帰的に作成する
# exist_ok=True: 既にディレクトリが存在してもエラーにしない


# ============================================================
# 3. 基本的なページ取得と待機戦略
# ============================================================

def demo_wait_strategies():
    """
    Playwrightの各種待機戦略を実演する。

    なぜ「待機」が重要か:
      動的なサイトでは、ページを開いた直後はまだデータが描画されていない
      ことがある。「何を・いつまで待つか」を適切に指定するのが
      スクレイピングを安定させるコツ。
    """
    print("=" * 60)
    print("3. 待機戦略のデモ")
    print("=" * 60)

    # sync_playwright() でPlaywrightインスタンスを作成
    with sync_playwright() as p:

        # --- ブラウザの起動 ---
        # headless=True: ブラウザウィンドウを表示しない（デフォルト）
        # headless=False にすると実際のブラウザが開いて動作を確認できる（デバッグ時に便利）
        browser = p.chromium.launch(headless=True)

        # --- ブラウザコンテキストの作成 ---
        # コンテキスト = ブラウザの「プロファイル」のようなもの
        # Cookie、ローカルストレージ、viewport などを独立して管理できる
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},  # 画面サイズ指定
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",  # UA偽装
            locale="ja-JP",  # ブラウザの言語設定
        )

        page = context.new_page()

        # ----- 待機戦略 1: wait_for_load_state() -----
        # ページ全体の読み込み状態を待つ
        # "load"       : window.onload イベント発火まで（画像等すべて読み込み完了）
        # "domcontentloaded" : DOMContentLoaded イベント発火まで
        # "networkidle" : ネットワークリクエストが500ms以上ない状態まで
        print("\n[待機1] wait_for_load_state('networkidle')")
        page.goto("https://books.toscrape.com/")
        page.wait_for_load_state("networkidle")
        print(f"  → ページタイトル: {page.title()}")

        # ----- 待機戦略 2: wait_for_selector() -----
        # 特定の要素がページに現れるまで待つ（動的コンテンツに最適）
        print("\n[待機2] wait_for_selector()")
        page.goto("https://books.toscrape.com/")
        # CSSセレクタで要素を指定
        page.wait_for_selector("article.product_pod")
        books_count = len(page.query_selector_all("article.product_pod"))
        print(f"  → 検出した書籍数: {books_count}")

        # ----- 待機戦略 3: wait_for_timeout() -----
        # 固定時間の待機（ミリ秒単位）
        # ※ なるべく使わない。他の待機戦略が使えない場合の最終手段
        print("\n[待機3] wait_for_timeout() ※非推奨・最終手段")
        page.wait_for_timeout(1000)  # 1秒待つ
        print("  → 1秒待機完了")

        # ----- 待機戦略 4: expect_response() -----
        # 特定のネットワークレスポンスを待つ
        # APIレスポンスを待ちたい場合に便利
        print("\n[待機4] expect_response()")
        # lambda関数でURLパターンをマッチさせる
        with page.expect_response(
            lambda response: "books.toscrape.com" in response.url
        ) as response_info:
            page.goto("https://books.toscrape.com/")
        response = response_info.value
        print(f"  → レスポンスステータス: {response.status}")
        print(f"  → レスポンスURL: {response.url}")

        # ブラウザを閉じる（重要！リソースリークを防ぐ）
        browser.close()

    print("\n待機戦略のデモ完了\n")


# ============================================================
# 4. 動的コンテンツからのデータ抽出
# ============================================================

def demo_data_extraction():
    """
    ページ内の要素からデータを抽出する方法を実演する。

    3つの方法を比較する:
      方法1: query_selector_all() + Python ループ（シンプル）
      方法2: evaluate()（ブラウザ内で JavaScript を実行して抽出）
      方法3: locator API（自動待機付き。Playwright の推奨）
    """
    print("=" * 60)
    print("4. データ抽出のデモ")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://books.toscrape.com/")
        page.wait_for_selector("article.product_pod")

        # --- 方法1: query_selector_all + Pythonループ ---
        # 一致した全要素をリストで受け取り、for で1つずつ処理する
        print("\n[方法1] query_selector_all でループ抽出")
        articles = page.query_selector_all("article.product_pod")

        books = []
        for article in articles[:5]:  # 最初の5冊だけ
            # text_content() で要素内のテキストを取得
            title = article.query_selector("h3 a").get_attribute("title")
            price = article.query_selector(".price_color").text_content()
            # strip() で前後の空白を除去（Pythonの文字列メソッド）
            availability = article.query_selector(".availability").text_content().strip()

            books.append({
                "title": title,
                "price": price,
                "availability": availability,
            })
            print(f"  書籍: {title[:40]}... | {price} | {availability}")

        # --- 方法2: evaluate（JavaScript実行） ---
        # ブラウザの中で JavaScript コードを実行してデータを取得する方法。
        # JavaScript はブラウザに組み込まれた言語で、evaluate() に文字列で渡す。
        # ここでは「読めなくてもOK」。こういう手段もある、という紹介
        # （ブラウザ内でしか取れない情報を取りたいときの最終手段として使う）
        print("\n[方法2] evaluate でJS実行して抽出")
        js_result = page.evaluate("""
            () => {
                // ブラウザ内で実行されるJavaScript
                const articles = document.querySelectorAll('article.product_pod');
                return Array.from(articles).slice(0, 3).map(article => ({
                    title: article.querySelector('h3 a').getAttribute('title'),
                    price: article.querySelector('.price_color').textContent,
                    rating: article.querySelector('p').className.replace('star-rating ', '')
                }));
            }
        """)
        # evaluate の戻り値はPythonのリストや辞書に自動変換される
        for book in js_result:
            print(f"  書籍: {book['title'][:40]}... | {book['price']} | 評価: {book['rating']}")

        # --- 方法3: locator API（推奨） ---
        # Playwright v1.14+ の新しいAPI。自動待機・自動リトライ付き
        print("\n[方法3] locator API（推奨）")
        # locator は要素への「参照」を保持し、操作時に自動で待機する
        book_locators = page.locator("article.product_pod")
        count = book_locators.count()
        print(f"  全書籍数: {count}")

        for i in range(min(3, count)):
            # nth(i) で i 番目の要素にアクセス
            title = book_locators.nth(i).locator("h3 a").get_attribute("title")
            price = book_locators.nth(i).locator(".price_color").text_content()
            print(f"  [{i+1}] {title[:40]}... | {price}")

        browser.close()

    print("\nデータ抽出のデモ完了\n")


# ============================================================
# 5. ページネーション（複数ページの巡回）
# ============================================================

def demo_pagination():
    """
    「次へ」ボタンをクリックして複数ページを巡回し、
    全ページのデータを収集する。

    実務ポイント:
      - 「次へ」ボタンが無くなったらループ終了
      - 各ページ遷移後にコンテンツの読み込みを待つ
      - 取得データを蓄積してCSVに保存
    """
    print("=" * 60)
    print("5. ページネーションのデモ（3ページ分取得）")
    print("=" * 60)

    all_books = []  # 全ページの書籍データを蓄積するリスト
    max_pages = 3   # デモ用に3ページまでに制限

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://books.toscrape.com/")
        page.wait_for_selector("article.product_pod")

        for page_num in range(1, max_pages + 1):
            print(f"\n--- ページ {page_num} ---")

            # 現在のページから書籍データを抽出
            articles = page.query_selector_all("article.product_pod")
            for article in articles:
                title = article.query_selector("h3 a").get_attribute("title")
                price = article.query_selector(".price_color").text_content()
                all_books.append({
                    "page": page_num,
                    "title": title,
                    "price": price,
                })

            print(f"  取得書籍数: {len(articles)}")
            print(f"  累計: {len(all_books)} 冊")

            # --- 「次へ」ボタンの確認とクリック ---
            # query_selector は要素が見つからない場合 None を返す
            next_button = page.query_selector("li.next a")

            if next_button is None or page_num >= max_pages:
                # 「次へ」ボタンがない = 最後のページ
                print("  → 最終ページに到達（またはページ上限）")
                break

            # 「次へ」ボタンをクリック
            next_button.click()

            # 新しいページのコンテンツが読み込まれるまで待機
            # ネットワーク通信が落ち着くまで待つ
            page.wait_for_load_state("networkidle")
            # さらに書籍要素が表示されるまで待つ（確実性のため）
            page.wait_for_selector("article.product_pod")

        browser.close()

    # --- CSVに保存 ---
    csv_path = os.path.join(OUTPUT_DIR, "books.csv")
    # newline="" は Windows での余分な空行を防ぐ
    # encoding="utf-8-sig" は Excelで開いたときに文字化けしないようにするBOM付きUTF-8
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["page", "title", "price"])
        writer.writeheader()  # ヘッダー行を書き込む
        writer.writerows(all_books)  # 全データを書き込む

    print(f"\n全 {len(all_books)} 冊をCSVに保存: {csv_path}")
    print("ページネーションのデモ完了\n")


# ============================================================
# 6. スクリーンショットとPDF保存
# ============================================================

def demo_screenshot_and_pdf():
    """
    ページのスクリーンショット取得とPDF保存を実演する。

    実務での使い所:
      - エビデンス取得（テスト結果の保存）
      - サイトの定期監視（見た目の差分チェック）
      - レポート生成（PDFとして保存）
    """
    print("=" * 60)
    print("6. スクリーンショットとPDF保存のデモ")
    print("=" * 60)

    with sync_playwright() as p:
        # ※ PDF保存は Chromium でのみ対応
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://books.toscrape.com/")
        page.wait_for_load_state("networkidle")

        # --- スクリーンショット（表示領域のみ） ---
        screenshot_path = os.path.join(OUTPUT_DIR, "page_screenshot.png")
        page.screenshot(path=screenshot_path)
        print(f"\n[スクショ1] 表示領域: {screenshot_path}")

        # --- スクリーンショット（フルページ） ---
        # full_page=True でページ全体をキャプチャ（スクロール領域含む）
        full_screenshot_path = os.path.join(OUTPUT_DIR, "page_full_screenshot.png")
        page.screenshot(path=full_screenshot_path, full_page=True)
        print(f"[スクショ2] フルページ: {full_screenshot_path}")

        # --- 特定要素のスクリーンショット ---
        # 要素を locator で指定してスクリーンショットを撮る
        element_screenshot_path = os.path.join(OUTPUT_DIR, "first_book.png")
        page.locator("article.product_pod").first.screenshot(path=element_screenshot_path)
        print(f"[スクショ3] 特定要素: {element_screenshot_path}")

        # --- PDF保存 ---
        # ※ headless=True の Chromium でのみ動作
        # format: A4, Letter など（デフォルトは Letter）
        # print_background: 背景色も印刷するか
        pdf_path = os.path.join(OUTPUT_DIR, "page.pdf")
        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,  # CSSの背景色も含める
            margin={
                "top": "1cm",
                "bottom": "1cm",
                "left": "1cm",
                "right": "1cm",
            },
        )
        print(f"[PDF] 保存先: {pdf_path}")

        browser.close()

    print("\nスクリーンショット・PDFのデモ完了\n")


# ============================================================
# 7. ネットワークリクエストのインターセプト
# ============================================================

def demo_network_intercept():
    """
    page.route() を使ってネットワークリクエストを制御する。

    実務での使い所:
      - 画像や広告をブロックしてスクレイピングを高速化
      - 特定APIのレスポンスを監視してデータを取得
      - リクエストをモック（テスト用）

    使い方:
      page.route("URLパターン", ハンドラ関数) を設定すると、
      パターンに一致するリクエストのたびにハンドラ関数が呼ばれる。
    """
    print("=" * 60)
    print("7. ネットワークインターセプトのデモ")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # --- ブロックするリソースタイプを定義 ---
        blocked_resource_types = {"image", "media", "font", "stylesheet"}
        # set（集合）を使うと in 演算子での検索が高速（O(1)）

        blocked_count = 0  # ブロックしたリクエスト数をカウント

        def handle_route(route):
            """
            全リクエストに対して呼ばれるハンドラ関数。
            リソースタイプに応じてブロックまたは続行する。
            """
            nonlocal blocked_count
            # nonlocal: 外側の関数の変数に代入するための宣言
            # （宣言なしで代入すると、この関数内の別変数として扱われてしまう）

            resource_type = route.request.resource_type

            if resource_type in blocked_resource_types:
                # abort() でリクエストをブロック（ダウンロードしない）
                route.abort()
                blocked_count += 1
            else:
                # continue_() でリクエストを通常通り実行
                # ※ continue は Pythonの予約語なので continue_() になっている
                route.continue_()

        # --- ルーティングの設定 ---
        # "**/*" は全てのURLにマッチするワイルドカード
        page.route("**/*", handle_route)

        print("\n画像・メディア・フォント・CSSをブロックしてページ取得...")
        page.goto("https://books.toscrape.com/")
        page.wait_for_load_state("domcontentloaded")

        title = page.title()
        print(f"  ページタイトル: {title}")
        print(f"  ブロックしたリクエスト数: {blocked_count}")

        # --- 特定URLパターンのブロック ---
        # 広告やトラッキングスクリプトをブロックする例
        print("\n[補足] 特定URLパターンのブロック例:")
        print('  page.route("**/analytics/**", lambda route: route.abort())')
        print('  page.route("**/ads/**", lambda route: route.abort())')
        print('  page.route("**/*.gif", lambda route: route.abort())')

        # --- リクエストの改変 ---
        # route.continue_() にオプションを渡すとリクエストを改変できる
        print("\n[補足] リクエスト改変の例:")
        print('  route.continue_(headers={**route.request.headers, "X-Custom": "value"})')

        browser.close()

    print("\nネットワークインターセプトのデモ完了\n")


# ============================================================
# 8. ブラウザコンテキストオプション
# ============================================================

def demo_browser_context_options():
    """
    ブラウザコンテキストの各種オプションを実演する。

    コンテキスト = ブラウザの独立した「セッション」。
    複数のコンテキストを作ることで、異なる設定で同時にページを操作できる。
    """
    print("=" * 60)
    print("8. ブラウザコンテキストオプションのデモ")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # --- モバイル端末のエミュレーション ---
        # Playwright に組み込まれたデバイス定義を使える
        iphone = p.devices["iPhone 13"]
        mobile_context = browser.new_context(**iphone)
        # **辞書 は「辞書の中身をキーワード引数として展開して渡す」記法（Lv03参照）
        mobile_page = mobile_context.new_page()
        mobile_page.goto("https://books.toscrape.com/")
        mobile_page.wait_for_load_state("networkidle")

        mobile_screenshot = os.path.join(OUTPUT_DIR, "mobile_view.png")
        mobile_page.screenshot(path=mobile_screenshot)
        print(f"\n[モバイル] viewport: {iphone['viewport']}")
        print(f"  UA: {iphone['user_agent'][:60]}...")
        print(f"  スクリーンショット: {mobile_screenshot}")
        mobile_context.close()

        # --- カスタムコンテキスト ---
        custom_context = browser.new_context(
            viewport={"width": 1920, "height": 1080},  # フルHD
            user_agent="CustomBot/1.0",                  # カスタムUA
            locale="en-US",                              # 英語ロケール
            timezone_id="America/New_York",              # タイムゾーン
            # geolocation={"latitude": 35.6762, "longitude": 139.6503},  # 位置情報（東京）
            # permissions=["geolocation"],  # 位置情報の許可
            color_scheme="dark",                         # ダークモード
            extra_http_headers={                         # 追加ヘッダー
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        custom_page = custom_context.new_page()
        custom_page.goto("https://books.toscrape.com/")
        custom_page.wait_for_load_state("networkidle")

        desktop_screenshot = os.path.join(OUTPUT_DIR, "desktop_dark_view.png")
        custom_page.screenshot(path=desktop_screenshot)
        print(f"\n[デスクトップ] viewport: 1920x1080, ダークモード")
        print(f"  スクリーンショット: {desktop_screenshot}")

        custom_context.close()
        browser.close()

    print("\nブラウザコンテキストオプションのデモ完了\n")


# ============================================================
# 9. 実践: 書籍一覧をスクレイピングしてCSV + スクリーンショット保存
# ============================================================

def practical_scraping():
    """
    ここまでのテクニックを組み合わせた実践的なスクレイピング。

    処理フロー:
      1. 画像をブロックして高速化
      2. 3ページ分の書籍データを取得
      3. 各ページのスクリーンショットを保存
      4. 全データをCSVに保存
    """
    print("=" * 60)
    print("9. 実践スクレイピング")
    print("=" * 60)

    all_books = []
    max_pages = 3

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        page = context.new_page()

        # 画像をブロックして高速化
        page.route("**/*.{png,jpg,jpeg,gif,svg,webp}", lambda route: route.abort())

        page.goto("https://books.toscrape.com/")
        page.wait_for_selector("article.product_pod")

        for page_num in range(1, max_pages + 1):
            print(f"\n--- ページ {page_num} を処理中 ---")

            # スクリーンショットを保存
            screenshot_path = os.path.join(OUTPUT_DIR, f"practical_page_{page_num}.png")
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"  スクリーンショット保存: {screenshot_path}")

            # 書籍データを抽出
            articles = page.query_selector_all("article.product_pod")
            for article in articles:
                title = article.query_selector("h3 a").get_attribute("title")
                price = article.query_selector(".price_color").text_content()
                # 星評価をクラス名から取得
                rating_class = article.query_selector("p.star-rating").get_attribute("class")
                # "star-rating Three" → "Three" を抽出
                rating = rating_class.replace("star-rating ", "")
                availability = article.query_selector(".availability").text_content().strip()

                all_books.append({
                    "page": page_num,
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "availability": availability,
                })

            print(f"  このページの書籍数: {len(articles)}")

            # 次のページへ
            next_button = page.query_selector("li.next a")
            if next_button is None or page_num >= max_pages:
                break

            next_button.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_selector("article.product_pod")

        browser.close()

    # CSVに保存
    csv_path = os.path.join(OUTPUT_DIR, "practical_books.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["page", "title", "price", "rating", "availability"],
        )
        writer.writeheader()
        writer.writerows(all_books)

    print(f"\n合計 {len(all_books)} 冊の書籍データをCSVに保存しました")
    print(f"  CSV: {csv_path}")
    print(f"  スクリーンショット: {OUTPUT_DIR}/practical_page_*.png")
    print("\n実践スクレイピング完了\n")


# ============================================================
# メイン実行
# ============================================================

if __name__ == "__main__":
    print("Lv06 - Playwrightスクレイピング実践")
    print("対象サイト: https://books.toscrape.com/")
    print()

    # 各デモを順番に実行
    # 個別にテストしたい場合はコメントアウトして実行
    demo_wait_strategies()
    demo_data_extraction()
    demo_pagination()
    demo_screenshot_and_pdf()
    demo_network_intercept()
    demo_browser_context_options()
    practical_scraping()

    print("=" * 60)
    print("全デモ完了！")
    print(f"出力ファイルは {OUTPUT_DIR} に保存されています")
    print("=" * 60)
