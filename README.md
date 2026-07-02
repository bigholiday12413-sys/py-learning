# Python + Playwright 学習ロードマップ（Lv0〜Lv16＋補講）

プログラミング経験がなくても、Python の基礎から始めて **Playwrightでブラウザ操作する exe ファイル** を作れるようになるまでの、段階的な学習コースです。
前提知識は不要。すべてのコードに日本語の解説コメントが付いています。

- 📋 **[ABOUT.md](ABOUT.md)** — このリポジトリの目的と最終ゴール

## 前提条件

- Python 3.11 以上がインストール済み
- `pip` コマンドが使える状態

```powershell
python --version   # Python 3.11.x 以上を確認
pip --version      # pip が使えることを確認
```

まだ環境がない人・上のコマンドが動かない人は **[lv00-setup](lv00-setup/README.md)** から始めよう
（Python のインストール、VS Code、ターミナルの基本、venv の予行演習まで解説）。

## 学習マップ

| Lv | フォルダ | テーマ | 学べること |
|----|---------|--------|-----------|
| 0 | `lv00-setup` | 環境構築 | Pythonインストール・VS Code・ターミナル・venv |
| 1 | `lv01-hello-python` | Python入門 | 変数・型・関数・if/for・リスト・辞書・f文字列 |
| 2 | `lv02-file-csv` | ファイル操作とCSV | open/with文・csv読み書き・pathlib・エンコーディング |
| 3 | `lv03-class-module` | クラスとモジュール | class・dataclass・import・pip・venv(仮想環境) |
| 4 | `lv04-web-scraping` | Webスクレイピング入門 | requests・BeautifulSoup・HTMLパース・セレクタ |
| 5 | `lv05-playwright-basics` | Playwright基礎 | ブラウザ起動・ページ遷移・要素取得・クリック |
| 6 | `lv06-playwright-scraping` | Playwrightスクレイピング | 動的サイト取得・待機戦略・スクリーンショット・PDF |
| 7 | `lv07-playwright-forms` | フォーム自動操作 | 入力・選択・チェック・ファイルアップロード・複数タブ |
| 8 | `lv08-exe-pyinstaller` | exe化 | PyInstaller・設定ファイル外出し・アイコン設定 |
| 9 | `lv09-gyomu-tool` | 実践：業務自動化ツール | 設定→ログイン→スクレイピング→操作→CSV出力→exe化 |

### 発展編（Lv9 完走後。Lv9 のツールを実務運用レベルに育てる）

| Lv | フォルダ | テーマ | 学べること |
|----|---------|--------|-----------|
| 10 | `lv10-excel-report` | Excelレポート出力 | openpyxl・書式設定・複数シート・集計・数式埋め込み |
| 11 | `lv11-sqlite-diff` | データ蓄積と差分検知 | SQLite・SQL基礎・スナップショット比較・価格監視 |
| 12 | `lv12-scheduler-notify` | 定期実行と通知 | schedule・タスクスケジューラ・Slack/ChatWork Webhook |
| 13 | `lv13-pytest` | テスト入門 | pytest・parametrize・fixture・テストしやすい設計 |

発展編は Lv10→13 の順でなくてもよい。興味のあるものから着手してOK
（Lv12 は Lv11 と組み合わせると効果が大きい／Lv13 はどのタイミングでも役立つ）。

### フレームワーク編（王道フレームワークの導入と活用）

| Lv | フォルダ | フレームワーク | 何ができるようになるか |
|----|---------|---------------|----------------------|
| 14 | `lv14-pandas` | pandas | データ処理の王道。Lv02の手書き集計が数行になる |
| 15 | `lv15-streamlit` | Streamlit | スクリプトがそのままWebアプリに。社内ツールUIの定番 |
| 16 | `lv16-fastapi` | FastAPI | ツールをWeb API化。他システムから呼べる窓口を作る |

**3つの役割分担**: pandas = データを加工する / Streamlit = 人間に見せる画面 / FastAPI = プログラムに提供する窓口。
Lv9のツールを核に、この3つを組み合わせると「取得 → 加工 → 画面とAPIで提供」の実務構成が完成する。

### 補講（本編と並行して読む）

| フォルダ / ファイル | テーマ | 読むタイミング |
|--------------------|--------|---------------|
| `appendix-debugging` | エラーの読み方・print/breakpoint デバッグ | Lv1 のあと |
| `appendix-devtools` | CSSセレクタの調べ方（F12・codegen） | Lv4 の途中 |
| `TROUBLESHOOTING.md` | よくあるつまずきFAQ（venv・文字化け・Playwright・exe） | 詰まったとき随時 |

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
3. **壊す・直す** — 値を変えたり機能を足したりして挙動を確認（各READMEに「改造課題」あり）。
   エラーが出たら `appendix-debugging` の読み方でトレースバックを解読する
4. 詰まったら前のレベルに戻ってOK。Lv5以降はLv1〜4の知識を前提にしています。
   環境や実行のトラブルは `TROUBLESHOOTING.md` を参照
