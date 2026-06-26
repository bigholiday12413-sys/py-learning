# Lv02 - ファイル操作と CSV

## テーマ

Python のファイル操作と CSV の読み書きを学ぶ。
`open()` / `with` 文 / `csv` モジュール / `pathlib` など、
JS/TS にはない Python らしいファイル処理パターンを体験する。

## 動かし方

```bash
cd py-learning/lv02-file-csv
python main.py
```

※ Python 3.10 以上を推奨。`python --version` で確認できる。
※ 実行すると `output/` フォルダに結果ファイルが生成される。

## 学べること

| # | トピック | JS/TS との対応 |
|---|---------|---------------|
| 1 | `open()` と読み書きモード (`r`, `w`, `a`) | `fs.readFileSync` / `fs.writeFileSync` |
| 2 | `with` 文 (コンテキストマネージャ) | `try/finally` でリソース解放するパターン |
| 3 | テキストファイルの読み書き | Node.js の `fs` モジュール |
| 4 | `csv.reader` / `csv.writer` | npm の `csv-parse` / `csv-stringify` |
| 5 | `csv.DictReader` / `csv.DictWriter` | オブジェクト配列としての CSV 処理 |
| 6 | `pathlib.Path` (モダンなパス操作) | Node.js の `path` モジュール |
| 7 | `os.path` vs `pathlib` の比較 | ― |
| 8 | `encoding` パラメータ (`utf-8`, `shift_jis`) | Node.js の `iconv-lite` など |

## 読む順番

1. この README を読む
2. `data/sample.csv` のデータを確認する
3. `main.py` を上から順に読む（コメントが詳しく書いてある）
4. 実際に `python main.py` で動かしてみる
5. `output/` に生成されたファイルを確認する
6. コードを改造して遊ぶ

## 改造課題

- [ ] CSV に「給与」列を追加して、部署ごとの平均給与を計算してみよう
- [ ] `data/` に自分で新しい CSV を作り、それを読み込むコードを書いてみよう
- [ ] JSON ファイルの読み書きも追加してみよう (`json` モジュール)
- [ ] `output/` に Excel 風の TSV (タブ区切り) ファイルを出力してみよう
- [ ] コマンドライン引数で入力ファイル名を指定できるようにしてみよう (`sys.argv`)
- [ ] `pathlib` を使って `output/` 内のファイル一覧を表示してみよう
