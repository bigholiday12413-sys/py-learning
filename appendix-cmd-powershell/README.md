# 補講C - cmd と PowerShell 入門：黒い画面と友達になる

## テーマ

このコースでは「ターミナルにコマンドを打つ」場面が最初から最後まで出てくる。
venv の有効化、pip install、exe の実行、タスクスケジューラへの登録……
すべてターミナル（Windows なら cmd か PowerShell）の上で行う作業だ。

この補講では、Windows の2つのシェル **cmd（コマンドプロンプト）** と **PowerShell** について、

- そもそも何が違うのか、どちらを使えばいいのか
- 権限（管理者権限・実行ポリシー）の基本
- ファイル・フォルダ操作のコマンド
- スクリプト（.bat / .ps1）を書いて自動化する第一歩

を身につける。

**読むタイミング: Lv00 のあと〜Lv03 あたりまでに一度通読推奨。
Lv08（exe化）・Lv12（タスクスケジューラ）の前には特に効いてくる。**

---

## 1. cmd と PowerShell って何が違うの？

どちらも「文字でコマンドを打って Windows を操作する画面（シェル）」だが、世代が違う。

| | cmd（コマンドプロンプト） | PowerShell |
|---|---|---|
| 登場時期 | MS-DOS 時代から続く古参 | 2006年〜。現在の Windows 標準 |
| コマンド体系 | `dir` `copy` `del` など短い独自コマンド | `動詞-名詞` 形式（`Get-ChildItem` など）＋豊富な別名 |
| 扱うデータ | ただの文字列 | オブジェクト（構造化データ） |
| スクリプト | `.bat` / `.cmd` ファイル | `.ps1` ファイル |
| 向いている場面 | 古いバッチ資産・ごく単純な処理 | 日常操作・自動化全般（**基本はこっち**） |

### 結論: 普段は PowerShell を使う

このコースの README のコマンド例もすべて PowerShell 前提。
ただし cmd も現役で残っていて、

- 会社の共有ツールが `.bat` ファイルで配られている
- 古い手順書が cmd のコマンドで書かれている
- venv の有効化スクリプトに `activate.bat`（cmd用）と `Activate.ps1`（PowerShell用）の両方がある

……という形で出会うので、「読める」程度には両方知っておくと強い。

### 開き方

| 方法 | 手順 |
|------|------|
| PowerShell を開く | スタートボタンを右クリック →「ターミナル」（または Win + X → ターミナル） |
| cmd を開く | Win + R → `cmd` と入力 → Enter |
| VS Code 内で開く | `` Ctrl + ` ``（バッククォート）。＋ボタン横の「∨」で cmd / PowerShell を切替できる |
| 今どっちにいるか見分ける | プロンプトが `PS C:\Users\...>` なら PowerShell、`C:\Users\...>`（PSなし）なら cmd |

> **Windows Terminal について**: Windows 11 では「ターミナル」アプリの中で
> PowerShell や cmd をタブとして開く構成になっている。ガワ（ターミナル）と
> 中身（シェル = PowerShell / cmd）は別物、と覚えておくと混乱しない。

---

## 2. 最低限の基本操作（両シェル共通）

| やりたいこと | 操作 |
|-------------|------|
| コマンドを実行 | 入力して Enter |
| 直前のコマンドを呼び出す | ↑キー（さらに前は↑を連打） |
| 入力を補完 | Tab キー（`cd lv0` + Tab でフォルダ名が補完される） |
| 実行中のプログラムを止める | Ctrl + C |
| 画面の文字をコピー | 範囲選択して Ctrl + C（選択中は中断されない） |
| 貼り付け | Ctrl + V または右クリック |
| 画面をきれいにする | `cls`（PowerShell では `clear` も可） |
| シェルを終了 | `exit` |

**Tab 補完と↑履歴は必ず体に叩き込むこと。** コマンドの手打ちはタイプミスの温床。

### プロンプトの読み方

```
PS C:\Users\taro\py-learning>
│  └────────┬────────────┘
│      今いるフォルダ（カレントディレクトリ）
└ PowerShell の印（cmd にはこれが無い）
```

コマンドは常に「今いるフォルダ」を基準に実行される。
`python main.py` が「ファイルが見つからない」と言われたら、
まず自分がどこにいるか（プロンプトのパス）を確認する癖をつけよう。

---

## 3. 権限の基本 — 「管理者として実行」と実行ポリシー

### 3-1. 一般権限と管理者権限

Windows のターミナルには2つのモードがある:

| | 一般（通常起動） | 管理者（管理者として実行） |
|---|---|---|
| できること | 自分のフォルダ内の操作、pip install（venv内）、プログラム実行など日常操作ほぼ全部 | ＋ `C:\Program Files` への書き込み、システム設定変更、サービス操作、全ユーザー向けインストール |
| 見分け方 | タイトルバーが普通 | タイトルバーに「管理者:」と付く |
| 開き方 | 普通に起動 | スタートで「PowerShell」を検索 → 右クリック →「**管理者として実行**」→ UAC（「変更を許可しますか？」画面）で「はい」 |

**原則: 普段は一般権限で作業する。** このコースの内容（venv・pip・python 実行・exe化）は
ほぼすべて一般権限で足りる。管理者が必要なのは例えば:

- ソフトを全ユーザー向けにインストールするとき
- `C:\Program Files` や `C:\Windows` 配下のファイルを触るとき
- `netstat -b` などシステム情報系の一部コマンド

逆に「アクセスが拒否されました / PermissionError」が出たときの原因は、
管理者権限の不足よりも **「そのファイルを別のプログラム（Excel など）が開きっぱなし」**
の方が圧倒的に多い。むやみに管理者で実行して解決しようとしないこと
（管理者で作ったファイルは今度は一般権限で消せなくなったりして、逆に面倒が増える）。

### 3-2. PowerShell の実行ポリシー（ExecutionPolicy）

PowerShell には「`.ps1` スクリプトの実行を制限する」独自の安全装置がある。
Lv00 でも触れた、**venv 有効化で全員が一度はハマるやつ**:

```
.\venv\Scripts\Activate.ps1 : このシステムではスクリプトの実行が無効になっているため、
ファイル ... を読み込むことができません。
```

これはウイルスでもバグでもなく、初期設定が「スクリプト実行禁止（Restricted）」なだけ。

```powershell
# 現在の設定を確認
Get-ExecutionPolicy
# → Restricted なら .ps1 は一切実行できない状態

