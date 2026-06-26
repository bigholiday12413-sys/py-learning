"""
Lv07: Playwrightクリック操作・フォーム自動入力
==============================================

Playwrightの同期APIを使って、ローカルHTMLフォームを自動操作する。
業務自動化で必要なフォーム操作パターンを網羅的に学ぶ。

JS/TS経験者向けポイント:
- Node版: await page.fill('#id', 'text')
- Python同期版: page.locator('#id').fill('text')  ← awaitなし
- Python非同期版: await page.locator('#id').fill('text')  ← asyncio使用
- このファイルでは同期APIのみ使用（業務スクリプトでは同期で十分）

実行方法:
    python main.py
"""

import os
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, Dialog, Page

# ============================================================
# 練習用HTMLファイルのパスを取得
# ============================================================
# __file__ は現在のスクリプトのパス
# practice_page.html は同じディレクトリにある
SCRIPT_DIR = Path(__file__).parent
PRACTICE_PAGE = SCRIPT_DIR / "practice_page.html"
# file:// プロトコルでローカルHTMLを開く
PRACTICE_URL = PRACTICE_PAGE.as_uri()

# スクリーンショット保存先
SCREENSHOT_DIR = SCRIPT_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


def demo_text_input(page: Page) -> None:
    """
    テキスト入力の基本操作
    ======================
    fill(): フィールドをクリアしてから入力する（最もよく使う）
    clear(): フィールドの値をクリアする
    type(): 1文字ずつ入力する（fill()より遅いが、キー入力イベントが発火する）

    JS/TS対比:
      Node: await page.fill('#username', 'tanaka')
      Python: page.locator('#username').fill('tanaka')
    """
    print("\n=== テキスト入力のデモ ===")

    # --- fill(): クリア → 入力を一括で行う（最も一般的） ---
    # locator() でCSSセレクタ指定。id属性なら #id
    page.locator("#username").fill("tanaka_taro")
    print("ユーザー名を入力: tanaka_taro")

    # メールアドレス入力
    page.locator("#email").fill("taro@example.com")
    print("メールアドレスを入力: taro@example.com")

    # パスワード入力（type="password" でも操作は同じ）
    page.locator("#password").fill("SecurePass123!")
    print("パスワードを入力: ********")

    # --- clear(): フィールドをクリアする ---
    # 入力済みのフィールドを空にしたい場合
    page.locator("#username").clear()
    print("ユーザー名をクリア")

    # 再度入力（業務ではリトライ時などに使う）
    page.locator("#username").fill("suzuki_hanako")
    print("ユーザー名を再入力: suzuki_hanako")

    # --- テキストエリアへの入力 ---
    # 改行を含むテキストも fill() で入力できる
    page.locator("#bio").fill("Python歴3年。\nPlaywrightで業務自動化に挑戦中。\nよろしくお願いします。")
    print("自己紹介を入力（複数行）")


def demo_select_option(page: Page) -> None:
    """
    セレクトボックス（ドロップダウン）の操作
    ========================================
    select_option() で選択する。指定方法は3パターン:
    1. value属性で指定: select_option(value="engineering")
    2. 表示テキストで指定: select_option(label="技術部")
    3. インデックスで指定: select_option(index=2)

    複数選択（multiple属性）の場合はリストで渡す。

    JS/TS対比:
      Node: await page.selectOption('#department', 'engineering')
      Python: page.locator('#department').select_option('engineering')
    """
    print("\n=== セレクトボックスのデモ ===")

    # --- 単一選択: value属性で指定（最も確実） ---
    page.locator("#department").select_option(value="engineering")
    print("部署を選択（value指定）: engineering → 技術部")

    # --- 単一選択: ラベル（表示テキスト）で指定 ---
    # value属性が分からないときに便利
    page.locator("#department").select_option(label="マーケティング部")
    print("部署を選択（label指定）: マーケティング部")

    # --- 単一選択: インデックスで指定 ---
    # 0始まりのインデックス（0 = "-- 選択してください --"）
    page.locator("#department").select_option(index=1)
    print("部署を選択（index指定）: index=1 → 営業部")

    # 最終的な選択を技術部にする
    page.locator("#department").select_option(value="engineering")

    # --- 複数選択: リストで渡す ---
    # multiple属性のある<select>に対して使う
    page.locator("#skills").select_option(value=["python", "typescript", "docker"])
    print("スキルを複数選択: Python, TypeScript, Docker")


