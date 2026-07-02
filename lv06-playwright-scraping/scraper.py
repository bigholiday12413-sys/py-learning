"""
Lv06 - 再利用可能なスクレイパークラス
=====================================

実務で使えるスクレイパーをクラスとして設計する。
以下のPythonパターンを学ぶ:
  - クラス設計（__init__, メソッド）… Lv03 の復習
  - コンテキストマネージャ（__enter__ / __exit__）→ 自作クラスを with 文で使えるようにする
  - loggingモジュール（printの代わりに構造化されたログ出力）
  - 型ヒントの実践的な使い方
"""

import csv
import logging
import os
import time
from typing import Optional
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


# ============================================================
# 1. ログ設定
# ============================================================
# logging モジュールは Python の標準ログライブラリ
# print() と違い、ログレベル（DEBUG, INFO, WARNING, ERROR）で出力を制御できる
# 本番環境では WARNING 以上のみ出力、開発時は DEBUG も出力、といった切り替えが可能

# ロガーを作成（モジュール名でロガーを識別する慣習）
logger = logging.getLogger(__name__)
# __name__ はモジュール名（このファイルでは "scraper" または "__main__"）

# ログフォーマットの設定
logging.basicConfig(
    level=logging.INFO,  # INFO以上のログを出力
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    # asctime: タイムスタンプ
    # levelname: ログレベル（INFO, WARNING, ERROR等）
    # name: ロガー名
    # message: ログメッセージ
    datefmt="%Y-%m-%d %H:%M:%S",
)


# ============================================================
# 2. スクレイパークラス
# ============================================================