# 「自分のアカウントに限り、ローカルのスクリプトは実行OK」に変更（推奨設定）
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
# 確認を求められたら Y → Enter
```

- `-Scope CurrentUser` = 自分のユーザーだけに適用。**管理者権限なしで実行できる**
- `RemoteSigned` = 自分のPCで作った/ローカルにあるスクリプトはOK、
  ネットからダウンロードした未署名スクリプトはブロック。安全性と利便性のバランスが良い定番設定
- 一度設定すれば以後ずっと有効。venv を作るたびに実行する必要はない

> cmd にはこの仕組みは無い（`.bat` は無条件で実行される）。
> 「PowerShell だけ venv の有効化でエラーが出る」のはこのため。

---

## 4. ファイル・フォルダ操作コマンド対照表

ここが本丸。cmd と PowerShell の両方を並べておくので、
**PowerShell 列を「使う用」、cmd 列を「読める用」** として覚えるとよい。

| やりたいこと | cmd | PowerShell（正式名） | PowerShell での実際の入力例 |
|-------------|-----|---------------------|---------------------------|
| 今いる場所を表示 | `cd`（引数なし） | `Get-Location` | `pwd` |
| フォルダの中身一覧 | `dir` | `Get-ChildItem` | `ls` または `dir` |
| フォルダ移動 | `cd lv01-hello-python` | `Set-Location` | `cd lv01-hello-python` |
| 1つ上へ | `cd ..` | 同左 | `cd ..` |
| ドライブ移動 | `d:` | 同左 | `cd d:\` |
| フォルダ作成 | `mkdir data` | `New-Item -ItemType Directory` | `mkdir data` |
| ファイル作成（空） | `type nul > memo.txt` | `New-Item memo.txt` | `ni memo.txt` |
| コピー | `copy a.txt b.txt` | `Copy-Item` | `cp a.txt b.txt` |
| フォルダごとコピー | `xcopy /E src dst` | `Copy-Item -Recurse` | `cp -Recurse src dst` |
| 移動 / 名前変更 | `move` / `ren a.txt b.txt` | `Move-Item` / `Rename-Item` | `mv a.txt b.txt` |
| ファイル削除 | `del a.txt` | `Remove-Item` | `rm a.txt` |
| フォルダ削除 | `rmdir /S /Q dir` | `Remove-Item -Recurse` | `rm -Recurse venv` |
| 中身を表示 | `type a.txt` | `Get-Content` | `cat a.txt` |
| 中身を検索 | `findstr "error" log.txt` | `Select-String` | `Select-String error log.txt` |
| ツリー表示 | `tree /F` | ―（cmdの`tree`が使える） | `tree /F` |
| コマンドの説明 | `help copy` | `Get-Help` | `Get-Help Copy-Item -Examples` |

PowerShell の `ls` `cd` `cp` `rm` `cat` は正式コマンド（`Get-ChildItem` など）の
**エイリアス（別名）**。Linux/macOS のコマンド名に寄せてあるので、
PowerShell で覚えたことは Lv00 の macOS 欄ともほぼ共通で使える。

### ⚠ 削除コマンドの注意

`del` / `rm` で消したファイルは **ごみ箱に入らず即消滅** する。
特に `-Recurse`（cmd の `/S`）付きのフォルダ削除は一瞬で丸ごと消える。

- 消す前に `ls` で中身を確認する
- Tab 補完でパスを入れる（手打ちのタイプミスで別フォルダを消す事故が実際にある）
- venv を作り直すときの `rm -Recurse venv` くらいから慣れていく

---

## 5. パスの基礎知識

### 絶対パスと相対パス

```powershell
# 絶対パス: ドライブから書き切る。どこにいても同じ場所を指す
cd C:\Users\taro\py-learning\lv01-hello-python

