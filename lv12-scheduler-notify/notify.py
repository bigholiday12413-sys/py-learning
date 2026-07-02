"""
notify.py - 通知モジュール（Slack / ChatWork）

「Webhook」という仕組みを使う。
Webhook = チャットサービス側が発行してくれる「ここにHTTPリクエストを送ると
メッセージが投稿される」専用URL。requests で POST するだけで通知できる。

★ Webhook URL は「知っている人は誰でも投稿できる」秘密情報。
  - コードに直接書かない（config.json 等に外出しする）
  - config.json を Git にコミットしない（.gitignore に入れる）
"""

import requests


def send_notification(message: str, notify_config: dict) -> None:
    """
    設定に応じて通知を送る。

    dry_run=true のときは実際には送らず、送る内容を画面に表示するだけ。
    （学習中や動作確認で誤爆しないための安全弁。実務ツールでも有効な設計）
    """
    if notify_config.get("dry_run", True):
        print("  [通知プレビュー(dry_run)]")
        for line in message.splitlines():
            print(f"  | {line}")
        return

    service = notify_config.get("service", "")

    if service == "slack":
        send_slack(message, notify_config["webhook_url"])
    elif service == "chatwork":
        send_chatwork(
            message,
            notify_config["chatwork_api_token"],
            notify_config["chatwork_room_id"],
        )
    else:
        print(f"  [警告] 未対応の通知サービス: {service!r}")


def send_slack(message: str, webhook_url: str) -> None:
    """
    Slack の Incoming Webhook に通知を送る。

    Webhook URL の取得方法（Slack管理画面で数分で終わる）:
      Slack App 管理 → Incoming Webhooks → 有効化 → チャンネルを選んでURL発行
    """
    # Slack は {"text": "本文"} という JSON を POST するだけ
    response = requests.post(webhook_url, json={"text": message}, timeout=10)
    response.raise_for_status()  # 4xx/5xx なら例外（Lv04で学んだ）
    print("  [通知] Slack に送信しました")


def send_chatwork(message: str, api_token: str, room_id: str) -> None:
    """
    ChatWork の指定ルームに通知を送る。

    APIトークンの取得方法:
      ChatWork 右上メニュー → サービス連携 → API Token
    """
    url = f"https://api.chatwork.com/v2/rooms/{room_id}/messages"
    response = requests.post(
        url,
        headers={"X-ChatWorkToken": api_token},  # トークンはヘッダーで渡す
        data={"body": message},
        timeout=10,
    )
    response.raise_for_status()
    print("  [通知] ChatWork に送信しました")


# ============================================================
# 単体テスト用（python notify.py で dry_run 表示を確認できる）
# ============================================================
if __name__ == "__main__":
    send_notification(
        "テスト通知です\n2行目もこの通り",
        {"dry_run": True},
    )
