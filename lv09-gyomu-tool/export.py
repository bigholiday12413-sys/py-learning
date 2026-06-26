"""
export.py - データ出力モジュール（CSV・JSON・サマリー）

スクレイピングで取得したデータをファイルに書き出すモジュール。

JS/TS との対比:
  - csv モジュール → npm の csv-writer や papaparse
  - json.dumps() → JSON.stringify()
  - open() + write() → fs.writeFileSync()
  - encoding="utf-8-sig" → BOM付きUTF-8（Excel対応）
"""

import csv
import json
import os
from datetime import datetime


def save_to_csv(data: list[dict], output_config: dict) -> str:
    """
    データをCSVファイルに保存する。

    日本語を含むCSVをExcelで開くために、UTF-8 BOM付き（utf-8-sig）で出力する。
    これは日本語環境のExcelでよくある文字化け対策。

    JS/TS との対比:
      - csv.DictWriter → npm の csv-writer
      - writeheader() → ヘッダー行を書き込む
      - writerows() → データ行をまとめて書き込む
      - '﻿' (BOM) → Node.js でも同じテクニックが使える

    Args:
        data: 出力するデータ（辞書のリスト）
        output_config: config.json の output セクション

    Returns:
        出力したファイルのパス
    """
    if not data:
        return ""

    # --- 出力ディレクトリを作成 ---
    output_dir = output_config["output_dir"]
    os.makedirs(output_dir, exist_ok=True)

    # --- ファイル名を生成 ---
    prefix = output_config["filename_prefix"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)

    # --- CSVを書き出す ---
    # encoding="utf-8-sig" で BOM 付き UTF-8 にする（Excelで文字化けしない）
    # JS では fs.writeFileSync(path, '﻿' + csvContent, 'utf-8') と書く
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        # --- ヘッダー行を最初のデータのキーから自動生成 ---
        # JS: Object.keys(data[0])
        fieldnames = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)

    return filepath


def save_to_json(data: list[dict], output_config: dict) -> str:
    """
    データをJSONファイルに保存する。

    JS/TS との対比:
      - json.dumps(data, ensure_ascii=False) → JSON.stringify(data, null, 2)
      - ensure_ascii=False → 日本語をそのまま出力（エスケープしない）
      - indent=2 → 見やすいインデント付き出力

    Args:
        data: 出力するデータ
        output_config: config.json の output セクション

    Returns:
        出力したファイルのパス
    """
    if not data:
        return ""

    # --- 出力ディレクトリを作成 ---
    output_dir = output_config["output_dir"]
    os.makedirs(output_dir, exist_ok=True)

    # --- ファイル名を生成 ---
    prefix = output_config["filename_prefix"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    # --- JSONを書き出す ---
    # ensure_ascii=False で日本語をそのまま出力する
    # JS: JSON.stringify(data, null, 2)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def generate_summary(results: dict) -> str:
    """
    処理結果のサマリーテキストを生成する。

    JS/TS との対比:
      - f-string → テンプレートリテラル `${variable}`
      - 三重クォート（\"\"\"...\"\"\"） → テンプレートリテラルの複数行版

    Args:
        results: 処理結果の辞書

    Returns:
        サマリーテキスト
    """
    start = results.get("start_time", datetime.now())
    end = results.get("end_time", datetime.now())
    duration = end - start

    # --- 分と秒に変換 ---
    total_seconds = int(duration.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    # --- サマリーテキストを組み立てる ---
    # f-string は JS のテンプレートリテラルと同じ使い方
    summary = f"""{'=' * 50}
  処理結果サマリー
{'=' * 50}

開始時刻: {start.strftime('%Y-%m-%d %H:%M:%S')}
終了時刻: {end.strftime('%Y-%m-%d %H:%M:%S')}
処理時間: {minutes}分 {seconds}秒

取得データ件数: {results.get('scraped_count', 0)} 件
実行アクション: {results.get('action_count', 0)} 件

出力ファイル:"""

    # --- 出力ファイル一覧 ---
    exported_files = results.get("exported_files", [])
    if exported_files:
        for f in exported_files:
            summary += f"\n  - {f}"
    else:
        summary += "\n  なし"

    # --- エラー情報 ---
    errors = results.get("errors", [])
    if errors:
        summary += f"\n\nエラー ({len(errors)} 件):"
        for err in errors:
            summary += f"\n  - {err}"
    else:
        summary += "\n\nエラー: なし"

    summary += f"\n\n{'=' * 50}"

    return summary
