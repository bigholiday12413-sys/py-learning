# Lv01 - Hello Python: はじめての Python

## テーマ

JS/TS 経験者が Python の基本文法を一通り体験する。
変数・型・文字列・リスト・辞書・関数・条件分岐・ループなど、
JavaScript との違いを意識しながら学ぶ。

## 動かし方

```bash
cd py-learning/lv01-hello-python
python main.py
```

※ Python 3.10 以上を推奨。`python --version` で確認できる。

## 学べること

| # | トピック | JS/TS との対応 |
|---|---------|---------------|
| 1 | 変数宣言 | `const` / `let` が不要 |
| 2 | データ型 (str, int, float, bool, None) | string, number, boolean, null/undefined |
| 3 | f-string | テンプレートリテラル `` `${x}` `` |
| 4 | リスト (list) | 配列 `[]` |
| 5 | 辞書 (dict) | オブジェクト `{}` |
| 6 | 関数 (def / lambda) | `function` / アロー関数 |
| 7 | 条件分岐 (if/elif/else) | `if/else if/else` + `{}` |
| 8 | for / while ループ | `for...of` / `while` |
| 9 | Truthy / Falsy | JS よりシンプルなルール |
| 10 | 型ヒント (Type Hints) | TypeScript の型注釈 |
| 11 | print フォーマット | `console.log` |

## 読む順番

1. この README を読む
2. `main.py` を上から順に読む（コメントが詳しく書いてある）
3. 実際に `python main.py` で動かしてみる
4. コードを改造して遊ぶ

## 改造課題

- [ ] 自己紹介の項目を増やしてみよう（趣味、好きな食べ物など）
- [ ] BMI を計算する関数を追加してみよう
- [ ] リストの中身をソートして表示してみよう (`sorted()`)
- [ ] 辞書に新しいキーを追加してみよう
- [ ] `while` ループで「3回まで名前入力をやり直せる」仕組みを作ってみよう
- [ ] `match` 文 (Python 3.10+) を使って好きな言語に応じたメッセージを出してみよう
