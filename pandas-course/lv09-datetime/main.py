"""
pandas講座 Lv09 - 日付データの扱い（datetime）
=================================================
「月次売上」「前月比」「曜日別の傾向」は、経理・営業レポートの定番。
これらはすべて「日付を扱う力」が土台になっている。

実行方法:
    python main.py
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


df = pd.read_csv(DATA_DIR / "daily_sales.csv")

section("0. 読み込んだデータ（日別売上, 2026年4〜6月）")
print(df.head())
print(f"\n列の型: date={df['date'].dtype}, revenue={df['revenue'].dtype}")
print("→ date 列は今のところ『ただの文字列』として読まれている点に注意")


# ============================================================
# 1. to_datetime ─ 文字列を「日付」として認識させる
# ============================================================
# CSVから読んだ日付は、そのままだと「2026-04-01」という文字列に過ぎない。
# to_datetime() で変換すると、年・月・曜日などを取り出せる特別な型になる。

section("1. pd.to_datetime(): 文字列を日付型に変換")

df["date"] = pd.to_datetime(df["date"])
print(f"変換後の型: {df['date'].dtype}")  # datetime64[ns] になる
print(df.head())


# ============================================================
# 2. dt アクセサ ─ 日付から年・月・曜日を取り出す
# ============================================================
# .str が文字列用のアクセサだったように（Lv03）、
# datetime型の列には .dt というアクセサがある。

section("2. .dt アクセサ: 年・月・曜日を取り出す")

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["weekday"] = df["date"].dt.day_name()  # "Monday" のような曜日名（英語）

print(df[["date", "year", "month", "day", "weekday"]].head())

# 日本語の曜日名にしたい場合の変換テーブル
weekday_jp = {
    "Monday": "月", "Tuesday": "火", "Wednesday": "水", "Thursday": "木",
    "Friday": "金", "Saturday": "土", "Sunday": "日",
}
df["weekday_jp"] = df["weekday"].map(weekday_jp)
# map(): 辞書に従って値を1対1で置き換える。Lv03のreplaceに近いが辞書ベースで書ける
print("\n--- 曜日を日本語に変換 ---")
print(df[["date", "weekday_jp"]].head())


# ============================================================
# 3. 曜日別の傾向を見る ─ Lv05のgroupbyとの組み合わせ
# ============================================================

section("3. 曜日別の平均売上（groupbyとの組み合わせ）")

by_weekday = df.groupby("weekday_jp")["revenue"].mean().round(0)
# 曜日の並び順を月〜日にしたい場合は reindex で順番を指定する
weekday_order = ["月", "火", "水", "木", "金", "土", "日"]
by_weekday = by_weekday.reindex(weekday_order)
print(by_weekday)


# ============================================================
# 4. 日付の範囲で絞り込む
# ============================================================

section("4. 日付の範囲で絞り込む")

# --- between(): 指定した範囲内かどうか ---
may_data = df[df["date"].between("2026-05-01", "2026-05-31")]
print(f"5月のデータ: {len(may_data)} 日分")
print(f"5月の売上合計: {may_data['revenue'].sum():,.0f} 円")

# --- 比較演算子でも書ける ---
after_june = df[df["date"] >= "2026-06-01"]
print(f"\n6月以降: {len(after_june)} 日分")


# ============================================================
# 5. resample ─ 日次データを月次・週次にまとめる
# ============================================================
# resample() を使うには、日付列をindexにする必要がある。
# 「日ごとのデータ」→「月ごとの合計」のような期間の集約に使う。

section("5. resample(): 日次 → 月次への集約")

df_indexed = df.set_index("date")  # date列をindexに設定
monthly = df_indexed["revenue"].resample("ME").sum()  # "ME" = Month End（月末）
print("--- 月次売上合計 ---")
print(monthly)

print("\n--- 週次売上合計（先頭5週）---")
weekly = df_indexed["revenue"].resample("W").sum()
print(weekly.head())


# ============================================================
# 6. 前月比・前週比 ─ pct_change()
# ============================================================
# 「先月と比べて何%増減したか」は経営会議で必ず聞かれる数字。

section("6. pct_change(): 前月比・前週比")

monthly_growth = (monthly.pct_change() * 100).round(1)
print("--- 月次売上と前月比(%) ---")
result = pd.DataFrame({"売上": monthly, "前月比(%)": monthly_growth})
print(result)
print("\n※ 最初の月は「前の月がない」ため NaN になる（正常な挙動）")


# ============================================================
# まとめ
# ============================================================
section("まとめ")

print("""
  やりたいこと                    書き方
  ───────────────────────────────  ─────────────────────────────────────
  文字列を日付型に変換            pd.to_datetime(df["列"])
  年・月・日・曜日を取り出す      df["日付列"].dt.year / .month / .day / .day_name()
  日付の範囲で絞り込む            df[df["日付列"].between("開始","終了")]
  日次→月次/週次に集約            df.set_index("日付列")["値"].resample("ME"/"W").sum()
  前月比・前週比                  集約後のSeries.pct_change()

  ★ resample を使うには、まず日付列を set_index() で index にする。
    「時系列データはindexに日付を置く」がpandasの基本作法。
""")
