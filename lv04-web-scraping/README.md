# Lv04 - Webスクレイピング入門

## テーマ

Python の `requests` + `BeautifulSoup4` を使って Web ページからデータを取得する。
「HTTP でページを取得 → HTML を解析 → 欲しいデータを抽出 → CSV に保存」という
スクレイピングの基本の流れを学ぶ。

練習用サイト [Books to Scrape](https://books.toscrape.com/) を対象にする。
（スクレイピング練習専用に公開されているサイト）

## 動かし方

```bash
# 1. venv（仮想環境）を作成する（初回のみ）
#    プロジェクトごとにライブラリを隔離するための仕組み
python -m venv venv

# 2. venv を有効化する
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Windows (cmd)
.\venv\Scripts\activate.bat
# macOS / Linux
source venv/bin/activate

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. 実行
python main.py
```

実行すると `books.csv` が出力される。

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `requests.get(url)` | URL に HTTP リクエストを送りページを取得 |
| `response.status_code` | 200(成功)/404(なし)などの結果コード |
| `response.headers` | サーバーが返す付加情報 |
| `response.text` / `.json()` | レスポンス本文（HTML文字列 / JSON→辞書） |
| `BeautifulSoup(html, "lxml")` | HTML 文字列を構造として解析する |
| `soup.select("css")` | CSS セレクタで一致する要素をすべて取得 |
| `soup.select_one("css")` | CSS セレクタで最初の1要素を取得 |
| `soup.find()` / `find_all()` | タグ名・属性で柔軟に検索 |
| `tag.get_text()` | タグに囲まれたテキストを取得 |
| `tag["href"]` / `tag.get("href")` | タグの属性値を取得 |
| `try / except` | ネットワークエラーへの対処 |
| `time.sleep(n)` | n 秒待機（リクエスト間隔を空ける） |
| `csv.DictWriter` | 取得データを CSV に保存 |

## 読む順番

1. この README を読む
2. `requirements.txt` を確認し、`pip install -r requirements.txt` を実行
3. `main.py` を上から順に読む（セクションごとにコメントで解説あり）
4. `python main.py` で動かして結果を確認
5. 出力された `books.csv` を開いてみる
6. 改造課題に挑戦する

## 改造課題

- [ ] 2ページ目以降も取得して、全ページの書籍一覧を CSV にまとめてみよう
- [ ] 各書籍の詳細ページにアクセスして、商品説明(description)も取得してみよう
- [ ] カテゴリ別に絞り込んでスクレイピングしてみよう
- [ ] JSON 形式でも保存できるようにしてみよう（`json.dump()`）
- [ ] `requests.Session()` を使ってセッションを維持するパターンを試してみよう
- [ ] コマンドライン引数でページ数を指定できるようにしてみよう（`argparse`）

## 注意事項（スクレイピングのマナー）

### robots.txt を確認する

サイトの `/robots.txt` には、クロール可否やクロール頻度のルールが書かれている。
スクレイピング前に必ず確認すること。

```
例: https://books.toscrape.com/robots.txt
```

### リクエスト間隔を空ける

短時間に大量のリクエストを送ると、サーバーに負荷をかけてしまう。
`time.sleep()` で最低 1 秒以上の間隔を空けるのがマナー。

### User-Agent を設定する

リクエスト元を明示するために `User-Agent` ヘッダーを設定する。
ボットであることを隠さず、連絡先を含めるのが丁寧。

### 利用規約を確認する

サイトの利用規約でスクレイピングが禁止されている場合は従うこと。
今回使う `books.toscrape.com` はスクレイピング練習用に公開されているので安心。

### 取得したデータの扱い

- 個人情報を含むデータの収集・保存には十分注意する
- 著作権のあるコンテンツの無断転載は禁止
- 商用利用する場合はサイト運営者に確認する
