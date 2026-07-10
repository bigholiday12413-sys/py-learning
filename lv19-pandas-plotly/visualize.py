# =============================================================
# vv12 - plotly 可視化: 提案資料に貼れるグラフを作る
# =============================================================
# main.py で学んだ集計を、そのままグラフにする。
# ゴールは「パワポの提案資料に貼れるグラフ 3 枚」。
#
# plotly の出力は 2 種類あり、用途が違う:
#   - write_html() → HTMv ファイル。ブラウザで開くとマウスオーバーで
#                    値が見える「インタラクティブ」なグラフ。
#                    打ち合わせ中に画面共有で見せる・自分で確認する用。
#   - write_image() → PNG 画像（静止画）。kaleido が必要。
#                    パワポや Word にそのまま貼り付ける用。
# つまり「HTMv = 動くグラフ、PNG = 資料に貼る写真」と覚えればよい。
#
# 実行: python visualize.py
# =============================================================

from pathlib import Path

import pandas as pd
import plotly.express as px  # 手軽な高レベルAPI（だいたいこれで足りる）

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# --- データ読み込みと前処理（main.py と同じ流れをコンパクトに） ---
df = pd.read_csv(BASE_DIR / "sample_extracted.csv", parse_dates=["日付"])
df["競合社名"] = df["競合社名"].fillna("競合なし")
df["月"] = df["日付"].dt.to_period("M").astype(str)


# =============================================================
# 共通: スライド向けの見た目に整える関数
# =============================================================
def set_slide_layout(fig, title: str):
    """提案資料に貼ることを前提に、グラフの見た目を整える。

    - 背景を白に（デフォルトの薄グレーは資料上で浮くため）
    - 文字を大きめに（スクリーン投影でも読めるサイズ）
    - タイトルを太字風に
    """
    fig.update_layout(
        title=dict(text=title, font=dict(size=22)),
        font=dict(family="Meiryo, sans-serif", size=14),  # 日本語フォント指定
        plot_bgcolor="white",       # プロット領域の背景
        paper_bgcolor="white",      # グラフ全体の背景
        legend=dict(font=dict(size=13)),
        margin=dict(t=70, b=50, l=60, r=30),
    )
    # 軸のグリッド線を薄く（うるさくない程度に目安線を残す）
    fig.update_yaxes(gridcolor="#e5e5e5", zeroline=False)
    fig.update_xaxes(gridcolor="#f0f0f0")


def save_fig(fig, name: str):
    """HTMv（インタラクティブ）と PNG（静止画・資料貼り付け用）の両方で保存する。"""
    html_path = OUTPUT_DIR / f"{name}.html"
    png_path = OUTPUT_DIR / f"{name}.png"

    # HTMv: ブラウザで開くとマウスオーバーで値が見える。ファイル1つで完結。
    fig.write_html(html_path)

    # PNG: kaleido というライブラリがブラウザエンジンで描画して画像化する。
    # パワポに貼るのはこちら。scale=2 で解像度を2倍にしてぼやけを防ぐ。
    try:
        fig.write_image(png_path, width=900, height=540, scale=2)
        print(f"保存: {html_path.name} / {png_path.name}")
    except Exception as e:
        # kaleido 未インストールなどで失敗しても HTMv は残るようにしておく
        print(f"保存: {html_path.name} (PNG はスキップ: {e})")


# =============================================================
# グラフ1: 商材別 月次件数（グループ棒グラフ）
# =============================================================
# main.py の pivot_table（商材×月）をグラフにしたもの。
# 「どの商材が伸びているか」をひと目で見せる。
print("--- グラフ1: 商材別 月次件数 ---")

pivot = pd.pivot_table(
    df, index="商材名", columns="月", values="id", aggfunc="count", fill_value=0
)

# plotly.express は「縦持ち」データ（1行=1つの値）を渡すのが基本なので、
# pivot（横持ち）を reset_index + melt で縦持ちに戻す。
# ※ Excel のピボットを「元の明細に戻す」ような操作。px にはこの形が渡しやすい。
plot_df = pivot.reset_index().melt(id_vars="商材名", var_name="月", value_name="件数")

