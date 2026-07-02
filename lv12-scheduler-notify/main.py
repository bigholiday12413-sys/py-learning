"""
Lv12 - 定期実行と通知
======================
「手で実行するツール」を「毎朝勝手に動いて結果を知らせてくれるツール」に進化させる。

2つの部品を学ぶ:
  1. スケジューラ … 決まった時刻・間隔で処理を実行する仕組み
  2. 通知         … 実行結果を Slack / ChatWork / メール等に送る仕組み

実行方法:
    pip install -r requirements.txt
    python main.py          # デモ: 5秒間隔のジョブを3回実行して終了する
"""

import json
import time
from datetime import datetime
from pathlib import Path

# schedule: 「毎日9時」「10分ごと」のような定期実行を簡単に書けるライブラリ
# pip install schedule
import schedule

from notify import send_notification

CONFIG_PATH = Path(__file__).parent / "config.json"


# ============================================================
# 1. 定期実行したい「仕事」を関数にする
# ============================================================
# スケジューラに渡すのはただの関数。
# Lv09 のツールなら main() をそのまま渡せる。

def job(config: dict) -> None:
    """
    定期実行される仕事の本体。
    ここでは「データ取得のフリをして、結果を通知する」デモ。
    実際は Lv09 のスクレイピング + Lv11 の差分検知に差し替える。
    """
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] ジョブ実行中...")

    # --- 仕事のシミュレーション（実際はスクレイピング等） ---
    result = {"scraped": 20, "changed": 2}

    # --- 結果を通知 ---
    message = (
        f"📗 書籍チェック完了 ({now})\n"
        f"取得: {result['scraped']} 件 / 変更検知: {result['changed']} 件"
    )
    send_notification(message, config["notify"])


# ============================================================
# 2. スケジュールの組み方
# ============================================================
# schedule ライブラリの書き方はほぼ英語の文章:
#
#   schedule.every(10).minutes.do(job)        # 10分ごと
#   schedule.every().hour.do(job)             # 1時間ごと
#   schedule.every().day.at("09:00").do(job)  # 毎日9時
#   schedule.every().monday.at("08:30").do(job)  # 毎週月曜8時半
#
# do() に渡すのは「関数そのもの」。job() と書くと今すぐ実行した戻り値を
# 渡してしまうので、() を付けずに job を渡すのがポイント。
# 引数が必要なら do(job, config) のように後ろに並べる。

def run_scheduler_demo(config: dict) -> None:
    """
    デモ用: 5秒ごとのジョブを登録し、3回実行したら終了する。

    実運用では while True: で無限に回し続ける（README参照）。
    学習用に必ず終わるようにしてある。
    """
    print("スケジューラ起動: 5秒ごとにジョブを実行します（3回で自動終了）")
    print("-" * 60)

    # 実行回数を数えるためのカウンタ。
    # 内側の関数から書き換えるので、数値ではなく辞書に入れておく
    # （Lv06 で学んだ nonlocal でも書けるが、辞書方式も実務でよく見る）
    state = {"count": 0}

    def counted_job():
        """job() を実行して回数を数えるラッパー関数"""
        job(config)
        state["count"] += 1
        print(f"  （{state['count']}/3 回目 完了）\n")

    schedule.every(5).seconds.do(counted_job)

    while state["count"] < 3:
        # run_pending(): 「実行時刻が来ているジョブ」をまとめて実行する。
        # この行を定期的に呼び続けるのがスケジューラの仕組み。
        # （= プログラム自体は起動しっぱなしにしておく必要がある）
        schedule.run_pending()
        time.sleep(0.5)  # CPUを無駄に回さないよう小休止

    schedule.clear()  # 登録済みジョブを全解除
    print("-" * 60)
    print("デモ終了。実運用の常駐方法は README を参照。")


# ============================================================
# メイン処理
# ============================================================

def main() -> None:
    print("=" * 60)
    print("Lv12 - 定期実行と通知")
    print("=" * 60)

    # 通知先の設定を読み込む（Lv08 で学んだ設定外出しパターン）
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    if config["notify"]["dry_run"]:
        print("※ dry_run=true のため、通知は送信されず画面表示のみ")
        print("  実際に送るには config.json に webhook URL を設定し dry_run を false に")
    print()

    run_scheduler_demo(config)


if __name__ == "__main__":
    main()
