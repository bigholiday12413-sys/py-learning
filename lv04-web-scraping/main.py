"""
Lv04 - Webスクレイピング入門
============================
requests + BeautifulSoup4 を使って Web ページからデータを取得する。
対象サイト: https://books.toscrape.com/ （スクレイピング練習専用サイト）

JS/TS 経験者向けに、fetch() や querySelector() との対応を示しながら進める。
"""

import csv
import time

import requests  # pip install requests  ← JS/TS の fetch() に相当
from bs4 import BeautifulSoup  # pip install beautifulsoup4  ← DOMParser に相当


# ============================================================
# 1. HTTP GET リクエスト（JS/TS の fetch() に相当）
# ============================================================
# JS/TS:
#   const response = await fetch("https://example.com");
#   const text = await response.text();
#
# Python:
#   response = requests.get("https://example.com")
#   text = response.text
#
# 違い:
#   - fetch() は非同期（async/await）だが、requests は同期的に動く
#   - requests はデフォルトでリダイレクトを自動追跡する
#   - requests はレスポンスボディに直接アクセスできる（.text, .json() など）

def demonstrate_http_request():
    """HTTP リクエストの基本を示すデモ"""
    print("=" * 60)
    print("1. HTTP GET リクエストの基本")
    print("=" * 60)

    # --- User-Agent ヘッダーを設定する ---
    # スクレイピング時はボットであることを明示するのがマナー
    # JS/TS: fetch(url, { headers: { "User-Agent": "..." } })
    headers = {
        "User-Agent": "PythonLearningBot/1.0 (学習用スクリプト)"
    }

    url = "https://books.toscrape.com/"

    # --- GET リクエストを送信 ---
    # JS/TS: const response = await fetch(url, { headers });
    response = requests.get(url, headers=headers)

    # --- ステータスコード ---
    # JS/TS: response.status     → 200
    # Python: response.status_code → 200
    print(f"ステータスコード: {response.status_code}")

    # --- レスポンスヘッダー ---
    # JS/TS: response.headers.get("content-type")
    # Python: response.headers["Content-Type"]  または .get("Content-Type")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"サーバー: {response.headers.get('Server', '不明')}")

    # --- エンコーディング ---
    # requests が自動判定してくれる（JS/TS にはない概念）
    print(f"エンコーディング: {response.encoding}")

    # --- レスポンスボディ ---
    # JS/TS: const text = await response.text();
    # Python: text = response.text （プロパティなので () 不要）
    html_text = response.text
    print(f"HTMLの長さ: {len(html_text)} 文字")
    print(f"HTML先頭100文字: {html_text[:100]}...")

    print()

    # --- JSON レスポンスの場合（参考） ---
    # JS/TS: const data = await response.json();
    # Python: data = response.json()
    # ※ books.toscrape.com は HTML なので JSON の例はコメントのみ
    # json_response = requests.get("https://api.example.com/data")
    # data = json_response.json()  # dict（辞書）として取得できる

    return response