# 相対パス: 「今いる場所」からの道順
cd lv01-hello-python      # 今いるフォルダの中の lv01-hello-python へ
cd ..\lv02-file-csv       # 1つ上がって隣のフォルダへ
.\venv\Scripts\Activate.ps1   # 「.」= 今いるフォルダ
```

- Windows の区切りは `\`（バックスラッシュ／円記号）。PowerShell では `/` もだいたい通る
- PowerShell では、今いるフォルダのスクリプトや exe を実行するとき
  **必ず `.\` を付ける**（`.\main.exe`）。cmd は `main.exe` だけで動くが、
  PowerShell は安全のため「今のフォルダ」を自動では探さない仕様

### スペースを含むパスは引用符で囲む

```powershell
cd "C:\Users\taro\OneDrive - 会社名\Documents"
# 囲まないと「C:\Users\taro\OneDrive」と「-」と「会社名\Documents」という
# 3つの引数だと解釈されてエラーになる
```

エクスプローラーでフォルダを右クリック →「パスのコピー」を使うと、
引用符付きの絶対パスがコピーできて便利。
逆にターミナルへフォルダを**ドラッグ＆ドロップ**してもパスが入力される。

### 環境変数と PATH

「`python` と打つだけで Python が起動する」のは、
**PATH という環境変数に登録されたフォルダの中からコマンドを探す** 仕組みのおかげ。
インストール時の「Add python.exe to PATH」はこの登録のことだった。

```powershell
# PowerShell: 環境変数の中身を見る
$env:PATH -split ";"      # PATH を1行ずつ表示
$env:USERPROFILE          # 自分のホームフォルダ

# コマンドの実体がどこにあるか調べる（venv が効いているかの確認にも使える）
Get-Command python        # cmd では: where python
```

```bat
:: cmd の場合は %変数名%
echo %PATH%
echo %USERPROFILE%
```

venv を有効化すると、この PATH の先頭に `venv\Scripts` が差し込まれて、
`python` が「venv の中の Python」を指すようになる——というのが venv の正体。
`Get-Command python` の結果が venv 内を指していれば、正しく有効化できている。

---

## 6. PowerShell らしさを少しだけ — パイプとオブジェクト

ここは読み物として。「PowerShell はここまでできる」を知っておくと、
将来シェル芸で作業を短縮できる場面に気づけるようになる。

PowerShell のコマンドは文字列ではなく**オブジェクト**（プロパティを持つデータ）を返し、
`|`（パイプ）で次のコマンドに流し込める。Python でいうと
「リスト内包表記をコマンドでやる」ような感覚:

```powershell
# フォルダ内の .csv だけを、サイズの大きい順に表示
ls *.csv | Sort-Object Length -Descending

# output フォルダ以下から、7日以上前のログファイルを探す
ls output -Recurse -Filter *.log | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }

# 上の結果を削除まで繋げる（実行前に -WhatIf で「もし実行したら」を確認できる）
ls output -Recurse -Filter *.log |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
    Remove-Item -WhatIf