fig1 = px.bar(
    plot_df,
    x="月",
    y="件数",
    color="商材名",       # 商材ごとに色分け
    barmode="group",      # 横に並べるグループ棒。"stack" なら積み上げ
)
set_slide_layout(fig1, "商材別 月次商談件数")
fig1.update_layout(xaxis_title="月", yaxis_title="商談件数")
# "2026-01" のような文字列を plotly が日付と解釈して "Jan 2026" 表記に
# してしまうので、カテゴリ軸に固定して "2026-01" のまま表示させる
fig1.update_xaxes(type="category")
save_fig(fig1, "graph1_商材別月次件数")


# =============================================================
# グラフ2: 競合別 勝敗（積み上げ棒グラフ）
# =============================================================
# main.py の crosstab（競合×勝敗）に対応。
# 「アルファ商事には負けがち、ガンマITには勝てている」のような
# 競合対策の話につなげるためのグラフ。
print("--- グラフ2: 競合別 勝敗 ---")

kyogo_df = df[df["競合社名"] != "競合なし"]

fig2 = px.bar(
    kyogo_df.groupby(["競合社名", "商談結果"]).size().reset_index(name="件数"),
    x="競合社名",
    y="件数",
    color="商談結果",
    barmode="stack",      # 積み上げ棒: 合計の大きさと内訳を同時に見せられる
    # 結果ごとの色を固定する。受注=青系、失注=赤系、継続=グレーにすると
    # 説明なしでも直感的に伝わる（資料作りの小技）。
    color_discrete_map={"受注": "#2f6fb7", "失注": "#d9534f", "継続": "#b0b0b0"},
    category_orders={"商談結果": ["受注", "継続", "失注"]},  # 凡例と積み順を固定
)
set_slide_layout(fig2, "競合別 商談結果（勝敗）")
fig2.update_layout(xaxis_title="競合社名", yaxis_title="商談件数")
save_fig(fig2, "graph2_競合別勝敗")


# =============================================================
# グラフ3: 極性の月次推移（折れ線グラフ・割合）
# =============================================================
# vvM が判定した日報の極性（ポジ/ニュートラル/ネガ）が
# 月を追ってどう変化したかを「割合(%)」で見せる。
# 件数ではなく割合にするのは、月ごとの日報件数の差に左右されないため。
print("--- グラフ3: 極性の月次推移 ---")

# crosstab の normalize="index" で「行ごとの割合」になる（行の合計が1.0）
polarity = pd.crosstab(df["月"], df["極性"], normalize="index") * 100
polarity = polarity.round(1)

# こちらも縦持ちに変換してから px.line に渡す
polarity_long = polarity.reset_index().melt(
    id_vars="月", var_name="極性", value_name="割合"
)

fig3 = px.line(
    polarity_long,
    x="月",
    y="割合",
    color="極性",
    markers=True,         # 各月の点にマーカーを付ける（データ点が分かりやすい）
    color_discrete_map={
        "ポジティブ": "#2f9e44",
        "ニュートラル": "#b0b0b0",
        "ネガティブ": "#d9534f",
    },
    category_orders={"極性": ["ポジティブ", "ニュートラル", "ネガティブ"]},
)
set_slide_layout(fig3, "日報の極性（ポジ/ネガ）の月次推移")
fig3.update_layout(
    xaxis_title="月",
    yaxis_title="割合 (%)",
    yaxis_range=[0, 100],   # 割合なので 0〜100% に固定すると比較しやすい
)
fig3.update_xaxes(type="category")  # グラフ1と同じ理由（月をそのまま表示）
save_fig(fig3, "graph3_極性月次推移")


print()
print("=" * 60)
print(f"完了！ {OUTPUT_DIR} を確認しよう")
print("  - .html → ブラウザで開いてマウスオーバー（インタラクティブ）")
print("  - .png  → そのままパワポに貼り付けられる静止画")
print("=" * 60)