def demo_radio_and_checkbox(page: Page) -> None:
    """
    ラジオボタン・チェックボックスの操作
    ====================================
    check(): チェックを付ける（既にチェック済みなら何もしない）
    uncheck(): チェックを外す（チェックボックスのみ。ラジオはuncheck不可）
    is_checked(): チェック状態を取得（bool）

    ラジオボタンは value属性で特定する。
    チェックボックスも value属性 または id で特定する。

    JS/TS対比:
      Node: await page.check('input[value="senior"]')
      Python: page.locator('input[value="senior"]').check()
    """
    print("\n=== ラジオボタン・チェックボックスのデモ ===")

    # --- ラジオボタン ---
    # name + value で特定するのが確実
    page.locator('input[name="experience"][value="senior"]').check()
    print("経験年数を選択: 5〜10年")

    # 選択状態を確認
    is_senior = page.locator('input[name="experience"][value="senior"]').is_checked()
    print(f"  チェック状態確認: {is_senior}")  # True

    # 別の選択肢に変更（ラジオなので自動的に前の選択は外れる）
    page.locator('input[name="experience"][value="mid"]').check()
    print("経験年数を変更: 3〜5年")

    # --- チェックボックス ---
    # 複数チェックが可能
    page.locator('input[name="workstyle"][value="remote"]').check()
    page.locator('input[name="workstyle"][value="flex"]').check()
    print("働き方を選択: リモートワーク, フレックスタイム")

    # チェックを外す（uncheck）
    page.locator('input[name="workstyle"][value="flex"]').uncheck()
    print("フレックスタイムのチェックを外す")

    # チェック状態の確認
    is_remote = page.locator('input[name="workstyle"][value="remote"]').is_checked()
    is_flex = page.locator('input[name="workstyle"][value="flex"]').is_checked()
    print(f"  リモートワーク: {is_remote}, フレックス: {is_flex}")

    # 副業OKも追加
    page.locator('input[name="workstyle"][value="side-job"]').check()
    print("副業OKもチェック")

    # 利用規約同意チェックボックス
    page.locator("#agree").check()
    print("利用規約に同意: チェック済み")


def demo_file_upload(page: Page) -> None:
    """
    ファイルアップロードの操作
    ==========================
    set_input_files(): <input type="file"> にファイルを設定する。
    ファイルダイアログを使わずに直接設定できる。

    - 単一ファイル: set_input_files("path/to/file")
    - 複数ファイル: set_input_files(["file1", "file2"])
    - ファイル解除: set_input_files([])

    JS/TS対比:
      Node: await page.setInputFiles('#resume', 'file.txt')
      Python: page.locator('#resume').set_input_files('file.txt')
    """
    print("\n=== ファイルアップロードのデモ ===")

    # テスト用の一時ファイルを作成
    temp_file = Path(tempfile.gettempdir()) / "test_resume.txt"
    temp_file.write_text("これはテスト用の履歴書ファイルです。\n名前: 鈴木花子\n", encoding="utf-8")

    # ファイルを設定（ファイルダイアログを開かずに直接指定）
    page.locator("#resume").set_input_files(str(temp_file))
    print(f"ファイルをアップロード: {temp_file.name}")

    # ファイルを解除したい場合（空リストを渡す）
    # page.locator("#resume").set_input_files([])
    # print("ファイルを解除")

    # テスト用ファイルを掃除
    # temp_file.unlink()  # デモなので残しておく


def demo_keyboard_operations(page: Page) -> None:
    """
    キーボード操作
    ==============
    press(): 特定のキーを押す（Enter, Tab, Escape, etc.）
    keyboard.type(): テキストを1文字ずつ入力（タイプライター風）
    keyboard.press(): グローバルなキー入力

    press()はlocator経由で要素にフォーカスした状態でキーを押す。
    keyboard.type()/press()はページ全体に対するキー操作。

    業務自動化では:
    - Enterキーで検索実行やフォーム送信
    - Tabキーで次のフィールドに移動
    - Ctrl+Aで全選択してから入力（既存値の上書き）

    JS/TS対比:
      Node: await page.press('#username', 'Enter')
      Python: page.locator('#username').press('Enter')
    """
    print("\n=== キーボード操作のデモ ===")

    # --- locator().press(): 特定の要素でキーを押す ---
    # ユーザー名フィールドにフォーカスしてTabで次へ移動
    page.locator("#username").press("Tab")
    print("Tab キーで次のフィールドに移動")

    # --- keyboard.type(): 1文字ずつ入力 ---
    # fill()と違い、keydown/keypress/keyupイベントが1文字ずつ発火する
    # オートコンプリートや入力補助が反応する場合に有効
    # ここでは既にemailフィールドに値があるのでクリアしてから
    page.locator("#email").clear()
    page.locator("#email").focus()
    page.keyboard.type("hanako@example.com", delay=50)  # 50msの遅延で入力
    print("keyboard.type()で1文字ずつメール入力: hanako@example.com")

    # --- keyboard.press(): グローバルキーの例 ---
    # Ctrl+A（全選択）のようなショートカットキー
    page.locator("#username").focus()
    page.keyboard.press("Control+a")  # 全選択
    page.keyboard.press("Backspace")   # 削除
    print("Ctrl+A → Backspace でユーザー名をクリア")

    # 再入力
    page.locator("#username").fill("yamada_ichiro")
    print("ユーザー名を再入力: yamada_ichiro")


