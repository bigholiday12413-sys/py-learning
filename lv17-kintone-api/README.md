# Lv17 - Kintone REST API 連携

## テーマ

Kintone の REST API を Python (`requests`) で叩いて、アプリのレコードを取得する。
Lv04 で学んだ「HTML を解析して無理やりデータを取る」スクレイピングと違い、
API は **最初から機械が読むために用意された窓口** なので、構造化された JSON がそのまま返ってくる。

最終目標は「日報アプリ（アプリ ID: 17）から約 200 件/日 のレコードを取得し、
LLM 分析に使えるように JSON / CSV で保存する」こと。
PAD の「Web サービスを呼び出します」アクションでやっていたことを Python に置き換えるイメージ。

## 動かし方

```bash
# 1. venv（仮想環境）を作成する（初回のみ）
python -m venv venv

# 2. venv を有効化する
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. 設定ファイルを作る（初回のみ）
#    config.example.json をコピーして config.json を作成し、中身を自分の環境に書き換える
# Windows (PowerShell)
Copy-Item config.example.json config.json
# macOS / Linux
cp config.example.json config.json

# 5. 実行
python main.py
```

**config.json は絶対に git にコミットしないこと**（API トークンが入るため）。
リポジトリ直下の `.gitignore` に `config.json` が入っているか確認しておく。

### API トークンの発行手順（Kintone 側の設定）

1. 対象アプリを開く → 右上の歯車アイコン（アプリの設定）をクリック
2. 「設定」タブ → 「カスタマイズ/サービス連携」の中の **「API トークン」** をクリック
3. 「生成する」ボタンを押すとトークンが 1 行追加される
4. アクセス権のチェックボックスで **「レコード閲覧」** にチェックを入れる
   （今回は取得だけなので閲覧権限だけで OK。書き込みするなら追加・編集も）
5. 「保存」を押し、さらに画面右上の **「アプリを更新」** を押す
   （← これを忘れるとトークンが有効にならない。ハマりポイント）
6. 表示されたトークン文字列を `config.json` の `api_token` に貼り付ける

## 学べること

| Python / Kintone API | PAD / JS 対応概念 |
|---------------------|------------------|
| `requests.get(url, headers=..., params=...)` | PAD「Web サービスを呼び出します」/ JS `fetch()` |
| `X-Cybozu-API-Token` ヘッダー | PAD のカスタムヘッダー欄に書いていたやつ |
| `params={"app": 17, "query": "..."}` | URL の `?app=17&query=...`（エンコードは requests が自動でやる） |
| Kintone クエリ構文（`order by` / `limit` / `offset`） | SQL の WHERE + ORDER BY に近い独自構文 |
| offset ページネーション | PAD の Loop + カウンタ変数 |
| seek 法（`$id > last_id`） | offset 10,000 制限を回避する定石パターン |
| `resp.raise_for_status()` | ステータスコード確認の定型 |
| `json.dump(..., ensure_ascii=False)` | `JSON.stringify(obj, null, 2)` |
| `encoding="utf-8-sig"` | Excel で文字化けしない CSV（BOM 付き UTF-8） |

## Lv04（スクレイピング）との違い

| 観点 | Lv04 スクレイピング | Lv17 API |
|------|--------------------|----------|
| データの形 | HTML（人間が見るための画面）を解析 | JSON（機械が読むためのデータ）がそのまま返る |
| 壊れやすさ | 画面デザインが変わると即死 | API の仕様が変わらない限り安定 |
| パース処理 | BeautifulSoup で CSS セレクタ地獄 | `resp.json()` の 1 行で dict になる |
| 認証 | ログインフォームを Playwright で突破など | ヘッダーにトークンを 1 行足すだけ |
| 許可 | robots.txt・利用規約を気にする | 公式に許可された窓口。堂々と使える |
| 速度・負荷 | 1 ページずつ・sleep 必須 | 1 リクエストで最大 500 件。サーバーに優しい |

**結論: API が用意されているなら、スクレイピングではなく必ず API を使う。**
スクレイピングは「API がない相手への最終手段」と覚えておく。

## 読む順番

1. この README を読む（特に API トークンの発行手順）
2. `config.example.json` を見て、`config.json` を作る
3. `main.py` を上から順に読む（STEP ごとにコメントで解説あり）
4. `python main.py` で動かして、`output/` に JSON と CSV ができるのを確認
5. `kintone_client.py` を読む（main.py の処理をクラスにまとめた再利用版）
6. 改造課題に挑戦する

## 改造課題

- [ ] `query` を変えて「今日の日報だけ」を取得してみよう（例: `作成日時 > TODAY()`）
- [ ] 特定のフィールドだけ取得する `fields` パラメータを使ってみよう（通信量削減）
- [ ] `kintone_client.py` に `add_record()`（レコード追加 = POST）を実装してみよう
- [ ] 取得結果を Lv11 で学ぶ SQLite に保存して、日次差分を取れるようにしてみよう
- [ ] トークンを config.json ではなく環境変数（`os.environ`）から読むようにしてみよう
- [ ] 429（リクエスト過多）が返ってきたら少し待ってリトライする処理を入れてみよう
- [ ] 取得した日報レコードを LLM に投げるためのプロンプト用テキストに整形してみよう
