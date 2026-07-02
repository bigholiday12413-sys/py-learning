# Lv00 - 環境構築：Python を動かせる状態にする

## テーマ

Lv01 に入る前の準備。Python のインストール、エディタの設定、
ターミナル（コマンド入力画面）の基本操作を身につける。

**すでに `python main.py` が動く人はこのレベルは飛ばしてOK。**

---

## 1. Python のインストール

### Windows

1. https://www.python.org/downloads/ から最新版（3.11以上）のインストーラをダウンロード
2. インストーラを起動したら、**必ず最初の画面で「Add python.exe to PATH」にチェックを入れる**
   （これを忘れると `python` コマンドが認識されない。最も多いつまずきポイント！）
3. 「Install Now」をクリック

インストール確認（PowerShell を開いて実行）:

```powershell
python --version
# → Python 3.12.x のように表示されればOK
```

`python` が認識されない場合は `py --version` を試す。
`py` で動くなら、このコース内の `python` はすべて `py` に読み替えてもよい
（根本解決したい場合は Python を再インストールして PATH のチェックを入れる）。

### macOS

```bash
# 公式インストーラ（python.org）を使うか、Homebrew で:
brew install python

python3 --version   # macOS では python3 コマンドになることが多い
```

macOS では `python` → `python3`、`pip` → `pip3` に読み替える。

---

## 2. エディタ: VS Code

コードを書く・読むためのエディタは **Visual Studio Code**（無料）を推奨。

1. https://code.visualstudio.com/ からダウンロードしてインストール
2. 左側の拡張機能アイコン（四角が4つのマーク）から以下をインストール:
   - **Python**（Microsoft製）… 補完・実行・デバッグ
   - **Japanese Language Pack**（メニューを日本語化したい場合）

便利な使い方:

- フォルダごと開く: メニュー「ファイル → フォルダーを開く」で `py-learning` を開く
- ターミナルを開く: `` Ctrl + ` ``（バッククォート）でVS Code内にターミナルが出る
- ファイル実行: `.py` ファイルを開いて右上の ▶ ボタン

---

## 3. ターミナルの基本操作

このコースでは「ターミナルにコマンドを打つ」場面が頻繁に出てくる。
最低限これだけ覚えれば進められる:

| やりたいこと | Windows (PowerShell) | macOS / Linux |
|-------------|---------------------|---------------|
| 今いる場所を表示 | `pwd` | `pwd` |
| フォルダの中身を見る | `dir` または `ls` | `ls` |
| フォルダを移動 | `cd lv01-hello-python` | 同じ |
| 1つ上に戻る | `cd ..` | 同じ |
| コマンド履歴 | ↑キー | 同じ |
| 入力補完 | Tabキー | 同じ |
| 実行中のプログラムを止める | `Ctrl + C` | 同じ |

**Tabキー補完は必ず使うこと。** `cd lv0` まで打って Tab を押せば残りが補完される。
長いフォルダ名を手打ちするとタイプミスの元。

---

## 4. venv（仮想環境）の予行演習

Lv03 以降で使う venv を、ここで一度試しておく。

venv は「プロジェクトごとに独立したライブラリ置き場」を作る仕組み。
プロジェクトAとBで違うバージョンのライブラリを使っても衝突しなくなる。

```powershell
# 適当な練習フォルダで実行
python -m venv venv        # venv という名前の仮想環境を作成

# 有効化（Windows PowerShell）
.\venv\Scripts\Activate.ps1

# 有効化（macOS / Linux）
source venv/bin/activate

# 有効化されると、プロンプトの先頭に (venv) と表示される
# この状態で pip install したものは、この venv の中にだけ入る

# 抜けるとき
deactivate
```

### ⚠ Windows でほぼ全員が最初にハマるエラー

```
.\venv\Scripts\Activate.ps1 : このシステムではスクリプトの実行が無効になっているため、
ファイル ... を読み込むことができません。
```

これは PowerShell のセキュリティ設定によるもの。以下を一度実行すれば解決する:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
# 「Y」を入力して Enter
```

その後、もう一度 `.\venv\Scripts\Activate.ps1` を実行する。

---

## 5. pip の基本

pip は Python のライブラリ（パッケージ）をインストールするコマンド。

```powershell
pip install requests          # ライブラリを1つ入れる
pip install -r requirements.txt   # ファイルに書かれた一覧を一括で入れる
pip list                      # 入っているライブラリの一覧
pip freeze > requirements.txt # 現在の環境を一覧ファイルに書き出す
```

原則: **venv を有効化してから pip install する**。
`(venv)` がプロンプトに出ていない状態で install すると、PC全体に入ってしまい、
プロジェクト間で混ざる原因になる。

---

## 動作確認チェックリスト

すべて ✔ になったら Lv01 へ進もう。

- [ ] `python --version` で 3.10 以上が表示される
- [ ] VS Code で `py-learning` フォルダを開けた
- [ ] ターミナルで `cd` と Tab補完 が使えた
- [ ] venv を作成して有効化できた（プロンプトに `(venv)` が出た）
- [ ] `deactivate` で venv から抜けられた

つまずいたら、リポジトリ直下の **TROUBLESHOOTING.md** も見てみること。
