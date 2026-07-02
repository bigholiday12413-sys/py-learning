"""
practice_errors.py - わざとエラーを起こして「読み方」を練習する

使い方:
    python practice_errors.py       # エラー一覧を表示
    python practice_errors.py 3     # 3番のエラーを実際に発生させる

各エラーを発生させたら、表示されたトレースバックを
「最後の行 → その1つ上の File/line」の順で読む練習をすること。
（読み方の解説は README.md にある）
"""

import sys


# ============================================================
# エラーを発生させる関数たち
# ============================================================
# それぞれの関数の中に「なぜエラーになるか」「どう直すか」を
# コメントで書いてある。まず実行してトレースバックを読み、
# その後にコメントの答え合わせをするのがおすすめ。


def error_01_name():
    """NameError: 存在しない名前を使った"""
    message = "こんにちは"
    print(mesage)  # ← "message" のタイプミス
    # 直し方: 変数名を正しく書く → print(message)
    # トレースバックには「'mesage' is not defined」と
    # どの名前が見つからないかが表示される


def error_02_type():
    """TypeError: 型が合わない演算をした"""
    age = input_mock()      # input() は常に「文字列」を返す（Lv01参照）
    print(age + 1)          # ← 文字列 + 数値 はエラー
    # 直し方: int() で数値に変換する → int(age) + 1


def input_mock():
    """input() の代わり（練習用に固定値を返す）"""
    return "25"  # 数字に見えるが str 型


def error_03_value():
    """ValueError: 型は合うが値が不正"""
    number = int("abc")  # ← "abc" は数値に変換できない
    # 直し方: 変換できない可能性がある入力は try/except ValueError で囲む（Lv01参照）


def error_04_key():
    """KeyError: 辞書にそのキーがない"""
    profile = {"name": "太郎", "age": 25}
    print(profile["adress"])  # ← "address" のタイプミス（しかも元のキーにも無い）
    # 直し方1: 正しいキー名を使う
    # 直し方2: profile.get("address") なら無くても None が返りエラーにならない


def error_05_index():
    """IndexError: リストにその番号の要素がない"""
    items = ["a", "b", "c"]  # 番号は 0, 1, 2 まで
    print(items[3])          # ← 3番は存在しない
    # 直し方: len(items) で長さを確認する。最後の要素なら items[-1]


def error_06_attribute():
    """AttributeError: その属性・メソッドは存在しない"""
    name = "python"
    print(name.upperr())  # ← "upper" のタイプミス
    # 直し方: 正しいメソッド名にする → name.upper()
    # ※ 「'NoneType' object has no attribute ...」と出た場合は、
    #    変数が None になっている（関数が値を返していない等）のが原因。頻出！


def error_07_zero_division():
    """ZeroDivisionError: 0で割った"""
    scores = []                        # 空のリスト
    average = sum(scores) / len(scores)  # ← len が 0 なので 0除算
    # 直し方: 空かどうか先にチェックする
    #   if scores:
    #       average = sum(scores) / len(scores)


def error_08_file_not_found():
    """FileNotFoundError: ファイルが見つからない"""
    with open("sonzai_shinai.csv", encoding="utf-8") as f:  # ← 存在しないファイル
        print(f.read())
    # 直し方: パスを確認する。実行場所によって相対パスの基準が変わるので、
    #   Path(__file__).parent を基準に組み立てるのが安全（Lv02参照）


def error_09_module_not_found():
    """ModuleNotFoundError: ライブラリが見つからない"""
    import sonzaishinai_library  # ← インストールしていないライブラリ
    # 直し方: pip install <ライブラリ名>
    # ※ インストールしたはずなのに出る場合は「venvの有効化忘れ」を疑う（頻出！）
    #   プロンプトに (venv) が表示されているか確認すること


def error_10_indentation():
    """IndentationError: インデントがおかしい（このファイルの一番下を参照）"""
    print("このエラーは実行前（読み込み時）に発生するタイプ。")
    print("practice_errors.py の末尾のコメントを外して再実行すると体験できる。")
    print("SyntaxError / IndentationError は『どの行を実行したか』に関係なく、")
    print("ファイルを読み込んだ瞬間に発生するのが特徴。")


# ============================================================
# メニュー表示と実行
# ============================================================

ERRORS = {
    "1": ("NameError（名前のタイプミス）", error_01_name),
    "2": ("TypeError（文字列 + 数値）", error_02_type),
    "3": ("ValueError（int('abc')）", error_03_value),
    "4": ("KeyError（辞書のキー間違い）", error_04_key),
    "5": ("IndexError（リストの範囲外）", error_05_index),
    "6": ("AttributeError（メソッド名間違い）", error_06_attribute),
    "7": ("ZeroDivisionError（空リストの平均）", error_07_zero_division),
    "8": ("FileNotFoundError（ファイルなし）", error_08_file_not_found),
    "9": ("ModuleNotFoundError（ライブラリなし）", error_09_module_not_found),
    "10": ("IndentationError（説明のみ）", error_10_indentation),
}


def show_menu():
    print("=" * 60)
    print("  エラー体験メニュー")
    print("=" * 60)
    for num, (label, _) in ERRORS.items():
        print(f"  {num:>2}: {label}")
    print()
    print("使い方: python practice_errors.py <番号>")
    print("例:     python practice_errors.py 1")
    print()
    print("エラーが表示されたら:")
    print("  1. 一番下の行（エラーの種類と説明）を読む")
    print("  2. その上の File \"...\", line N で場所を特定する")
    print("  3. この練習ファイルの該当関数のコメントで答え合わせする")


if __name__ == "__main__":
    # コマンドライン引数: sys.argv はコマンドの単語リスト
    # 例: python practice_errors.py 3 → sys.argv は ["practice_errors.py", "3"]
    if len(sys.argv) < 2:
        show_menu()
    else:
        choice = sys.argv[1]
        if choice in ERRORS:
            label, func = ERRORS[choice]
            print(f">>> {label} を発生させます。トレースバックを読んでみよう！\n")
            func()  # ← ここでエラーが発生する（わざと try/except で囲んでいない）
        else:
            print(f"番号 {choice} はありません。1〜10 を指定してください。")
            show_menu()


# ============================================================
# IndentationError 体験用（10番の説明を読んでから）
# ============================================================
# 以下の2行の「#」を外して保存し、python practice_errors.py を実行すると、
# メニューすら表示されずに IndentationError になることを確認できる。
#
# def broken():
#         print("インデントが")
#     print("揃っていない")   # ← 上の行とスペースの数が違う
