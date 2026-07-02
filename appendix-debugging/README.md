# 補講A - エラーの読み方とデバッグ入門

## テーマ

プログラミング学習の時間の半分は「エラーと向き合う時間」。
エラーメッセージ（トレースバック）を **恐れず・読み飛ばさず・下から読む** 習慣がつくと、
学習速度が一気に上がる。

このコースの各レベルには「壊す・直す」という改造課題があるが、
壊したときに何が起きたか読めなければ直せない。その技術をここで身につける。

**読むタイミング: Lv01 を一通り動かした後がおすすめ。**

## 動かし方

```bash
cd appendix-debugging

# エラー一覧を表示
python practice_errors.py

# 番号を指定して、実際にエラーを発生させる（例: 3番）
python practice_errors.py 3
```

---

## 1. トレースバックの読み方

Python がエラーで止まると、こういう表示が出る:

```
Traceback (most recent call last):
  File "main.py", line 25, in <module>
    result = calc_average(scores)
  File "main.py", line 10, in calc_average
    return total / count
ZeroDivisionError: division by zero
```

読み方のルールは3つ:

1. **最後の行から読む。** `ZeroDivisionError: division by zero` がエラーの正体。
   「エラーの種類: 説明」という形式になっている。
2. **最後の `File "...", line N` がエラーの発生場所。**
   この例では main.py の10行目、`calc_average` 関数の中。
3. 上に並んでいるのは「呼び出しの経路」。
   25行目で `calc_average` を呼び → その中の10行目で失敗した、という流れ。

つまり「**一番下がエラーの種類、その1つ上が発生場所**」。
まずこの2行だけ読めば、原因の8割は見当がつく。

### 分からないエラーが出たら

エラーの最後の行（`ZeroDivisionError: division by zero` など）を
**そのままコピーして検索**する。同じエラーで悩んだ人が世界中にいる。

---

## 2. よくあるエラー図鑑

| エラー | 意味 | よくある原因 |
|--------|------|-------------|
| `SyntaxError` | 文法が間違っている | `:` の付け忘れ、括弧・クォートの閉じ忘れ |
| `IndentationError` | インデントがおかしい | スペースの数が揃っていない、タブとスペース混在 |
| `NameError` | その名前は存在しない | 変数名のタイプミス、定義前に使った |
| `TypeError` | 型が合わない | 文字列と数値を `+` した、引数の数が違う |
| `ValueError` | 型は合うが値が不正 | `int("abc")` のような変換失敗 |
| `KeyError` | 辞書にそのキーがない | キー名のタイプミス。`.get()` なら回避可能 |
| `IndexError` | リストにその番号がない | `items[5]` だが要素が3個しかない |
| `AttributeError` | その属性/メソッドはない | メソッド名のタイプミス、`None` に対して操作した |
| `ModuleNotFoundError` | ライブラリが見つからない | `pip install` 忘れ、**venv の有効化忘れ**（頻出！） |
| `FileNotFoundError` | ファイルが見つからない | パスの間違い、実行時のカレントディレクトリ違い |
| `UnicodeDecodeError` | 文字コードが合わない | `encoding=` の指定間違い（Lv02参照） |
| `ZeroDivisionError` | 0で割った | 件数0のデータで平均を計算した など |

`practice_errors.py` でこれらを**実際に発生させて**、表示を目で確認しよう。

---

## 3. print デバッグ — 最初にして最強の手法

「エラーは出ないが結果がおかしい」ときは、途中の値を print で見る。

```python
def calc_average(scores):
    print(f"DEBUG: scores = {scores!r}")   # ← 途中の値を確認
    total = sum(scores)
    count = len(scores)
    print(f"DEBUG: total={total}, count={count}")
    return total / count
```

コツ:

- `f"{変数!r}"` の `!r` を付けると、文字列がクォート付きで表示される。
  `"5"`（文字列）と `5`(数値) の違い、見えない空白などを発見できる
- `print(type(x))` で型を確認する。「数値のつもりが文字列だった」は頻出バグ
- 確認が終わったら DEBUG の print は消す（`DEBUG:` と付けておくと消し忘れを探しやすい）

---

## 4. breakpoint() — プログラムを一時停止して中を覗く

`breakpoint()` を書いた行でプログラムが一時停止し、対話モード（pdb）に入る。

```python
def calc_average(scores):
    breakpoint()          # ← ここで一時停止する
    total = sum(scores)
    return total / len(scores)
```

停止中に使う最低限のコマンド:

| コマンド | 意味 |
|---------|------|
| `p 変数名` | 変数の中身を表示（print） |
| `n` | 次の行へ進む（next） |
| `c` | 停止を解除して続行（continue） |
| `q` | プログラムを終了（quit） |

print を何か所も仕込むより速いことも多い。まずは `p 変数名` と `q` だけ覚えればOK。

---

## 5. Playwright のデバッグ（Lv05 以降で読む）

ブラウザ自動化のエラーはほぼこれ:

```
TimeoutError: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("#submit-btn")
```

「30秒待ったが要素が見つからなかった」という意味。Call log に **どのセレクタを待っていたか** が出るので必ず読む。

チェック手順:

1. `headless=False, slow_mo=500` にして **目で見る**（何が起きているか一目瞭然）
2. セレクタが正しいか、補講B（開発者ツール）の方法で確認する
3. 要素が iframe の中にないか確認する（Lv07参照）
4. エラー直前のスクリーンショットを撮る:
   ```python
   try:
       page.locator("#submit-btn").click()
   except Exception:
       page.screenshot(path="error.png")   # 失敗時の画面を保存
       raise                                # エラー自体は握りつぶさず再送出
   ```

---

## 改造課題

- [ ] `practice_errors.py` の全エラーを一通り発生させて、トレースバックの最終行を読む
- [ ] 各エラーの関数を「エラーが出ないコード」に修正してみよう
- [ ] Lv01 の main.py をわざと1か所壊して、トレースバックから壊した場所を特定する練習をしよう
- [ ] `breakpoint()` を Lv02 の main.py に仕込んで、CSV から読んだ `rows` の中身を `p rows` で覗いてみよう
