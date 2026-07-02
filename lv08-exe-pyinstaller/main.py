"""
Lv08: exe化を意識したPythonスクリプトの書き方

このスクリプトは、PyInstallerでexe化することを前提に書かれている。
ポイント:
  - sys.frozen でexe実行かスクリプト実行かを判定
  - 設定ファイル（config.json）を外部から読み込む
  - ログ出力でデバッグしやすくする
  - エラーハンドリングで非エンジニアにも分かるメッセージを表示

最重要ポイント:
  exe化すると「ファイルパスの基準」が変わる。
  スクリプト実行時と exe 実行時の両方で正しく動くパス解決を
  最初から組み込んでおくのが、exe化で失敗しないコツ。
"""

import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


# =============================================================================
# パス解決（exe化で最も重要な部分）
# =============================================================================

def get_base_path() -> Path:
    """
    スクリプトのベースパスを取得する。

    exe化されている場合:
      sys.frozen が True になり、sys._MEIPASS にバンドルされた
      ファイルの展開先パスが入る（--onefile の場合は一時ディレクトリ）。

    スクリプトとして実行している場合:
      このファイルが置かれているディレクトリを返す。
    """
    if getattr(sys, 'frozen', False):
        # --- exe化されている場合 ---
        # sys._MEIPASS: PyInstallerがバンドルしたファイルを展開したディレクトリ
        # --onefile の場合、起動時に一時ディレクトリに展開される
        return Path(sys._MEIPASS)
    else:
        # --- 通常のスクリプト実行の場合 ---
        return Path(__file__).resolve().parent


def get_exe_dir() -> Path:
    """
    exeファイル自体が置かれているディレクトリを取得する。

    --onefile でビルドした場合、get_base_path() は一時ディレクトリを返すが、
    この関数はexeファイルの実際の場所を返す。

    config.jsonなど「exeと同じフォルダに置くファイル」を読むときはこちらを使う。
    """
    if getattr(sys, 'frozen', False):
        # --- exe化されている場合 ---
        # sys.executable はexeファイル自体のパス
        return Path(sys.executable).parent
    else:
        # --- 通常のスクリプト実行の場合 ---
        return Path(__file__).resolve().parent


# =============================================================================
# ロギング設定
# =============================================================================

def setup_logging(log_dir: Path, debug: bool = False) -> logging.Logger:
    """
    ログ出力を設定する。

    exe化したツールでは print() だけでなく、ファイルにもログを残すと
    問題が起きたときにデバッグしやすい。
    （logging モジュールの基本は Lv06 の scraper.py を参照）
    """
    # ログディレクトリが無ければ作成
    log_dir.mkdir(parents=True, exist_ok=True)

    # ログファイル名に日付を入れる
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

    # ログレベルの設定
    log_level = logging.DEBUG if debug else logging.INFO

    # ロガーの作成
    logger = logging.getLogger("web_scraper")
    logger.setLevel(log_level)

    # 既存のハンドラをクリア（二重登録防止）
    logger.handlers.clear()

    # フォーマッター: 日時、レベル、メッセージを出力
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ファイルハンドラ: ログファイルに出力
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # コンソールハンドラ: 画面にも出力
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# =============================================================================
# 設定ファイルの読み込み
# =============================================================================

