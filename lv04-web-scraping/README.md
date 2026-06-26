# Lv04 - Webスクレイピング入門

## テーマ

Python の `requests` + `BeautifulSoup4` を使って Web ページからデータを取得する。
JS/TS の `fetch()` + `document.querySelector()` との違いを意識しながら、
HTTP リクエスト・HTML パース・データ抽出の流れを学ぶ。

練習用サイト [Books to Scrape](https://books.toscrape.com/) を対象にする。
（スクレイピング練習専用に公開されているサイト）

## 動かし方

```bash
# 1. venv（仮想環境）を作成する（初回のみ）
#    JS/TS の node_modules に相当する隔離環境
python -m venv venv

# 2. venv を有効化する
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Windows (cmd)
.\venv\Scripts\activate.bat
# macOS / Linux
source venv/bin/activate

# 3. 依存パッケージをインストール
#    JS/TS の npm install に相当
pip install -r requirements.txt

# 4. 実行
python main.py
```

実行すると `books.csv` が出力される。

## 学べること

| Python | JS/TS 対応概念 |
|--------|---------------|
| `requests.get(url)` | `fetch(url)` |
| `response.status_code` | `response.status` |
| `response.headers` | `response.headers` |
| `response.text` / `.json()` | `response.text()` / `.json()` |
| `BeautifulSoup(html, "lxml")` | `new DOMParser().parseFromString()` |
| `soup.select("css")` | `document.querySelectorAll("css")` |
| `soup.select_one("css")` | `document.querySelector("css")` |
| `soup.find()` / `find_all()` | なし（BS4 独自の検索メソッド） |
| `tag.get_text()` | `element.textContent` |
| `tag["href"]` / `tag.get("href")` | `element.getAttribute("href")` |
| `try / except` | `try / catch` |
| `time.sleep(n)` | `await new Promise(r => setTimeout(r, n*1000))` |
| `csv.writer` | 外部ライブラリ or 手動文字列組み立て |

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
