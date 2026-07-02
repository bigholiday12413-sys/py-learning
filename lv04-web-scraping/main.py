"""
Lv04 - Webスクレイピング入門
============================
requests + BeautifulSoup4 を使って Web ページからデータを取得する。
対象サイト: https://books.toscrape.com/ （スクレイピング練習専用サイト）

「HTTP でページを取得する → HTML を解析する → 欲しいデータを抜き出す」
というスクレイピングの基本の流れを学ぶ。
"""

import csv
import time

import requests  # pip install requests  ← HTTP リクエストを送るライブラリ
from bs4 import BeautifulSoup  # pip install beautifulsoup4  ← HTML を解析するライブラリ


# ============================================================
# 1. HTTP GET リクエスト
# ============================================================
# ブラウザで URL を開くと、裏では「HTTP リクエスト」がサーバーに送られ、
# サーバーが HTML を返している。requests ライブラリを使うと、
# この一連のやりとりをコードから実行できる。
#
#   response = requests.get("https://example.com")
#   text = response.text
#
# ポイント:
#   - requests.get() は同期的に動く（レスポンスが返るまで次の行に進まない）
#   - リダイレクトは自動で追跡してくれる
#   - レスポンスの中身には .text や .json() で直接アクセスできる

def demonstrate_http_request():
    """HTTP リクエストの基本を示すデモ"""
    print("=" * 60)
    print("1. HTTP GET リクエストの基本")
    print("=" * 60)

    # --- User-Agent ヘッダーを設定する ---
    # User-Agent は「誰がアクセスしているか」をサーバーに伝えるヘッダー。
    # スクレイピング時はボットであることを明示するのがマナー
    headers = {
        "User-Agent": "PythonLearningBot/1.0 (学習用スクリプト)"
    }

    url = "https://books.toscrape.com/"

    # --- GET リクエストを送信 ---
    response = requests.get(url, headers=headers)

    # --- ステータスコード ---
    # 200 = 成功、404 = ページが見つからない、500 = サーバーエラー など
    print(f"ステータスコード: {response.status_code}")

    # --- レスポンスヘッダー ---
    # サーバーが返す付加情報。辞書のようにアクセスできる
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"サーバー: {response.headers.get('Server', '不明')}")

    # --- エンコーディング ---
    # 文字コードは requests が自動判定してくれる
    print(f"エンコーディング: {response.encoding}")

    # --- レスポンスボディ ---
    # .text で HTML 全文を文字列として取得（プロパティなので () 不要）
    html_text = response.text
    print(f"HTMLの長さ: {len(html_text)} 文字")
    print(f"HTML先頭100文字: {html_text[:100]}...")

    print()

    # --- JSON レスポンスの場合（参考） ---
    # API のように JSON を返す URL なら .json() で辞書として受け取れる
    # ※ books.toscrape.com は HTML なので JSON の例はコメントのみ
    # json_response = requests.get("https://api.example.com/data")
    # data = json_response.json()  # dict（辞書）として取得できる

    return response


# ============================================================
# 2. BeautifulSoup で HTML をパースする
# ============================================================
# 取得した HTML はただの長い文字列。そこから「タイトルの部分」「リンクの部分」
# を探すために、HTML を構造として解析（パース）するのが BeautifulSoup。
#
#   from bs4 import BeautifulSoup
#   soup = BeautifulSoup(html, "lxml")
#
# ポイント:
#   - "lxml" は高速なパーサー（他に "html.parser"（標準）, "html5lib" もある）
#   - 解析後は CSS セレクタなどで要素を検索できる
#   - CSS セレクタ: ".book" は class="book" の要素、"#books" は id="books" の要素、
#     "h3 a" は「h3 の中の a タグ」を意味する（Web 制作で使う指定方法と同じ）

