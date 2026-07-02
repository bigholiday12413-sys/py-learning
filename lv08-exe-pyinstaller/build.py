"""
Lv08: PyInstallerビルドスクリプト

このスクリプトを実行すると、main.py をexe化する。
PyInstallerのコマンドラインオプションをPythonスクリプトで管理することで、
ビルド設定をバージョン管理しやすくする。

使い方:
  python build.py

ビルドコマンドをスクリプト化しておくことで、
長いオプションを覚えなくても誰でも同じ設定でビルドできるようにする。
"""

import subprocess
import sys
import shutil
from pathlib import Path


# =============================================================================
# ビルド設定
# =============================================================================

# 出力するexeの名前（拡張子は不要）
EXE_NAME = "web_scraper"

# エントリーポイントとなるスクリプト
ENTRY_SCRIPT = "main.py"

# アイコンファイル（.ico形式、無ければNone）
# ICOファイルがあればexeにアイコンが設定される
ICON_FILE = None  # 例: "app_icon.ico"

# =============================================================================
# --onefile vs --onedir の選択
# =============================================================================
# --onefile:
#   - すべてを1つのexeファイルにまとめる
#   - 配布がとにかく楽（ファイル1つ渡すだけ）
#   - 起動時に一時ディレクトリに展開するので起動が少し遅い
#   - ファイルサイズが大きくなりやすい
#
# --onedir:
#   - exeと依存ファイルをフォルダにまとめる
#   - 起動が速い（展開不要）
#   - フォルダごと渡す必要がある
#   - ウイルス対策ソフトの誤検知が少ない傾向
#
# 結論: 社内ツール配布なら --onefile が楽。パフォーマンス重視なら --onedir。
USE_ONEFILE = True

# =============================================================================
# --noconsole vs --console の選択
# =============================================================================
# --console (デフォルト):
#   - コンソールウィンドウ（黒い画面）を表示する
#   - print() の出力が見える
#   - CLIツールやデバッグ時はこちら
#
# --noconsole (--windowed):
#   - コンソールウィンドウを表示しない
#   - GUIアプリ（tkinter等）で使う
#   - print() の出力は見えなくなるので注意
#
# 結論: このツールはCLIなので --console を使う
USE_CONSOLE = True

# =============================================================================
# バンドルするデータファイル
# =============================================================================
# --add-data で指定すると、exeにファイルをバンドルできる。
# 書式: "ソースパス;展開先パス"（Windowsはセミコロン区切り）
#
# 注意: config.json はバンドルしない方がよい！
#   バンドルすると設定変更のたびに再ビルドが必要になる。
#   exeと同じフォルダに config.json を別途配置する運用を推奨。
#
# バンドルするファイルがある場合の例:
# ADD_DATA = [
#     "templates;templates",      # templatesフォルダごとバンドル
#     "assets/logo.png;assets",   # 画像ファイルをバンドル
# ]
ADD_DATA = []

# =============================================================================
# 隠れたインポート（Hidden Imports）
# =============================================================================
# PyInstallerが自動検出できないimportを手動で指定する。
# 動的import（importlib.import_module等）を使っている場合に必要。
#
# 例: Playwrightを使う場合
# HIDDEN_IMPORTS = ["playwright", "playwright.sync_api"]
HIDDEN_IMPORTS = []

# =============================================================================
# 除外するモジュール
# =============================================================================
# 不要なモジュールを除外してexeサイズを小さくする。
# テスト用ライブラリなど、本番で使わないものを指定。
EXCLUDE_MODULES = [
    "unittest",
    "test",
    "tkinter",  # GUIを使わないなら除外してサイズ削減
]


def build():
    """
    PyInstallerを実行してexeを生成する。
    """
    # --- このスクリプトのディレクトリを基準にする ---
    script_dir = Path(__file__).resolve().parent

    # --- 前回のビルド成果物をクリーンアップ ---
    # build/ と dist/ は PyInstaller が自動生成するディレクトリ
    # build/: 中間ファイル（.o, .pyz など）
    # dist/:  完成した exe が出力される
    for cleanup_dir in ["build", "dist"]:
        target = script_dir / cleanup_dir
        if target.exists():
            print(f"クリーンアップ: {target}")
            shutil.rmtree(target)

    # --- .spec ファイルの削除 ---
    # .spec ファイル: PyInstallerのビルド設定ファイル
    # 初回ビルド時に自動生成される
    # このファイルを直接編集してビルドすることも可能:
    #   pyinstaller web_scraper.spec
    spec_file = script_dir / f"{EXE_NAME}.spec"
    if spec_file.exists():
        print(f"クリーンアップ: {spec_file}")
        spec_file.unlink()

    # --- PyInstallerコマンドの構築 ---
    cmd = [
        sys.executable,         # 現在のPython実行ファイル
        "-m", "PyInstaller",    # PyInstallerをモジュールとして実行
    ]

    # ワンファイル or ワンディレクトリ
    cmd.append("--onefile" if USE_ONEFILE else "--onedir")

    # コンソール表示
    cmd.append("--console" if USE_CONSOLE else "--noconsole")

    # exe名の設定
    cmd.extend(["--name", EXE_NAME])

    # アイコンの設定
    if ICON_FILE and (script_dir / ICON_FILE).exists():
        cmd.extend(["--icon", str(script_dir / ICON_FILE)])

    # バンドルデータの追加
    for data in ADD_DATA:
        cmd.extend(["--add-data", data])

    # 隠れたインポートの追加
    for hidden in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", hidden])

    # 除外モジュールの設定
    for exclude in EXCLUDE_MODULES:
        cmd.extend(["--exclude-module", exclude])

    # --- その他の便利なオプション ---
    # --clean: ビルドキャッシュをクリア
    cmd.append("--clean")

    # --noconfirm: 上書き確認をスキップ
    cmd.append("--noconfirm")

    # エントリーポイントのスクリプト
    cmd.append(str(script_dir / ENTRY_SCRIPT))

    # --- コマンドの表示（デバッグ用） ---
    print()
    print("=" * 60)
    print("PyInstaller ビルド開始")
    print("=" * 60)
    print()
    print("実行コマンド:")
    print(f"  {' '.join(cmd)}")
    print()

    # --- ビルド実行 ---
    result = subprocess.run(cmd, cwd=str(script_dir))

    # --- 結果の表示 ---
    print()
    if result.returncode == 0:
        if USE_ONEFILE:
            exe_path = script_dir / "dist" / f"{EXE_NAME}.exe"
        else:
            exe_path = script_dir / "dist" / EXE_NAME / f"{EXE_NAME}.exe"

        print("=" * 60)
        print("ビルド成功！")
        print(f"  exe: {exe_path}")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"  サイズ: {size_mb:.1f} MB")
        print()
        print("配布手順:")
        print(f"  1. {exe_path} をコピー")
        print(f"  2. config.json を同じフォルダに配置")
        print(f"  3. フォルダごと相手に渡す")
        print("=" * 60)
    else:
        print("=" * 60)
        print("ビルド失敗！")
        print("  上のエラーメッセージを確認してください。")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    build()
