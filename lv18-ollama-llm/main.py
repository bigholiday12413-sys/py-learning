# -*- coding: utf-8 -*-
"""
Lv18 - ローカルLLM（Ollama）で構造化抽出: 1件抽出デモ

営業日報のテキスト1件を Ollama (qwen3:8b) に投げて、
5項目（商材名・顧客名・競合情報・商談結果・顧客の反応）を JSON で抜き出す。

ポイント:
- Ollama の API はただの REST API。Lv17 の Kintone と同じく requests.post() で叩ける。
  → 専用SDKは不要。「LLM も HTTP の向こうにいるだけ」と分かるのが今回の狙い。
- 出力を JSON スキーマで縛る（format パラメータ）＝構造化出力
- temperature=0 で毎回同じ出力にする（抽出タスクの鉄則）

【補足】公式の pip パッケージを使う書き方もある:
    pip install ollama
    ------------------------------------------------
    import ollama
    res = ollama.chat(
        model="qwen3:8b",
        messages=[{"role": "user", "content": "..."}],
        format=SCHEMA,           # JSONスキーマ指定も可能
        options={"temperature": 0},
        think=False,
    )
    print(res["message"]["content"])
    ------------------------------------------------
    中身は結局 http://localhost:11434 を叩いているだけなので、
    仕組みを理解するために本ファイルでは requests で直接叩く。
"""

import json

import requests

# ============================================================
# 1. 定数（接続先とモデル名）
# ============================================================

# Ollama はインストールすると localhost:11434 で API サーバーが常駐する。
# /api/chat がチャット形式（system / user の役割分け）のエンドポイント。
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"  # 事前に `ollama pull qwen3:8b` しておくこと

# ============================================================
# 2. 出力スキーマ（JSONスキーマで出力の「型」を定義する）
# ============================================================
# Ollama の format パラメータに JSON スキーマを渡すと、
# モデルの出力がこのスキーマに沿った JSON になるよう強制される。
# 「プロンプトでJSONをお願いする」だけより格段に安定する。
#
# 各フィールドに ["string", "null"] を指定しているのは、
# 「本文に書かれていない項目は null を返してよい」と型レベルで許可するため。
EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "商材名": {"type": ["string", "null"]},
        "顧客名": {"type": ["string", "null"]},
        "競合情報": {"type": ["string", "null"]},
        "商談結果": {"type": ["string", "null"]},
        "顧客の反応": {"type": ["string", "null"]},
    },
    "required": ["商材名", "顧客名", "競合情報", "商談結果", "顧客の反応"],
}

# ============================================================
# 3. プロンプト設計
# ============================================================
# system プロンプト: モデルの「役割」と「ルール」を決める（毎回共通）
# user プロンプト  : 実際に処理させるデータ（日報本文）を渡す（毎回変わる）
#
# 日本語プロンプトのコツ:
# - 項目の定義を曖昧にしない（「競合」→「他社の製品名や動き」まで書く）
# - 「本文にない情報は null」と明示する（書かないと LLM が捏造しがち）
# - 指示は箇条書きで短く。長文の丁寧な説明より安定する
SYSTEM_PROMPT = """あなたは営業日報から情報を抽出するアシスタントです。
与えられた日報の本文から、以下の5項目を抽出して JSON で出力してください。

- 商材名: 提案・販売している自社の商品やサービスの名前
- 顧客名: 訪問・商談した相手の会社名（担当者の個人名ではなく会社名）
- 競合情報: 本文に登場する他社製品名・他社の動きなどの競合に関する情報
- 商談結果: 商談がどうなったか（例: 受注、失注、継続検討、次回デモ実施 など）
- 顧客の反応: 顧客の反応の極性。「ポジティブ」「ネガティブ」「中立」のいずれか

ルール:
- 本文に書かれていない項目は必ず null にすること。推測で埋めてはいけない
- 本文の表記をできるだけそのまま使うこと（勝手に言い換えない）
- JSON のみを出力すること"""


def extract_from_report(report_text: str) -> dict:
    """日報本文1件を Ollama に投げて、5項目の dict を返す。

    失敗時（接続エラー・JSON壊れ等）は例外を投げるので、
    呼び出し側で try/except すること（batch_extract.py 参照）。
    """
    # ----- リクエストボディの組み立て -----
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"次の日報から抽出してください。\n\n{report_text}"},
        ],
        # format に JSON スキーマを渡すと構造化出力になる。
        # スキーマの代わりに文字列 "json" を渡すと「とにかく JSON」という緩い縛りになる。
        # 項目名まで固定したいので、ここではスキーマを渡す。
        "format": EXTRACT_SCHEMA,
        "options": {
            # temperature=0: 出力のランダム性をなくす。
            # 抽出タスクは「創造性」が不要で、同じ入力→同じ出力であってほしいので必ず 0。
            "temperature": 0,
        },
        # qwen3 は回答前に「思考（thinking）」テキストを出すモデル。
        # 抽出では不要な上にトークンを大量に消費して遅くなるので無効化する。
        # ※プロンプト末尾に「/no_think」と書いて無効化する方法もあるが、
        #   API パラメータで指定するほうが確実。
        "think": False,
        # stream=False: 応答を一括で受け取る（True だと1トークンずつ流れてくる）
        "stream": False,
    }

    # ----- API 呼び出し（Lv17 の Kintone API と同じ形！） -----
    # timeout は長め（120秒）に。初回はモデルのロードで数十秒かかることがある。
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()  # 4xx/5xx なら例外を投げる

    # ----- 応答から本文を取り出す -----
    # 応答の構造: {"message": {"role": "assistant", "content": "{...JSON文字列...}"}, ...}
    content = response.json()["message"]["content"]

    # ----- JSON 文字列 → dict に変換 -----
    # format でスキーマを縛っていても、ごく稀に壊れた JSON が返ることがあるため
    # json.loads() は必ず try/except で包む。
    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        # 呼び出し側でリトライ・エラー記録できるよう、情報を付けて投げ直す
        raise ValueError(f"LLM の出力が JSON として解析できませんでした: {e}\n出力内容: {content!r}")

    return result


# ============================================================
# 4. 動作確認（このファイルを直接実行したときだけ動く）
# ============================================================
if __name__ == "__main__":
    # サンプルの日報1件（実際は sample_reports.csv に10件入っている）
    sample_report = (
        "本日、株式会社山田製作所の田中様を訪問。勤怠管理システム「タイムキーパーPro」を"
        "デモした。現在他社のジョブカンを利用中とのことだが、月額費用に不満がある様子。"
        "反応は良好で、来週見積もりを提出することになった。"
    )

    print("=== 日報本文 ===")
    print(sample_report)
    print()
    print("Ollama に問い合わせ中...（初回はモデルのロードで数十秒かかることがあります）")
    print()

    try:
        result = extract_from_report(sample_report)
    except requests.exceptions.ConnectionError:
        # Ollama が起動していないときはここに来る
        print("エラー: Ollama に接続できません。")
        print("Ollama がインストール済みか、タスクトレイで起動しているか確認してください。")
        print("起動していない場合はターミナルで `ollama serve` を実行してください。")
        raise SystemExit(1)

    print("=== 抽出結果 ===")
    # ensure_ascii=False: 日本語をエスケープせずそのまま表示する（Lv02 でやったやつ）
    print(json.dumps(result, ensure_ascii=False, indent=2))
