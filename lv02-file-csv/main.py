"""
Lv02 - ファイル操作と CSV
=========================
Python のファイル読み書き・CSV処理・パス操作を学ぶ。
JS/TS 経験者向けに、Node.js の fs モジュールとの違いを意識しながら進める。

実行方法:
    python main.py
"""

import csv
import os
from pathlib import Path


# ============================================================
# 0. パスの準備 ― pathlib.Path でファイルパスを組み立てる
# ============================================================
# JS/TS では:
#   const path = require('path');
#   const dataDir = path.join(__dirname, 'data');
#
# Python (pathlib) では:
#   Path(__file__) で「このスクリプト自身」のパスを取得し、
#   .parent で親ディレクトリ、/ 演算子でパスを結合する。

# __file__ はこのスクリプトのファイルパス（Python 組み込み変数）
BASE_DIR = Path(__file__).parent            # main.py があるフォルダ
DATA_DIR = BASE_DIR / "data"                # data/ フォルダ
OUTPUT_DIR = BASE_DIR / "output"            # output/ フォルダ

# output/ フォルダがなければ作成（JS の fs.mkdirSync(..., { recursive: true }) に相当）
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Lv02 - ファイル操作と CSV")
print("=" * 60)


# ============================================================
# 1. テキストファイルの書き込み ― open() と with 文
# ============================================================
print("\n--- 1. テキストファイルの書き込み ---")

# ● open() のモード一覧:
#   'r'  = 読み取り (read)    ← デフォルト
#   'w'  = 上書き書き込み (write) ← ファイルがなければ新規作成
#   'a'  = 追記 (append)     ← 末尾に追加
#   'x'  = 新規作成 (exclusive) ← ファイルが既にあるとエラー
#   'b'  = バイナリモード     ← 'rb', 'wb' のように組み合わせる

# ● with 文 (コンテキストマネージャ):
#   JS/TS では try/finally でリソースを解放するが、Python では with 文が担う。
#
#   JS/TS のイメージ:
#     const fd = fs.openSync('file.txt', 'w');
#     try {
#       fs.writeSync(fd, 'Hello');
#     } finally {
#       fs.closeSync(fd);  // 必ず閉じる
#     }
#
#   Python:
#     with open('file.txt', 'w') as f:
#         f.write('Hello')
#     # ← with ブロックを抜けると自動で f.close() が呼ばれる
#     # 例外が発生しても必ず閉じてくれるので安全！

output_text_path = OUTPUT_DIR / "hello.txt"

# 'w' モード: ファイルを新規作成 or 上書き
with open(output_text_path, "w", encoding="utf-8") as f:
    f.write("こんにちは、Python！\n")
    f.write("ファイル操作の練習です。\n")
    f.write("with 文を使うとファイルを自動で閉じてくれます。\n")

print(f"  書き込み完了: {output_text_path}")


# ============================================================
# 2. テキストファイルの読み込み
# ============================================================
print("\n--- 2. テキストファイルの読み込み ---")

# 方法 1: read() で全文を一括読み込み
# JS/TS の fs.readFileSync('file.txt', 'utf-8') に相当
with open(output_text_path, "r", encoding="utf-8") as f:
    content = f.read()  # 文字列として全文を取得
print("  [read() で全文読み込み]")
print(f"  {content}")

# 方法 2: readlines() で行ごとのリストとして読み込み
with open(output_text_path, "r", encoding="utf-8") as f:
    lines = f.readlines()  # 各行を要素とするリスト（改行文字 \n 付き）
print("  [readlines() で行リスト]")
for i, line in enumerate(lines):
    print(f"    {i}: {line.rstrip()}")  # rstrip() で末尾の改行を除去

# 方法 3: for ループで1行ずつ処理（メモリ効率が良い）
# 大きなファイルの場合はこの方法がおすすめ
print("  [for ループで1行ずつ]")
with open(output_text_path, "r", encoding="utf-8") as f:
    for line in f:  # ファイルオブジェクトは直接イテレーション可能！
        print(f"    >>> {line.rstrip()}")


# ============================================================
# 3. テキストファイルへの追記 ('a' モード)
# ============================================================
print("\n--- 3. テキストファイルへの追記 ---")

