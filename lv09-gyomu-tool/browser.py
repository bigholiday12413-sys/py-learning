"""
browser.py - ブラウザ管理モジュール

BrowserManager クラスで Playwright ブラウザのライフサイクルを管理する。
with 文（コンテキストマネージャ）で使い、自動的にクリーンアップする。
（__enter__ / __exit__ の仕組みは Lv06 の scraper.py で学んだ通り）
"""

import os
import logging
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Browser


class BrowserManager:
    """
    ブラウザの起動・終了を管理するクラス。
    with 文で使うことで、エラー時にも確実にブラウザが閉じる。

    使い方:
        with BrowserManager(config, logger) as bm:
            page = bm.page
            page.goto("https://example.com")

    class に __enter__ と __exit__ を定義すると、そのクラスは
    with 文で使えるようになる（コンテキストマネージャ）。
    """

    def __init__(self, browser_config: dict, logger: logging.Logger):
        """
        初期化。設定値を保持するだけで、ブラウザはまだ起動しない。

        Args:
            browser_config: config.json の browser セクション
            logger: ロガーインスタンス
        """
        self.config = browser_config
        self.logger = logger

        # --- 後で代入するインスタンス変数を None で初期化しておく ---
        # （__enter__ が呼ばれるまでは実体がないため）
        self._playwright = None
        self._browser: Browser | None = None
        self.page: Page | None = None

    def __enter__(self):
        """
        with 文に入ったとき呼ばれる。ブラウザを起動する。
        with 文のブロックに入る直前に自動実行される。
        """
        self.logger.info("ブラウザを起動しています...")

        # --- Playwright を起動 ---
        self._playwright = sync_playwright().start()

        # --- ブラウザを起動 ---
        # headless や slow_mo は config.json から渡される
        self._browser = self._playwright.chromium.launch(
            headless=self.config.get("headless", True),
            slow_mo=self.config.get("slow_mo", 0),
        )

        # --- 新しいページを作成 ---
        self.page = self._browser.new_page()

        # --- タイムアウトを設定 ---
        timeout = self.config.get("timeout", 30000)
        self.page.set_default_timeout(timeout)
        self.page.set_default_navigation_timeout(timeout)

        self.logger.info(
            f"ブラウザ起動完了 (headless={self.config.get('headless', True)})"
        )

        # --- with ... as bm の bm にこのインスタンスを返す ---
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        with 文を抜けるとき呼ばれる。ブラウザを安全に終了する。
        エラーが発生した場合はスクリーンショットを保存する。

        Args:
            exc_type: 例外の型（正常終了なら None）
            exc_val: 例外の値
            exc_tb: トレースバック
        """
        # --- エラー発生時はスクリーンショットを保存 ---
        if exc_type is not None:
            self.logger.warning(f"エラーが発生しました: {exc_val}")
            self._save_error_screenshot()

        # --- ブラウザを閉じる ---
        self._close()

        # --- False を返すと例外が再送出される（通常はこれでOK） ---
        return False

    def _save_error_screenshot(self):
        """
        エラー時のスクリーンショットを保存する。
        デバッグに便利。ブラウザの状態を画像で確認できる。
        """
        try:
            if self.page:
                # --- スクリーンショットのファイル名に日時を含める ---
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_dir = "output"
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = os.path.join(
                    screenshot_dir, f"error_{timestamp}.png"
                )

                self.page.screenshot(path=screenshot_path)
                self.logger.info(f"エラー時スクリーンショット: {screenshot_path}")
        except Exception as e:
            # スクリーンショットの保存自体が失敗しても、元の処理には影響させない
            self.logger.warning(f"スクリーンショットの保存に失敗: {e}")

    def _close(self):
        """
        ブラウザ関連リソースを順番に閉じる。
        片方の終了に失敗しても、もう片方は必ず閉じるようにしている。
        """
        try:
            if self._browser:
                self._browser.close()
                self.logger.info("ブラウザを閉じました")
        except Exception as e:
            self.logger.warning(f"ブラウザの終了でエラー: {e}")

        try:
            if self._playwright:
                self._playwright.stop()
        except Exception as e:
            self.logger.warning(f"Playwright の終了でエラー: {e}")
