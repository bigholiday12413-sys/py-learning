"""
models.py - クラス定義・継承・dataclass の学習

「データとそれを扱う処理をひとまとめにする」仕組みであるクラスを学ぶ
"""

from dataclasses import dataclass, field
from typing import Optional


# ============================================================
# 1. 基本的なクラス定義
# ============================================================
# クラスは「モノの設計図」。設計図から作った実体をインスタンスと呼ぶ。
#
#   class Person:
#       def __init__(self, name, age):
#           self.name = name
#           self.age = age
#
#   person = Person("太郎", 30)   # インスタンス生成（new などは不要）
#
# ポイント:
#   - __init__ はインスタンス生成時に自動で呼ばれる特別なメソッド（コンストラクタ）
#   - self は「このインスタンス自身」を指す。メソッドの第1引数に必ず書く
#   - self.name = name で「このインスタンスの属性 name」に値を保存する
# ============================================================

class Person:
    """人を表すクラス"""

    # --- クラス変数 ---
    # ここ（メソッドの外）に書いた変数は「全インスタンスで共有」される。
    # インスタンスごとの値は __init__ の中で self.xxx に代入する。
    species: str = "Homo sapiens"

    def __init__(self, name: str, age: int) -> None:
        """
        コンストラクタ

        ポイント:
        - self は明示的に第1引数に書く（呼び出す側は渡さなくてよい）
        - 引数の型ヒント `: str` と戻り値の型ヒント `-> None` は Lv01 で学んだ通り
        """
        # --- インスタンス変数 ---
        # self.xxx = ... と代入した瞬間にその属性が作られる
        self.name: str = name
        self.age: int = age

    def greet(self) -> str:
        """
        メソッド定義

        メソッド = クラスの中に定義した関数。
        第1引数に必ず self を書き、self.name のように自分の属性へアクセスする。
        呼び出しは person.greet() のように書く（self は自動で渡される）。
        """
        return f"こんにちは、{self.name}です。{self.age}歳です。"

    # --- __str__: 人間向けの文字列表現 ---
    # print() や str() に渡したときに呼ばれる特別なメソッド。
    # 定義しておくと print(person) が読みやすい表示になる。
    def __str__(self) -> str:
        return f"Person({self.name}, {self.age}歳)"

    # --- __repr__: 開発者向けの文字列表現 ---
    # デバッグ時やインタプリタでの表示に使われる。
    # 理想的には eval(repr(obj)) でオブジェクトを再生成できる形式にする
    def __repr__(self) -> str:
        return f"Person(name='{self.name}', age={self.age})"


# ============================================================
# 2. 継承
# ============================================================
# 継承 = 既存のクラスを土台にして、機能を追加・変更した新しいクラスを作ること。
#
#   class Employee(Person):   ← カッコ内に親クラスを書く
#
# ポイント:
#   - 親クラスの属性・メソッドをそのまま引き継ぐ
#   - super().__init__() で親の __init__ を呼び、共通部分の初期化を任せる
#   - 同名メソッドを定義すれば上書き（オーバーライド）できる
#   - Python は複数の親を持つ「多重継承」も可能（まずは単一継承から）
# ============================================================

class Employee(Person):
    """従業員クラス（Person を継承）"""

    def __init__(self, name: str, age: int, employee_id: str, department: str = "未配属") -> None:
        """
        ポイント:
        - super() は「親クラス」を指す。super().__init__(...) で親の初期化を実行
        - department のようにデフォルト値付きの引数も定義できる
        """
        # 親クラスの __init__ を呼ぶ（name と age の初期化は親に任せる）
        super().__init__(name, age)

        self.employee_id: str = employee_id
        self.department: str = department

    def greet(self) -> str:
        """
        メソッドオーバーライド

        親クラスと同名のメソッドを定義すると上書きされる。
        親のバージョンを部分的に使いたいときは super().greet() で呼び出せる。
        （なお Python 3.12+ には @typing.override という明示用デコレータもある）
        """
        # 親クラスのメソッドを呼ぶ: super().greet()
        base_greeting = super().greet()
        return f"{base_greeting} 社員番号: {self.employee_id}、部署: {self.department}"

    def __str__(self) -> str:
        return f"Employee({self.name}, {self.department})"

    def __repr__(self) -> str:
        return (
            f"Employee(name='{self.name}', age={self.age}, "
            f"employee_id='{self.employee_id}', department='{self.department}')"
        )


# ============================================================
# 3. プロパティ（getter / setter）
# ============================================================
# 属性の読み書きに「処理を挟みたい」ときに使うのがプロパティ。
# 例: 値を設定するときにバリデーションしたい、値を毎回計算で求めたい。
#
# ポイント:
#   - @property を付けたメソッドは「属性のように」読み出せる: circle.radius
#   - @xxx.setter を付けたメソッドは「代入したとき」に呼ばれる: circle.radius = 10
#   - _ プレフィックスは「外から直接触らないで」という慣習（強制力はない）
#   - __ プレフィックスにすると名前が変換され、外部からのアクセスがさらに困難になる
# ============================================================

