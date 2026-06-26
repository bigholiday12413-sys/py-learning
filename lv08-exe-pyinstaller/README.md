# Lv08: Pythonスクリプトのexe化（PyInstaller）

## テーマ

Pythonスクリプトを `.exe` ファイルに変換して、Python環境がないPCでも実行できるようにする。
非エンジニアの同僚にツールを配布する際に必須の知識。

> **JS/TS開発者向けメモ**:
> Node.jsでいうと `pkg` や `nexe` に相当する。
> ただしPythonのexe化はNode.jsよりハマりポイントが多い。

---

## 動かし方

```bash
# 1. 仮想環境を作成・有効化
python -m venv .venv
.venv\Scripts\activate

# 2. 依存パッケージのインストール
pip install -r requirements.txt

# 3. Playwrightブラウザのインストール（初回のみ）
playwright install chromium

# 4. スクリプトとして実行（動作確認）
python main.py

# 5. exe化ビルド
python build.py

# 6. 生成されたexeを実行
dist\web_scraper.exe
```

---

## 学べること

| 項目 | 内容 |
|------|------|
| PyInstallerの基本 | exe化の仕組みと使い方 |
| 外部ファイルの扱い | config.jsonなど設定ファイルの読み込み |
| パス解決 | スクリプト実行時 vs exe実行時のパスの違い |
| `sys.frozen` | exe化されたかどうかの判定方法 |
| ビルドスクリプト | PyInstallerのオプション管理 |
| 配布の実務 | 同僚にexeを渡す際の注意点 |
| Playwright特有の問題 | ブラウザバイナリの扱い |

---

## PyInstallerとは

PyInstallerは、Pythonスクリプトを単体の実行ファイル（.exe）に変換するツール。

### 仕組み

1. Pythonインタープリタ本体を同梱
2. importしているライブラリをすべて収集
3. スクリプト本体と合わせて1つのexe（またはフォルダ）にまとめる

### JS/TSとの比較

| Python (PyInstaller) | JS/TS (pkg) |
|---------------------|-------------|
| Pythonランタイムを同梱 | Node.jsランタイムを同梱 |
| pip依存を自動収集 | node_modulesを同梱 |
| `.spec`ファイルで設定 | `package.json`のpkgフィールド |
| `--onefile` で単一exe | デフォルトで単一バイナリ |

---

## exe化の流れ

```
main.py + 依存ライブラリ + Pythonランタイム
    ↓ PyInstaller
  build/ (中間ファイル)
  dist/  (完成したexe)
  *.spec (ビルド設定ファイル)
```

### 重要な概念

- **`--onefile`**: すべてを1つのexeにまとめる（配布しやすい、起動が少し遅い）
- **`--onedir`**: フォルダにまとめる（起動が速い、ファイル数が多い）
- **`--noconsole`**: コンソールウィンドウを表示しない（GUI用）
- **`--console`**: コンソールウィンドウを表示する（CLI用、デバッグ用）

---

## よくあるハマりポイント

### 1. パスの問題（最も頻出）
exe化すると、ファイルパスの基準が変わる。
`sys.frozen` と `sys._MEIPASS` を使って適切に処理する必要がある。

### 2. ウイルス対策ソフトの誤検知
PyInstallerで作ったexeは、ウイルス対策ソフトに誤検知されやすい。
→ 社内IT部門への事前申告が必要

### 3. DLL不足エラー
依存ライブラリが使うDLLが同梱されない場合がある。
→ `--hidden-import` や `--add-binary` で手動追加

### 4. Playwrightのブラウザバイナリ
Playwright使用時、ブラウザバイナリ（Chromiumなど）はexeに同梱しない方がよい。
→ 配布先で `playwright install chromium` を実行してもらう

### 5. ファイルサイズが大きい
Pythonランタイムごと同梱するため、100MB以上になることも。
→ `--exclude-module` で不要なモジュールを除外

---

## 読む順番

1. **この `README.md`** — 全体像を把握
2. **`main.py`** — exe化を意識したPythonスクリプトの書き方
3. **`config.json`** — 外部設定ファイルの構造
4. **`build.py`** — ビルドスクリプトの仕組み
5. **`build_guide.md`** — 実際にビルド＆配布する手順
6. **`requirements.txt`** — 依存パッケージ一覧

---

## 改造課題

### 課題1: GUIアプリのexe化
`tkinter` を使った簡単なGUIアプリを作り、`--noconsole` でexe化してみよう。

### 課題2: 設定ファイルの暗号化
`config.json` にパスワードなどを含める場合、暗号化して読み込む仕組みを作ろう。

### 課題3: 自動アップデート機能
exeのバージョンを管理し、新しいバージョンがあれば通知する仕組みを考えてみよう。

### 課題4: ログファイルの出力先
exe実行時にログを `%APPDATA%` 以下に保存するように改造しよう。

### 課題5: 複数環境対応
開発環境（`dev`）と本番環境（`prod`）で設定ファイルを切り替える仕組みを作ろう。