def demonstrate_parsing():
    """HTML パースの基本を示すデモ"""
    print("=" * 60)
    print("2. BeautifulSoup による HTML パース")
    print("=" * 60)

    # --- サンプル HTML ---
    sample_html = """
    <html>
    <body>
        <h1 class="title">書籍一覧</h1>
        <div id="books">
            <div class="book" data-price="29.99">
                <a href="/book/1">Python入門</a>
                <span class="author">田中太郎</span>
                <img src="/images/python.jpg" alt="Python入門">
            </div>
            <div class="book" data-price="39.99">
                <a href="/book/2">Python実践</a>
                <span class="author">鈴木花子</span>
                <img src="/images/python2.jpg" alt="Python実践">
            </div>
        </div>
    </body>
    </html>
    """

    # --- HTML をパース ---
    # "lxml" は高速パーサー。requirements.txt に lxml を入れておく
    # "html.parser" は Python 標準で追加インストール不要
    soup = BeautifulSoup(sample_html, "lxml")

    # --------------------------------------------------------
    # 2a. select() - CSS セレクタで複数要素を取得
    # --------------------------------------------------------
    # 一致する要素すべてをリスト (list[Tag]) で返す
    print("--- select()（複数要素の取得）---")
    books = soup.select(".book")
    print(f"見つかった書籍数: {len(books)}")

    for book in books:
        print(f"  書籍HTML: {book}")

    print()

    # --------------------------------------------------------
    # 2b. select_one() - CSS セレクタで1つだけ取得
    # --------------------------------------------------------
    # 最初に一致した要素だけを返す。見つからなければ None
    print("--- select_one()（1要素の取得）---")
    title = soup.select_one("h1.title")
    print(f"タイトル要素: {title}")
    print(f"タイトルテキスト: {title.get_text()}")
    # ※ 見つからないと None が返るので、実務では
    #    if title is not None: のようなチェックを入れると安全

    print()

    # --------------------------------------------------------
    # 2c. find() / find_all() - BS4 独自の検索メソッド
    # --------------------------------------------------------
    # CSS セレクタでは書きにくい条件（属性値の組み合わせなど）で検索できる。
    print("--- find() / find_all()（BS4独自メソッド）---")

    # find_all() は select() に似ているが、タグ名や属性で柔軟に検索できる
    # 全ての <span> で class="author" のものを取得
    authors = soup.find_all("span", class_="author")
    print(f"著者一覧: {[a.get_text() for a in authors]}")

    # find() は find_all() の最初の1件だけ返す版
    first_book = soup.find("div", class_="book")
    print(f"最初の書籍: {first_book}")

    # 属性値で検索（data-* 属性など）
    # ※ data-price のようにハイフン付き属性は attrs= で辞書指定する
    expensive = soup.find("div", attrs={"data-price": "39.99"})
    print(f"39.99の書籍: {expensive.select_one('a').get_text()}")

    print()

    # --------------------------------------------------------
    # 2d. テキストと属性の取得
    # --------------------------------------------------------
    print("--- テキスト・属性の取得 ---")

    for book in soup.select(".book"):
        link = book.select_one("a")
        img = book.select_one("img")

        # --- テキストを取得 ---
        # tag.get_text() でタグに囲まれた文字列を取得
        # （子が1つだけなら tag.string でも可）
        book_title = link.get_text()

        # --- 属性を取得 ---
        # tag["href"]     → 属性がないと KeyError（エラー）になる
        # tag.get("href") → 属性がないと None を返す（安全）
        href = link["href"]
        src = img.get("src", "なし")  # デフォルト値を指定可能
        alt = img.get("alt", "")
        price = book.get("data-price", "不明")

        print(f"  タイトル: {book_title}")
        print(f"  リンク: {href}")
        print(f"  画像: {src} (alt={alt})")
        print(f"  価格: {price}")
        print()


# ============================================================
# 3. 実践: books.toscrape.com をスクレイピング
# ============================================================
# 書籍一覧ページから以下の情報を取得して CSV に保存する:
#   - タイトル
#   - 価格
#   - 在庫状況
#   - 星評価
#   - 詳細ページの URL