class Circle:
    """円クラス（プロパティの例）"""

    def __init__(self, radius: float) -> None:
        # _radius の _ は「内部用の属性なので直接触らないで」という目印
        self._radius: float = radius

    # --- getter ---
    # circle.radius と「読み出した」ときにこのメソッドが呼ばれる
    @property
    def radius(self) -> float:
        """半径を取得"""
        return self._radius

    # --- setter ---
    # circle.radius = 10 と「代入した」ときにこのメソッドが呼ばれる
    @radius.setter
    def radius(self, value: float) -> None:
        """半径を設定（バリデーション付き）"""
        if value < 0:
            # raise でエラー（例外）を発生させる。呼び出し側は try/except で捕まえられる
            raise ValueError("半径は0以上でなければなりません")
        self._radius = value

    # --- 読み取り専用プロパティ ---
    # setter を定義しなければ読み取り専用になる（代入しようとするとエラー）
    @property
    def area(self) -> float:
        """面積を計算（読み取り専用）"""
        import math
        return math.pi * self._radius ** 2

    def __str__(self) -> str:
        return f"Circle(radius={self._radius:.2f}, area={self.area:.2f})"


# ============================================================
# 4. @dataclass デコレータ
# ============================================================
# 「データを入れておくためのクラス」を書くとき、__init__ や __repr__ を
# 毎回手書きするのは面倒。@dataclass を付けると自動生成してくれる。
#
# 自動生成されるもの:
#   - __init__ … フィールド定義から自動で作られる
#   - __repr__ … デバッグしやすい表示
#   - __eq__  … 全フィールドの値で == 比較できるようになる
#
# 設定情報・CSVの1行・APIレスポンスなど「構造化されたデータ」を
# 表すのに非常に便利で、実務でも多用する。
# ============================================================

@dataclass
class Product:
    """
    商品クラス（dataclass版）

    以下が自動生成される:
    - __init__(self, id, name, price, in_stock)
    - __repr__(self) -> "Product(id=1, name='りんご', ...)"
    - __eq__(self, other) -> フィールド比較
    """
    id: int
    name: str
    price: float
    in_stock: bool = True  # デフォルト値も設定可能


# --- frozen=True で不変（イミュータブル）にできる ---
# 生成後にフィールドを変更しようとするとエラーになる。
# 「途中で書き換わっては困るデータ」に使う。
@dataclass(frozen=True)
class ImmutablePoint:
    """変更不可能な座標（frozen dataclass）"""
    x: float
    y: float


# --- field() でより細かい制御 ---
@dataclass
class Team:
    """
    チームクラス

    field(default_factory=list) について:
    - リストや辞書のような「変更可能な値」をデフォルト値に直接書くと、
      全インスタンスで同じリストが共有されてしまう危険があるため、
      Python は members: list[str] = [] という書き方をエラーにする
    - default_factory=list とすると「インスタンスごとに新しい空リスト」を作ってくれる
    """
    name: str
    members: list[str] = field(default_factory=list)
    description: Optional[str] = None  # Optional[str] = 「str または None」の意味

    def add_member(self, member: str) -> None:
        """メンバーを追加"""
        self.members.append(member)

    def __str__(self) -> str:
        member_list = ", ".join(self.members) if self.members else "(なし)"
        return f"Team '{self.name}': [{member_list}]"


# ============================================================
# 5. クラスメソッドとスタティックメソッド
# ============================================================
# 通常のメソッドは「インスタンス」に対して呼ぶが、
# クラスそのものに対して呼びたいメソッドもある。
#
#   - @classmethod: 第1引数にクラス自体 (cls) を受け取る。
#     「別の形式のデータからインスタンスを作る」ファクトリメソッドの定番
#   - @staticmethod: self も cls も受け取らない。
#     クラスに関連する「ただの関数」を名前空間としてまとめたいときに使う
# ============================================================

class Temperature:
    """温度クラス（クラスメソッド・スタティックメソッドの例）"""

    def __init__(self, celsius: float) -> None:
        self.celsius: float = celsius

    # --- クラスメソッド: ファクトリパターン ---
    # Temperature.from_fahrenheit(212) のようにクラスから直接呼ぶ。
    # cls は「このクラス自体」を指す（継承時にはサブクラスが渡される）
    @classmethod
    def from_fahrenheit(cls, fahrenheit: float) -> "Temperature":
        """華氏から生成するファクトリメソッド"""
        celsius = (fahrenheit - 32) * 5 / 9
        return cls(celsius)  # cls() = Temperature() と同等

    # --- スタティックメソッド ---
    # self も cls も受け取らない = ただの名前空間付き関数
    @staticmethod
    def is_freezing(celsius: float) -> bool:
        """氷点下かどうかを判定"""
        return celsius <= 0

    @property
    def fahrenheit(self) -> float:
        """華氏に変換"""
        return self.celsius * 9 / 5 + 32

    def __str__(self) -> str:
        return f"{self.celsius:.1f}°C ({self.fahrenheit:.1f}°F)"