# 'a' モード: 既存ファイルの末尾に追加（ファイルがなければ新規作成）
with open(output_text_path, "a", encoding="utf-8") as f:
    f.write("--- ここから追記 ---\n")
    f.write("append モードで追加した行です。\n")

# 追記後の内容を確認
with open(output_text_path, "r", encoding="utf-8") as f:
    print(f"  追記後の内容:\n{f.read()}")


# ============================================================
# 4. CSV ファイルの読み込み ― csv.reader (リスト形式)
# ============================================================
print("\n--- 4. CSV の読み込み (csv.reader) ---")

# csv.reader は各行をリスト（配列）として返す
# JS/TS では npm の csv-parse を使うことが多いが、Python は標準ライブラリで対応

csv_path = DATA_DIR / "sample.csv"

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)

    # next() でヘッダ行を先に取得
    # JS/TS のイテレータの .next().value に相当
    header = next(reader)
    print(f"  ヘッダ: {header}")

    # 残りのデータ行をループ
    rows = []
    for row in reader:
        print(f"  行データ: {row}")  # row は ['田中太郎', '営業部', '28'] のようなリスト
        rows.append(row)

print(f"  合計 {len(rows)} 件のデータを読み込みました")


# ============================================================
# 5. CSV ファイルの読み込み ― csv.DictReader (辞書形式)
# ============================================================
print("\n--- 5. CSV の読み込み (csv.DictReader) ---")

# csv.DictReader は各行を辞書（オブジェクト）として返す
# JS/TS で言うと、CSV をパースして [{名前: '田中太郎', 部署: '営業部', ...}, ...] にするイメージ
# ヘッダ行を自動でキーとして使ってくれるので便利！

employees = []  # 全従業員データを格納するリスト

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    # reader.fieldnames でヘッダ（カラム名）のリストを取得できる
    print(f"  カラム名: {reader.fieldnames}")

    for row in reader:
        # row は OrderedDict: {'名前': '田中太郎', '部署': '営業部', '年齢': '28'}
        print(f"  {row['名前']} さん ({row['部署']}, {row['年齢']}歳)")
        employees.append(row)

print(f"  合計 {len(employees)} 件のデータを読み込みました")


# ============================================================
# 6. データの加工 ― 部署ごとの集計
# ============================================================
print("\n--- 6. データの加工 (部署ごとの集計) ---")

# JS/TS なら reduce() や Object.groupBy() を使うところ
# Python では辞書を使って手動で集計するか、collections.defaultdict を使う

dept_stats: dict[str, list[int]] = {}  # {部署名: [年齢リスト]}

for emp in employees:
    dept = emp["部署"]
    age = int(emp["年齢"])  # CSV の値は全て文字列なので int() で変換

    if dept not in dept_stats:
        dept_stats[dept] = []
    dept_stats[dept].append(age)

# 集計結果を表示
print("  部署別の集計結果:")
summary_data = []  # 後で CSV に書き出すためのデータ

for dept, ages in dept_stats.items():
    count = len(ages)
    avg_age = sum(ages) / count
    min_age = min(ages)
    max_age = max(ages)
    print(f"    {dept}: {count}人, 平均年齢 {avg_age:.1f}歳, "
          f"最年少 {min_age}歳, 最年長 {max_age}歳")
    summary_data.append({
        "部署": dept,
        "人数": count,
        "平均年齢": round(avg_age, 1),
        "最年少": min_age,
        "最年長": max_age,
    })


# ============================================================
# 7. CSV ファイルの書き込み ― csv.writer (リスト形式)
# ============================================================
print("\n--- 7. CSV の書き込み (csv.writer) ---")

# csv.writer でリスト形式で CSV を書き出す
# newline='' を指定しないと、Windows で空行が入ることがあるので注意！
# （JS/TS にはない Python 特有の罠）

output_csv_path = OUTPUT_DIR / "summary_list.csv"

with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)

    # ヘッダ行を書き込み
    writer.writerow(["部署", "人数", "平均年齢", "最年少", "最年長"])

    # データ行を書き込み
    for data in summary_data:
        writer.writerow([
            data["部署"],
            data["人数"],
            data["平均年齢"],
            data["最年少"],
            data["最年長"],
        ])

