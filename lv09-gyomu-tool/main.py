"""
main.py - 業務自動化ツールのエントリポイント

処理の流れ:
  1. config.json から設定を読み込む
  2. ログを設定する（ファイル＋コンソール）
  3. ブラウザを起動する
  4. （任意）ログイン処理を行う
  5. データをスクレイピングする
  6. （任意）クリック操作を行う
  7. データをCSV/JSONに出力する
  8. ブラウザを閉じる

JS/TS との対比:
  - json の読み込み → Node.js なら require('./config.json') や fs.readFileSync
  - logging → Node.js なら winston や pino に相当
  - if __name__ == "__main__" → Node.js にはない概念。Python 独自のエントリポイント判定
"""

import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# --- 同じフォルダにあるモジュールをインポート ---
# JS/TS の import { BrowserManager } from './browser' と同じ感覚
from browser import BrowserManager
from scraper import PageScraper
from actions import perform_login, perform_cart_actions
from export import save_to_csv, save_to_json, generate_summary


def load_config(config_path: str) -> dict:
    """
    設定ファイルを読み込む。
    JS でいう JSON.parse(fs.readFileSync('config.json', 'utf-8'))
    """
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # ファイルが見つからない場合のエラーメッセージ
        print(f"[エラー] 設定ファイルが見つかりません: {config_path}")
        print("config.json を同じフォルダに配置してください。")
        sys.exit(1)
    except json.JSONDecodeError as e:
        # JSON の書式エラー
        print(f"[エラー] 設定ファイルの書式が不正です: {e}")
        sys.exit(1)


def setup_logging(output_dir: str) -> logging.Logger:
    """
    ログの設定。コンソールとファイルの両方に出力する。

    JS/TS との対比:
      - Python の logging モジュール → winston や pino の設定に近い
      - handler（出力先）を追加する設計 → winston の transports と同じ発想
    """
    # --- 出力ディレクトリがなければ作成 ---
    os.makedirs(output_dir, exist_ok=True)

    # --- ロガーを作成 ---
    logger = logging.getLogger("gyomu_tool")
    logger.setLevel(logging.DEBUG)

    # --- フォーマットを定義 ---
    # JS の console.log とは違い、Python は出力形式を細かく制御できる
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --- コンソール出力ハンドラ ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- ファイル出力ハンドラ ---
    log_filename = f"tool_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(output_dir, log_filename)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info(f"ログファイル: {log_path}")
    return logger


def main():
    """
    メイン処理。全体のワークフローを制御する。

    JS/TS との対比:
      - async function main() { ... } に相当
      - Python の Playwright は sync API も用意されているので await 不要
    """
    print("=" * 50)
    print("  業務自動化ツール - 開始")
    print("=" * 50)

    # --- 設定の読み込み ---
    # exe 化した場合にも対応するため、実行ファイルの場所を基準にする
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    config_path = base_dir / "config.json"
    config = load_config(str(config_path))

    # --- ログの設定 ---
    output_dir = config["output"]["output_dir"]
    logger = setup_logging(output_dir)
    logger.info("設定ファイルを読み込みました")

    # --- 処理結果を集計する変数 ---
    results = {
        "start_time": datetime.now(),
        "scraped_count": 0,
        "action_count": 0,
        "exported_files": [],
        "errors": [],
    }

    try:
        # --- ブラウザを起動 ---
        # with 文でブラウザのライフサイクルを管理する
        # JS の try/finally で browser.close() するのと同じ
        with BrowserManager(config["browser"], logger) as bm:
            page = bm.page

            # --- ステップ1: ログイン（設定で有効な場合のみ） ---
            if config["login"]["enabled"]:
                logger.info("ログイン処理を開始します...")
                perform_login(page, config["login"], logger)
                logger.info("ログイン完了")
            else:
                logger.info("ログインはスキップします（設定で無効）")

            # --- ステップ2: スクレイピング ---
            logger.info("スクレイピングを開始します...")
            scraper = PageScraper(page, config["scraping"], logger)
            data = scraper.scrape(config["target_url"])
            results["scraped_count"] = len(data)
            logger.info(f"スクレイピング完了: {len(data)} 件のデータを取得")

            # --- ステップ3: アクション（設定で有効な場合のみ） ---
            if config["actions"]["add_to_cart"] and data:
                logger.info("カート追加アクションを開始します...")
                action_count = perform_cart_actions(
                    page, data, config["actions"], logger
                )
                results["action_count"] = action_count
                logger.info(f"アクション完了: {action_count} 件実行")
            else:
                logger.info("アクションはスキップします")

            # --- ステップ4: データ出力 ---
            logger.info("データを出力します...")
            output_config = config["output"]

            if "csv" in output_config["formats"]:
                csv_path = save_to_csv(data, output_config)
                results["exported_files"].append(csv_path)
                logger.info(f"CSV出力: {csv_path}")

            if "json" in output_config["formats"]:
                json_path = save_to_json(data, output_config)
                results["exported_files"].append(json_path)
                logger.info(f"JSON出力: {json_path}")

    except Exception as e:
        # --- エラーをキャッチしてユーザーに分かりやすく表示 ---
        logger.error(f"処理中にエラーが発生しました: {e}", exc_info=True)
        results["errors"].append(str(e))

    finally:
        # --- 処理結果のサマリーを出力 ---
        results["end_time"] = datetime.now()
        summary = generate_summary(results)

        # サマリーをファイルに保存
        summary_path = os.path.join(output_dir, "summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)

        # コンソールにも表示
        print()
        print(summary)


# --- エントリポイント ---
# JS/TS にはないPython独自の仕組み。
# このファイルが直接実行されたときだけ main() を呼ぶ。
# 他のファイルから import されたときは呼ばれない。
if __name__ == "__main__":
    main()
