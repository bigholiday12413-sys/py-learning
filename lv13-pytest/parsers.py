"""
parsers.py - テスト対象のモジュール

Lv09 のスクレイパーに出てきた「取得した文字列を加工する処理」を
独立した関数として切り出したもの。

★ テストしやすいコードの鉄則:
  「データの加工ロジック」と「ブラウザ操作・通信」を分離する。
  加工ロジックが純粋な関数（入力→出力だけ）になっていれば、
  ブラウザを起動しなくてもテストできる。
"""


def parse_price(price_text: str) -> float:
    """
    価格表示の文字列を数値に変換する。

    例: "£51.77" → 51.77
        "  £51.77  " → 51.77（前後の空白は無視）

    Raises:
        ValueError: 数値に変換できない文字列だった場合
    """
    cleaned = price_text.strip().replace("£", "").replace(",", "")
    return float(cleaned)


def parse_rating(class_attr: str) -> int:
    """
    星評価の CSS クラス文字列から評価値を読み取る（Lv09 の再掲）。

    例: "star-rating Three" → 3
        "star-rating"       → 0（評価情報なし）
    """
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    for part in class_attr.split():
        if part in rating_map:
            return rating_map[part]
    return 0


def normalize_title(title: str, max_length: int = 50) -> str:
    """
    タイトルを整形する。
      - 前後の空白を除去
      - 連続する空白を1つにまとめる
      - max_length を超える場合は末尾を "..." にして切り詰める
    """
    # split() は引数なしだと「任意の空白の連続」で分割するので、
    # join し直すことで空白の正規化になる
    cleaned = " ".join(title.split())

    if len(cleaned) > max_length:
        return cleaned[: max_length - 3] + "..."
    return cleaned


def summarize_by_rating(books: list[dict]) -> dict[int, int]:
    """
    書籍リストを星評価ごとに数える。

    例: [{"rating": 3}, {"rating": 3}, {"rating": 5}]
        → {3: 2, 5: 1}
    """
    counts: dict[int, int] = {}
    for book in books:
        rating = book["rating"]
        counts[rating] = counts.get(rating, 0) + 1
    return counts