class PlaywrightScraper:
    """
    Playwrightを使った再利用可能なWebスクレイパー。

    使い方（コンテキストマネージャ）:
        with PlaywrightScraper(headless=True) as scraper:
            data = scraper.scrape_page("https://example.com", "h1")
            scraper.save_to_csv(data, "output.csv")

    コンテキストマネージャのメリット:
      - with ブロックを抜けるときに自動でブラウザを閉じる
      - エラーが発生しても確実にリソースを解放する
      - Lv02 の with open(...) と同じ仕組みを「自作クラス」で実現できる
        （__enter__ と __exit__ を定義するだけ）
    """

    def __init__(
        self,
        headless: bool = True,
        block_images: bool = False,
        viewport_width: int = 1280,
        viewport_height: int = 720,
        user_agent: Optional[str] = None,
        timeout: int = 30000,
    ):
        """
        スクレイパーの初期化（コンストラクタ）。

        Args:
            headless: ブラウザを非表示で実行するか（デフォルト: True）
            block_images: 画像リクエストをブロックするか（高速化用）
            viewport_width: ブラウザの幅（ピクセル）
            viewport_height: ブラウザの高さ（ピクセル）
            user_agent: カスタムUser-Agent文字列（None=デフォルト）
            timeout: デフォルトのタイムアウト時間（ミリ秒）
        """
        # 設定をインスタンス変数に保存
        # Python では self.xxx で「このインスタンスの変数」を示す
        self._headless = headless
        self._block_images = block_images
        self._viewport_width = viewport_width
        self._viewport_height = viewport_height
        self._user_agent = user_agent
        self._timeout = timeout

        # Playwrightのインスタンス（後で初期化）
        # Optional[型] = 「その型 または None」という意味
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

        # 出力ディレクトリの準備
        self._output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self._output_dir, exist_ok=True)

        logger.info("PlaywrightScraper を初期化しました（headless=%s）", headless)

    # ============================================================
    # 3. コンテキストマネージャ（__enter__ / __exit__）
    # ============================================================

    def __enter__(self):
        """
        with 文に入ったときに呼ばれる。
        ブラウザを起動してページを準備する。

        戻り値が with ... as xxx の xxx に入る
        """
        logger.info("ブラウザを起動中...")

        # Playwrightの起動
        self._playwright = sync_playwright().start()
        # sync_playwright() は通常 with 文で使うが、
        # クラス内で管理する場合は .start() / .stop() を使う

        # ブラウザの起動
        self._browser = self._playwright.chromium.launch(headless=self._headless)

        # コンテキスト（セッション）の作成
        context_options = {
            "viewport": {
                "width": self._viewport_width,
                "height": self._viewport_height,
            },
        }
        if self._user_agent:
            context_options["user_agent"] = self._user_agent

        self._context = self._browser.new_context(**context_options)

        # ページの作成
        self._page = self._context.new_page()
        self._page.set_default_timeout(self._timeout)
        # set_default_timeout: 全操作のデフォルトタイムアウトを設定

        # 画像ブロックの設定
        if self._block_images:
            self._page.route(
                "**/*.{png,jpg,jpeg,gif,svg,webp,ico}",
                lambda route: route.abort(),
            )
            logger.info("画像リクエストのブロックを有効化")

        logger.info("ブラウザ起動完了")
        return self  # with ... as scraper の scraper に自分自身を返す

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        with ブロックを抜けるときに呼ばれる（正常終了・例外発生 両方）。
        ブラウザを確実に閉じる。

        Args:
            exc_type: 例外の型（正常終了時は None）
            exc_val: 例外の値（正常終了時は None）
            exc_tb: トレースバック（正常終了時は None）

        Returns:
            False: 例外を再送出する（Trueにすると例外を握りつぶす）
        """
        logger.info("ブラウザを終了中...")
        self.close()

        # 例外が発生していた場合はログに記録
        if exc_type is not None:
            logger.error("例外が発生しました: %s: %s", exc_type.__name__, exc_val)

        return False  # 例外を再送出（呼び出し元に例外を伝える）

    def close(self):
        """リソースを手動で解放する（with文を使わない場合用）。"""
        if self._context:
            self._context.close()
            self._context = None
        if self._browser:
            self._browser.close()
            self._browser = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        logger.info("全リソースを解放しました")

    # ============================================================
    # 4. ページ操作メソッド
    # ============================================================

    @property
    def page(self) -> Page:
        """
        現在のページオブジェクトを返すプロパティ。

        @property デコレータを使うと、メソッドをプロパティとしてアクセスできる:
          scraper.page  ← () なしでアクセス（Lv03 の Circle.radius と同じ）
        """
        if self._page is None:
            raise RuntimeError("ブラウザが起動していません。with文を使ってください。")
        return self._page

    def goto(self, url: str, wait_until: str = "networkidle") -> None:
        """
        URLに移動して読み込みを待つ。

        Args:
            url: 移動先のURL
            wait_until: 待機条件（"load", "domcontentloaded", "networkidle"）
        """
        logger.info("ページ移動: %s", url)
        self.page.goto(url)
        self.page.wait_for_load_state(wait_until)
        logger.info("ページ読み込み完了: %s", self.page.title())

    def extract_text_list(self, selector: str) -> list[str]:
        """
        セレクタにマッチする全要素のテキストをリストで返す。

        Args:
            selector: CSSセレクタ

        Returns:
            テキストのリスト

        使用例:
            prices = scraper.extract_text_list(".price_color")
            # → ["£51.77", "£53.74", "£50.10", ...]
        """
        elements = self.page.query_selector_all(selector)
        # リスト内包表記（Lv01参照）: 各要素からテキストを取り出し、
        # 前後の空白を除去した新しいリストを1行で作る
        return [el.text_content().strip() for el in elements]

    def extract_attribute_list(self, selector: str, attribute: str) -> list[str]:
        """
        セレクタにマッチする全要素の属性値をリストで返す。

        Args:
            selector: CSSセレクタ
            attribute: 取得する属性名（href, src, title など）

        Returns:
            属性値のリスト
        """
        elements = self.page.query_selector_all(selector)
        results = []
        for el in elements:
            value = el.get_attribute(attribute)
            if value is not None:
                results.append(value)
        return results

    def extract_table_data(
        self,
        row_selector: str,
        column_configs: list[dict],
    ) -> list[dict]:
        """
        表形式のデータを抽出する汎用メソッド。

        Args:
            row_selector: 各行に該当する要素のCSSセレクタ
            column_configs: 列の抽出設定のリスト。各辞書は以下のキーを持つ:
                - "name": 列名（CSV/辞書のキー名）
                - "selector": 行内での子要素セレクタ
                - "type": "text" または "attribute"
                - "attribute": type="attribute" の場合の属性名

        Returns:
            辞書のリスト（各辞書が1行のデータ）

        使用例:
            data = scraper.extract_table_data(
                row_selector="article.product_pod",
                column_configs=[
                    {"name": "title", "selector": "h3 a", "type": "attribute", "attribute": "title"},
                    {"name": "price", "selector": ".price_color", "type": "text"},
                ],
            )
        """
        rows = self.page.query_selector_all(row_selector)
        results = []

        for row in rows:
            row_data = {}
            for config in column_configs:
                el = row.query_selector(config["selector"])
                if el is None:
                    row_data[config["name"]] = ""
                    continue

                if config["type"] == "attribute":
                    row_data[config["name"]] = el.get_attribute(config.get("attribute", "")) or ""
                else:  # "text"
                    row_data[config["name"]] = el.text_content().strip()

            results.append(row_data)

        logger.info("%d 行のデータを抽出しました（セレクタ: %s）", len(results), row_selector)
        return results

    # ============================================================
    # 5. ページネーション
    # ============================================================

    def scrape_with_pagination(
        self,
        url: str,
        row_selector: str,
        column_configs: list[dict],
        next_button_selector: str = "li.next a",
        max_pages: int = 5,
    ) -> list[dict]:
        """
        ページネーションをたどりながらデータを収集する。

        Args:
            url: 最初のページのURL
            row_selector: データ行のCSSセレクタ
            column_configs: extract_table_data と同じ列設定
            next_button_selector: 「次へ」ボタンのCSSセレクタ
            max_pages: 最大ページ数

        Returns:
            全ページのデータを結合した辞書リスト
        """
        all_data = []
        self.goto(url)
        self.page.wait_for_selector(row_selector)

        for page_num in range(1, max_pages + 1):
            logger.info("ページ %d / %d を処理中...", page_num, max_pages)

            # 現在のページからデータを抽出
            page_data = self.extract_table_data(row_selector, column_configs)
            # 各行にページ番号を追加
            for row in page_data:
                row["page"] = page_num
            all_data.extend(page_data)
            # extend: リストに別のリストの全要素を追加する（append は1要素だけ）

            # 「次へ」ボタンを探す
            next_button = self.page.query_selector(next_button_selector)
            if next_button is None or page_num >= max_pages:
                logger.info("ページネーション完了（%d ページ処理済み）", page_num)
                break

            # 次のページへ遷移
            next_button.click()
            self.page.wait_for_load_state("networkidle")
            self.page.wait_for_selector(row_selector)

        logger.info("合計 %d 件のデータを収集しました", len(all_data))
        return all_data

    # ============================================================
    # 6. スクリーンショットと保存
    # ============================================================

    def take_screenshot(self, filename: str, full_page: bool = False) -> str:
        """
        スクリーンショットを保存する。

        Args:
            filename: ファイル名（拡張子 .png）
            full_page: ページ全体をキャプチャするか

        Returns:
            保存したファイルのパス
        """
        filepath = os.path.join(self._output_dir, filename)
        self.page.screenshot(path=filepath, full_page=full_page)
        logger.info("スクリーンショットを保存: %s", filepath)
        return filepath

    def save_to_csv(
        self,
        data: list[dict],
        filename: str,
        fieldnames: Optional[list[str]] = None,
    ) -> str:
        """
        辞書リストをCSVファイルに保存する。

        Args:
            data: 保存するデータ（辞書のリスト）
            filename: ファイル名
            fieldnames: CSVの列名リスト（Noneの場合はデータの最初の行のキーを使用）

        Returns:
            保存したファイルのパス
        """
        if not data:
            logger.warning("保存するデータが空です")
            return ""

        filepath = os.path.join(self._output_dir, filename)
        # fieldnames が指定されていない場合、最初のデータのキーを使う
        if fieldnames is None:
            fieldnames = list(data[0].keys())

        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        logger.info("%d 件のデータをCSVに保存: %s", len(data), filepath)
        return filepath


# ============================================================
# 7. 実行例
# ============================================================

def main():
    """
    PlaywrightScraper クラスの使用例。
    with 文で安全にリソースを管理する。
    """
    print("=" * 60)
    print("PlaywrightScraper クラスの実行例")
    print("=" * 60)

    # --- with 文でスクレイパーを使用 ---
    # with を抜けると自動で __exit__ が呼ばれ、ブラウザが閉じる
    with PlaywrightScraper(
        headless=True,
        block_images=True,  # 画像ブロックで高速化
        viewport_width=1280,
        viewport_height=720,
    ) as scraper:

        # 列の抽出設定を定義
        columns = [
            {"name": "title", "selector": "h3 a", "type": "attribute", "attribute": "title"},
            {"name": "price", "selector": ".price_color", "type": "text"},
            {"name": "rating", "selector": "p.star-rating", "type": "attribute", "attribute": "class"},
            {"name": "availability", "selector": ".availability", "type": "text"},
        ]

        # ページネーション付きスクレイピング実行
        start_time = time.time()
        data = scraper.scrape_with_pagination(
            url="https://books.toscrape.com/",
            row_selector="article.product_pod",
            column_configs=columns,
            max_pages=3,
        )
        elapsed = time.time() - start_time

        # 評価クラス名を読みやすい形に変換
        # "star-rating Three" → "Three"
        for row in data:
            row["rating"] = row["rating"].replace("star-rating ", "")

        # CSVに保存
        csv_path = scraper.save_to_csv(
            data,
            "scraper_results.csv",
            fieldnames=["page", "title", "price", "rating", "availability"],
        )

        # 最後のページのスクリーンショットを保存
        scraper.take_screenshot("scraper_final_page.png", full_page=True)

        # 結果の表示
        print(f"\n処理時間: {elapsed:.2f} 秒")
        print(f"取得データ数: {len(data)} 件")
        print(f"CSV保存先: {csv_path}")

        # 最初の5件を表示
        print("\n--- 最初の5件 ---")
        for i, book in enumerate(data[:5], 1):
            print(f"  [{i}] {book['title'][:45]}...")
            print(f"      価格: {book['price']} | 評価: {book['rating']} | {book['availability']}")

    # ← ここで with ブロック終了、自動で __exit__ → close() が呼ばれる
    print("\nブラウザは自動的に閉じられました（コンテキストマネージャ）")

    print("\n" + "=" * 60)
    print("実行完了！")
    print("=" * 60)


if __name__ == "__main__":
    main()
