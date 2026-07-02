# トラブルシューティング — よくあるつまずきと対処法

コースを進めていて動かなくなったら、まずここを見る。
（エラーメッセージの読み方そのものは `appendix-debugging/` を参照）

---

## 環境まわり

### `python` コマンドが認識されない

```
'python' は、内部コマンドまたは外部コマンド、操作可能なプログラム
またはバッチ ファイルとして認識されていません。
```

- **原因**: インストール時に「Add python.exe to PATH」のチェックを忘れた
- **対処1**: `py --version` を試す。動くなら `python` を `py` に読み替えて進められる
- **対処2**: Python をアンインストール → 再インストールし、最初の画面で PATH のチェックを入れる

### venv の有効化で「スクリプトの実行が無効」エラー（Windows）

```
.\venv\Scripts\Activate.ps1 : このシステムではスクリプトの実行が無効になっているため...
```

PowerShell のセキュリティ設定が原因。一度だけ以下を実行:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

`Y` を入力後、あらためて `.\venv\Scripts\Activate.ps1` を実行する。

### `pip install` したのに `ModuleNotFoundError` が出る

- **原因の9割**: venv を有効化していない状態で実行している
- **確認**: プロンプトの先頭に `(venv)` が表示されているか
- venv 有効化 → `pip list` で目的のライブラリが入っているか確認 → 無ければ `pip install -r requirements.txt`
- VS Code の ▶ ボタンで実行している場合は、右下の Python インタープリタ表示をクリックして
  `venv` 内の Python（`.\venv\Scripts\python.exe`）を選択する

### 会社のネットワークで `pip install` が失敗する（SSL/プロキシ）

```
WARNING: Retrying ... ProxyError / SSLError
```

- 社内プロキシ環境が原因のことが多い。IT部門にプロキシ設定（`--proxy` オプションや証明書）を確認する
- 自宅ネットワークで試すと切り分けができる

---

## 文字化け・文字コードまわり

### `print()` で `UnicodeEncodeError: 'cp932' codec can't encode ...`

Windows のコンソールが古い文字コード（cp932）で動いているのが原因。
一番簡単な対処は、環境変数で Python を UTF-8 モードにすること:

```powershell
# PowerShell（そのセッションだけ有効）
$env:PYTHONUTF8 = "1"
python main.py
```

恒久的にしたい場合は、システムの環境変数に `PYTHONUTF8=1` を追加する。

### 出力した CSV を Excel で開くと文字化けする

- `encoding="utf-8"` ではなく **`encoding="utf-8-sig"`**（BOM付き）で出力する（Lv02・Lv04参照）
- すでに utf-8 で出力済みのファイルは、メモ帳で開いて「UTF-8 (BOM付き)」で保存し直せば読める

### CSV の読み込みで `UnicodeDecodeError`

- そのファイルの文字コードと `encoding=` の指定が合っていない
- 日本語の業務CSV（Excel出力）は `encoding="cp932"`（Shift-JIS）のことが多い。
  `utf-8` → ダメなら `cp932` → ダメなら `utf-8-sig` の順に試す（Lv02参照）

---

## Playwright まわり

### `playwright install` していないというエラー

```
BrowserType.launch: Executable doesn't exist at ...
╔══ Looks like Playwright was just installed or updated. ══╗
```

メッセージの指示どおり、venv を有効化した状態で実行する:

```powershell
playwright install chromium
```

### `TimeoutError: Timeout 30000ms exceeded`

「指定した要素が制限時間内に見つからなかった」という意味。チェック順:

1. `headless=False, slow_mo=500` にして **目で見て** 何が起きているか確認
2. エラーの `Call log` に出ているセレクタが正しいか、DevTools の Ctrl+F 検索で確認（補講B参照）
3. 要素が iframe の中にないか（`frame_locator` が必要。Lv07参照）
4. ページの読み込みが遅いだけなら `page.wait_for_selector(..., timeout=60000)` のように延長

### ブラウザは開くが真っ白のまま / ページが表示されない

- ネットワーク（プロキシ）の問題か、対象サイトがボットを弾いている可能性
- まず `page.goto("https://books.toscrape.com/")` のような練習サイトで動作確認し、
  コードの問題かサイト側の問題かを切り分ける

---

## exe 化（PyInstaller）まわり

### 作った exe がウイルス対策ソフトに削除される

- PyInstaller 製 exe は誤検知されやすい（Lv08参照）
- 社内配布の場合は IT 部門に事前申告して除外設定してもらうのが正攻法

### exe を実行すると一瞬で閉じて何も分からない

- コンソールがエラー表示と同時に閉じている
- **PowerShell から exe を実行する**とメッセージが残る:
  ```powershell
  cd dist
  .\gyomu-tool.exe
  ```
- Lv08 の main.py のように、終了前に `input()` で待つ実装にしておくのも有効

### exe にすると config.json が読めない

- exe 化するとパスの基準が変わるのが原因。`sys.frozen` / `sys.executable` を使った
  パス解決が必要（Lv08 の `get_exe_dir()` を参照）
- config.json は **exe と同じフォルダ** に置く

---

## それでも解決しないとき

1. エラーメッセージの **最後の行** をそのままコピーして Web 検索する
2. 「最小の再現コード」を作る — 問題の処理だけを10行程度に切り出して単体で動かすと、
   原因の切り分けが一気に進む
3. 前のレベルの動くコードと **差分を見比べる**（何を変えたら壊れたのか）
