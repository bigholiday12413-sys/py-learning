"""
utils.py - モジュール・デコレータ・可変長引数の学習

複数ファイルにコードを分割し、再利用する方法を学ぶ
"""

import functools
import time
from typing import Any, Callable


# ============================================================
# 1. モジュールとインポート
# ============================================================
# Python では「1つの .py ファイル = 1つのモジュール」。
# 他のファイルの関数やクラスは import で読み込んで使う。
#
# ポイント:
#   - export のような宣言は不要。ファイル内のすべてが自動的に公開される
#   - _ プレフィックスの名前は「内部用」の慣習（from module import * で除外される）
#   - __all__ リストで「公開するもの」を明示できる（★ベストプラクティス）
#
# インポートの書き方:
#   from models import Person          # 特定の名前だけ読み込む
#   from models import Person as P     # 別名を付けて読み込む
#   import models                      # モジュール全体を読み込む → models.Person
#   from models import *               # 全部読み込む（名前衝突しやすいので非推奨）
# ============================================================

# --- __all__: 公開するもの一覧 ---
# from utils import * した時にこのリストのものだけがインポートされる
__all__ = [
    "format_name",
    "log_call",
    "retry",
    "merge_dicts",
    "print_args_demo",
]


# ============================================================
# 2. *args と **kwargs（可変長引数）
# ============================================================
# 「引数がいくつ渡されるか分からない」関数を作るための仕組み。
#
#   - *args: 位置引数を何個でも受け取り、タプルにまとめる
#   - **kwargs: キーワード引数（name=値 の形）を何個でも受け取り、辞書にまとめる
#   - 両方同時に使える
#
# 逆方向にも使える（アンパック）:
#   f(*my_list)   … リストの中身を個別の引数として渡す
#   f(**my_dict)  … 辞書の中身をキーワード引数として渡す
# ============================================================

def print_args_demo(*args: Any, **kwargs: Any) -> None:
    """
    *args, **kwargs のデモ

    例: print_args_demo(1, "hello", x=10)
        → args = (1, "hello")、kwargs = {"x": 10}

    位置引数とキーワード引数が自動的に分かれて入ってくる。
    """
    print("--- *args, **kwargs デモ ---")

    # *args はタプル（変更できないリストのようなもの）
    print(f"  位置引数 (args): {args}")
    print(f"  args の型: {type(args)}")  # <class 'tuple'>

    # **kwargs は辞書
    print(f"  キーワード引数 (kwargs): {kwargs}")
    print(f"  kwargs の型: {type(kwargs)}")  # <class 'dict'>

    # kwargs の中身を展開
    for key, value in kwargs.items():
        print(f"    {key} = {value}")


def merge_dicts(*dicts: dict) -> dict:
    """
    複数の辞書をマージする

    後に渡した辞書の値が優先される（同じキーは上書き）。

    参考: Python 3.9+ では | 演算子でも書ける: dict1 | dict2
          ** 演算子によるアンパックでも書ける: {**dict1, **dict2}
    """
    result: dict = {}
    for d in dicts:
        # .update() は辞書に別の辞書の中身を取り込む（同じキーは上書き）
        result.update(d)
    return result


# ============================================================
# 3. デコレータ
# ============================================================
# デコレータ = 「関数を受け取って、機能を追加した新しい関数を返す」仕組み。
# 関数定義の直前に @デコレータ名 と書くだけで適用できる。
#
#   @log_call
#   def my_function(x, y):
#       return x + y
#
# は、以下と同じ意味:
#
#   def my_function(x, y):
#       return x + y
#   my_function = log_call(my_function)   # 関数を包み替えている
#
# 「ログ出力」「リトライ」「実行時間計測」のような、
# 多くの関数に共通して付けたい処理を1か所にまとめられる。
# ============================================================