# ============================================================
# 2. BeautifulSoup で HTML をパースする
# ============================================================
# JS/TS:
#   const parser = new DOMParser();
#   const doc = parser.parseFromString(html, "text/html");
#
# Python:
#   from bs4 import BeautifulSoup
#   soup = BeautifulSoup(html, "lxml")
#
# 違い:
#   - ブラウザの DOM ではなく、独立した HTML パーサー
#   - "lxml" は高速なパーサー（他に "html.parser"（標準）, "html5lib" もある）
#   - Tag オブジェクトは Element に近いが、メソッド名が異なる

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
                <a href="/book/2">JavaScript実践</a>
                <span class="author">鈴木花子</span>
                <img src="/images/js.jpg" alt="JavaScript実践">
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
    # JS/TS: document.querySelectorAll(".book")  → NodeList
    # Python: soup.select(".book")               → list[Tag]
    print("--- select()（querySelectorAll 相当）---")
    books = soup.select(".book")
    print(f"見つかった書籍数: {len(books)}")

    for book in books:
        print(f"  書籍HTML: {book}")

    print()

    # --------------------------------------------------------
    # 2b. select_one() - CSS セレクタで1つだけ取得
    # --------------------------------------------------------
    # JS/TS: document.querySelector("h1.title")  → Element | null
    # Python: soup.select_one("h1.title")        → Tag | None
    print("--- select_one()（querySelector 相当）---")
    title = soup.select_one("h1.title")
    print(f"タイトル要素: {title}")
    print(f"タイトルテキスト: {title.get_text()}")
    # ※ None チェックは JS/TS と同じく必要
    #    JS/TS: if (title !== null)
    #    Python: if title is not None:  または  if title:

    print()

    # --------------------------------------------------------
    # 2c. find() / find_all() - BS4 独自の検索メソッド
    # --------------------------------------------------------
    # JS/TS には直接対応するものがない。
    # CSS セレクタでは書きにくい条件で検索できる。
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
        # JS/TS: element.textContent  または  element.innerText
        # Python: tag.get_text()      または  tag.string（子が1つだけの場合）
        book_title = link.get_text()

        # --- 属性を取得 ---
        # JS/TS: element.getAttribute("href")  または  element.href
        # Python: tag["href"]                  または  tag.get("href")
        #   tag["href"]  → 属性がないと KeyError（JS なら undefined）
        #   tag.get("href")  → 属性がないと None を返す（安全）
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
    # JS/TS: try { ... } catch (error) { ... }
    # Python: try: ... except Exception as e: ...
    #
    # 違い:
    #   - Python は例外の型を指定できる（catch の条件分岐に相当）
    #   - 複数の except を書ける（JS は catch 1つで instanceof で分岐）
    try:
        print(f"リクエスト送信中: {base_url}")
        response = requests.get(base_url, headers=headers, timeout=10)

        # --- ステータスコードをチェック ---
        # raise_for_status() は 4xx/5xx エラーで例外を投げる
        # JS/TS: if (!response.ok) throw new Error(`HTTP ${response.status}`);
        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        # ネットワーク接続エラー
        # JS/TS: catch (error) { if (error instanceof TypeError) ... }
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
        # その他の requests 関連エラー（基底クラス）
        # JS/TS: catch (error) { ... }  ← 全てキャッチ
        print(f"エラー: リクエスト中に問題が発生しました: {e}")
        return []

    print(f"ステータス: {response.status_code} OK")
    print()

    # --- HTML をパース ---
    soup = BeautifulSoup(response.text, "lxml")

    # --- 書籍一覧を取得 ---
    # ブラウザの DevTools で HTML 構造を確認するのと同じ要領で、
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
        # JS/TS: element.textContent.trim()

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
        # 相対 URL を絶対 URL に変換する
        detail_url = title_tag["href"] if title_tag else ""
        # JS/TS: new URL(href, baseUrl).toString()
        # Python: urllib.parse.urljoin() でも可能だが、ここは文字列結合で十分
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
# JS/TS では CSV 出力にライブラリ（papaparse など）を使うことが多いが、
# Python には標準ライブラリに csv モジュールがある。

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
    # JS/TS: fs.writeFileSync("books.csv", csvString) に相当
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
# JS/TS: await new Promise(resolve => setTimeout(resolve, 1000));
# Python: time.sleep(1)
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
            continue  # JS/TS の continue と同じ。このページをスキップして次へ

        soup = BeautifulSoup(response.text, "lxml")
        # ... データ抽出 ...

        # --- リクエスト間隔を空ける ---
        # 最低1秒は待つのがマナー
        # JS/TS: await new Promise(r => setTimeout(r, 1000));
        time.sleep(1)

        print(f"  完了。次のページまで1秒待機...")
    '''
    print(example_code)


# ============================================================
# メイン処理
# ============================================================
# JS/TS にはない Python 独自のパターン。
# このファイルが直接実行されたときだけ実行される。
# import された場合は実行されない。
#
# JS/TS で近いのは:
#   if (import.meta.url === `file://${process.argv[1]}`) { ... }
#   （ESM の場合。実際にはあまり使わない）

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