print(f"  書き込み完了: {output_csv_path}")


# ============================================================
# 8. CSV ファイルの書き込み ― csv.DictWriter (辞書形式)
# ============================================================
print("\n--- 8. CSV の書き込み (csv.DictWriter) ---")

# csv.DictWriter は辞書のリストから CSV を書き出す
# fieldnames でカラムの順番を指定する

output_dict_csv_path = OUTPUT_DIR / "summary_dict.csv"

with open(output_dict_csv_path, "w", encoding="utf-8", newline="") as f:
    fieldnames = ["部署", "人数", "平均年齢", "最年少", "最年長"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    # writeheader() でヘッダ行を自動書き込み
    writer.writeheader()

    # writerows() で複数行を一括書き込み（writerow() は1行ずつ）
    writer.writerows(summary_data)

print(f"  書き込み完了: {output_dict_csv_path}")


# ============================================================
# 9. エンコーディング ― UTF-8 と Shift-JIS
# ============================================================
print("\n--- 9. エンコーディング (UTF-8 / Shift-JIS) ---")

# 日本語ファイルでは文字コード（エンコーディング）が重要！
# - UTF-8: 現代の標準。Python のデフォルト。Web でも標準。
# - Shift-JIS (cp932): Windows の日本語環境で昔から使われている。
#   Excel で開く CSV は Shift-JIS のことが多い。
#
# JS/TS (Node.js) では iconv-lite などの外部ライブラリが必要だが、
# Python は open() の encoding パラメータだけで対応できる！

# Shift-JIS の CSV を読み込む
sjis_path = DATA_DIR / "sample_sjis.csv"

# sample_sjis.csv が存在しない場合は、UTF-8 版から Shift-JIS 版を生成する
if not sjis_path.exists():
    print("  sample_sjis.csv が見つからないため、UTF-8 版から生成します...")
    with open(csv_path, "r", encoding="utf-8") as f_in:
        content = f_in.read()
    with open(sjis_path, "w", encoding="shift_jis", newline="") as f_out:
        f_out.write(content)
    print(f"  生成完了: {sjis_path}")

# Shift-JIS のファイルを読み込む
print("  Shift-JIS ファイルの読み込み:")
with open(sjis_path, "r", encoding="shift_jis") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"    {row['名前']} ({row['部署']})")

# Shift-JIS で出力する（Excel で直接開ける CSV を作りたいとき）
output_sjis_path = OUTPUT_DIR / "summary_sjis.csv"
with open(output_sjis_path, "w", encoding="shift_jis", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["部署", "人数", "平均年齢", "最年少", "最年長"])
    writer.writeheader()
    writer.writerows(summary_data)

print(f"  Shift-JIS で書き込み完了: {output_sjis_path}")

# BOM 付き UTF-8（Excel で文字化けしない UTF-8 CSV）
# encoding='utf-8-sig' を使うと BOM (Byte Order Mark) が先頭に付く
output_bom_path = OUTPUT_DIR / "summary_utf8bom.csv"
with open(output_bom_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["部署", "人数", "平均年齢", "最年少", "最年長"])
    writer.writeheader()
    writer.writerows(summary_data)

print(f"  BOM付きUTF-8 で書き込み完了: {output_bom_path}")


# ============================================================
# 10. pathlib.Path の便利機能
# ============================================================
print("\n--- 10. pathlib.Path の便利機能 ---")

# pathlib は Python 3.4 で追加されたモダンなパス操作ライブラリ。
# os.path よりもオブジェクト指向的で直感的に使える。
#
# JS/TS の path モジュールとの対応:
#   path.join(a, b)      → Path(a) / b          （/ 演算子で結合）
#   path.basename(p)     → Path(p).name         （ファイル名）
#   path.dirname(p)      → Path(p).parent       （親ディレクトリ）
#   path.extname(p)      → Path(p).suffix       （拡張子）
#   path.resolve(p)      → Path(p).resolve()    （絶対パス）
#   fs.existsSync(p)     → Path(p).exists()     （存在チェック）
#   fs.statSync(p).isFile → Path(p).is_file()   （ファイルか？）

sample_path = DATA_DIR / "sample.csv"