def log_call(func: Callable) -> Callable:
    """
    関数呼び出しをログ出力するデコレータ

    使い方:
        @log_call
        def my_function(x, y):
            return x + y

    仕組み:
        1. func として元の関数を受け取る
        2. 「ログを出してから func を呼ぶ」wrapper 関数を定義する
        3. wrapper を返す → 以後 my_function() を呼ぶと wrapper が動く
    """
    # @functools.wraps(func) で元の関数の __name__ や __doc__ を保持する
    # これがないとデコレートされた関数の名前が "wrapper" になってしまう
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 引数の文字列表現を作る
        args_str = ", ".join(repr(a) for a in args)
        kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        print(f"  [LOG] {func.__name__}({all_args}) を呼び出し")
        result = func(*args, **kwargs)
        print(f"  [LOG] {func.__name__} -> {result!r}")
        return result

    return wrapper


def retry(max_attempts: int = 3, delay: float = 0.1) -> Callable:
    """
    引数付きデコレータ（リトライ処理）

    使い方:
        @retry(max_attempts=3, delay=0.5)
        def unstable_function():
            ...

    構造（関数が3段ネストする）:
        retry(max_attempts=3)   →  デコレータ関数 decorator を返す
        decorator(func)         →  wrapper 関数を返す
        wrapper(...)            →  実際に呼ばれる。失敗したら繰り返す

    ★ ネストが深く見えるが、「引数を覚えた関数を段階的に作っている」
      だけ。外側の変数 (max_attempts 等) を内側の関数が参照できる
      性質（クロージャ）を利用している。
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    print(f"  [RETRY] {func.__name__} 試行 {attempt}/{max_attempts} 失敗: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_error  # type: ignore
        return wrapper
    return decorator


# ============================================================
# 4. ユーティリティ関数
# ============================================================

@log_call
def format_name(first: str, last: str, *, title: str = "") -> str:
    """
    名前をフォーマットする

    引数リストの * より後ろはキーワード専用引数になる:
      format_name("太郎", "山田", title="部長")  # OK
      format_name("太郎", "山田", "部長")        # エラー！ title は名前で指定必須

    「この引数は名前を付けて呼んでほしい」を強制でき、
    呼び出し側のコードが読みやすくなる。
    """
    if title:
        return f"{title} {last} {first}"
    return f"{last} {first}"


# ============================================================
# 5. __name__ == "__main__" ガード
# ============================================================
# __name__ は Python が自動で用意する変数。
#   - ファイルを直接実行したとき:      __name__ == "__main__"
#   - 他のファイルから import されたとき: __name__ == "utils" (モジュール名)
#
# つまり if __name__ == "__main__": の中は
# 「直接実行されたときだけ」動く。
# テストコードやデモコードを書くのに便利 ★
# ============================================================

if __name__ == "__main__":
    # このブロックは python utils.py と直接実行した時だけ動く
    # main.py から import utils した時は動かない
    print("=" * 50)
    print("utils.py を直接実行中（テスト用）")
    print("=" * 50)

    # *args, **kwargs のデモ
    print("\n--- 可変長引数のテスト ---")
    print_args_demo(1, 2, 3, name="Python", version=3.12)

    # 辞書マージのデモ
    print("\n--- 辞書マージのテスト ---")
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 3, "c": 4}  # b は上書きされる
    merged = merge_dicts(d1, d2)
    print(f"  {d1} + {d2} = {merged}")

    # デコレータのデモ
    print("\n--- デコレータのテスト ---")
    result = format_name("太郎", "山田", title="部長")
    print(f"  結果: {result}")

    # リトライデコレータのデモ
    print("\n--- リトライデコレータのテスト ---")
    call_count = 0

    @retry(max_attempts=3, delay=0.1)
    def flaky_function() -> str:
        """2回失敗して3回目に成功する関数"""
        global call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError(f"接続エラー（{call_count}回目）")
        return "成功！"

    try:
        result = flaky_function()
        print(f"  最終結果: {result}")
    except Exception as e:
        print(f"  最終エラー: {e}")