```

`-WhatIf` は「実際には実行せず、何が起きるかだけ表示する」PowerShell 共通の安全スイッチ。
削除系を組んだら、まず `-WhatIf` 付きで試すのが行儀の良い使い方。

Python でも `subprocess` や `pathlib` で同じことができるので、
「使い捨てはシェル、繰り返し使うものは Python スクリプト」と使い分けるのが実務の型。

---

## 7. スクリプト化 — .bat と .ps1 の第一歩

毎回同じコマンド列を打つなら、ファイルに保存して1発実行にできる。
これは Lv08（exe化）や Lv12（タスクスケジューラ）で実際に使うテクニック。

### .bat（cmd 用）— 「ダブルクリックで動く」のが強み

`run_tool.bat` として保存（メモ帳/VS Code で作成。文字コードは ANSI か UTF-8）:

```bat
@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
python main.py
pause
```

| 行 | 意味 |
|----|------|
| `@echo off` | コマンド自体の表示を消して出力を見やすくする |
| `cd /d %~dp0` | **この bat ファイルが置いてあるフォルダ** に移動（定番イディオム。ダブルクリック起動でもカレントが正しくなる） |
| `call venv\...\activate.bat` | venv を有効化（bat から bat を呼ぶときは `call` が必要） |
| `python main.py` | 本体を実行 |
| `pause` | 「続行するには何かキーを...」で画面を止める（結果やエラーを読めるように） |

これを配れば、ターミナルを触れない人でも **ダブルクリックだけ** でツールを実行できる。
Lv09 で作る業務ツールを同僚に渡すときの定番手法。

### .ps1（PowerShell 用）— 書きやすく高機能、ただし実行に一手間

`run_tool.ps1`:

```powershell
# このスクリプトが置いてあるフォルダに移動
Set-Location $PSScriptRoot

# venv を有効化して実行
.\venv\Scripts\Activate.ps1
python main.py
```

実行方法:

```powershell
.\run_tool.ps1
```

注意点:

- 第3章の実行ポリシー設定（`RemoteSigned`）が済んでいることが前提
- `.ps1` は **ダブルクリックしても実行されない**（既定ではメモ帳等で開くだけ）。
  これはセキュリティ上わざとそうなっている
- ダブルクリック配布したいなら `.bat` を使うか、`.bat` から `.ps1` を呼ぶ:

```bat
@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_tool.ps1"
pause
```

> `-ExecutionPolicy Bypass` は「この1回の起動に限り実行ポリシーを無視する」指定。
> 自分で書いたスクリプトを自分のPCで動かす用途では定番だが、
> 出所不明の bat/ps1 でこれを見たら中身を読んでから実行すること。

---

## 8. このコースで実際に使う場面 まとめ

| 場面 | 使うもの |
|------|---------|
| venv 有効化（PowerShell） | `.\venv\Scripts\Activate.ps1`（要・実行ポリシー設定） |
| venv 有効化（cmd） | `venv\Scripts\activate.bat` |
| pip でライブラリ導入 | `pip install -r requirements.txt`（一般権限でOK） |
| Lv08: exe をターミナルから試す | `.\dist\main.exe`（PowerShell は `.\` を忘れずに） |
| Lv09: ツールを同僚に配る | `.bat` でダブルクリック起動をお膳立て |
| Lv12: タスクスケジューラ登録 | 「プログラム」欄に bat/exe のパス、「開始（オプション）」欄に作業フォルダを指定 |
| ログをさっと確認 | `cat output\app.log` / `Select-String ERROR output\app.log` |

---

## 動作確認チェックリスト

- [ ] PowerShell と cmd をそれぞれ開いて、プロンプトの違い（`PS` の有無）を確認した
- [ ] `Get-ExecutionPolicy` の結果を確認し、必要なら `RemoteSigned` に変更した
- [ ] `mkdir` → `ni`（ファイル作成） → `cp` → `mv` → `rm` を練習フォルダで一通り試した
- [ ] スペース入りのパスを引用符付きで `cd` できた
- [ ] `Get-Command python` で python の実体パスを確認した（venv 有効化前後で見比べると◎）
- [ ] `.bat` ファイルを1つ作ってダブルクリックで動かした

ここまでできれば、このコースのターミナル操作で詰まることはほぼ無い。
エラーが出たときは `TROUBLESHOOTING.md` と補講A（エラーの読み方）も参照。
