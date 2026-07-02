"""
Lv01 - Hello Python: はじめての Python
=======================================
Python の基本文法を一通り体験するプログラム。
前提知識は不要。各セクションに日本語の解説コメントを付けている。

実行: python main.py
"""

# ============================================================
# 0. セクション区切り用のヘルパー
# ============================================================


def section(title: str) -> None:
    """セクションタイトルを見やすく表示するだけのユーティリティ"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ============================================================
# 1. 変数 ─ 「名前 = 値」と書くだけ
# ============================================================
# Python の変数は「名前 = 値」と書くだけで作れる。
#
# - 宣言のためのキーワードは不要
# - 行末のセミコロン(;)も不要
# - 同じ名前に再代入すれば値を上書きできる
# - 慣習として「定数のつもりの値」は UPPER_SNAKE_CASE で書く
#   （ただし言語レベルで書き換えを禁止する仕組みはない）

section("1. 変数（Variables）")

# --- 文字列 (str) ─ テキストを扱う型。"..." または '...' で囲む ---
name: str = "Python太郎"  # 「: str」は型ヒント（後述）。付けなくても動く

# --- 整数 (int) ─ 小数点のない数値 ---
age: int = 25

# --- 浮動小数点 (float) ─ 小数点のある数値。int とは別の型 ---
height: float = 170.5

# --- 真偽値 (bool) ─ True / False の2値。先頭が大文字なのに注意！ ---
is_student: bool = True

# --- None ─ 「値がない」ことを表す特別な値 ---
nickname = None  # type: str | None  # Python 3.10+ の Union 記法

print(f"name     = {name}       (型: {type(name).__name__})")
print(f"age      = {age}            (型: {type(age).__name__})")
print(f"height   = {height}        (型: {type(height).__name__})")
print(f"is_student = {is_student}        (型: {type(is_student).__name__})")
print(f"nickname = {nickname}        (型: {type(nickname).__name__})")

# type() を使うと、その値がどの型なのかを確認できる


# ============================================================
# 2. f-string ─ 文字列に値を埋め込む
# ============================================================
# 文字列の先頭に f を付けると、{} の中に変数や式を埋め込める。
#   f"こんにちは、{name}さん！"
#
# - {} 内には変数だけでなく計算式や関数呼び出しも書ける
# - Python で文字列を組み立てるときの第一選択

section("2. f-string（文字列に値を埋め込む）")

greeting = f"こんにちは、{name}さん！ {age}歳ですね。"
print(greeting)

# {} の中に式も書ける
print(f"来年は {age + 1} 歳です。")
print(f"名前の文字数: {len(name)} 文字")  # len() は文字列やリストの長さを返す組み込み関数


# ============================================================
# 3. リスト (list) ─ 複数の値を順番に並べて持つ
# ============================================================
# リストは複数の値を順番付きで格納するデータ構造。[] で作る。
#
# - 先頭の要素は langs[0]（番号は 0 から始まる）
# - 負の番号で後ろから数えられる: langs[-1] は最後の要素
# - スライス記法 langs[1:3] で一部分を切り出せる

section("3. リスト（list）")

langs: list[str] = ["Python", "SQL", "HTML"]

print(f"好きな言語: {langs}")
print(f"最初の要素: {langs[0]}")         # 0番目 = 先頭
print(f"最後の要素: {langs[-1]}")        # -1 は「後ろから1番目」
print(f"スライス [0:2]: {langs[0:2]}")   # 0番目から2番目の手前まで（0と1）

# 要素追加は .append()
langs.append("Go")
print(f"append 後: {langs}")

# 要素が含まれるかは in 演算子で調べる
print(f"'Python' in langs = {'Python' in langs}")

# リスト内包表記 ─ 「各要素を変換した新しいリスト」を1行で作る記法
#   [変換式 for 変数 in リスト]
upper_langs = [lang.upper() for lang in langs]  # .upper() は大文字化
print(f"大文字化: {upper_langs}")

# 条件付き内包表記 ─ if を付けると「条件を満たす要素だけ」を対象にできる
#   [変換式 for 変数 in リスト if 条件]
long_langs = [lang.upper() for lang in langs if len(lang) > 4]
print(f"5文字以上を大文字化: {long_langs}")


# ============================================================
# 4. 辞書 (dict) ─ キーと値のペアで持つ
# ============================================================
# 辞書は「キー: 値」のペアを格納するデータ構造。{} で作る。
#   profile = {"name": "Taro", "age": 25}
#
# - 値の取り出しは profile["name"]
# - profile.get("name") ならキーが無くてもエラーにならず None が返る
# - キーは文字列に限らず、数値なども使える

section("4. 辞書（dict）")

profile: dict[str, str | int | list[str]] = {
    "name": name,
    "age": age,
    "langs": langs,
}

print(f"プロフィール: {profile}")
print(f"名前: {profile['name']}")         # [] でアクセス。キーが無いと KeyError になる
print(f"年齢: {profile.get('age')}")      # .get() はキーが無くても None を返す安全なアクセス

# キーの存在チェックも in 演算子
print(f"'name' in profile = {'name' in profile}")

# キーと値を同時にループするには .items() を使う
print("--- 辞書の中身を展開 ---")
for key, value in profile.items():
    print(f"  {key}: {value}")


# ============================================================
# 5. 関数 ─ def と lambda
# ============================================================
# 関数は def で定義する。
#   def 関数名(引数):
#       処理
#       return 戻り値
#
# - ブロックは {} ではなくインデント（半角スペース4つ）で表す
# - return を省略すると None が返る
# - 引数にはデフォルト値を設定できる

section("5. 関数（def / lambda）")


def greet(target_name: str, greeting: str = "こんにちは") -> str:
    """
    あいさつ関数。
    greeting には省略時のデフォルト値 "こんにちは" を設定している。
    def の直下に書くこの文字列は docstring といい、関数の説明を書く場所。
    """
    return f"{greeting}、{target_name}さん！"


print(greet("Alice"))                      # デフォルト引数を使用
print(greet("Bob", "おはよう"))             # 引数を指定
print(greet(greeting="やあ", target_name="Carol"))  # キーワード引数: 名前指定なら順番は自由

# --- lambda ─ 名前のない1行関数 ---
# lambda 引数: 式  という形で、その場で小さな関数を作れる。
# 1つの式しか書けないので、複数行のロジックは def を使う。
double = lambda x: x * 2  # noqa: E731 (学習用なので lint 警告を抑制)
print(f"double(5) = {double(5)}")

# --- 複数の戻り値 ---
# return a, b のようにカンマで並べると複数の値をまとめて返せる（実体はタプル）。
# 受け取る側も lo, hi = ... と書いて一度に受け取れる。


def min_max(numbers: list[int]) -> tuple[int, int]:
    """リストの最小値と最大値を返す"""
    return min(numbers), max(numbers)


lo, hi = min_max([3, 1, 4, 1, 5, 9, 2, 6])
print(f"min_max: 最小={lo}, 最大={hi}")


# ============================================================
# 6. 条件分岐 ─ if / elif / else
# ============================================================
#   if 条件:
#       処理
#   elif 別の条件:
#       処理
#   else:
#       処理
#
# - 条件に括弧 () は不要（付けてもエラーにはならない）
# - ブロックはインデントで表す。行末のコロン(:)を忘れずに
# - 値の比較は ==（等しい）と !=（等しくない）
# - None かどうかのチェックは == ではなく is None と書くのが慣習

section("6. 条件分岐（if / elif / else）")


def check_age(target_age: int) -> str:
    """年齢に応じたメッセージを返す"""
    if target_age < 0:
        return "不正な年齢です"
    elif target_age < 13:
        return "子供です"
    elif target_age < 20:
        return "ティーンエイジャーです"
    elif target_age < 65:
        return "大人です"
    else:
        return "シニアです"


test_ages = [5, 15, 25, 70]
for a in test_ages:
    print(f"  {a}歳 → {check_age(a)}")

# --- 条件式（1行で書く if/else）---
#   値A if 条件 else 値B
# 「条件が真なら値A、偽なら値B」を1行で書ける。
status = "成人" if age >= 20 else "未成年"
print(f"\n{name}さん({age}歳)は {status} です。")

# --- None チェック ---
# None との比較は is を使う（== でも動くことが多いが is が正式な慣習）
if nickname is None:
    print("ニックネームは未設定です (None)")


# ============================================================
# 7. ループ ─ for / while
# ============================================================
# ■ for ループ
#   for 変数 in リストなど:
#       処理
# リストや文字列などの「繰り返せるもの」から1つずつ取り出して処理する。
#
# ■ while ループ
#   while 条件:
#       処理
# 条件が真の間ずっと繰り返す。break で途中終了、continue で次の周回へ。

section("7. ループ（for / while）")

# --- for ... in ---
print("--- for ... in ---")
for lang in langs:
    print(f"  言語: {lang}")

# --- range() ─ 連続した数値の並びを作る ---
# 「N回繰り返したい」ときは range() と組み合わせる。
# range(5)        → 0, 1, 2, 3, 4
# range(1, 6)     → 1, 2, 3, 4, 5
# range(0, 10, 2) → 0, 2, 4, 6, 8
print("\n--- range(5) ---")
for i in range(5):
    print(f"  i = {i}")

# --- enumerate() ─ 番号付きでループする ---
# 要素と同時に「何番目か」も欲しいときに使う。
print("\n--- enumerate() ---")
for i, lang in enumerate(langs):
    print(f"  {i}: {lang}")

# --- while ループ ---
print("\n--- while ループ ---")
count = 3
while count > 0:
    print(f"  カウントダウン: {count}")
    count -= 1  # count = count - 1 の省略形。count-- という書き方は無い
print("  発射！")


# ============================================================
# 8. Truthy / Falsy ─ if に「真偽値以外」を渡すとどうなるか
# ============================================================
# if の条件には True/False 以外の値も書ける。
# そのとき「偽(falsy)」と判定されるのは以下のような「空」を表す値:
#   False, None, 0, 0.0, ""(空文字列), [](空リスト), {}(空辞書), set()
# それ以外はすべて「真(truthy)」。
#
# 例: if my_list: は「リストに中身があれば」という意味になる。

section("8. Truthy / Falsy")

test_values = [
    ("True", True),
    ("False", False),
    ("1", 1),
    ("0", 0),
    ("''（空文字列）", ""),
    ("'hello'", "hello"),
    ("[]（空リスト）", []),
    ("[1, 2]", [1, 2]),
    ("{}（空辞書）", {}),
    ("None", None),
]

for label, val in test_values:
    # bool() で truthy/falsy を確認できる
    result = "truthy" if val else "falsy"
    print(f"  {label:20s} → {result}")

print()
print("  ※ ポイント: 「空っぽ」を表す値はすべて falsy になる")


# ============================================================
# 9. 型ヒント (Type Hints) ─ 型をコードに書き残す
# ============================================================
#   def add(a: int, b: int) -> int:
# のように、引数や戻り値の型をコードに書いておける機能。
#
# - 実行時にはチェックされない（違う型を渡してもエラーにならない）
# - エディタの補完や、静的解析ツール (mypy, pyright) での型チェックに役立つ
# - 変数にも付けられる: name: str = "Taro"
# - 付けなくても動くが、読みやすさのため本コースでは積極的に使う

section("9. 型ヒント（Type Hints）")


def add(a: int, b: int) -> int:
    """二つの数を足す"""
    return a + b


def concat_items(items: list[str], separator: str = ", ") -> str:
    """リストの要素を区切り文字でつないで1つの文字列にする"""
    return separator.join(items)


# 「str または None」のように複数の型を許す場合は | でつなぐ (Python 3.10+)
def find_lang(langs_list: list[str], query: str) -> str | None:
    """リストから言語を検索する。見つからなければ None を返す。"""
    for lang in langs_list:
        if lang.lower() == query.lower():
            return lang
    return None


print(f"add(3, 5) = {add(3, 5)}")
print(f"concat_items: {concat_items(langs)}")
print(f"find_lang('python'): {find_lang(langs, 'python')}")
print(f"find_lang('rust'):   {find_lang(langs, 'rust')}")


# ============================================================
# 10. print フォーマット ─ 画面への出力いろいろ
# ============================================================
# print() は画面に文字を出力する組み込み関数。
# 出力の組み立て方にはいくつかの方法がある。

section("10. print フォーマット")

# 方法1: f-string（推奨）
print(f"[f-string]   名前: {name}, 年齢: {age}")

# 方法2: カンマ区切り（自動でスペースが入る）
print("[カンマ区切り]", "名前:", name, "年齢:", age)

# 方法3: .format() メソッド（f-string 登場前の主流。古いコードで見かける）
print("[.format()]   名前: {}, 年齢: {}".format(name, age))

# 数値のフォーマット ─ {値:書式} の形で桁数などを指定できる
pi = 3.141592653589793
print(f"\n円周率: {pi}")
print(f"  小数点2桁: {pi:.2f}")       # 3.14
print(f"  小数点4桁: {pi:.4f}")       # 3.1416
print(f"  パーセント: {0.856:.1%}")   # 85.6%
print(f"  カンマ区切り: {1234567:,}") # 1,234,567

# end / sep パラメータ
# print() は通常、最後に改行を付けるが、end で変更できる
print("\n  カウント:", end=" ")        # 改行しない
for i in range(1, 6):
    print(i, end=" ")
print("(end=' ' で改行を抑制)")

print("  ハイフン区切り:", "A", "B", "C", sep="-")  # sep でセパレータ変更


# ============================================================
# 11. インタラクティブ: 自己紹介プログラム
# ============================================================
# input("メッセージ") でユーザーのキーボード入力を受け取れる。
# 戻り値は常に文字列(str)なので、数値が欲しければ int() で変換する。

section("11. 自己紹介プログラム（対話型）")

print("あなたの情報を入力してください。")
print("（そのまま Enter を押すとデフォルト値が使われます）")
print()

# 「x or デフォルト値」は「x が空ならデフォルト値を使う」という定番パターン
# （空文字列は falsy なので、未入力のとき右側の値が採用される）
user_name = input("  お名前: ") or "名無しさん"

# 数値入力は int() / float() で変換
age_input = input("  年齢: ") or "20"
try:
    # int() は数値に変換できない文字列を渡すと ValueError を発生させる。
    # try/except で囲むと、エラーが起きてもプログラムを止めずに対処できる。
    user_age = int(age_input)
except ValueError:
    print("  ※ 数値に変換できなかったので 20 にします")
    user_age = 20

lang_input = input("  好きなプログラミング言語（カンマ区切り）: ") or "Python"
# .split(",") で文字列をカンマで分割してリストにし、
# .strip() で各要素の前後の空白を取り除く
user_langs = [s.strip() for s in lang_input.split(",")]

print()
print("=" * 40)
print("  ★ あなたの自己紹介カード ★")
print("=" * 40)
print(f"  名前:   {user_name}")
print(f"  年齢:   {user_age}歳 ({check_age(user_age)})")
print(f"  言語:   {', '.join(user_langs)}")
print(f"  言語数: {len(user_langs)}個")

if len(user_langs) >= 3:
    print("  → たくさんの言語を知っていますね！")
elif len(user_langs) == 1:
    print(f"  → {user_langs[0]} が好きなんですね！")
else:
    print("  → いい組み合わせですね！")

print("=" * 40)

# ============================================================
# まとめ
# ============================================================

section("まとめ: Python 基本文法チートシート")

summary = """
  やりたいこと                    書き方
  ─────────────────────────────  ─────────────────────────
  変数を作る                     name = "Taro"
  画面に出力                     print(name)
  文字列に値を埋め込む           f"Hello {name}"
  リストを作る                   items = [1, 2, 3]
  リストに追加                   items.append(4)
  含まれるか調べる               x in items
  長さを調べる                   len(items)
  辞書を作る                     d = {"key": value}
  辞書から取り出す               d["key"] / d.get("key")
  関数を定義                     def f(x):
  名前のない1行関数              lambda x: x * 2
  条件分岐                       if / elif / else
  1行 if/else                    a if 条件 else b
  リストをループ                 for x in items:
  N回ループ                      for i in range(n):
  型を調べる                     type(x)
  エラー処理                     try / except
  文字列→数値                    int("123")
  キーボード入力                 input("名前: ")
"""

print(summary)
print("お疲れさまでした！ 次は Lv02 へ進みましょう。")
