"""
main.py - Lv03 クラスとモジュール メインエントリポイント

models.py と utils.py をインポートして実際に使う。
プログラムの「入口」となるファイル。
"""

# ============================================================
# インポートの書き方
# ============================================================
#   from models import Person, Employee  # 特定の名前だけ読み込む
#   from utils import format_name        # 特定の名前だけ読み込む
#   import utils                          # モジュール全体を読み込む
#
# ★ 同じフォルダにある .py ファイルは、拡張子を除いた
#   ファイル名（モジュール名）で import できる
# ★ export のような宣言は不要。ファイル内の全てが自動公開される
# ============================================================

from models import Person, Employee, Circle, Product, ImmutablePoint, Team, Temperature
from utils import format_name, log_call, merge_dicts, print_args_demo, retry


def section(title: str) -> None:
    """セクション区切りを表示するヘルパー"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def demo_basic_class() -> None:
    """基本クラスのデモ"""
    section("1. 基本クラス（Person）")

    # --- インスタンス生成 ---
    # クラス名をそのまま関数のように呼ぶ。new のようなキーワードは不要 ★
    person = Person("太郎", 30)

    # メソッド呼び出し
    print(person.greet())

    # __str__ / __repr__ が使われる場面
    print(f"str():  {person}")       # __str__ が呼ばれる
    print(f"repr(): {person!r}")     # __repr__ が呼ばれる（!r フォーマット指定子）

    # クラス変数へのアクセス（クラス名からもインスタンスからも読める）
    print(f"種族: {Person.species}")
    print(f"種族（インスタンス経由）: {person.species}")

    # 型チェック ─ isinstance(値, クラス) で「そのクラスのインスタンスか」を判定
    print(f"isinstance チェック: {isinstance(person, Person)}")


def demo_inheritance() -> None:
    """継承のデモ"""
    section("2. 継承（Employee は Person を継承）")

    emp = Employee("花子", 28, "E001", "開発部")

    # オーバーライドされた greet() が呼ばれる
    print(emp.greet())

    # 親クラスのプロパティもアクセス可能
    print(f"名前: {emp.name}")         # Person から継承
    print(f"社員番号: {emp.employee_id}")  # Employee 固有

    # isinstance は親クラスに対しても True になる
    print(f"Employee は Person か: {isinstance(emp, Person)}")
    print(f"Employee は Employee か: {isinstance(emp, Employee)}")

    # type() は「実際のクラスそのもの」を返すので、親クラスとは一致しない
    print(f"type は Person か: {type(emp) is Person}")      # False
    print(f"type は Employee か: {type(emp) is Employee}")   # True


def demo_property() -> None:
    """プロパティ（getter/setter）のデモ"""
    section("3. プロパティ（Circle）")

    circle = Circle(5.0)
    print(f"円: {circle}")
    print(f"半径: {circle.radius}")    # getter が呼ばれる
    print(f"面積: {circle.area:.2f}")  # 読み取り専用プロパティ

    # setter でバリデーション
    circle.radius = 10.0               # setter が呼ばれる
    print(f"半径変更後: {circle}")

    # バリデーションエラーのテスト
    # raise された例外は try/except で受け止められる
    try:
        circle.radius = -1.0  # ValueError が発生する
    except ValueError as e:
        print(f"バリデーションエラー: {e}")


def demo_dataclass() -> None:
    """dataclass のデモ"""
    section("4. @dataclass")

    # --- 基本的な dataclass ---
    product1 = Product(id=1, name="りんご", price=150.0)
    product2 = Product(id=1, name="りんご", price=150.0)
    product3 = Product(id=2, name="みかん", price=100.0, in_stock=False)

    print(f"商品1: {product1}")        # 自動生成された __repr__ が使われる
    print(f"商品3: {product3}")

    # __eq__ も自動生成される（全フィールドの「値」で比較）★
    # 通常のクラスでは別々に作ったインスタンスは == で False になるが、
    # dataclass なら中身が同じであれば True になる
    print(f"product1 == product2: {product1 == product2}")  # True!
    print(f"product1 == product3: {product1 == product3}")  # False

    # --- frozen dataclass（イミュータブル） ---
    point = ImmutablePoint(x=1.0, y=2.0)
    print(f"\n不変オブジェクト: {point}")
    try:
        point.x = 10.0  # type: ignore  # FrozenInstanceError が発生
    except Exception as e:
        print(f"変更エラー: {type(e).__name__}: {e}")

    # --- field() を使った dataclass ---
    team = Team(name="Alphaチーム")
    team.add_member("太郎")
    team.add_member("花子")
    print(f"\n{team}")


def demo_class_static_methods() -> None:
    """クラスメソッド・スタティックメソッドのデモ"""
    section("5. クラスメソッド・スタティックメソッド（Temperature）")

    # 通常のコンストラクタ
    temp1 = Temperature(100.0)
    print(f"摂氏で生成: {temp1}")

    # クラスメソッド（ファクトリ）で生成
    # インスタンスではなく「クラス」から直接呼ぶ
    temp2 = Temperature.from_fahrenheit(212.0)
    print(f"華氏から生成: {temp2}")

    # スタティックメソッドも「クラス」から直接呼ぶ
    print(f"0°Cは氷点下か: {Temperature.is_freezing(0)}")
    print(f"20°Cは氷点下か: {Temperature.is_freezing(20)}")


def demo_module_features() -> None:
    """モジュール機能のデモ"""
    section("6. モジュール機能（utils.py）")

    # --- デコレータ付き関数 ---
    print("--- @log_call デコレータ ---")
    name = format_name("太郎", "山田", title="部長")
    print(f"結果: {name}\n")

    # --- *args, **kwargs ---
    print("--- 可変長引数 ---")
    # 位置引数 (1, "hello", True) とキーワード引数 (x=10, name=...) が
    # 自動的に分かれて受け取られる ★
    print_args_demo(1, "hello", True, x=10, name="テスト")

    # --- 辞書マージ ---
    print("\n--- 辞書マージ ---")
    defaults = {"theme": "dark", "lang": "ja", "font_size": 14}
    user_prefs = {"theme": "light", "font_size": 16}
    merged = merge_dicts(defaults, user_prefs)
    print(f"  デフォルト: {defaults}")
    print(f"  ユーザー設定: {user_prefs}")
    print(f"  マージ結果: {merged}")

    # Python 3.9+ なら | 演算子で1行で書ける
    merged_new = defaults | user_prefs  # 右側の値が優先される
    print(f"  | 演算子: {merged_new}")


def demo_retry_decorator() -> None:
    """リトライデコレータのデモ"""
    section("7. 引数付きデコレータ（@retry）")

    attempt_count = 0

    @retry(max_attempts=3, delay=0.1)
    def fetch_data() -> dict:
        """2回失敗して3回目に成功するシミュレーション"""
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("サーバーに接続できません")
        return {"status": "ok", "data": [1, 2, 3]}

    try:
        result = fetch_data()
        print(f"  取得成功: {result}")
    except ConnectionError as e:
        print(f"  最終的に失敗: {e}")


# ============================================================
# エントリポイント
# ============================================================
# このガードは Python の慣習（詳細は utils.py の解説を参照）。
# このファイルが直接実行された時だけ以下が動く。
# 他のファイルから import main しても動かない。
# ============================================================

if __name__ == "__main__":
    print("Lv03 - クラスとモジュール デモ")
    print("Python のクラス・継承・モジュールを実際に動かして学ぶ")

    demo_basic_class()
    demo_inheritance()
    demo_property()
    demo_dataclass()
    demo_class_static_methods()
    demo_module_features()
    demo_retry_decorator()

    section("まとめ")
    print("""
  ★ Python のクラス:
    1. インスタンス生成は Person("太郎", 30)（new は不要）
    2. self は明示的にメソッドの第1引数に書く
    3. __init__ がコンストラクタ
    4. __str__ / __repr__ で文字列表現を定義できる
    5. @property で getter/setter を定義
    6. @dataclass でボイラープレートを削減
    7. @classmethod でファクトリメソッド
    8. 多重継承も可能

  ★ Python のモジュール:
    1. 1ファイル = 1モジュール。export 不要（全て自動公開）
    2. __all__ で公開範囲を制御
    3. __name__ == "__main__" でエントリポイントを制御
    4. *args / **kwargs で柔軟な引数を受け取れる
    5. デコレータが言語レベルでサポートされている
""")
