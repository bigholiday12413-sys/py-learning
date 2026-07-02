# Lv03 - クラスとモジュール

## テーマ

Python のクラス定義・継承・モジュールシステムを学ぶ。
「データと処理をひとまとめにする」クラスと、
「コードをファイルに分けて再利用する」モジュールは、大きなプログラムを書く土台になる。

## 動かし方

```bash
# 1. venv（仮想環境）を作成する（初回のみ）
#    プロジェクトごとにライブラリを隔離するための仕組み
python -m venv venv

# 2. venv を有効化する
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Windows (cmd)
.\venv\Scripts\activate.bat
# macOS / Linux
source venv/bin/activate

# 3. 依存パッケージをインストール（今回は空だが手順として覚える）
pip install -r requirements.txt

# 4. 実行
python main.py
```

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `class`, `__init__`, `self` | モノの設計図・コンストラクタ・自分自身への参照 |
| 継承 (`class Child(Parent)`) | 既存クラスを土台に機能を追加する |
| `@dataclass` | データ入れ用クラスの `__init__` 等を自動生成 |
| `__str__`, `__repr__` | `print()` したときの表示を定義する |
| `import` / モジュール | 1ファイル = 1モジュール。他ファイルの機能を読み込む |
| `__name__ == "__main__"` | 「直接実行されたときだけ動く」ブロック |
| `*args`, `**kwargs` | 個数不定の引数を受け取る |
| デコレータ (`@`) | 関数に共通機能を後付けする |
| `@property` | 属性の読み書きに処理を挟む（getter/setter） |

## 読む順番

1. **models.py** - クラス定義・継承・dataclass を学ぶ
2. **utils.py** - モジュール・デコレータ・可変長引数を学ぶ
3. **main.py** - 上記をインポートして使う実践例

## 改造課題

1. `models.py` に新しいクラス `Manager(Employee)` を追加し、部下リストを持たせてみよう
2. `utils.py` に実行時間を計測するデコレータ `@timer` を作ってみよう
3. `models.py` に `@dataclass` で `Project` クラスを作り、`Employee` と紐づけてみよう
4. `__repr__` を活用して、デバッグしやすい出力を設計してみよう
5. 別ファイル `services.py` を作り、`models.py` と `utils.py` を組み合わせてみよう

## requirements.txt について

`requirements.txt` は Python プロジェクトの依存パッケージ（外部ライブラリ）を
書き並べておくファイル。`pip install -r requirements.txt` で一括インストールできる。

```bash
# パッケージ追加時
pip install requests
pip freeze > requirements.txt  # 現在の環境のパッケージ一覧を書き出す
```

今回は外部パッケージを使わないため空だが、
プロジェクト構成の基本として置いている。