def load_config(config_path: Path) -> dict:
    """
    設定ファイル（config.json）を読み込む。

    exe化したアプリでは、設定を外部ファイルにしておくと
    再ビルドせずに挙動を変えられるので便利。

    JSON は「テキストで書ける設定データの形式」で、Python の辞書と
    ほぼ同じ見た目。標準ライブラリ json で読み書きできる。
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"設定ファイルが見つかりません: {config_path}\n"
            f"config.json をexeと同じフォルダに配置してください。"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 必須項目のチェック
    required_keys = ["target_url", "output_dir"]
    for key in required_keys:
        if key not in config:
            raise KeyError(
                f"設定ファイルに必須項目 '{key}' がありません。\n"
                f"config.json を確認してください。"
            )

    return config


# =============================================================================
# メイン処理: Webページの取得と保存
# =============================================================================

def fetch_page(url: str, logger: logging.Logger) -> str:
    """
    指定URLのHTMLを取得する。

    この例ではPlaywrightではなく標準ライブラリのurllibを使用。
    理由: exe化の学習に集中するため、依存を最小限にする。

    Playwrightを使う場合のexe化の注意点は build_guide.md を参照。
    """
    logger.info(f"ページ取得開始: {url}")

    # User-Agentを設定（ブロック回避）
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    request = Request(url, headers=headers)

    try:
        with urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8")
            logger.info(f"ページ取得成功: {len(html)} 文字")
            return html

    except HTTPError as e:
        # HTTPエラー（404, 500など）
        logger.error(f"HTTPエラー: {e.code} {e.reason}")
        raise RuntimeError(
            f"ページの取得に失敗しました（HTTPエラー {e.code}）。\n"
            f"URLが正しいか確認してください: {url}"
        )

    except URLError as e:
        # ネットワークエラー（DNS解決失敗、接続拒否など）
        logger.error(f"ネットワークエラー: {e.reason}")
        raise RuntimeError(
            f"ネットワーク接続に失敗しました。\n"
            f"インターネット接続を確認してください。\n"
            f"詳細: {e.reason}"
        )


def save_result(html: str, output_dir: Path, logger: logging.Logger) -> Path:
    """
    取得したHTMLをファイルに保存する。
    """
    # 出力ディレクトリが無ければ作成
    output_dir.mkdir(parents=True, exist_ok=True)

    # ファイル名に日時を入れて重複を避ける
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"result_{timestamp}.html"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"結果を保存しました: {output_file}")
    return output_file


# =============================================================================
# 実行環境情報の表示
# =============================================================================

def show_environment_info(logger: logging.Logger):
    """
    実行環境の情報を表示する。デバッグ時に役立つ。

    sys.frozen の値で、exe化されているかどうかが分かる。
    """
    logger.info("=" * 50)
    logger.info("実行環境情報")
    logger.info("=" * 50)

    # exe化されているかどうか
    is_frozen = getattr(sys, 'frozen', False)
    logger.info(f"  exe化: {'はい' if is_frozen else 'いいえ（スクリプト実行）'}")

    # Pythonバージョン
    logger.info(f"  Python: {sys.version}")

    # 実行ファイルのパス
    logger.info(f"  実行ファイル: {sys.executable}")

    # ベースパス（バンドルされたファイルの場所）
    logger.info(f"  ベースパス: {get_base_path()}")

    # exeディレクトリ（exeファイルの実際の場所）
    logger.info(f"  exeディレクトリ: {get_exe_dir()}")

    # カレントディレクトリ
    logger.info(f"  カレントディレクトリ: {os.getcwd()}")

    logger.info("=" * 50)


# =============================================================================
# メインエントリーポイント
# =============================================================================

def main():
    """
    メイン処理。

    エラーハンドリングのポイント:
      - 非エンジニア向けのツールでは、エラーメッセージを日本語で分かりやすく
      - トレースバックは非エンジニアには意味不明なので、ログファイルに記録
      - 画面にはユーザーが対処できる情報だけ表示
    """
    # --- exe/スクリプトの実行ディレクトリを取得 ---
    exe_dir = get_exe_dir()

    # --- ロガーの初期化（仮: デバッグモードはあとで設定から読む） ---
    log_dir = exe_dir / "logs"
    logger = setup_logging(log_dir, debug=True)

    try:
        # --- 実行環境情報を表示 ---
        show_environment_info(logger)

        # --- 設定ファイルの読み込み ---
        # config.json は exe と同じフォルダに置く
        # （バンドルに含めず、外部ファイルとして配布する）
        config_path = exe_dir / "config.json"
        logger.info(f"設定ファイルを読み込み中: {config_path}")
        config = load_config(config_path)

        # 設定値の取得
        target_url = config["target_url"]
        output_dir = exe_dir / config["output_dir"]
        debug_mode = config.get("debug", False)

        # デバッグモードに応じてログレベルを再設定
        if not debug_mode:
            logger = setup_logging(log_dir, debug=False)

        logger.info(f"対象URL: {target_url}")
        logger.info(f"出力先: {output_dir}")

        # --- ページ取得 ---
        html = fetch_page(target_url, logger)

        # --- 結果保存 ---
        output_file = save_result(html, output_dir, logger)

        # --- 完了メッセージ ---
        print()
        print("=" * 50)
        print("  処理が完了しました！")
        print(f"  保存先: {output_file}")
        print("=" * 50)
        print()

    except FileNotFoundError as e:
        # 設定ファイルが無い場合
        logger.error(str(e))
        print()
        print(f"【エラー】{e}")
        print()

    except KeyError as e:
        # 設定ファイルに必要な項目が無い場合
        logger.error(str(e))
        print()
        print(f"【エラー】{e}")
        print()

    except RuntimeError as e:
        # ネットワークエラーなど
        logger.error(str(e))
        print()
        print(f"【エラー】{e}")
        print()

    except Exception as e:
        # 想定外のエラー
        logger.exception("予期しないエラーが発生しました")
        print()
        print("【エラー】予期しないエラーが発生しました。")
        print(f"詳細はログファイルを確認してください: {log_dir}")
        print()

    finally:
        # --- exe実行時はウィンドウがすぐ閉じないように待機 ---
        if getattr(sys, 'frozen', False):
            print("Enterキーを押すと終了します...")
            input()


if __name__ == "__main__":
    main()
