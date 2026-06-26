@echo off
REM ============================================
REM  業務自動化ツール ビルドスクリプト
REM  exe化してconfig.jsonと一緒に配布する
REM ============================================

echo ========================================
echo  業務自動化ツール - ビルド開始
echo ========================================

REM 仮想環境を有効化
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo [OK] 仮想環境を有効化しました
) else (
    echo [警告] 仮想環境が見つかりません。グローバル環境で実行します。
)

REM PyInstaller がインストールされているか確認
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller をインストールします...
    pip install pyinstaller
)

REM ビルド実行
echo.
echo [INFO] exe ファイルをビルドしています...
python -m PyInstaller --onefile --name gyomu-tool main.py

if errorlevel 1 (
    echo.
    echo [エラー] ビルドに失敗しました。
    pause
    exit /b 1
)

REM config.json を dist/ にコピー
echo.
echo [INFO] config.json を dist/ にコピーしています...
copy /Y config.json dist\config.json

echo.
echo ========================================
echo  ビルド完了！
echo  dist\gyomu-tool.exe が生成されました。
echo  config.json と一緒に配布してください。
echo ========================================
echo.
pause
