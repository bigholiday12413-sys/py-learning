"""
scraper.py - スクレイピングロジック

Webページからデータを抽出するモジュール。
ページネーション（次ページへの遷移）にも対応。

JS/TS との対比:
  - page.locator() → Puppeteer の page.$() や page.$$() に相当
  - locator.all() → document.querySelectorAll() の結果を配列にしたもの
  - inner_text() → element.textContent
  - get_attribute() → element.getAttribute()
"""

import logging
from playwright.sync_api import Page


class PageScraper:
    """
    ページからデータを抽出するクラス。

    使い方:
        scraper = PageScraper(page, config, logger)
        data = scraper.scrape("https://books.toscrape.com/")

    JS/TS との対比:
        class PageScraper {
            constructor(page, config, logger) { ... }
            async scrape(url) { ... }
        }
    """

    def __init__(self, page: Page, scraping_config: dict, logger: logging.Logger):
        """
        初期化。ページオブジェクトと設定を保持する。

        Args:
            page: Playwright の Page オブジェクト
            scraping_config: config.json の scraping セクション
            logger: ロガーインスタンス
        """
        self.page = page
        self.selectors = scraping_config["selectors"]
        self.max_pages = scraping_config.get("max_pages", 3)
        self.logger = logger

    def scrape(self, start_url: str) -> list[dict]:
        """
        指定URLからデータを取得する。ページネーションにも対応。

        JS/TS との対比:
          - list[dict] → Array<{ title: string, price: string, ... }>
          - ページネーションは while ループ。JS でも同じパターン。

        Args:
            start_url: 開始ページのURL

        Returns:
            取得データのリスト（辞書のリスト）
        """
        all_data = []
        current_page_num = 1

        # --- 最初のページに移動 ---
        self.page.goto(start_url)
        self.page.wait_for_load_state("networkidle")
        self.logger.info(f"ページを読み込みました: {start_url}")

        while current_page_num <= self.max_pages:
            self.logger.info(f"--- ページ {current_page_num} を処理中 ---")

            # --- 現在のページからデータを抽出 ---
            page_data = self._extract_page_data()
            all_data.extend(page_data)
            self.logger.info(f"ページ {current_page_num}: {len(page_data)} 件取得")

            # --- 次のページがあるか確認 ---
            if current_page_num < self.max_pages and self._has_next_page():
                self._go_to_next_page()
                current_page_num += 1
            else:
                # 最大ページ数に達した、または次のページがない
                break

        self.logger.info(f"全ページ合計: {len(all_data)} 件のデータを取得")
        return all_data

    def _extract_page_data(self) -> list[dict]:
        """
        現在のページから書籍データを抽出する。

        JS/TS との対比:
          - locator.all() → [...document.querySelectorAll('.product_pod')]
          - 各要素から inner_text() → element.textContent
          - リスト内包表記 → Array.map()

        Returns:
            書籍データのリスト
        """
        data = []

        # --- 書籍コンテナをすべて取得 ---
        # JS: const books = await page.$$('article.product_pod')
        container_selector = self.selectors["book_container"]
        books = self.page.locator(container_selector).all()

        for book in books:
            try:
                # --- 各書籍の情報を抽出 ---
                # JS: const title = await book.$eval('h3 a', el => el.title)
                title_el = book.locator(self.selectors["title"])
                title = title_el.get_attribute("title") or title_el.inner_text()

                # JS: const price = await book.$eval('.price_color', el => el.textContent)
                price = book.locator(self.selectors["price"]).inner_text()

                # --- 星評価を取得 ---
                # class="star-rating Three" のような形式から評価を抜き出す
                rating_el = book.locator(self.selectors["rating"])
                rating_class = rating_el.get_attribute("class") or ""
                rating = self._parse_rating(rating_class)

                # --- リンクURLを取得 ---
                link = title_el.get_attribute("href") or ""

                # --- 辞書にまとめる ---
                # JS ならオブジェクト { title, price, rating, link }
                data.append(
                    {
                        "title": title.strip(),
                        "price": price.strip(),
                        "rating": rating,
                        "link": link,
                    }
                )
            except Exception as e:
                # 1件の抽出失敗が全体を止めないようにする
                self.logger.warning(f"データ抽出エラー（スキップ）: {e}")
                continue

        return data

    def _parse_rating(self, class_attr: str) -> str:
        """
        CSSクラスから星評価を読み取る。
        例: "star-rating Three" → "3"

        JS/TS との対比:
          dict のルックアップ → JS の Object や Map と同じ
        """
        # --- 評価名と数値の対応表 ---
        rating_map = {
            "One": "1",
            "Two": "2",
            "Three": "3",
            "Four": "4",
            "Five": "5",
        }

        # --- クラス名を分割して評価名を探す ---
        for part in class_attr.split():
            if part in rating_map:
                return rating_map[part]

        return "不明"

    def _has_next_page(self) -> bool:
        """
        次のページへのリンクが存在するか確認する。

        JS/TS との対比:
          - locator.count() → document.querySelectorAll('.next').length
          - bool を返す → JS と同じ
        """
        next_button = self.page.locator("li.next a")
        return next_button.count() > 0

    def _go_to_next_page(self):
        """
        次のページに遷移する。

        JS/TS との対比:
          - click() → element.click()
          - wait_for_load_state() → page.waitForNavigation()
        """
        self.logger.info("次のページに遷移します...")
        self.page.locator("li.next a").click()
        self.page.wait_for_load_state("networkidle")