def scrape_books():
    """books.toscrape.com から書籍情報を取得する実践例"""
    print("=" * 60)
    print("3. 実践: books.toscrape.com をスクレイピング")
    print("=" * 60)

    base_url = "https://books.toscrape.com/"

    # --- User-Agent を設定（スクレイピングのマナー） ---
    headers = {
        "User-Agent": "PythonLearningBot/1.0 (学習用スクリプト)"
    }

    # --- エラーハンドリング ---
    # ネットワーク越しの処理は失敗がつきもの。try/except で対処する。
    #
    # ポイント:
    #   - except には例外の型を指定でき、型ごとに処理を分けられる
    #   - 具体的な例外から順に書き、最後に基底クラスで受けるのが定石
    try:
        print(f"リクエスト送信中: {base_url}")
        response = requests.get(base_url, headers=headers, timeout=10)

        # --- ステータスコードをチェック ---
        # raise_for_status() は 4xx/5xx エラーで例外を投げる
        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        # ネットワーク接続エラー
        print("エラー: サイトに接続できません。ネットワークを確認してください。")
        return []

    except requests.exceptions.Timeout:
        # タイムアウト
        print("エラー: リクエストがタイムアウトしました。")
        return []

    except requests.exceptions.HTTPError as e:
        # HTTP エラー（4xx, 5xx）
        print(f"エラー: HTTPエラーが発生しました: {e}")
        return []

    except requests.exceptions.RequestException as e:
        # その他の requests 関連エラー（上記すべての基底クラス）
        print(f"エラー: リクエスト中に問題が発生しました: {e}")
        return []

    print(f"ステータス: {response.status_code} OK")
    print()

    # --- HTML をパース ---
    soup = BeautifulSoup(response.text, "lxml")

    # --- 書籍一覧を取得 ---
    # ブラウザの開発者ツール（F12）で HTML 構造を確認し、
    # CSS セレクタを使って目的の要素を特定する
    book_elements = soup.select("article.product_pod")
    print(f"取得した書籍数: {len(book_elements)}")

    # --- 星評価のマッピング ---
    # books.toscrape.com では星評価が class 名で表現されている
    # 例: <p class="star-rating Three"> → 3つ星
    star_mapping = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    books = []

    for book_el in book_elements:
        # --- タイトルを取得 ---
        # <h3><a href="..." title="タイトル">タイトル</a></h3>
        # title 属性に完全なタイトルが入っている（テキストは省略されることがある）
        title_tag = book_el.select_one("h3 a")
        title = title_tag["title"] if title_tag else "不明"

        # --- 価格を取得 ---
        # <p class="price_color">£51.77</p>
        price_tag = book_el.select_one(".price_color")
        price = price_tag.get_text(strip=True) if price_tag else "不明"
        # get_text(strip=True) は前後の空白を除去する

        # --- 在庫状況を取得 ---
        # <p class="instock availability">
        #     <i class="icon-ok"></i> In stock
        # </p>
        stock_tag = book_el.select_one(".availability")
        stock = stock_tag.get_text(strip=True) if stock_tag else "不明"

        # --- 星評価を取得 ---
        # <p class="star-rating Three"></p>
        # class 属性はリストとして取得できる
        star_tag = book_el.select_one(".star-rating")
        if star_tag:
            # tag["class"] はクラス名のリストを返す
            # 例: ["star-rating", "Three"]
            classes = star_tag.get("class", [])
            # "star-rating" 以外のクラス名が星の数
            star_class = [c for c in classes if c != "star-rating"]
            stars = star_mapping.get(star_class[0], 0) if star_class else 0
        else:
            stars = 0

        # --- 詳細ページの URL を取得 ---
        # href には相対 URL（"catalogue/..." など）が入っているので、
        # ベース URL と結合して絶対 URL にする
        detail_url = title_tag["href"] if title_tag else ""
        # 本格的には urllib.parse.urljoin() を使うが、ここは文字列結合で十分
        full_url = base_url + detail_url

        book_data = {
            "title": title,
            "price": price,
            "stock": stock,
            "stars": stars,
            "url": full_url,
        }
        books.append(book_data)

        # --- 結果を表示 ---
        print(f"  [{stars}星] {title}")
        print(f"         価格: {price} / {stock}")
        print(f"         URL:  {full_url}")

    print()
    return books


