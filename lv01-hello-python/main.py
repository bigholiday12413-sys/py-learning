"""
Lv01 - Hello Python: はじめての Python
=======================================
JS/TS 経験者向けに、Python の基本文法を一通り紹介するプログラム。
各セクションに JS/TS との比較コメントを付けている。

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
# 1. 変数 ─ const / let は不要
# ============================================================
# JS:  const name = "Taro";   let age = 25;
# Py:  name = "Taro"          age = 25
#
# - Python には const / let / var のようなキーワードがない
# - セミコロン(;)も不要
# - 慣習として「定数」は UPPER_SNAKE_CASE で書く（ただし言語レベルの制約はない）

section("1. 変数（Variables）")

# --- 文字列 (str) ─ JS の string と同じ ---
name: str = "Python太郎"  # 型ヒント付き（後述）

# --- 整数 (int) ─ JS の number に相当するが、整数と小数が別の型 ---
age: int = 25

# --- 浮動小数点 (float) ─ JS の number ---
height: float = 170.5

# --- 真偽値 (bool) ─ JS: true/false → Py: True/False（先頭大文字！） ---
is_student: bool = True

# --- None ─ JS の null に相当。undefined は Python に存在しない ---
nickname = None  # type: str | None  # Python 3.10+ の Union 記法

print(f"name     = {name}       (型: {type(name).__name__})")
print(f"age      = {age}            (型: {type(age).__name__})")
print(f"height   = {height}        (型: {type(height).__name__})")
print(f"is_student = {is_student}        (型: {type(is_student).__name__})")
print(f"nickname = {nickname}        (型: {type(nickname).__name__})")

# type() で型を確認できる ─ JS の typeof に相当


# ============================================================
# 2. f-string ─ テンプレートリテラル
# ============================================================
# JS:  `こんにちは、${name}さん！ ${age}歳ですね。`
# Py:  f"こんにちは、{name}さん！ {age}歳ですね。"
#
# - 先頭に f を付けるだけ。バッククォート不要
# - {} 内で式も書ける

section("2. f-string（テンプレートリテラル）")

greeting = f"こんにちは、{name}さん！ {age}歳ですね。"
print(greeting)

# 式を埋め込める（JS と同じ）
print(f"来年は {age + 1} 歳です。")
print(f"名前の文字数: {len(name)} 文字")  # len() は JS の .length に相当


# ============================================================
# 3. リスト (list) ─ JS の配列
# ============================================================
# JS:  const langs = ["JS", "TS", "Python"];
# Py:  langs = ["JS", "TS", "Python"]
#
# - ほぼ同じ書き方
# - ただし push() → append()、includes() → in 演算子
# - スライス記法 langs[1:3] が強力（JS にはない）

section("3. リスト（list = JS の配列）")

langs: list[str] = ["JavaScript", "TypeScript", "Python"]

print(f"好きな言語: {langs}")
print(f"最初の要素: {langs[0]}")         # JS と同じ
print(f"最後の要素: {langs[-1]}")        # JS: langs[langs.length - 1] → Py: langs[-1]
print(f"スライス [0:2]: {langs[0:2]}")   # JS にはないスライス記法

# 要素追加
# JS:  langs.push("Go")
# Py:  langs.append("Go")
langs.append("Go")
print(f"append 後: {langs}")

# 要素が含まれるか
# JS:  langs.includes("Python")
# Py:  "Python" in langs
print(f"'Python' in langs = {'Python' in langs}")

# リスト内包表記 ─ JS の .map() に相当する強力な記法
# JS:  langs.map(l => l.toUpperCase())
# Py:  [l.upper() for l in langs]
upper_langs = [lang.upper() for lang in langs]
print(f"大文字化: {upper_langs}")

# フィルタ付き内包表記 ─ JS の .filter().map()
# JS:  langs.filter(l => l.length > 4).map(l => l.toUpperCase())
# Py:  [l.upper() for l in langs if len(l) > 4]
long_langs = [lang.upper() for lang in langs if len(lang) > 4]
print(f"5文字以上を大文字化: {long_langs}")


# ============================================================
# 4. 辞書 (dict) ─ JS のオブジェクト / Map
# ============================================================
# JS:  const profile = { name: "Taro", age: 25 };
# Py:  profile = { "name": "Taro", "age": 25 }
#
# - キーは必ずクォートが必要（JS はなくてもOKだった）
# - アクセスは profile["name"] または profile.get("name")
# - JS の profile.name のようなドットアクセスはできない

section("4. 辞書（dict = JS のオブジェクト）")

profile: dict[str, str | int | list[str]] = {
    "name": name,
    "age": age,
    "langs": langs,
}

print(f"プロフィール: {profile}")
print(f"名前: {profile['name']}")         # JS: profile.name
print(f"年齢: {profile.get('age')}")      # .get() は KeyError を出さない安全なアクセス

# キーの存在チェック
# JS:  "name" in profile  (← 実は JS も in 使える！)
# Py:  "name" in profile
print(f"'name' in profile = {'name' in profile}")

# キーと値のループ
# JS:  Object.entries(profile).forEach(([k, v]) => ...)
# Py:  for k, v in profile.items():
print("--- 辞書の中身を展開 ---")
for key, value in profile.items():
    print(f"  {key}: {value}")


# ============================================================
# 5. 関数 ─ def と lambda
# ============================================================
# JS:  function greet(name) { return `Hello, ${name}`; }
# Py:  def greet(name): return f"Hello, {name}"
#
# - ブレース {} ではなくインデント（半角スペース4つ）でブロックを表す
# - return を省略すると None が返る（JS の undefined に相当）
# - デフォルト引数は JS と同じ感覚で使える

section("5. 関数（def / lambda）")


def greet(target_name: str, greeting: str = "こんにちは") -> str:
    """
    あいさつ関数。
    JS/TS で書くなら:
      function greet(targetName: string, greeting: string = "こんにちは"): string {
          return `${greeting}、${targetName}さん！`;
      }
    """
    return f"{greeting}、{target_name}さん！"


print(greet("Alice"))                      # デフォルト引数を使用
print(greet("Bob", "おはよう"))             # 引数を指定
print(greet(greeting="やあ", target_name="Carol"))  # キーワード引数（JS にはない！）

# --- lambda ─ JS のアロー関数の超簡易版 ---
# JS:  const double = (x) => x * 2;
# Py:  double = lambda x: x * 2
#
# lambda は1式しか書けない。複数行のロジックは def を使う。
double = lambda x: x * 2  # noqa: E731 (学習用なので lint 警告を抑制)
print(f"double(5) = {double(5)}")

# --- 複数の戻り値 ─ JS にはない Python の便利機能 ---
# JS ではオブジェクトや配列で返すが、Python はタプルで直接返せる


def min_max(numbers: list[int]) -> tuple[int, int]:
    """リストの最小値と最大値を返す"""
    return min(numbers), max(numbers)


lo, hi = min_max([3, 1, 4, 1, 5, 9, 2, 6])
print(f"min_max: 最小={lo}, 最大={hi}")


# ============================================================
# 6. 条件分岐 ─ if / elif / else
# ============================================================
# JS:  if (x > 0) { ... } else if (x === 0) { ... } else { ... }
# Py:  if x > 0: ...  elif x == 0: ...  else: ...
#
# - 括弧 () は不要（付けてもエラーにはならない）
# - ブレース {} ではなくインデントでブロックを示す
# - else if → elif
# - === は存在しない。== は値の等価比較（JS の === に近い）
# - 厳密な同一性チェックは is を使う（None のチェックで多用）

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

# --- 三項演算子 ---
# JS:  const msg = age >= 20 ? "成人" : "未成年";
# Py:  msg = "成人" if age >= 20 else "未成年"
#      ↑ 順番が違うので注意！
status = "成人" if age >= 20 else "未成年"
print(f"\n{name}さん({age}歳)は {status} です。")

# --- None チェック ---
# JS:  if (nickname === null) { ... }
# Py:  if nickname is None: ...   ← == ではなく is を使うのが慣習
if nickname is None:
    print("ニックネームは未設定です (None)")


# ============================================================
# 7. ループ ─ for / while
# ============================================================
# ■ for ループ
# JS:  for (const lang of langs) { ... }     ← for...of
# Py:  for lang in langs: ...
#
# JS:  for (let i = 0; i < 5; i++) { ... }   ← C-style for
# Py:  for i in range(5): ...                ← range() を使う
#
# ■ while ループ
# JS と同じ感覚。break / continue も使える。

section("7. ループ（for / while）")

# --- for ... in ---
print("--- for ... in ---")
for lang in langs:
    print(f"  言語: {lang}")

# --- range() ─ JS にはない便利な関数 ---
# range(5)       → 0, 1, 2, 3, 4
# range(1, 6)    → 1, 2, 3, 4, 5
# range(0, 10, 2) → 0, 2, 4, 6, 8
print("\n--- range(5) ---")
for i in range(5):
    print(f"  i = {i}")

# --- enumerate() ─ JS の forEach((item, index) => ...) に相当 ---
# JS:  langs.forEach((lang, i) => console.log(`${i}: ${lang}`));
# Py:  for i, lang in enumerate(langs):
print("\n--- enumerate() ---")
for i, lang in enumerate(langs):
    print(f"  {i}: {lang}")

# --- while ループ ---
print("\n--- while ループ ---")
count = 3
while count > 0:
    print(f"  カウントダウン: {count}")
    count -= 1  # Py には count-- がない！ -= 1 を使う
print("  発射！")


# ============================================================
# 8. Truthy / Falsy ─ JS よりシンプル
# ============================================================
# JS の falsy: false, 0, "", null, undefined, NaN (6つ)
# Py の falsy: False, None, 0, 0.0, "", [], {}, set() など「空」のもの
#
# JS と違って:
# - 空の配列 [] は JS では truthy だが、Python では falsy！
# - 空のオブジェクト {} も JS では truthy だが、Python では falsy！

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
print("  ※ 注意: JS では [] と {{}} は truthy だが、Python では falsy！")


# ============================================================
# 9. 型ヒント (Type Hints) ─ TypeScript の型注釈
# ============================================================
# JS/TS:  function add(a: number, b: number): number { return a + b; }
# Py:     def add(a: int, b: int) -> int: return a + b
#
# - Python の型ヒントは実行時に無視される（TypeScript の型と同じ）
# - 静的解析ツール (mypy, pyright) で型チェックできる
# - 変数にも付けられる: name: str = "Taro"

section("9. 型ヒント（Type Hints）")


def add(a: int, b: int) -> int:
    """二つの数を足す"""
    return a + b


def concat_items(items: list[str], separator: str = ", ") -> str:
    """リストの要素を連結する ─ JS の .join() と同じ"""
    return separator.join(items)


# Optional 的な型 ─ TS: string | null → Py: str | None (Python 3.10+)
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
# 10. print フォーマット ─ console.log の代わり
# ============================================================
# JS:  console.log("名前:", name, "年齢:", age);
# Py:  print("名前:", name, "年齢:", age)     ← 同じ感覚で使える
#
# Python の print() は色々なフォーマット方法がある

section("10. print フォーマット")

# 方法1: f-string（推奨）
print(f"[f-string]   名前: {name}, 年齢: {age}")

# 方法2: カンマ区切り（自動でスペースが入る）
print("[カンマ区切り]", "名前:", name, "年齢:", age)

# 方法3: .format() メソッド（f-string 登場前の主流）
print("[.format()]   名前: {}, 年齢: {}".format(name, age))

# 数値のフォーマット
pi = 3.141592653589793
print(f"\n円周率: {pi}")
print(f"  小数点2桁: {pi:.2f}")       # 3.14
print(f"  小数点4桁: {pi:.4f}")       # 3.1416
print(f"  パーセント: {0.856:.1%}")   # 85.6%
print(f"  カンマ区切り: {1234567:,}") # 1,234,567

# end / sep パラメータ
# JS にはない、print() 固有の便利機能
print("\n  カウント:", end=" ")        # 改行しない
for i in range(1, 6):
    print(i, end=" ")
print("(end=' ' で改行を抑制)")

print("  ハイフン区切り:", "A", "B", "C", sep="-")  # sep でセパレータ変更


# ============================================================
# 11. インタラクティブ: 自己紹介プログラム
# ============================================================
# JS:  const name = prompt("名前は？");        ← ブラウザ
#      const name = await readline.question()  ← Node.js (readline)
# Py:  name = input("名前は？")               ← シンプル！

section("11. 自己紹介プログラム（対話型）")

print("あなたの情報を入力してください。")
print("（そのまま Enter を押すとデフォルト値が使われます）")
print()

# input() は常に文字列を返す ─ 数値が欲しい場合は int() や float() で変換
user_name = input("  お名前: ") or "名無しさん"  # or でデフォルト値（JS と同じパターン）

# 数値入力は int() / float() で変換
age_input = input("  年齢: ") or "20"
try:
    # JS: parseInt(ageInput) → Py: int(age_input)
    # エラー処理: JS の try/catch → Py の try/except
    user_age = int(age_input)
except ValueError:
    print("  ※ 数値に変換できなかったので 20 にします")
    user_age = 20

lang_input = input("  好きなプログラミング言語（カンマ区切り）: ") or "Python"
# JS:  langInput.split(",").map(s => s.trim())
# Py:  [s.strip() for s in lang_input.split(",")]
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

section("まとめ: JS/TS → Python 対応表")

summary = """
  JS/TS                          Python
  ─────────────────────────────  ─────────────────────────
  const / let / var              (なし。そのまま代入)
  true / false                   True / False
  null / undefined               None
  `Hello ${name}`                f"Hello {name}"
  array.push(x)                  list.append(x)
  array.includes(x)              x in list
  array.length                   len(list)
  { key: value }                 { "key": value }
  obj.key                        dict["key"] / dict.get("key")
  function f(x) {}               def f(x):
  (x) => x * 2                   lambda x: x * 2
  if / else if / else            if / elif / else
  for (const x of arr)           for x in arr
  x === y                        x == y
  x !== y                        x != y
  console.log()                  print()
  typeof x                       type(x)
  try / catch                    try / except
  parseInt("123")                int("123")
  x ? a : b                     a if x else b
"""

print(summary)
print("お疲れさまでした！ 次は Lv02 へ進みましょう。")
