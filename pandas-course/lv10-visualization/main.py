"""
pandas講座 Lv10 - グラフ化の基本
==================================
集計した数字は、表よりグラフの方が一瞬で伝わることが多い。
ここでは pandas に組み込まれた .plot() と、その裏で動いている
matplotlib の最低限を扱う。

★ 日本語が文字化けする（□□□になる）場合:
  Windows なら "Meiryo"、macOS なら "Hiragino Sans" のような
  日本語フォントを指定する必要がある（下記 FONT_CANDIDATES 参照）。

実行方法:
    python main.py
出力:
    output/ 以下に png ファイルが生成される（画面表示ではなくファイル保存）
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

matplotlib.use("Agg")  # 画面を持たない環境でも動くように、ファイル保存専用モードにする

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


# --- 日本語フォントの設定 ---
# 環境によって使えるフォント名が違うため、候補を順に試す
FONT_CANDIDATES = ["IPAexGothic", "Noto Sans CJK JP", "Meiryo", "Hiragino Sans", "Yu Gothic"]
available_fonts = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
for font_name in FONT_CANDIDATES:
    if font_name in available_fonts:
        plt.rcParams["font.family"] = font_name
        print(f"日本語フォント: {font_name} を使用")
        break
else:
    print("※ 日本語フォントが見つからないため、グラフの日本語が文字化けする場合があります")
plt.rcParams["axes.unicode_minus"] = False  # マイナス記号の文字化け対策


orders = pd.read_csv(DATA_DIR / "orders.csv")
daily = pd.read_csv(DATA_DIR / "daily_sales.csv")
orders["subtotal"] = orders["quantity"] * orders["unit_price"]
daily["date"] = pd.to_datetime(daily["date"])

section("0. データ確認")
print(f"orders: {len(orders)} 件 / daily_sales: {len(daily)} 日分")


# ============================================================
# 1. df.plot() ─ 集計結果をそのままグラフにする
# ============================================================
# groupby(Lv05)の結果はSeries/DataFrameなので、そのまま .plot() できる。
# kind= で棒グラフ・折れ線・円グラフなどを切り替える。

section("1. カテゴリ別売上 ─ 棒グラフ (kind='bar')")

by_category = orders.groupby("category")["subtotal"].sum().sort_values(ascending=False)

ax = by_category.plot(kind="bar", title="カテゴリ別売上", figsize=(8, 5), color="steelblue")
ax.set_ylabel("売上（円）")
ax.set_xlabel("カテゴリ")
plt.xticks(rotation=30, ha="right")  # ラベルが重ならないよう斜めにする
plt.tight_layout()  # ラベルがはみ出さないよう自動調整

fig_path = OUTPUT_DIR / "category_bar.png"
plt.savefig(fig_path)
plt.close()  # 次のグラフのために描画をリセット
print(f"保存: {fig_path}")


# ============================================================
# 2. 時系列の折れ線グラフ ─ 月次推移
# ============================================================
# 「推移」を見せたいデータは折れ線グラフが定番。resample(Lv09)と組み合わせる。

section("2. 月次売上推移 ─ 折れ線グラフ (kind='line')")

monthly = daily.set_index("date")["revenue"].resample("ME").sum()

ax = monthly.plot(kind="line", marker="o", title="月次売上推移", figsize=(8, 5))
ax.set_ylabel("売上（円）")
ax.set_xlabel("月")
plt.tight_layout()

fig_path = OUTPUT_DIR / "monthly_line.png"
plt.savefig(fig_path)
plt.close()
print(f"保存: {fig_path}")


# ============================================================
# 3. 日次データの折れ線 ─ ばらつきの大きいデータの見せ方
# ============================================================

section("3. 日次売上の推移（生データ）")

ax = daily.set_index("date")["revenue"].plot(
    kind="line", title="日次売上（4〜6月）", figsize=(10, 4), linewidth=1,
)
ax.set_ylabel("売上（円）")
plt.tight_layout()

fig_path = OUTPUT_DIR / "daily_line.png"
plt.savefig(fig_path)
plt.close()
print(f"保存: {fig_path}")


# ============================================================
# 4. 構成比を見せる ─ 円グラフと100%積み上げ棒
# ============================================================
# 円グラフは「全体に対する割合」を直感的に見せられるが、
# 項目数が多いと逆に読みにくくなる（実務では5〜6項目までが目安）。

section("4. カテゴリ構成比 ─ 円グラフ (kind='pie')")

ax = by_category.plot(
    kind="pie", title="カテゴリ別売上構成比", autopct="%1.1f%%", figsize=(6, 6), ylabel="",
)
plt.tight_layout()

fig_path = OUTPUT_DIR / "category_pie.png"
plt.savefig(fig_path)
plt.close()
print(f"保存: {fig_path}")


# ============================================================
# 5. 複数系列の比較 ─ 積み上げ棒グラフ
# ============================================================
# Lv08で学んだpivot_tableの結果は、そのまま複数系列のグラフにできる。

section("5. 月次×カテゴリ ─ 積み上げ棒グラフ")

orders["month"] = pd.to_datetime(orders["order_date"]).dt.strftime("%Y-%m")
pivot = orders.pivot_table(index="month", columns="category", values="subtotal", aggfunc="sum", fill_value=0)

ax = pivot.plot(kind="bar", stacked=True, title="月次×カテゴリ 売上（積み上げ）", figsize=(9, 5))
ax.set_ylabel("売上（円）")
ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))  # 凡例をグラフの外に出す
plt.xticks(rotation=0)
plt.tight_layout()

fig_path = OUTPUT_DIR / "monthly_category_stacked.png"
plt.savefig(fig_path)
plt.close()
print(f"保存: {fig_path}")


# ============================================================
# まとめ
# ============================================================
section("まとめ: ビジネスで使うグラフの選び方")

print(f"""
  伝えたいこと              グラフの種類              書き方
  ────────────────────────  ─────────────────────────  ─────────────────────────
  項目ごとの比較            棒グラフ                  .plot(kind="bar")
  時間の推移                折れ線グラフ              .plot(kind="line")
  全体に対する割合          円グラフ（項目5〜6個まで）.plot(kind="pie")
  複数系列の内訳＋合計      積み上げ棒グラフ          .plot(kind="bar", stacked=True)

  保存先: {OUTPUT_DIR}
  （このスクリプトは matplotlib.use("Agg") でファイル保存専用にしている。
   Jupyter やスクリプト内で画面に直接表示したい場合はこの指定を外し、
   plt.savefig() の代わりに plt.show() を使う）
""")
