"""
Lv15 - Streamlit：スクリプトを社内Webツールにする
===================================================
Streamlit は「Python スクリプトがそのまま Web アプリになる」フレームワーク。
HTML / CSS / JavaScript を1行も書かずに、画面付きツールが作れる。

実行方法（python ではなく streamlit コマンドで起動する！）:
    pip install -r requirements.txt
    streamlit run app.py
    → ブラウザが自動で開く（http://localhost:8501）

★ Streamlit の動作モデル（最重要）:
  「画面の部品を操作するたびに、このスクリプトが上から全部再実行される」
  st.slider() などの入力部品は「現在の値」を返すただの関数呼び出しなので、
  普通の Python スクリプトを書く感覚のまま画面が作れる。
"""

from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st  # 慣習として st という別名で import する

# ============================================================
# 0. サンプルデータ
# ============================================================
# 実際は Lv09 のスクレイパーや Lv11 の SQLite から読み込む。
# ここでは Lv14 と同じ書籍データを埋め込みで用意する。

BOOKS = [
    {"title": "A Light in the Attic", "category": "Poetry", "price": 51.77, "rating": 3},
    {"title": "Tipping the Velvet", "category": "Historical", "price": 53.74, "rating": 1},
    {"title": "Soumission", "category": "Fiction", "price": 50.10, "rating": 1},
    {"title": "Sharp Objects", "category": "Mystery", "price": 47.82, "rating": 4},
    {"title": "Sapiens: A Brief History", "category": "History", "price": 54.23, "rating": 5},
    {"title": "The Requiem Red", "category": "Mystery", "price": 22.65, "rating": 1},
    {"title": "The Dirty Little Secrets", "category": "Business", "price": 33.34, "rating": 4},
    {"title": "The Coming Woman", "category": "Historical", "price": 17.93, "rating": 3},
    {"title": "The Boys in the Boat", "category": "History", "price": 22.60, "rating": 4},
    {"title": "The Black Maria", "category": "Poetry", "price": 52.15, "rating": 1},
    {"title": "Starving Hearts", "category": "Fiction", "price": 13.99, "rating": 2},
    {"title": "Shakespeare's Sonnets", "category": "Poetry", "price": 20.66, "rating": 4},
    {"title": "Set Me Free", "category": "Fiction", "price": 17.46, "rating": 5},
]


# ============================================================
# 1. ページ設定とタイトル
# ============================================================
# st.xxx() を呼ぶと、その場所に画面部品が上から順に配置されていく

st.set_page_config(page_title="書籍データ ダッシュボード", page_icon="📗")

st.title("📗 書籍データ ダッシュボード")
st.caption(f"Lv15 - Streamlit デモ | 最終表示: {datetime.now().strftime('%H:%M:%S')}")


# ============================================================
# 2. サイドバー ─ 絞り込み条件の入力部品
# ============================================================
# with st.sidebar: の中に書いた部品は左のサイドバーに置かれる。
# 各部品は「ユーザーが今選んでいる値」をそのまま返す。

with st.sidebar:
    st.header("絞り込み条件")

    # スライダー: (ラベル, 最小, 最大, 初期値) → 現在値が返る
    min_rating = st.slider("星評価（以上）", 1, 5, 1)

    # 数値入力
    max_price = st.number_input("価格上限（£）", min_value=0.0, value=60.0, step=5.0)

    # 複数選択: 選択肢リストから複数選べる
    all_categories = sorted({b["category"] for b in BOOKS})  # set内包表記で重複除去
    categories = st.multiselect("カテゴリ", all_categories, default=all_categories)

    st.divider()
    st.caption("※ 条件を変えるたびにスクリプト全体が再実行され、画面が更新される")


# ============================================================
# 3. データの絞り込み（Lv14 の pandas をそのまま活用）
# ============================================================

df = pd.DataFrame(BOOKS)
filtered = df[
    (df["rating"] >= min_rating)
    & (df["price"] <= max_price)
    & (df["category"].isin(categories))   # isin: 「リストのどれかに一致」
]


# ============================================================
# 4. メトリクス表示 ─ ダッシュボードの顔
# ============================================================
# st.columns(3) で横3分割し、各列に st.metric（大きな数字表示）を置く

col1, col2, col3 = st.columns(3)
col1.metric("該当冊数", f"{len(filtered)} 冊")
col2.metric("平均価格", f"£{filtered['price'].mean():.2f}" if len(filtered) else "―")
col3.metric("平均評価", f"★{filtered['rating'].mean():.1f}" if len(filtered) else "―")


# ============================================================
# 5. テーブルとグラフ
# ============================================================

st.subheader("書籍一覧")
if filtered.empty:
    # 0件のときの案内を忘れない（Lv13 で学んだ「ゼロ件の挙動」）
    st.warning("条件に合う書籍がありません。条件を緩めてください。")
else:
    # st.dataframe: ソート・検索付きのインタラクティブな表になる
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.subheader("カテゴリ別 冊数")
    # value_counts() でカテゴリごとの件数 → そのまま棒グラフに
    st.bar_chart(filtered["category"].value_counts())


# ============================================================
# 6. ダウンロードボタン ─ 結果を配れるようにする
# ============================================================
# 「絞り込んだ結果をCSV/Excelで持ち帰れる」だけで業務ツールとして一気に実用的になる

st.subheader("結果のダウンロード")

dl_col1, dl_col2 = st.columns(2)

# CSV: 文字列にしてから bytes に変換して渡す（utf-8-sig は Lv02 の知識）
csv_bytes = filtered.to_csv(index=False).encode("utf-8-sig")
dl_col1.download_button(
    "📄 CSV をダウンロード",
    data=csv_bytes,
    file_name="books_filtered.csv",
    mime="text/csv",
)

# Excel: メモリ上のファイル(BytesIO)に書き出して渡す（ディスクを経由しない）
excel_buffer = BytesIO()
filtered.to_excel(excel_buffer, index=False)
dl_col2.download_button(
    "📊 Excel をダウンロード",
    data=excel_buffer.getvalue(),
    file_name="books_filtered.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)


# ============================================================
# 7. ボタンで処理を実行する ─ 業務ツールへの応用の入口
# ============================================================
# 実際のツールでは、このボタンから Lv09 のスクレイパーを呼び出す。
# st.button() は「今回の再実行がこのボタン押下によるものなら True」を返す。

st.divider()
st.subheader("データ更新（デモ）")

if st.button("🔄 最新データを取得する"):
    # 時間のかかる処理は st.spinner で「実行中」表示を出す
    with st.spinner("取得中...（実際はここで Lv09 のスクレイパーを呼ぶ）"):
        import time
        time.sleep(1.5)  # スクレイピングの代わりの待機
    st.success("取得完了！（デモなのでデータは変わりません）")
    st.caption("→ 本物にするには、ここで scraper.scrape() を呼んで結果を表示する")
