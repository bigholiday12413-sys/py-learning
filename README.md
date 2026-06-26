# Python + Playwright 学習ロードマップ（Lv1〜Lv9）

Python未経験から **Playwrightでブラウザ操作する exe ファイル** を作れるようになるまでの、段階的な学習コースです。
すべてのコードに日本語の解説コメントが付いています。

- 📋 **[ABOUT.md](ABOUT.md)** — このリポジトリの目的と最終ゴール

## 前提条件

- Python 3.11 以上がインストール済み
- `pip` コマンドが使える状態

```powershell
python --version   # Python 3.11.x 以上を確認
pip --version      # pip が使えることを確認
```

## 学習マップ

| Lv | フォルダ | テーマ | 学べること |
|----|---------|--------|-----------|
| 1 | `lv01-hello-python` | Python入門 | 変数・型・関数・if/for・リスト・辞書・f文字列 |
| 2 | `lv02-file-csv` | ファイル操作とCSV | open/with文・csv読み書き・pathlib・エンコーディング |
| 3 | `lv03-class-module` | クラスとモジュール | class・dataclass・import・pip・venv(仮想環境) |
| 4 | `lv04-web-scraping` | Webスクレイピング入門 | requests・BeautifulSoup・HTMLパース・セレクタ |
| 5 | `lv05-playwright-basics` | Playwright基礎 | ブラウザ起動・ページ遷移・要素取得・クリック |
| 6 | `lv06-playwright-scraping` | Playwrightスクレイピング | 動的サイト取得・待機戦略・スクリーンショット・PDF |
| 7 | `lv07-playwright-forms` | フォーム自動操作 | 入力・選択・チェック・ファイルアップロード・複数タブ |
| 8 | `lv08-exe-pyinstaller` | exe化 | PyInstaller・設定ファイル外出し・アイコン設定 |
| 9 | `lv09-gyomu-tool` | 実践：業務自動化ツール | 設定→ログイン→スクレイピング→操作→CSV出力→exe化 |

## 動かし方

### Lv1〜Lv3（標準ライブラリのみ）

```powershell
cd lv01-hello-python
python main.py
```

### Lv4〜Lv9（外部ライブラリを使用）

```powershell
cd lv04-web-scraping

# 仮想環境を作成して有効化（初回のみ）
python -m venv venv
.\venv\Scripts\Activate.ps1

# ライブラリをインストール（初回のみ）
pip install -r requirements.txt

# Lv5以降は Playwright のブラウザもインストール（初回のみ）
playwright install chromium

# 実行
python main.py
```

## おすすめの進め方

1. **コードを読む** — 各ファイルの解説コメントを上から読む
2. **動かす** — `python main.py` で実行して結果を確認
3. **壊す・直す** — 値を変えたり機能を足したりして挙動を確認（各READMEに「改造課題」あり）
4. 詰まったら前のレベルに戻ってOK。Lv5以降はLv1〜4の知識を前提にしています
