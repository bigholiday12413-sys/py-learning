# Lv03 - クラスとモジュール

## テーマ

Pythonのクラス定義・継承・モジュールシステムを学ぶ。
JS/TSの `class`, `extends`, `import/export` との違いを意識しながら進める。

## 動かし方

```bash
# 1. venv（仮想環境）を作成する（初回のみ）
#    JS/TS の node_modules に相当する隔離環境
python -m venv venv

# 2. venv を有効化する
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Windows (cmd)
.\venv\Scripts\activate.bat
# macOS / Linux
source venv/bin/activate

# 3. 依存パッケージをインストール（今回は空だが手順として覚える）
#    JS/TS の npm install に相当
pip install -r requirements.txt

# 4. 実行
python main.py
```

## 学べること

| Python | JS/TS 対応概念 |
|--------|---------------|
| `class`, `__init__`, `self` | `class`, `constructor`, `this` |
| 継承 (`class Child(Parent)`) | `class Child extends Parent` |
| `@dataclass` | TypeScript の `interface` / クラスの自動生成 |
| `__str__`, `__repr__` | `toString()` |
| `import` / モジュール | `import` / `export` |
| `__name__ == "__main__"` | トップレベル実行ガード（ESM にはない概念） |
| `*args`, `**kwargs` | `...rest` / スプレッド構文 |
| デコレータ (`@`) | TypeScript デコレータ |
| 型ヒント | TypeScript の型注釈 |

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

`requirements.txt` は Python プロジェクトの依存パッケージを管理するファイル。
JS/TS の `package.json` の `dependencies` セクションに相当する。

```bash
# パッケージ追加時
pip install requests
pip freeze > requirements.txt  # 現在の環境を書き出す（npm lock に近い）
```

今回は外部パッケージを使わないため空だが、
プロジェクト構成の基本として置いている。
