"""
Lv16 - FastAPI：ツールをWeb API化する
======================================
FastAPI は Web API を作るためのモダンな定番フレームワーク。

Web API とは:
  「URLにリクエストを送ると、JSONでデータが返ってくる窓口」。
  Lv04 で requests.get() を使って「呼ぶ側」を経験した。
  今度は「呼ばれる側」を自分で作る。

なぜツールをAPI化するのか:
  - 他のシステムやExcelマクロ、別のPythonツールから機能を呼び出せる
  - スクレイピング処理を1か所（サーバー）に集約し、結果だけ配れる
  - Streamlit(Lv15)が「人間向けの画面」なら、FastAPIは「プログラム向けの窓口」

FastAPI の看板機能:
  - 型ヒント（Lv01）がそのままバリデーションとドキュメントになる
  - http://127.0.0.1:8000/docs に「試せるAPI仕様書」が自動生成される

実行方法:
    pip install -r requirements.txt
    uvicorn main:app --reload
    → ブラウザで http://127.0.0.1:8000/docs を開く
"""

from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# ============================================================
# 1. アプリ本体の作成
# ============================================================
# FastAPI() のインスタンスに「この URL に来たらこの関数」を登録していく。
# uvicorn main:app の「app」はこの変数名を指している。

app = FastAPI(
    title="書籍データAPI",
    description="Lv09 のスクレイピング結果を配信する学習用API（Lv16）",
    version="1.0.0",
)


# ============================================================
# 2. データモデル ─ pydantic の BaseModel
# ============================================================
# Lv03 の @dataclass に似ているが、pydantic は「バリデーション」までやってくれる。
# 例: price に文字列が来たら自動で 422 エラーを返す（自分で if を書かなくてよい）。
# Field(...) で「必須」「範囲」などの制約も宣言できる。

class Book(BaseModel):
    """書籍1冊を表すモデル（レスポンスにもリクエストにも使う）"""
    id: int
    title: str
    category: str
    price: float = Field(ge=0, description="価格（£）。0以上")
    rating: int = Field(ge=0, le=5, description="星評価 0〜5")


class BookCreate(BaseModel):
    """登録リクエスト用モデル（id はサーバー側で採番するので持たない）"""
    title: str
    category: str
    price: float = Field(ge=0)
    rating: int = Field(ge=0, le=5)


# ============================================================
# 3. データ置き場（デモ用のメモリ内リスト）
# ============================================================
# 実際は Lv11 の SQLite に差し替える（改造課題）。
# サーバーを再起動すると追加分は消える点に注意。

BOOKS: list[Book] = [
    Book(id=1, title="A Light in the Attic", category="Poetry", price=51.77, rating=3),
    Book(id=2, title="Tipping the Velvet", category="Historical", price=53.74, rating=1),
    Book(id=3, title="Sharp Objects", category="Mystery", price=47.82, rating=4),
    Book(id=4, title="Sapiens: A Brief History", category="History", price=54.23, rating=5),
    Book(id=5, title="The Requiem Red", category="Mystery", price=22.65, rating=1),
    Book(id=6, title="Set Me Free", category="Fiction", price=17.46, rating=5),
]


# ============================================================
# 4. エンドポイント（URLと関数の対応）を定義する
# ============================================================

@app.get("/")
def read_root() -> dict:
    """
    動作確認用のトップページ。

    @app.get("/") は「GET / に来たらこの関数を呼ぶ」という登録（デコレータ! Lv03参照）。
    戻り値の辞書は自動で JSON に変換されて返る。
    """
    return {
        "message": "書籍データAPIへようこそ",
        "docs": "http://127.0.0.1:8000/docs を開くと試せる仕様書が見られます",
        "time": datetime.now().isoformat(),
    }


@app.get("/books")
def list_books(min_rating: int = 0, max_price: float | None = None) -> list[Book]:
    """
    書籍一覧（絞り込み付き）。

    関数の引数がそのまま「クエリパラメータ」になる:
      /books?min_rating=4&max_price=50
    型ヒント通りに自動変換され、変換できない値は FastAPI が 422 エラーにしてくれる。
    """
    result = [b for b in BOOKS if b.rating >= min_rating]
    if max_price is not None:
        result = [b for b in result if b.price <= max_price]
    return result


@app.get("/books/{book_id}")
def get_book(book_id: int) -> Book:
    """
    書籍1件の取得。

    URL の {book_id} 部分が引数として渡される（パスパラメータ）:
      /books/3 → book_id = 3
    見つからないときは HTTPException で 404 を返すのが REST API の作法。
    """
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail=f"書籍 id={book_id} は存在しません")


@app.post("/books", status_code=201)
def create_book(payload: BookCreate) -> Book:
    """
    書籍の登録。

    引数の型が BaseModel（BookCreate）だと、リクエストボディの JSON を
    自動で受け取り・検証してくれる。
      - price に "abc" が来たら → 422 エラー（自分でチェック不要）
      - rating=9 が来たら     → 422 エラー（Field の le=5 制約）
    """
    new_id = max(b.id for b in BOOKS) + 1
    book = Book(id=new_id, **payload.model_dump())
    # model_dump(): モデルを辞書に変換。**で展開して Book に渡す（Lv03 の **kwargs）
    BOOKS.append(book)
    return book


@app.get("/stats")
def get_stats() -> dict:
    """
    集計エンドポイント。「データそのもの」ではなく「集計結果」を返す例。
    """
    if not BOOKS:
        return {"count": 0}
    prices = [b.price for b in BOOKS]
    return {
        "count": len(BOOKS),
        "avg_price": round(sum(prices) / len(prices), 2),
        "max_price": max(prices),
        "by_rating": {
            str(r): len([b for b in BOOKS if b.rating == r]) for r in range(1, 6)
        },
    }


# ============================================================
# 5. async エンドポイント ─ Lv05 の async/await の回収
# ============================================================
# FastAPI は def と async def の両方をサポートする。
# 「他のAPIを await で呼ぶ」「Playwright async 版を使う」ような
# 待ち時間の多い処理は async def にすると、待っている間も他のリクエストを捌ける。

@app.get("/slow-demo")
async def slow_demo() -> dict:
    """
    非同期処理のデモ。1秒待つ間も、サーバーは他のリクエストを処理できる。
    （time.sleep(1) と書くとサーバー全体が止まる。Lv05 async 版で学んだ違い！）
    """
    import asyncio
    await asyncio.sleep(1)
    return {"message": "1秒待ちましたが、その間も他のリクエストを捌けていました"}
