"""
browser.py - ブラウザ管理モジュール

BrowserManager クラスで Playwright ブラウザのライフサイクルを管理する。
with 文（コンテキストマネージャ）で使い、自動的にクリーンアップする。

JS/TS との対比:
  - コンテキストマネージャ → try/finally で browser.close() するパターン
  - __enter__ / __exit__ → JS にはない仕組み。Python の with 文専用メソッド
  - Playwright の API 自体は JS版とほぼ同じ
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

    JS/TS との対比:
        class に __enter__ と __exit__ を定義するのが Python のコンテキストマネージャ。
        JS なら以下のように書く:
            const browser = await chromium.launch();
            try {
                const page = await browser.newPage();
                // ...処理
            } finally {
                await browser.close();
            }
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

        # --- 後で代入するインスタンス変数を宣言 ---
        # JS/TS では constructor で this.xxx = null とするのと同じ
        self._playwright = None
        self._browser: Browser | None = None
        self.page: Page | None = None

    def __enter__(self):
        """
        with 文に入ったとき呼ばれる。ブラウザを起動する。

        JS/TS にはこの仕組みがない。Python 独自のプロトコル。
        with 文のブロックに入る直前に自動実行される。
        """
        self.logger.info("ブラウザを起動しています...")

        # --- Playwright を起動 ---
        self._playwright = sync_playwright().start()

        # --- ブラウザを起動 ---
        # JS 版の chromium.launch({ headless: true }) と同じ
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
        JS の finally ブロックで browser.close() するのと同じ。
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
