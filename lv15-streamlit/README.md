# Lv15 - Streamlit：スクリプトを社内Webツールにする【フレームワーク編】

## テーマ

**Streamlit** は「Python スクリプトがそのまま Web アプリになる」フレームワーク。
HTML / CSS / JavaScript を1行も書かずに、絞り込みUI・グラフ・ダウンロードボタン付きの
ツール画面が作れる。社内向けデータツールの現代的な定番。

Lv08 では exe で配布したが、Streamlit は別の配布戦略:
**「1台のPCやサーバーで動かして、みんなにはURLを配る」**。

## 動かし方

```bash
cd lv15-streamlit
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows / macOSは source venv/bin/activate
pip install -r requirements.txt

# ★ python ではなく streamlit コマンドで起動する
streamlit run app.py
```

ブラウザが自動で開く（開かなければ http://localhost:8501 へ）。
終了はターミナルで `Ctrl + C`。

## 最重要: Streamlit の動作モデル

> **画面の部品を操作するたびに、スクリプト全体が上から再実行される。**

```python
min_rating = st.slider("星評価（以上）", 1, 5, 1)   # ← スライダーの「現在値」が返る
filtered = df[df["rating"] >= min_rating]           # ← 普通のPythonで絞り込むだけ
st.dataframe(filtered)                              # ← 表を表示
```

スライダーを動かす → スクリプト再実行 → `min_rating` が新しい値になる → 画面が更新される。
イベント処理やコールバックを書かなくても、**上から下に読めるスクリプトのまま**画面が動く。
これが Streamlit が「Python 使いにとって最速のUI」と言われる理由。

## 学べること

| トピック | ひとことで言うと |
|---------|----------------|
| `st.title` / `st.caption` / `st.subheader` | 見出しとテキスト |
| `st.sidebar` | 左サイドバーに条件入力をまとめる |
| `st.slider` / `st.number_input` / `st.multiselect` | 入力部品（現在値が返る関数） |
| `st.columns` + `st.metric` | ダッシュボードの数字表示 |
| `st.dataframe` | ソート・検索付きのインタラクティブ表 |
| `st.bar_chart` | 1行グラフ |
| `st.download_button` | 絞り込み結果をCSV/Excelで配布 |
| `st.button` + `st.spinner` | 「実行ボタン+実行中表示」パターン |
| `BytesIO` | ディスクを経由せずメモリ上でExcelを作る |

## exe（Lv08）との使い分け

| | exe 配布 (Lv08) | Streamlit (Lv15) |
|--|----------------|------------------|
| 配るもの | exe ファイル | URL |
| 実行場所 | 各自のPC | 1か所（サーバー/自分のPC） |
| 更新 | 全員に再配布 | サーバー側を1回更新するだけ |
| 向き | オフライン・個人ツール | チームで共有するツール・ダッシュボード |

## 読む順番

1. この README（特に「動作モデル」）
2. `app.py` を上から読む
3. `streamlit run app.py` で起動し、サイドバーの条件を動かして再実行を体感する
4. 改造課題へ

## 改造課題

- [ ] 価格の下限スライダーも追加して、価格帯で絞れるようにしよう
- [ ] `st.tabs()` で「一覧」「グラフ」「集計」の3タブ構成にしてみよう
- [ ] Lv11 の SQLite から読み込むようにして、スナップショット選択機能を付けよう（`st.selectbox`）
- [ ] 「🔄 最新データを取得する」ボタンに Lv09 の実スクレイパーを接続しよう
- [ ] `st.session_state` を調べて、ボタンで取得したデータを再実行後も保持できるようにしよう（1段上の理解）

## 補足: 公開・共有の選択肢

- 社内LANなら `streamlit run app.py --server.address 0.0.0.0` で同一ネットワークから閲覧可能
  （社内ルールとセキュリティを必ず確認すること）
- Streamlit Community Cloud を使うと無料でインターネット公開もできる
  （業務データを載せないこと。公開範囲の判断は慎重に）