# ============================================================
# 4. CSV に保存する
# ============================================================
# CSV 出力は Lv02 で学んだ標準ライブラリの csv モジュールを使う。

def save_to_csv(books: list[dict], filename: str = "books.csv"):
    """書籍データを CSV ファイルに保存する"""
    print("=" * 60)
    print("4. CSV にデータを保存")
    print("=" * 60)

    if not books:
        print("保存するデータがありません。")
        return

    # --- CSV ファイルに書き込む ---
    # encoding="utf-8-sig" は Excel で開いたときに文字化けしないためのBOM付きUTF-8
    # newline="" は Windows での余分な空行を防ぐ
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        # --- ヘッダー行を定義 ---
        fieldnames = ["title", "price", "stock", "stars", "url"]

        # --- csv.DictWriter を使う ---
        # 辞書のキーをヘッダーに対応させて書き込める
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # ヘッダー行を書き込む
        writer.writeheader()

        # データ行を書き込む
        for book in books:
            writer.writerow(book)

    print(f"{len(books)} 件のデータを {filename} に保存しました。")
    print()


# ============================================================
# 5. リクエスト間隔を空ける（スクレイピングのマナー）
# ============================================================
# 複数ページを巡回する場合、リクエストの間に待機時間を入れる。
# サーバーへの負荷を軽減し、アクセス拒否を防ぐため。
#
# time.sleep(秒数) でプログラムを指定秒数だけ停止できる。
#
# 今回は1ページだけなので実際には使わないが、
# 複数ページ対応時のパターンとして示す。

def scrape_with_delay_example():
    """複数ページをスクレイピングする場合のパターン（参考）"""
    print("=" * 60)
    print("5. 複数ページ巡回のパターン（参考コード）")
    print("=" * 60)

    # --- 実際にはリクエストしないデモ ---
    # 複数ページを巡回する場合のコード例を示す
    print("以下は複数ページ対応の参考コードです（実行はスキップ）:")
    print()

    example_code = '''
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"

    all_books = []

    for page_num in range(1, 51):  # 全50ページ
        url = base_url.format(page_num)
        print(f"ページ {page_num} を取得中: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"  エラー: {e}")
            continue  # このページをスキップして次のループへ

        soup = BeautifulSoup(response.text, "lxml")
        # ... データ抽出 ...

        # --- リクエスト間隔を空ける ---
        # 最低1秒は待つのがマナー
        time.sleep(1)

        print(f"  完了。次のページまで1秒待機...")
    '''
    print(example_code)


# ============================================================
# メイン処理
# ============================================================
# Lv03 で学んだ __name__ == "__main__" ガード。
# このファイルが直接実行されたときだけ実行される。
# import された場合は実行されない。

if __name__ == "__main__":
    print()
    print("*" * 60)
    print("  Lv04 - Webスクレイピング入門")
    print("  対象: https://books.toscrape.com/")
    print("*" * 60)
    print()

    # 1. HTTP リクエストの基本デモ
    demonstrate_http_request()

    # 2. HTML パースの基本デモ
    demonstrate_parsing()

    # リクエスト間隔を空ける（サーバーへの配慮）
    print("次のリクエストまで1秒待機中...")
    time.sleep(1)

    # 3. 実践スクレイピング
    books = scrape_books()

    # 4. CSV に保存
    save_to_csv(books)

    # 5. 複数ページ巡回のパターン（参考）
    scrape_with_delay_example()

    print("=" * 60)
    print("完了！ books.csv を確認してみてください。")
    print("=" * 60)
