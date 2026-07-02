"""
Lv11 - SQLiteでデータ蓄積と差分検知
====================================
スクレイピング結果を「実行のたびにデータベースへ蓄積」し、
前回実行時との差分（新規・削除・価格変更）を自動検出する。

なぜデータベースか:
  - CSVの山は「いつ・何が変わったか」を調べるのが大変
  - DBに履歴を貯めれば「前回との比較」「期間指定の検索」が一瞬でできる
  - 差分検知は業務自動化の定番ニーズ（新着検知・価格監視・在庫監視）

SQLite は Python 標準ライブラリ (sqlite3) だけで使える
「ファイル1つで完結する本物のデータベース」。サーバー不要。

実行方法:
    python main.py        # 1回目: 初回スナップショット保存
    python main.py        # 2回目: 前回との差分を検出（データが少し変化する）
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "books.db"


# ============================================================
# 0. サンプルデータ ─ スクレイピング結果のシミュレーション
# ============================================================
# 実際は Lv09 の scraper が返す list[dict] を使う。
# ここでは「実行するたびに少し変化するデータ」を再現するため、
# 実行回数（DB内のスナップショット数）によって返す内容を変える。

RUN_1 = [
    {"title": "A Light in the Attic", "price": 51.77},
    {"title": "Tipping the Velvet", "price": 53.74},
    {"title": "Soumission", "price": 50.10},
    {"title": "Sharp Objects", "price": 47.82},
]

RUN_2 = [
    {"title": "A Light in the Attic", "price": 51.77},   # 変化なし
    {"title": "Tipping the Velvet", "price": 49.99},     # ← 値下げ！
    # "Soumission" は削除（取扱終了）
    {"title": "Sharp Objects", "price": 47.82},          # 変化なし
    {"title": "Sapiens: A Brief History", "price": 54.23},  # ← 新商品！
]


def fetch_books(run_count: int) -> list[dict]:
    """
    スクレイピングの代わりにサンプルデータを返す。
    実際のツールではここを Lv09 の PageScraper.scrape() に差し替える。
    """
    return RUN_1 if run_count == 0 else RUN_2


# ============================================================
# 1. データベースの準備
# ============================================================

def init_db(conn: sqlite3.Connection) -> None:
    """
    テーブルを作成する（既にあれば何もしない）。

    SQL とは:
      データベースに命令するための言語。Python の中に文字列として書く。
      CREATE TABLE = 表を作る / INSERT = 行を追加 / SELECT = 検索

    テーブル設計:
      snapshots … 「いつ実行したか」を1行で表す
      books     … 各実行で取得した書籍。どの実行分かを snapshot_id で紐づける
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER NOT NULL,
            title       TEXT NOT NULL,
            price       REAL NOT NULL,
            FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
        )
    """)
    conn.commit()  # 変更を確定する（保存に相当）


def count_snapshots(conn: sqlite3.Connection) -> int:
    """これまでの実行（スナップショット）回数を返す。"""
    # SELECT の結果は fetchone() で1行取り出せる。結果はタプル
    row = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()
    return row[0]


# ============================================================
# 2. スナップショットの保存
# ============================================================

def save_snapshot(conn: sqlite3.Connection, books: list[dict]) -> int:
    """
    今回の取得結果を1スナップショットとして保存し、そのIDを返す。

    ★ SQLに値を埋め込むときは必ず「?」プレースホルダを使う。
      f-string で SQL を組み立てると、値に ' などが入ったとき壊れるうえ、
      SQLインジェクションという重大なセキュリティ問題の原因になる。
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # INSERT して、その行の自動採番IDを受け取る
    cursor = conn.execute("INSERT INTO snapshots (created_at) VALUES (?)", (now,))
    snapshot_id = cursor.lastrowid

    # 書籍をまとめて INSERT（executemany = 同じSQLを複数データで繰り返す）
    conn.executemany(
        "INSERT INTO books (snapshot_id, title, price) VALUES (?, ?, ?)",
        [(snapshot_id, b["title"], b["price"]) for b in books],
    )
    conn.commit()

    print(f"スナップショット #{snapshot_id} を保存しました（{len(books)} 件, {now}）")
    return snapshot_id