def demo_mouse_operations(page: Page) -> None:
    """
    マウス操作
    ==========
    mouse.click(x, y): 指定座標をクリック
    mouse.dblclick(x, y): ダブルクリック
    mouse.move(x, y): マウスを移動（ホバー操作）

    通常はlocator().click()を使うが、
    座標指定が必要な場合（Canvas操作、地図操作など）にmouseを使う。

    JS/TS対比:
      Node: await page.mouse.click(100, 200)
      Python: page.mouse.click(100, 200)
    """
    print("\n=== マウス操作のデモ ===")

    # --- locator().click(): 要素を直接クリック（通常はこちらを使う） ---
    page.locator("#submit-btn").scroll_into_view_if_needed()
    print("送信ボタンまでスクロール")

    # --- mouse.move(): マウスカーソルを移動 ---
    # ホバーで表示が変わる要素のテストなどに使用
    box = page.locator("#submit-btn").bounding_box()
    if box:
        # ボタンの中央にマウスを移動
        center_x = box["x"] + box["width"] / 2
        center_y = box["y"] + box["height"] / 2
        page.mouse.move(center_x, center_y)
        print(f"マウスを送信ボタンの中央に移動: ({center_x:.0f}, {center_y:.0f})")

    # --- mouse.click(): 座標でクリック ---
    # Canvas操作や地図操作のように、要素セレクタが使えない場合に必要
    # ここではデモのため、ボタン座標を使ってクリック
    if box:
        # ※ 実際にクリックするとフォーム送信されるので、ここではコメントアウト
        # page.mouse.click(center_x, center_y)
        print("（mouse.click()はフォーム送信を避けるためスキップ）")


def demo_dialog_handling(page: Page) -> None:
    """
    ダイアログ（alert / confirm / prompt）の処理
    =============================================
    page.on("dialog", handler): ダイアログのイベントハンドラを登録
    dialog.accept(): OKをクリック（promptの場合はテキストを渡せる）
    dialog.dismiss(): キャンセルをクリック

    重要: ハンドラを登録しないとダイアログが出るとPlaywrightがハングする。
    業務自動化では「確認ダイアログ→OK」のパターンが非常に多い。

    JS/TS対比:
      Node: page.on('dialog', dialog => dialog.accept())
      Python: page.on('dialog', lambda dialog: dialog.accept())
    """
    print("\n=== ダイアログ処理のデモ ===")

    # --- alert の処理 ---
    # alertはaccept()で閉じる（OKボタンしかない）
    def handle_alert(dialog: Dialog) -> None:
        """alertダイアログを処理するハンドラ"""
        print(f"  ダイアログ検出: type={dialog.type}, message='{dialog.message}'")
        dialog.accept()
        print("  → accept() で閉じた")

    # ハンドラを登録してからボタンをクリック
    page.on("dialog", handle_alert)
    page.locator("#alert-btn").click()
    print("アラートボタンをクリック → ダイアログを処理")

    # ハンドラを解除（次のデモ用）
    page.remove_listener("dialog", handle_alert)

    # --- confirm の処理 ---
    def handle_confirm(dialog: Dialog) -> None:
        """confirmダイアログでOKを押すハンドラ"""
        print(f"  ダイアログ検出: type={dialog.type}, message='{dialog.message}'")
        dialog.accept()  # OKを押す（dismiss()でキャンセル）
        print("  → accept() でOKを押した")

    page.on("dialog", handle_confirm)
    page.locator("#confirm-btn").click()
    print("確認ダイアログボタンをクリック → OKを押す")
    page.remove_listener("dialog", handle_confirm)

    # --- prompt の処理 ---
    def handle_prompt(dialog: Dialog) -> None:
        """promptダイアログにテキストを入力して閉じるハンドラ"""
        print(f"  ダイアログ検出: type={dialog.type}, message='{dialog.message}'")
        # accept()に文字列を渡すとpromptに入力される
        dialog.accept("Playwright太郎")
        print("  → accept('Playwright太郎') で入力してOK")

    page.on("dialog", handle_prompt)
    page.locator("#prompt-btn").click()
    print("入力ダイアログボタンをクリック → テキストを入力してOK")
    page.remove_listener("dialog", handle_prompt)


