# exe化 ビルド＆配布ガイド

## 1. 環境準備

### 1-1. 仮想環境の作成

```bash
# プロジェクトディレクトリで実行
python -m venv .venv

# 仮想環境を有効化（Windows）
.venv\Scripts\activate

# 有効化の確認（パスが.venv内のPythonを指していればOK）
where python
```

### 1-2. パッケージのインストール

```bash
pip install -r requirements.txt
```

### 1-3. 動作確認（exe化の前に必ず実行）

```bash
python main.py
```

- `output/` フォルダに `result_YYYYMMDD_HHMMSS.html` が保存されれば成功
- `logs/` フォルダにログファイルが出力される

---

## 2. exe化ビルド

### 方法A: ビルドスクリプトを使う（推奨）

```bash
python build.py
```

`build.py` にすべてのオプションがまとまっているので、チームで統一したビルドができる。

### 方法B: PyInstallerを直接実行する

```bash
pyinstaller --onefile --console --name web_scraper --clean --noconfirm main.py
```

### ビルド成果物

```
プロジェクト/
├── build/          ← 中間ファイル（削除してOK）
├── dist/
│   └── web_scraper.exe  ← これが完成したexe！
└── web_scraper.spec     ← ビルド設定ファイル（次回から再利用可能）
```

### .spec ファイルについて

初回ビルド時に自動生成される `.spec` ファイルは、ビルド設定のPythonスクリプト。
次回以降は `.spec` ファイルを指定してビルドすることもできる:

```bash
pyinstaller web_scraper.spec
```

`.spec` ファイルを直接編集すれば、`build.py` より細かい設定が可能。

---

## 3. 配布方法

### 配布物の構成

```
配布フォルダ/
├── web_scraper.exe    ← 実行ファイル
└── config.json        ← 設定ファイル（exeと同じフォルダに配置）
```

### 配布手順

1. `dist/web_scraper.exe` を取り出す
2. `config.json` を `web_scraper.exe` と同じフォルダに配置
3. フォルダごとZIP圧縮して共有（またはファイルサーバーに配置）

### 利用者への案内テンプレート

```
【ツールの使い方】

1. 配布されたZIPファイルを解凍してください
2. config.json の target_url を確認・変更してください
3. web_scraper.exe をダブルクリックで実行してください
4. 処理が完了すると output フォルダに結果が保存されます

※ 初回実行時にWindowsの警告が出る場合は「詳細情報」→「実行」を押してください
※ ウイルス対策ソフトが反応する場合は、IT部門に除外設定を依頼してください
```

---

## 4. よくあるエラーと解決策

### 4-1. ModuleNotFoundError（モジュールが見つからない）

**症状**: exe実行時に「ModuleNotFoundError: No module named 'xxx'」

**原因**: PyInstallerが依存モジュールを検出できなかった

**解決策**:
```bash
# build.py の HIDDEN_IMPORTS に追加
HIDDEN_IMPORTS = ["問題のモジュール名"]

# または直接コマンドで指定
pyinstaller --hidden-import 問題のモジュール名 main.py
```

### 4-2. FileNotFoundError（ファイルが見つからない）

**症状**: exe実行時に「設定ファイルが見つかりません」

**原因**: config.json がexeと同じフォルダに無い

**解決策**:
- config.json を exe と同じフォルダに配置する
- パスの確認: `main.py` の `get_exe_dir()` がexeの場所を正しく返しているか確認

### 4-3. DLL関連エラー

**症状**: exe実行時に「DLL load failed」や「ImportError: DLL load failed」

**原因**: 依存するDLLファイルがexeに同梱されていない

**解決策**:
```bash
# 特定のDLLを手動で追加
pyinstaller --add-binary "パス/to/xxx.dll;." main.py
```

