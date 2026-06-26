"""
models.py - クラス定義・継承・dataclass の学習

JS/TS開発者向け: Pythonのクラスシステムを JS/TS と比較しながら学ぶ
"""

from dataclasses import dataclass, field
from typing import Optional


# ============================================================
# 1. 基本的なクラス定義
# ============================================================
# JS/TS:
#   class Person {
#     constructor(name, age) {
#       this.name = name;  // this でインスタンスを参照
#       this.age = age;
#     }
#   }
#
# Python:
#   - constructor は __init__ メソッド
#   - this の代わりに self を使う
#   - self は「暗黙」ではなく「明示的に」第1引数に書く（★重要な違い）
# ============================================================

class Person:
    """人を表すクラス"""

    # --- クラス変数（JS の static プロパティに相当） ---
    # JS/TS: static species = "Homo sapiens"
    species: str = "Homo sapiens"

    def __init__(self, name: str, age: int) -> None:
        """
        コンストラクタ

        JS/TS との違い:
        - Python は self を明示的に書く（JS の this は暗黙）
        - 型ヒントは `: str` のように書く（TS の `: string` に相当）
        - 戻り値の型ヒント `-> None` は TS の `: void` に相当
        """
        # --- インスタンス変数 ---
        # JS/TS: this.name = name
        self.name: str = name
        self.age: int = age

    def greet(self) -> str:
        """
        メソッド定義

        JS/TS:
          greet() { return `Hello, I'm ${this.name}`; }

        Python:
          - メソッドの第1引数に必ず self を書く
          - f-string は JS のテンプレートリテラルに相当
        """
        return f"こんにちは、{self.name}です。{self.age}歳です。"

    # --- __str__: 人間向けの文字列表現 ---
    # JS/TS の toString() に相当
    # print() や str() で呼ばれる
    def __str__(self) -> str:
        return f"Person({self.name}, {self.age}歳)"

    # --- __repr__: 開発者向けの文字列表現 ---
    # JS/TS には直接対応するものがない
    # デバッグ時やインタプリタでの表示に使われる
    # 理想的には eval(repr(obj)) でオブジェクトを再生成できる形式にする
    def __repr__(self) -> str:
        return f"Person(name='{self.name}', age={self.age})"


# ============================================================
# 2. 継承
# ============================================================
# JS/TS:
#   class Employee extends Person {
#     constructor(name, age, employeeId) {
#       super(name, age);    // 親の constructor を呼ぶ
#       this.employeeId = employeeId;
#     }
#   }
#
# Python:
#   - class Employee(Person): で継承を表す
#   - super().__init__() で親の __init__ を呼ぶ
#   - JS の extends と同じ概念だが、多重継承も可能（★Pythonの特徴）
# ============================================================

class Employee(Person):
    """従業員クラス（Person を継承）"""

    def __init__(self, name: str, age: int, employee_id: str, department: str = "未配属") -> None:
        """
        JS/TS との違い:
        - super() に引数不要（Python3）
        - デフォルト引数は JS/TS と同じ書き方
        """
        # 親クラスの __init__ を呼ぶ
        # JS/TS: super(name, age)
        super().__init__(name, age)

        self.employee_id: str = employee_id
        self.department: str = department

    def greet(self) -> str:
        """
        メソッドオーバーライド

        JS/TS と同じく、同名メソッドを定義すれば上書きされる。
        ただし Python には override キーワードはない
        （typing.override デコレータは Python 3.12+ で追加された）
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
# JS/TS:
#   class Circle {
#     #radius;  // プライベートフィールド
#     get area() { return Math.PI * this.#radius ** 2; }
#     set radius(value) {
#       if (value < 0) throw new Error("...");
#       this.#radius = value;
#     }
#   }
#
# Python:
#   - @property デコレータで getter を定義
#   - @xxx.setter デコレータで setter を定義
#   - _ プレフィックスは「プライベート」の慣習（強制ではない）
#   - __ プレフィックスは名前マングリングで外部アクセスを困難にする
# ============================================================

class Circle:
    """円クラス（プロパティの例）"""

    def __init__(self, radius: float) -> None:
        # _ プレフィックス = 「外から直接触らないで」という慣習
        # JS/TS の #radius（プライベートフィールド）に近いが、強制力はない
        self._radius: float = radius

    # --- getter ---
    # JS/TS: get radius() { return this.#radius; }
    @property
    def radius(self) -> float:
        """半径を取得"""
        return self._radius

    # --- setter ---
    # JS/TS: set radius(value) { ... }
    @radius.setter
    def radius(self, value: float) -> None:
        """半径を設定（バリデーション付き）"""
        if value < 0:
            # JS/TS: throw new Error("...")
            raise ValueError("半径は0以上でなければなりません")
        self._radius = value

    # --- 読み取り専用プロパティ ---
    # setter を定義しなければ読み取り専用になる
    # JS/TS: get area() { return ...; }  （setterなし）
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
# TypeScript:
#   interface Product {
#     id: number;
#     name: string;
#     price: number;
#     inStock: boolean;
#   }
#
# Python の @dataclass:
#   - TS の interface + クラスの自動実装に近い
#   - __init__, __repr__, __eq__ を自動生成してくれる
#   - ボイラープレートを大幅に削減（★非常に便利）
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
# TS: Readonly<Product> に相当する概念
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
    - Python ではミュータブルなデフォルト値（list, dict等）を直接書けない
    - JS/TS でも同様の問題がある:
      class Team { members = [] }  // 全インスタンスで共有されてしまう
    - default_factory で毎回新しいリストを生成する
    """
    name: str
    members: list[str] = field(default_factory=list)
    description: Optional[str] = None  # Optional = string | null (TS)

    def add_member(self, member: str) -> None:
        """メンバーを追加"""
        self.members.append(member)

    def __str__(self) -> str:
        member_list = ", ".join(self.members) if self.members else "(なし)"
        return f"Team '{self.name}': [{member_list}]"


# ============================================================
# 5. クラスメソッドとスタティックメソッド
# ============================================================
# JS/TS:
#   class MyClass {
#     static staticMethod() { ... }        // クラスから直接呼ぶ
#     static fromString(s) { ... }         // ファクトリメソッド
#   }
#
# Python:
#   - @staticmethod: インスタンスもクラスも受け取らない（JS の static に近い）
#   - @classmethod: 第1引数にクラス自体を受け取る（ファクトリメソッドに便利）
# ============================================================

class Temperature:
    """温度クラス（クラスメソッド・スタティックメソッドの例）"""

    def __init__(self, celsius: float) -> None:
        self.celsius: float = celsius

    # --- クラスメソッド: ファクトリパターン ---
    # JS/TS: static fromFahrenheit(f) { return new Temperature(...) }
    # Python: cls が「このクラス自体」を指す（継承時にサブクラスが渡される）
    @classmethod
    def from_fahrenheit(cls, fahrenheit: float) -> "Temperature":
        """華氏から生成するファクトリメソッド"""
        celsius = (fahrenheit - 32) * 5 / 9
        return cls(celsius)  # cls() = Temperature() と同等

    # --- スタティックメソッド ---
    # JS/TS の static メソッドとほぼ同じ
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