def demo_multiple_tabs(page: Page) -> None:
    """
    複数タブの操作
    ==============
    context.new_page(): 新しいタブを開く
    page.bring_to_front(): タブを前面に持ってくる

    target="_blank" のリンクをクリックした場合:
    context.expect_page() で新しいタブを捕捉する。

    業務自動化では:
    - メインページからリンク先を新しいタブで開いてデータ取得
    - 複数のシステムを並行して操作
    などの場面で必要。

    JS/TS対比:
      Node: const newPage = await context.newPage()
      Python: new_page = context.new_page()
    """
    print("\n=== 複数タブ操作のデモ ===")

    context = page.context

    # --- 新しいタブを直接開く ---
    new_page = context.new_page()
    new_page.goto("data:text/html,<h1>新しいタブのページ</h1><p>これは2番目のタブです。</p>")
    print(f"新しいタブを開いた: タブ数={len(context.pages)}")

    # 新しいタブでの操作
    title_text = new_page.locator("h1").text_content()
    print(f"  新しいタブのタイトル: {title_text}")

    # 元のタブに戻る
    page.bring_to_front()
    print("元のタブに戻った")

    # 新しいタブを閉じる
    new_page.close()
    print(f"新しいタブを閉じた: タブ数={len(context.pages)}")

    # --- target="_blank" のリンククリックで開くタブを捕捉 ---
    # expect_page() を使うと、新しいタブが開かれるのを待てる
    # ※ file:// から https:// へのナビゲーションは制限がある場合があるので
    #   ここではコンセプトだけ示す
    print("\n  【参考】target='_blank' のリンクでの新しいタブ捕捉:")
    print("  with context.expect_page() as new_page_info:")
    print("      page.locator('#new-tab-link').click()")
    print("  new_page = new_page_info.value")
    print("  new_page.wait_for_load_state()")
    print("  # → 新しいタブのページオブジェクトを取得できる")


def demo_iframe_handling(page: Page) -> None:
    """
    iframeの操作
    =============
    frame_locator(): iframe内の要素にアクセスするためのロケータを取得
    iframe内の要素は通常のlocator()では取得できないので注意。

    frame_locator()のチェーン:
    page.frame_locator('#iframe-id').locator('#element-in-iframe')

    業務自動化では:
    - 古い業務システムでiframeが多用されている
    - 埋め込みフォーム（決済フォームなど）がiframe内にある
    などの場面で必須。

    JS/TS対比:
      Node: page.frameLocator('#iframe').locator('#input')
      Python: page.frame_locator('#iframe').locator('#input')
      ※ camelCase vs snake_case の違いだけ
    """
    print("\n=== iframe操作のデモ ===")

    # iframe内の入力フィールドにアクセス
    # page.frame_locator() でiframeを特定し、その中の要素をlocator()で指定
    iframe = page.frame_locator("#practice-iframe")
    iframe.locator("#iframe-input").fill("iframeの中に入力しました")
    print("iframe内のテキストフィールドに入力")

    # iframe内のボタンをクリック
    iframe.locator("#iframe-btn").click()
    print("iframe内の送信ボタンをクリック")

    # iframe内の結果を取得
    result_text = iframe.locator("#iframe-result").text_content()
    print(f"iframe内の結果: {result_text}")


