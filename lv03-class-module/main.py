"""
main.py - Lv03 クラスとモジュール メインエントリポイント

models.py と utils.py をインポートして実際に使う。
JS/TS の index.ts に相当するファイル。
"""

# ============================================================
# インポートの書き方
# ============================================================
# JS/TS:
#   import { Person, Employee } from './models';
#   import { formatName } from './utils';
#   import * as utils from './utils';
#
# Python:
#   from models import Person, Employee  # 名前付きインポート
#   from utils import format_name        # 名前付きインポート
#   import utils                          # モジュール全体をインポート
#
# ★ Python には export 宣言が不要。ファイル内の全てが自動公開される
# ★ 相対パスの ./ は不要（同じディレクトリなら直接モジュール名を書く）
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
    # JS/TS: const person = new Person("太郎", 30)
    # Python: new キーワードは不要！ ★
    person = Person("太郎", 30)

    # メソッド呼び出し
    print(person.greet())

    # __str__ が使われる場面
    # JS/TS: console.log(person.toString())
    print(f"str():  {person}")       # __str__ が呼ばれる
    print(f"repr(): {person!r}")     # __repr__ が呼ばれる（!r フォーマット指定子）

    # クラス変数へのアクセス
    # JS/TS: Person.species または person.constructor.species
    print(f"種族: {Person.species}")
    print(f"種族（インスタンス経由）: {person.species}")

    # 型チェック
    # JS/TS: person instanceof Person
    print(f"isinstance チェック: {isinstance(person, Person)}")


def demo_inheritance() -> None:
    """継承のデモ"""
    section("2. 継承（Employee extends Person）")

    emp = Employee("花子", 28, "E001", "開発部")

    # オーバーライドされた greet() が呼ばれる
    print(emp.greet())

    # 親クラスのプロパティもアクセス可能
    print(f"名前: {emp.name}")         # Person から継承
    print(f"社員番号: {emp.employee_id}")  # Employee 固有

    # isinstance は親クラスでも True
    # JS/TS: emp instanceof Person === true
    print(f"Employee は Person か: {isinstance(emp, Person)}")
    print(f"Employee は Employee か: {isinstance(emp, Employee)}")

    # type() は厳密な型チェック（JS の constructor 比較に近い）
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
    # JS/TS: try { ... } catch (e) { ... }
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

    # __eq__ も自動生成される（全フィールドで比較）
    # JS/TS: product1 === product2 は False（参照比較）
    # Python の dataclass: product1 == product2 は True（値比較）★
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
    # JS/TS: const temp2 = Temperature.fromFahrenheit(212)
    temp2 = Temperature.from_fahrenheit(212.0)
    print(f"華氏から生成: {temp2}")

    # スタティックメソッド
    # JS/TS: Temperature.isFreezing(0)
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
    # JS/TS: printArgsDemo(1, "hello", true, { x: 10, name: "test" })
    # Python: 位置引数とキーワード引数が分離される ★
    print_args_demo(1, "hello", True, x=10, name="テスト")

    # --- 辞書マージ ---
    print("\n--- 辞書マージ（スプレッド相当） ---")
    defaults = {"theme": "dark", "lang": "ja", "font_size": 14}
    user_prefs = {"theme": "light", "font_size": 16}
    merged = merge_dicts(defaults, user_prefs)
    print(f"  デフォルト: {defaults}")
    print(f"  ユーザー設定: {user_prefs}")
    print(f"  マージ結果: {merged}")

    # Python 3.9+ の書き方（JS/TS のスプレッドに最も近い）
    merged_new = defaults | user_prefs  # { ...defaults, ...userPrefs } と同等
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
# JS/TS にはない概念。Python ではこのガードが慣習。
# このファイルが直接実行された時だけ以下が動く。
# 他のファイルから import main しても動かない。
# ============================================================

if __name__ == "__main__":
    print("Lv03 - クラスとモジュール デモ")
    print("Python のクラス・継承・モジュールを JS/TS と比較しながら学ぶ")

    demo_basic_class()
    demo_inheritance()
    demo_property()
    demo_dataclass()
    demo_class_static_methods()
    demo_module_features()
    demo_retry_decorator()

    section("まとめ")
    print("""
  ★ Python vs JS/TS クラスの主な違い:
    1. new キーワード不要: Person("太郎", 30)
    2. self は明示的に書く（JS の this は暗黙）
    3. __init__ が constructor に相当
    4. __str__ / __repr__ が toString() に相当
    5. @property で getter/setter を定義
    6. @dataclass でボイラープレートを削減
    7. @classmethod でファクトリメソッド
    8. 多重継承が可能（JS/TS は単一継承のみ）

  ★ Python vs JS/TS モジュールの主な違い:
    1. export 不要（全て自動公開）
    2. __all__ で公開範囲を制御
    3. __name__ == "__main__" でエントリポイントを制御
    4. *args / **kwargs で柔軟な引数を受け取れる
    5. デコレータが言語レベルでサポートされている
""")
