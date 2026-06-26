# Lv07: Playwrightクリック操作・フォーム自動入力

## テーマ

Playwrightを使ったフォーム操作の自動化を学ぶ。
テキスト入力、ドロップダウン選択、チェックボックス、ラジオボタン、ファイルアップロードなど、
業務自動化で頻出するフォーム操作パターンを網羅的に習得する。

JS/TS経験者向け: PythonのPlaywright同期APIはNode版とほぼ同じメソッド名だが、
`await`不要の同期APIが使える点が大きな違い。

## 動かし方

```bash
# 仮想環境の作成と有効化
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 依存パッケージのインストール
pip install -r requirements.txt

# Playwrightブラウザのインストール（初回のみ）
playwright install chromium

# 実行
python main.py
```

## 学べること

| カテゴリ | 内容 |
|---------|------|
| テキスト入力 | `fill()`, `clear()`, `type()` の使い分け |
| ドロップダウン | `select_option()` で値・ラベル・インデックス指定 |
| チェックボックス/ラジオ | `check()`, `uncheck()`, `is_checked()` |
| ファイルアップロード | `set_input_files()` でファイル選択 |
| キーボード操作 | `press()`, `keyboard.type()`, `keyboard.press()` |
| マウス操作 | `mouse.click()`, `mouse.move()` |
| ダイアログ処理 | `page.on("dialog", ...)` でalert/confirm/promptを処理 |
| 複数タブ | `context.new_page()` でタブを開き切り替え |
| iframe操作 | `frame_locator()` でiframe内要素にアクセス |
| スクリーンショット | 操作前後のスクリーンショットで検証 |

## 読む順番

1. `practice_page.html` - 練習用HTMLページの構造を確認
2. `main.py` - 各フォーム操作のコードを読む（上から順にステップアップ）
3. 実際に `python main.py` を実行してスクリーンショットを確認

## 改造課題

1. **バリデーション確認**: メールアドレスに不正な値を入力し、HTML5バリデーションエラーを検出するコードを書く
2. **フォームリセット**: フォームを埋めた後、全フィールドをクリアしてリセットする処理を追加
3. **動的フォーム**: practice_page.htmlにJSで動的に追加されるフィールドを作り、それを操作するコードを書く
4. **外部サイト練習**: `https://the-internet.herokuapp.com/` の各ページでフォーム操作を試す
5. **データ駆動テスト**: CSVファイルから複数のテストデータを読み込み、ループでフォームに入力する