def demo_screenshot(page: Page, step_name: str) -> str:
    """
    スクリーンショットの撮影
    ========================
    page.screenshot(): ページ全体またはビューポートのスクリーンショットを撮る

    オプション:
    - path: 保存先のファイルパス
    - full_page: True にするとページ全体を撮影（スクロール分も含む）
    - type: "png" または "jpeg"

    業務自動化では:
    - 操作前後の証跡としてスクリーンショットを残す
    - エラー発生時のデバッグ用にスクリーンショットを保存
    - テスト結果のビジュアル確認

    JS/TS対比:
      Node: await page.screenshot({ path: 'screenshot.png', fullPage: true })
      Python: page.screenshot(path='screenshot.png', full_page=True)
    """
    screenshot_path = str(SCREENSHOT_DIR / f"{step_name}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"スクリーンショット保存: screenshots/{step_name}.png")
    return screenshot_path


def demo_form_submit_and_verify(page: Page) -> None:
    """
    フォーム送信と結果検証
    ======================
    実際の業務自動化フロー:
    1. フォームを入力
    2. 送信ボタンをクリック
    3. 結果を確認（テキスト取得、要素の存在チェック等）

    検証でよく使うメソッド:
    - text_content(): テキストを取得
    - inner_text(): 表示されているテキストを取得
    - is_visible(): 要素が表示されているか
    - wait_for_selector(): 要素が出現するまで待つ
    """
    print("\n=== フォーム送信と結果検証のデモ ===")

    # 送信ボタンをクリック
    page.locator("#submit-btn").click()
    print("送信ボタンをクリック")

    # 結果表示エリアが表示されるまで待つ
    page.locator("#results").wait_for(state="visible")
    print("結果エリアが表示された")

    # 結果のテキストを取得して検証
    result_text = page.locator("#results-content").text_content()
    print(f"送信結果:\n{result_text}")

    # 特定の値が含まれているか検証
    if result_text and "yamada_ichiro" in result_text:
        print("✔ ユーザー名が正しく送信されていることを確認")
    else:
        print("✘ ユーザー名が結果に含まれていません")


def main() -> None:
    """
    メイン処理: 全デモを順番に実行
    ==============================
    Playwrightの基本構造:
    1. sync_playwright() でPlaywrightインスタンスを取得
    2. browser = p.chromium.launch() でブラウザを起動
    3. page = browser.new_page() で新しいページを開く
    4. 各操作を実行
    5. browser.close() で終了

    headless=False にするとブラウザが表示される（デバッグ時に便利）
    slow_mo=500 にすると操作間に500msの遅延が入る（動作確認用）
    """
    print("=" * 60)
    print("Lv07: Playwrightフォーム自動入力デモ")
    print("=" * 60)

    with sync_playwright() as p:
        # ブラウザを起動（headless=Falseで画面表示、slow_moで操作をゆっくり見る）
        # ※ 本番運用時は headless=True（デフォルト）にする
        browser = p.chromium.launch(
            headless=False,  # ブラウザウィンドウを表示
            slow_mo=300,     # 各操作の間に300msの遅延（操作を目視確認しやすい）
        )

        # ブラウザコンテキスト（≒ シークレットウィンドウ）を作成
        # viewport でウィンドウサイズを指定
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
        )

        # 新しいページ（タブ）を開く
        page = context.new_page()

        # 練習ページを開く
        print(f"\n練習ページを開く: {PRACTICE_URL}")
        page.goto(PRACTICE_URL)
        page.wait_for_load_state("domcontentloaded")

        # --- 操作前のスクリーンショット ---
        demo_screenshot(page, "01_before")

        # --- 各デモを順番に実行 ---
        demo_text_input(page)
        demo_screenshot(page, "02_after_text_input")

        demo_select_option(page)
        demo_screenshot(page, "03_after_select")

        demo_radio_and_checkbox(page)
        demo_screenshot(page, "04_after_radio_checkbox")

        demo_file_upload(page)
        demo_screenshot(page, "05_after_file_upload")

        demo_keyboard_operations(page)
        demo_screenshot(page, "06_after_keyboard")

        demo_mouse_operations(page)
        demo_screenshot(page, "07_after_mouse")

        demo_dialog_handling(page)
        demo_screenshot(page, "08_after_dialogs")

        demo_iframe_handling(page)
        demo_screenshot(page, "09_after_iframe")

        # --- フォーム送信と結果検証 ---
        demo_form_submit_and_verify(page)
        demo_screenshot(page, "10_after_submit")

        # --- 複数タブ操作 ---
        demo_multiple_tabs(page)
        demo_screenshot(page, "11_final")

        print("\n" + "=" * 60)
        print("全デモ完了！")
        print(f"スクリーンショット保存先: {SCREENSHOT_DIR}")
        print("=" * 60)

        # ブラウザを閉じる
        # ※ with文を使っているので明示的にcloseしなくても良いが、
        #   明示的にする方が分かりやすい
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
