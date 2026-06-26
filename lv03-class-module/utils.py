"""
utils.py - モジュール・デコレータ・可変長引数の学習

JS/TS開発者向け: Python のモジュールシステムとユーティリティパターンを学ぶ
"""

import functools
import time
from typing import Any, Callable


# ============================================================
# 1. モジュールとインポート
# ============================================================
# JS/TS:
#   // 名前付きエクスポート
#   export function helper() { ... }
#   export const VALUE = 42;
#
#   // デフォルトエクスポート
#   export default class MyClass { ... }
#
#   // インポート
#   import { helper, VALUE } from './utils';
#   import MyClass from './utils';
#
# Python:
#   - export は不要。ファイル内のすべてが自動的にエクスポートされる
#   - _ プレフィックスの名前は「プライベート」扱い（from module import * で除外）
#   - __all__ リストで公開するものを明示できる（★ベストプラクティス）
#   - デフォルトエクスポートの概念はない
#
# インポートの書き方:
#   from models import Person          # JS: import { Person } from './models'
#   from models import Person as P     # JS: import { Person as P } from './models'
#   import models                      # JS: import * as models from './models'
#   from models import *               # JS: import * from './models'（非推奨）
# ============================================================

# --- __all__: 公開するもの一覧 ---
# JS/TS の index.ts で re-export するパターンに近い
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
# JS/TS:
#   function example(...args) { }           // rest パラメータ
#   example(...myArray);                     // スプレッド構文
#   function example({name, age}) { }        // 分割代入
#
# Python:
#   - *args: 位置引数をタプルとして受け取る（JS の ...args に相当）
#   - **kwargs: キーワード引数を辞書として受け取る（JS のオブジェクト分割代入に近い）
#   - 両方同時に使えるのが強力
# ============================================================

def print_args_demo(*args: Any, **kwargs: Any) -> None:
    """
    *args, **kwargs のデモ

    JS/TS との比較:
      // JS - rest パラメータ
      function demo(...args) {
        console.log(args);  // 配列
      }

      // Python は位置引数とキーワード引数を分けて受け取れる
      // これは JS にない機能 ★
    """
    print("--- *args, **kwargs デモ ---")

    # *args はタプル（JS の arguments に近いが、本当の配列/タプル）
    print(f"  位置引数 (args): {args}")
    print(f"  args の型: {type(args)}")  # <class 'tuple'>

    # **kwargs は辞書（JS のオブジェクト引数に近い）
    print(f"  キーワード引数 (kwargs): {kwargs}")
    print(f"  kwargs の型: {type(kwargs)}")  # <class 'dict'>

    # kwargs の中身を展開
    for key, value in kwargs.items():
        print(f"    {key} = {value}")


def merge_dicts(*dicts: dict) -> dict:
    """
    複数の辞書をマージする

    JS/TS:
      const merged = { ...dict1, ...dict2, ...dict3 };
      // または
      const merged = Object.assign({}, dict1, dict2, dict3);

    Python:
      - ** 演算子で辞書をアンパック（スプレッドに相当）
      - Python 3.9+ では | 演算子も使える: dict1 | dict2
    """
    result: dict = {}
    for d in dicts:
        # JS/TS の Object.assign(result, d) に相当
        result.update(d)
    return result


# ============================================================
# 3. デコレータ
# ============================================================
# TypeScript:
#   // TSデコレータ（実験的機能）
#   function Log(target, key, descriptor) {
#     const original = descriptor.value;
#     descriptor.value = function(...args) {
#       console.log(`Calling ${key}`);
#       return original.apply(this, args);
#     };
#   }
#
#   class MyClass {
#     @Log
#     myMethod() { ... }
#   }
#
# Python:
#   - デコレータは「関数を受け取って関数を返す高階関数」
#   - TS のデコレータよりシンプルで汎用的
#   - @functools.wraps で元の関数情報を保持する（★重要）
# ============================================================

def log_call(func: Callable) -> Callable:
    """
    関数呼び出しをログ出力するデコレータ

    使い方:
        @log_call
        def my_function(x, y):
            return x + y

    JS/TS で同じことをするなら:
        function logCall(fn) {
          return function(...args) {
            console.log(`Calling ${fn.name} with`, args);
            const result = fn(...args);
            console.log(`${fn.name} returned`, result);
            return result;
          };
        }
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

    構造:
        retry(max_attempts=3)  →  デコレータ関数を返す
        そのデコレータ関数(func)  →  wrapper関数を返す

    JS/TS で書くなら:
        function retry(maxAttempts = 3, delay = 100) {
          return function(fn) {
            return async function(...args) {
              for (let i = 0; i < maxAttempts; i++) {
                try { return fn(...args); }
                catch (e) {
                  if (i === maxAttempts - 1) throw e;
                  await new Promise(r => setTimeout(r, delay));
                }
              }
            };
          };
        }

    ★ Python のデコレータは「関数のネスト」が深くなりがちだが、
      概念的には JS のクロージャと同じ
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

    * の後のパラメータはキーワード専用引数（★Pythonならではの機能）
    JS/TS にはない概念:
      format_name("太郎", "山田", title="部長")  # OK
      format_name("太郎", "山田", "部長")          # エラー！ title は名前で指定必須

    JS/TS で近いことをするなら:
      function formatName(first, last, { title = "" } = {}) { ... }
    """
    if title:
        return f"{title} {last} {first}"
    return f"{last} {first}"


# ============================================================
# 5. __name__ == "__main__" ガード
# ============================================================
# JS/TS:
#   - ESM (import/export) にはこの概念がない
#   - CommonJS では稀に使う: if (require.main === module) { ... }
#
# Python:
#   - ファイルが直接実行された時だけ __name__ == "__main__" が True になる
#   - 他のファイルから import された時は __name__ == "utils" (モジュール名) になる
#   - テストコードやデモコードを書くのに便利 ★
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

    # スプレッド（アンパック）のデモ
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
