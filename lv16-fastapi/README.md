# Lv16 - FastAPI：ツールをWeb API化する【フレームワーク編】

## テーマ

**FastAPI** で「URLを叩くとJSONが返ってくる窓口（Web API）」を自分で作る。

Lv04 では `requests.get()` で API を「呼ぶ側」を経験した。今度は「呼ばれる側」。
スクレイピングや集計の機能をAPIにしておくと、他のシステム・他の人のスクリプト・
Excelマクロなど、あらゆるところから機能を呼び出せるようになる。

| 人間向け | プログラム向け |
|---------|---------------|
| Streamlit (Lv15) = 画面 | FastAPI (Lv16) = 窓口(API) |

## 動かし方

```bash
cd lv16-fastapi
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows / macOSは source venv/bin/activate
pip install -r requirements.txt

# uvicorn = FastAPI アプリを動かすサーバー。--reload でコード変更を即反映
uvicorn main:app --reload
```

起動したらブラウザで開く:

- http://127.0.0.1:8000/ … 動作確認
- **http://127.0.0.1:8000/docs … 自動生成されたAPI仕様書（ここが感動ポイント）**

`/docs` では各エンドポイントを「Try it out」ボタンで**その場で実行**できる。
この仕様書はコードの型ヒントから自動生成されている。仕様書とコードがズレない。

終了はターミナルで `Ctrl + C`。

## 用意されているエンドポイント

| メソッド | URL | 内容 |
|---------|-----|------|
| GET | `/` | 動作確認 |
| GET | `/books?min_rating=4&max_price=50` | 一覧（クエリパラメータで絞り込み） |
| GET | `/books/3` | 1件取得（無ければ404） |
| POST | `/books` | 登録（JSONボディを自動検証） |
| GET | `/stats` | 集計結果を返す |
| GET | `/slow-demo` | async デモ（Lv05の回収） |

curl や Lv04 の requests でも呼べる:

```python
import requests
r = requests.get("http://127.0.0.1:8000/books", params={"min_rating": 4})
print(r.json())   # ← 呼ぶ側(Lv04)と作る側(Lv16)がつながる瞬間
```

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `@app.get("/...")` | URLと関数の対応付け（デコレータ! Lv03の実用例） |
| パスパラメータ `/books/{id}` | URLの一部を引数として受け取る |
| クエリパラメータ | 関数の引数がそのまま `?key=value` になる |
| pydantic `BaseModel` | dataclass(Lv03)の進化形。自動バリデーション付き |
| `Field(ge=0, le=5)` | 「0以上5以下」のような制約を宣言 |
| `HTTPException` | 404などのエラー応答の作法 |
| 422 自動エラー | 不正な入力は自分で if を書かなくても弾かれる |
| `/docs` 自動生成 | 型ヒントが「試せる仕様書」になる |
| `async def` エンドポイント | 待ち時間の多い処理の並行処理（Lv05の回収） |

## FastAPI の何が「王道」なのか

1. **型ヒント駆動**: Lv01 から書いてきた型ヒントが、そのまま入力検証・変換・仕様書になる
2. **自動ドキュメント**: `/docs` により「APIの使い方を聞かれたらURLを渡すだけ」
3. **高速・async対応**: Playwright async 版(Lv05)などと自然に組み合わせられる

## 読む順番

1. この README
2. `main.py` を上から読む（モデル定義 → エンドポイント）
3. `uvicorn main:app --reload` で起動し、**/docs で全エンドポイントを実際に叩く**
4. POST /books にわざと `rating=9` を送って 422 エラーを確認する（自動検証の体感）
5. 改造課題へ

## 改造課題

- [ ] `DELETE /books/{book_id}` を追加しよう（404処理も忘れずに）
- [ ] `GET /books` に `category` での絞り込みを追加しよう
- [ ] メモリ内リストを Lv11 の SQLite に差し替えよう（再起動してもデータが残る）
- [ ] `POST /scrape` を作り、Lv09 のスクレイパーを起動して結果を保存するAPIにしよう
- [ ] Lv13 の知識で `fastapi.testclient.TestClient` を使ったAPIテストを書こう
- [ ] Lv15 の Streamlit からこの API を requests で呼んで表示しよう（画面と窓口の分離構成）

## 補足: Flask / Django との関係

| フレームワーク | 特徴 | 向き |
|---------------|------|------|
| **FastAPI** | 型ヒント駆動・自動ドキュメント・async | API開発の現代の第一候補 |
| Flask | 最小構成で歴史が長い | 小さなWebアプリ・学習資料が豊富 |
| Django | 管理画面・認証・ORMまで全部入り | 大規模なWebサービスを丸ごと作る |

このコースの文脈（ツールのAPI化）なら FastAPI が最短。
「Webサービスそのもの」を作りたくなったら Django を調べるとよい。