def load_snapshot(conn: sqlite3.Connection, snapshot_id: int) -> dict[str, float]:
    """
    指定スナップショットの書籍を {タイトル: 価格} の辞書で返す。
    差分比較は「タイトルをキーにした辞書」同士で行うと簡単。
    """
    rows = conn.execute(
        "SELECT title, price FROM books WHERE snapshot_id = ?",
        (snapshot_id,),
    ).fetchall()
    return {title: price for title, price in rows}
    # ↑ 辞書内包表記: リスト内包表記の辞書版 {キー: 値 for ...}


# ============================================================
# 3. 差分検知 ─ このレベルの核心
# ============================================================

def detect_diff(old: dict[str, float], new: dict[str, float]) -> dict:
    """
    2つのスナップショットを比較して差分を返す。

    集合演算を使うと差分が簡潔に書ける:
      dict.keys() は集合のように扱えて、
      new.keys() - old.keys() = 「新しい方にしかないキー」（新規）
      old.keys() - new.keys() = 「古い方にしかないキー」（削除）
      new.keys() & old.keys() = 「両方にあるキー」（価格比較の対象）
    """
    added = sorted(new.keys() - old.keys())
    removed = sorted(old.keys() - new.keys())

    changed = []
    for title in sorted(new.keys() & old.keys()):
        if new[title] != old[title]:
            changed.append({"title": title, "old": old[title], "new": new[title]})

    return {"added": added, "removed": removed, "changed": changed}


def print_diff_report(diff: dict) -> None:
    """差分を人間向けのレポートとして表示する。"""
    print()
    print("=" * 60)
    print("  前回実行時からの差分レポート")
    print("=" * 60)

    if not (diff["added"] or diff["removed"] or diff["changed"]):
        print("  変更はありませんでした。")
        return

    for title in diff["added"]:
        print(f"  [新規]     {title}")
    for title in diff["removed"]:
        print(f"  [取扱終了] {title}")
    for item in diff["changed"]:
        direction = "値下げ↓" if item["new"] < item["old"] else "値上げ↑"
        print(f"  [{direction}] {item['title']}: £{item['old']} → £{item['new']}")

    total = len(diff["added"]) + len(diff["removed"]) + len(diff["changed"])
    print(f"\n  合計 {total} 件の変更を検出しました")


# ============================================================
# 4. 履歴の照会 ─ DBに貯めたからこそできること
# ============================================================

def show_history(conn: sqlite3.Connection) -> None:
    """全スナップショットの一覧と件数を表示する。"""
    print()
    print("--- 実行履歴 ---")
    # JOIN: 2つのテーブルを snapshot_id で結合して集計する
    rows = conn.execute("""
        SELECT s.id, s.created_at, COUNT(b.id)
        FROM snapshots s
        LEFT JOIN books b ON b.snapshot_id = s.id
        GROUP BY s.id
        ORDER BY s.id
    """).fetchall()
    for snap_id, created_at, book_count in rows:
        print(f"  #{snap_id}  {created_at}  {book_count} 件")


# ============================================================
# メイン処理
# ============================================================

def main() -> None:
    print("=" * 60)
    print("Lv11 - SQLiteでデータ蓄積と差分検知")
    print("=" * 60)

    # sqlite3.connect() は DB ファイルを開く（無ければ自動作成）。
    # with 文で使うとブロック終了時に commit/rollback が適切に処理される
    with sqlite3.connect(DB_PATH) as conn:
        init_db(conn)

        run_count = count_snapshots(conn)
        print(f"これまでの実行回数: {run_count} 回")

        # --- 「スクレイピング」してスナップショット保存 ---
        books = fetch_books(run_count)
        new_id = save_snapshot(conn, books)

        # --- 前回スナップショットがあれば差分を出す ---
        if new_id > 1:
            old_data = load_snapshot(conn, new_id - 1)
            new_data = load_snapshot(conn, new_id)
            diff = detect_diff(old_data, new_data)
            print_diff_report(diff)
        else:
            print("\n初回実行のため差分はありません。")
            print("もう一度 python main.py を実行すると差分検知を体験できます。")

        show_history(conn)

    print()
    print(f"データベースファイル: {DB_PATH}")
    print("（削除すれば履歴はリセットされる。DBの中身は README の「DBを覗く」参照）")


if __name__ == "__main__":
    main()