print(f"  ファイル名:       {sample_path.name}")        # sample.csv
print(f"  拡張子:           {sample_path.suffix}")      # .csv
print(f"  拡張子なしの名前: {sample_path.stem}")        # sample
print(f"  親ディレクトリ:   {sample_path.parent}")      # .../data
print(f"  絶対パス:         {sample_path.resolve()}")   # フルパス
print(f"  存在するか:       {sample_path.exists()}")    # True
print(f"  ファイルか:       {sample_path.is_file()}")   # True
print(f"  ディレクトリか:   {sample_path.is_dir()}")    # False

# glob() でファイル検索（JS/TS の glob パッケージに相当）
print("\n  data/ 内の CSV ファイル一覧:")
for csv_file in DATA_DIR.glob("*.csv"):
    print(f"    {csv_file.name}")

# output/ 内の全ファイル一覧
print("\n  output/ 内の全ファイル一覧:")
for out_file in sorted(OUTPUT_DIR.iterdir()):
    # stat() でファイルサイズを取得
    size = out_file.stat().st_size
    print(f"    {out_file.name} ({size} bytes)")


# ============================================================
# 11. os.path vs pathlib の比較
# ============================================================
print("\n--- 11. os.path vs pathlib の比較 ---")

# os.path は古い（Python 2 時代からある）API。文字列ベースで操作する。
# pathlib は新しい（Python 3.4+）API。Path オブジェクトで操作する。
# 新しいコードでは pathlib を使うのがおすすめ！

file_path_str = str(sample_path)  # 文字列に変換

# ---- os.path (旧式) ----
print("  [os.path (旧式)]")
print(f"    結合:     {os.path.join('data', 'sample.csv')}")
print(f"    ファイル名: {os.path.basename(file_path_str)}")
print(f"    親Dir:    {os.path.dirname(file_path_str)}")
print(f"    拡張子:   {os.path.splitext(file_path_str)}")  # ('...sample', '.csv')
print(f"    存在:     {os.path.exists(file_path_str)}")
print(f"    絶対パス: {os.path.abspath(file_path_str)}")

# ---- pathlib (新式) ----
print("  [pathlib (新式) ← こちらを使おう！]")
print(f"    結合:     {Path('data') / 'sample.csv'}")
print(f"    ファイル名: {sample_path.name}")
print(f"    親Dir:    {sample_path.parent}")
print(f"    拡張子:   {sample_path.suffix}")
print(f"    存在:     {sample_path.exists()}")
print(f"    絶対パス: {sample_path.resolve()}")

# pathlib ならではの便利メソッド
print("\n  pathlib ならではの機能:")

# read_text() / write_text() ― open/close を省略できる簡易メソッド
# 小さなファイルならこれで十分！
quick_path = OUTPUT_DIR / "quick.txt"
quick_path.write_text("pathlib で簡単書き込み！\n", encoding="utf-8")
quick_content = quick_path.read_text(encoding="utf-8")
print(f"    read_text(): {quick_content.rstrip()}")

# with_suffix() ― 拡張子を変更した新しい Path を返す
json_path = sample_path.with_suffix(".json")
print(f"    with_suffix('.json'): {json_path.name}")  # sample.json

# with_stem() ― ファイル名（拡張子なし）を変更 (Python 3.9+)
backup_path = sample_path.with_stem("sample_backup")
print(f"    with_stem('sample_backup'): {backup_path.name}")  # sample_backup.csv


# ============================================================
# 12. まとめ
# ============================================================
print("\n" + "=" * 60)
print("まとめ")
print("=" * 60)
print("""
  1. open() でファイルを開き、with 文で安全に閉じる
  2. モード: 'r'(読み取り), 'w'(上書き), 'a'(追記)
  3. csv.reader / csv.writer → リスト形式の CSV 処理
  4. csv.DictReader / csv.DictWriter → 辞書形式の CSV 処理
  5. encoding='utf-8' / 'shift_jis' / 'utf-8-sig' で文字コード指定
  6. pathlib.Path を使えばパス操作がシンプルに書ける
  7. newline='' は Windows での CSV 書き込みで必須！

  生成されたファイル:
""")

for out_file in sorted(OUTPUT_DIR.iterdir()):
    print(f"    {out_file}")

print()
