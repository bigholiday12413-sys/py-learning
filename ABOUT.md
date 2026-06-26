# このリポジトリについて

## 目的

Python未経験のJS/TS開発者が、**最短ルートで Playwright によるブラウザ自動操作 exe** を作れるようになること。

## 最終ゴール

- Playwright でWebサイトにログインし、画面をスクレイピングし、ボタンをクリックする
- その処理を PyInstaller で **exe ファイル** にパッケージングする
- 設定ファイル（JSON/TOML）を外出しして、コード変更なしで対象サイトや操作を切り替えられるようにする

## JSとの対応表（頭の中で変換するためのガイド）

| JavaScript / TypeScript | Python |
|------------------------|--------|
| `const` / `let` | 変数代入（宣言キーワード不要） |
| `console.log()` | `print()` |
| `===` | `==`（Pythonは型強制しない） |
| `null` / `undefined` | `None` |
| `true` / `false` | `True` / `False` |
| `if (...) { }` | `if ...:` （インデントでブロック） |
| `for (const x of arr)` | `for x in arr:` |
| `array.map(fn)` | `[fn(x) for x in arr]`（リスト内包表記） |
| `array.filter(fn)` | `[x for x in arr if cond]` |
| `{ key: value }` | `{"key": value}`（dict） |
| `interface` / `type` | `dataclass` / `TypedDict` |
| `async/await` | `async/await`（asyncioベース） |
| `npm install` | `pip install` |
| `package.json` | `requirements.txt` / `pyproject.toml` |
| `node_modules/` | `venv/`（仮想環境） |
| `.gitignore` に `node_modules/` | `.gitignore` に `venv/` |

## 各レベルの所要時間目安

| Lv | 所要時間 | 備考 |
|----|---------|------|
| 1 | 30分 | JS経験者なら読むだけでOK |
| 2 | 30分 | with文とpathlib がポイント |
| 3 | 45分 | dataclass は TS の interface に近い |
| 4 | 45分 | requests + BS4 は定番 |
| 5 | 1時間 | Playwright の核心。ここからが本番 |
| 6 | 1時間 | 待機戦略が実務の肝 |
| 7 | 1時間 | フォーム操作パターン集 |
| 8 | 45分 | exe化のハマりポイントを押さえる |
| 9 | 2時間 | 総合演習。ここが完成すればゴール |