Visual C++ ランタイムが必要な場合は、配布先に以下をインストールしてもらう:
- [Visual C++ 再頒布可能パッケージ](https://learn.microsoft.com/ja-jp/cpp/windows/latest-supported-vc-redist)

### 4-4. ウイルス対策ソフトの誤検知

**症状**: exeがウイルスとして検出される、または削除される

**原因**: PyInstallerのexeは実行時に一時ディレクトリにファイルを展開する挙動が、
マルウェアの振る舞いに似ているためスキャナに検出されやすい。

**解決策**:
1. `--onedir` でビルドすると誤検知率が下がる場合がある
2. 社内IT部門にexeのホワイトリスト登録を依頼する
3. 社内配布用のコード署名証明書でexeに署名する
4. VirusTotalで事前にスキャンして結果を共有する

### 4-5. exeの起動が遅い

**症状**: ダブルクリックから実行開始まで数秒〜十数秒かかる

**原因**: `--onefile` は起動時に一時ディレクトリにすべてのファイルを展開する

**解決策**:
- `--onedir` でビルドすると起動が速くなる（ただしファイル数が増える）
- 依存モジュールを減らして同梱ファイルサイズを削減する
- `--exclude-module` で不要なモジュールを除外する

### 4-6. パスの問題（frozen vs script）

**症状**: スクリプト実行時は動くのに、exe化すると動かない

**原因**: `__file__` や `os.getcwd()` の値がexe化前後で変わる

**解決策**:
`main.py` にある `get_base_path()` と `get_exe_dir()` を使い分ける:

| 用途 | 使う関数 |
|------|----------|
| バンドルしたファイルを読む | `get_base_path()` |
| exe隣の外部ファイルを読む | `get_exe_dir()` |
| ログや出力ファイルを保存する | `get_exe_dir()` |

---

## 5. Playwright + PyInstaller の注意点

### 5-1. 問題の概要

Playwrightはブラウザバイナリ（Chromium等）を別途ダウンロードして使用する。
このブラウザバイナリをexeにバンドルするかどうかが最大の論点。

### 5-2. 方法の比較

| 方法 | メリット | デメリット |
|------|----------|------------|
| バンドルしない（推奨） | exeサイズが小さい、更新が容易 | 初回セットアップが必要 |
| バンドルする | 配布先で追加作業不要 | exeが500MB超、更新が大変 |

### 5-3. 推奨: ブラウザバイナリはバンドルしない

**配布時のセットアップ手順を案内する方式を推奨。**

配布先で一度だけ以下を実行してもらう:

```bash
# Pythonがインストールされていない環境でも、
# npx で playwright をインストールできる
npx playwright install chromium
```

または、Pythonがある環境なら:

```bash
pip install playwright
playwright install chromium
```

### 5-4. ブラウザパスの設定

Playwrightがブラウザを見つけられるように、環境変数を設定する:

```python
import os

# ブラウザバイナリの検索パスを指定
# デフォルト: %LOCALAPPDATA%\ms-playwright
# カスタム: 任意のパスを指定可能
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"  # カレントディレクトリ基準

# または絶対パスで指定
# os.environ["PLAYWRIGHT_BROWSERS_PATH"] = r"C:\browsers"
```

### 5-5. Playwrightをexeにバンドルする場合（非推奨）

どうしてもバンドルしたい場合の手順:

```python
# build.py に追加
import subprocess

# ブラウザのインストール先を確認
result = subprocess.run(
    ["playwright", "install", "--dry-run", "chromium"],
    capture_output=True, text=True
)
print(result.stdout)

# PyInstallerの --add-data でブラウザフォルダをバンドル
# 注意: 300MB以上になる
ADD_DATA = [
    f"{browser_path};playwright/driver/package/.local-browsers",
]
```

**注意**: この方法はexeのサイズが非常に大きくなり（500MB以上）、
ブラウザのアップデートのたびに再ビルドが必要になるため推奨しない。

---

## 6. ビルドのチェックリスト

ビルド前に確認すべき項目:

- [ ] `python main.py` でスクリプトが正常に動作するか
- [ ] `config.json` の設定値は適切か
- [ ] `requirements.txt` に必要なパッケージがすべて記載されているか
- [ ] `build.py` の `EXE_NAME` は適切か
- [ ] `build.py` の `USE_ONEFILE` / `USE_CONSOLE` は適切か
- [ ] 除外モジュール（`EXCLUDE_MODULES`）に必要なものが含まれていないか

ビルド後に確認すべき項目:

- [ ] `dist/` にexeが生成されたか
- [ ] exeのサイズは妥当か（通常 20〜100MB 程度）
- [ ] config.json をexeと同じフォルダに配置したか
- [ ] exe をダブルクリックして正常に動作するか
- [ ] ログファイルが `logs/` フォルダに出力されるか
- [ ] 別のPC（Python未インストール）で動作するか
