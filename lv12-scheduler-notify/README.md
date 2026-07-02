# Lv12 - 定期実行と通知【発展編】

## テーマ

「手で実行するツール」を **「毎朝勝手に動いて、結果をチャットで知らせてくれるツール」** に進化させる。

- **スケジューラ**: 決まった時刻・間隔で処理を自動実行する
- **通知**: 実行結果を Slack / ChatWork に送る（Webhook の仕組み）

Lv9〜11 で作れるようになった処理を、この2つと組み合わせると
「毎朝9時にサイトをチェックし、変更があったらSlackに知らせる」ような
完全自動の監視ツールが完成する。

## 動かし方

```bash
cd lv12-scheduler-notify
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows / macOSは source venv/bin/activate
pip install -r requirements.txt

python main.py       # 5秒間隔のジョブが3回動いて自動終了するデモ
python notify.py     # 通知モジュール単体の dry_run 確認
```

デフォルトは `dry_run: true` なので、通知は**送信されず画面表示のみ**。
実際に送るには `config.json` に自分の Webhook URL を設定し、`dry_run` を `false` にする。

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `schedule.every(...).do(job)` | 「毎日9時」「10分ごと」を1行で書く |
| `schedule.run_pending()` ループ | スケジューラが動く仕組み（常駐プロセス） |
| `do(job, 引数)` | 関数は `()` を付けずに渡す（付けると即実行になる） |
| Webhook | チャットに投稿できる専用URL。POSTするだけで通知 |
| `requests.post(json=... / data=...)` | Lv04 の GET に続く POST の実践 |
| `dry_run` 設計 | 誤爆を防ぐ安全弁。実務ツールの定石 |
| 秘密情報の扱い | トークン類はコードに書かず設定ファイルへ（+ .gitignore） |

## schedule の書き方チートシート

```python
import schedule

schedule.every(10).minutes.do(job)           # 10分ごと
schedule.every().hour.do(job)                # 1時間ごと
schedule.every().day.at("09:00").do(job)     # 毎日 9:00
schedule.every().monday.at("08:30").do(job)  # 毎週月曜 8:30

while True:                                  # 実運用の常駐ループ
    schedule.run_pending()
    time.sleep(30)
```

## 実運用の選択肢: schedule vs OSのスケジューラ

| | schedule ライブラリ | Windowsタスクスケジューラ / cron |
|--|--------------------|--------------------------------|
| 仕組み | Python が起動しっぱなし | OS が時刻になったら exe/スクリプトを起動 |
| PC再起動後 | 手で起動し直す必要あり | 自動で復帰する |
| 向き | 開発中・分単位の細かい制御 | **本番運用はこちらが定石** |

### Windowsタスクスケジューラへの登録手順（Lv08のexeを毎朝動かす例）

1. スタートメニューで「タスクスケジューラ」を検索して起動
2. 「基本タスクの作成」→ 名前を付ける（例: 書籍チェック）
3. トリガー: 毎日 → 時刻 9:00
4. 操作: プログラムの開始 → `dist\gyomu-tool.exe` を指定
5. 「開始（オプション）」に exe のあるフォルダを入れる（config.json を見つけられるように）

これで **PCが起動していれば毎朝自動実行** される。通知（notify.py）を組み込んでおけば、
結果はチャットに届くので画面を見に行く必要もない。

## Webhook URL の取得方法

- **Slack**: [api.slack.com/apps](https://api.slack.com/apps) → Create New App → Incoming Webhooks を有効化 → チャンネルを選んで URL 発行
- **ChatWork**: 右上メニュー → サービス連携 → API Token を発行（+ 通知先ルームのID）

## ⚠ 秘密情報の扱い（実務で必ず守ること）

Webhook URL や API トークンは「知っている人は誰でも投稿できる」秘密情報。

- コードに直接書かない → `config.json` に外出し（Lv08 のパターン）
- **Git にコミットしない** → `.gitignore` に `config.json` を追加し、
  代わりにダミー値の `config.example.json` をコミットするのが定石
- 万一漏らしたら、発行元の管理画面で無効化して再発行する

## 読む順番

1. この README
2. `notify.py` — Webhook 通知の仕組み（dry_run の安全弁に注目）
3. `main.py` — スケジューラの組み方
4. 実行してデモを確認
5. 改造課題へ

## 改造課題

- [ ] 自分の Slack / ChatWork の Webhook を発行して、実際に通知を送ってみよう
- [ ] Lv11 の差分検知と組み合わせ、「変更があったときだけ」通知するようにしよう
- [ ] ジョブが例外で落ちても常駐ループが止まらないよう try/except を入れよう（実運用の必須改造）
- [ ] 通知にメール（`smtplib`）の選択肢を追加してみよう
- [ ] Lv08 の手順で exe 化し、Windowsタスクスケジューラに登録して「完全自動化」を完成させよう
