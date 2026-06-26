"""
actions.py - ブラウザ操作（ログイン・クリック・フォーム入力）

ページ上のフォーム入力やボタンクリックなどの操作をまとめたモジュール。

JS/TS との対比:
  - page.fill() → Puppeteer の page.type() に相当
  - page.click() → element.click() と同じ
  - locator.wait_for() → page.waitForSelector()
"""

import logging
from playwright.sync_api import Page


def perform_login(page: Page, login_config: dict, logger: logging.Logger):
    """
    ログイン処理を行う。
    デモサイト（books.toscrape.com）にはログイン機能がないため、
    ここではフォーム操作のデモとしてログインページに移動し、
    フォームに値を入力する流れを示す。

    JS/TS との対比:
      - page.goto() → page.goto() （同じ）
      - page.fill() → page.type() または page.fill()
      - page.click() → page.click()

    Args:
        page: Playwright の Page オブジェクト
        login_config: config.json の login セクション
        logger: ロガーインスタンス
    """
    login_url = login_config["login_url"]
    username = login_config["username"]
    password = login_config["password"]

    logger.info(f"ログインページに移動: {login_url}")
    page.goto(login_url)
    page.wait_for_load_state("networkidle")

    # --- ユーザー名の入力 ---
    # JS: await page.fill('#id_login', username)
    username_field = page.locator("#id_login")
    if username_field.count() > 0:
        username_field.fill(username)
        logger.info("ユーザー名を入力しました")
    else:
        logger.warning("ユーザー名フィールドが見つかりません")

    # --- パスワードの入力 ---
    password_field = page.locator("#id_password")
    if password_field.count() > 0:
        password_field.fill(password)
        logger.info("パスワードを入力しました")
    else:
        logger.warning("パスワードフィールドが見つかりません")

    # --- ログインボタンをクリック ---
    # JS: await page.click('button[type="submit"]')
    submit_button = page.locator('input[type="submit"], button[type="submit"]')
    if submit_button.count() > 0:
        submit_button.first.click()
        page.wait_for_load_state("networkidle")
        logger.info("ログインフォームを送信しました")
    else:
        logger.warning("送信ボタンが見つかりません")

    # --- ログイン結果の確認 ---
    # エラーメッセージが表示されていないか確認する
    error_message = page.locator(".alert-danger, .error")
    if error_message.count() > 0:
        logger.warning("ログインに失敗した可能性があります（エラーメッセージ検出）")
    else:
        logger.info("ログイン処理完了（エラーメッセージなし）")


def perform_cart_actions(
    page: Page,
    data: list[dict],
    actions_config: dict,
    logger: logging.Logger,
) -> int:
    """
    カートへの追加アクションを行う。
    スクレイピングで取得した書籍データのうち、指定数だけ詳細ページを開いて
    カートに追加する。

    JS/TS との対比:
      - for ループ → for...of や Array.forEach
      - enumerate() → JS なら entries() や index 付きの forEach
      - try/except → try/catch

    Args:
        page: Playwright の Page オブジェクト
        data: スクレイピングで取得したデータリスト
        actions_config: config.json の actions セクション
        logger: ロガーインスタンス

    Returns:
        成功したアクションの数
    """
    max_items = actions_config.get("max_items", 2)
    success_count = 0

    # --- 指定数だけ処理する ---
    # JS: data.slice(0, maxItems).forEach((item, i) => { ... })
    for i, item in enumerate(data[:max_items]):
        try:
            logger.info(f"[{i + 1}/{max_items}] {item['title']} をカートに追加...")

            # --- 書籍の詳細ページに移動 ---
            detail_url = item.get("link", "")
            if not detail_url:
                logger.warning("リンクが見つかりません。スキップします。")
                continue

            # --- 相対URLを絶対URLに変換 ---
            # books.toscrape.com のリンクは相対パスなので補完する
            if detail_url.startswith("catalogue/") or detail_url.startswith("../"):
                base_url = "https://books.toscrape.com/"
                # "../" を除去してベースURLと結合
                clean_path = detail_url.replace("../", "")
                detail_url = base_url + clean_path

            page.goto(detail_url)
            page.wait_for_load_state("networkidle")

            # --- 「Add to basket」ボタンをクリック ---
            # JS: await page.click('button.btn-primary')
            add_button = page.locator("button.btn-primary, .add-to-basket")
            if add_button.count() > 0:
                add_button.first.click()
                page.wait_for_load_state("networkidle")
                success_count += 1
                logger.info(f"カートに追加しました: {item['title']}")
            else:
                logger.warning("カート追加ボタンが見つかりません")

        except Exception as e:
            # 1件の失敗で全体を止めない
            logger.error(f"カート追加エラー: {item['title']} - {e}")
            continue

    return success_count
