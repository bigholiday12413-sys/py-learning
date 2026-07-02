"""
test_parsers.py - parsers.py のテスト

実行方法:
    pytest            # このフォルダの全テストを実行
    pytest -v         # 各テストの名前も表示（最初はこちらが分かりやすい）

pytest のルール:
  - ファイル名が test_*.py のものをテストとして探す
  - その中の test_ で始まる関数を1つずつ実行する
  - assert 文が全て成立すれば PASS、1つでも失敗すれば FAIL
"""

import pytest

from parsers import normalize_title, parse_price, parse_rating, summarize_by_rating


# ============================================================
# 1. 一番シンプルなテスト ─ assert するだけ
# ============================================================
# assert 式 は「式が True でなければエラーにする」文。
# pytest は失敗時に「期待値と実際の値」を親切に表示してくれる。


def test_parse_price_basic():
    """基本形: £付き価格が float になる"""
    assert parse_price("£51.77") == 51.77


def test_parse_price_with_spaces():
    """前後に空白があっても変換できる"""
    assert parse_price("  £51.77  ") == 51.77


def test_parse_price_with_comma():
    """桁区切りカンマ入りも変換できる"""
    assert parse_price("£1,234.50") == 1234.50


# ============================================================
# 2. 「エラーになること」をテストする
# ============================================================
# 異常系のテスト。pytest.raises で「この例外が出るはず」を表明する。
# 例外が出なかったらテスト失敗になる。


def test_parse_price_invalid_text():
    """数値でない文字列は ValueError になる"""
    with pytest.raises(ValueError):
        parse_price("価格未定")


# ============================================================
# 3. parametrize ─ 同じテストを複数データで回す
# ============================================================
# 入力と期待値のペアを並べるだけで、1件ずつ独立したテストとして実行される。
# 「表でテストケースを管理する」感覚で書ける、pytest の看板機能。


@pytest.mark.parametrize(
    ("class_attr", "expected"),
    [
        ("star-rating One", 1),
        ("star-rating Three", 3),
        ("star-rating Five", 5),
        ("star-rating", 0),          # 評価クラスなし
        ("", 0),                      # 空文字列
        ("Three star-rating", 3),     # 順番が逆でも拾える
    ],
)
def test_parse_rating(class_attr: str, expected: int):
    assert parse_rating(class_attr) == expected


# ============================================================
# 4. 文字列整形のテスト ─ 境界値を意識する
# ============================================================
# バグは「ちょうど境界」に潜む。max_length ちょうど / ±1 を必ず試す。


def test_normalize_title_strips_and_collapses_spaces():
    assert normalize_title("  A  Light   in the Attic ") == "A Light in the Attic"


def test_normalize_title_exact_length_not_truncated():
    """max_length ちょうどの長さは切り詰めない（境界値）"""
    title = "x" * 50
    assert normalize_title(title, max_length=50) == title


def test_normalize_title_truncates_long_title():
    """max_length を超えたら末尾 ... で切り詰め、全体は max_length に収まる"""
    result = normalize_title("x" * 60, max_length=50)
    assert result.endswith("...")
    assert len(result) == 50


# ============================================================
# 5. 集計のテスト ─ 辞書の比較も assert 一発
# ============================================================


def test_summarize_by_rating():
    books = [
        {"rating": 3},
        {"rating": 3},
        {"rating": 5},
        {"rating": 1},
    ]
    assert summarize_by_rating(books) == {3: 2, 5: 1, 1: 1}


def test_summarize_by_rating_empty():
    """空リストなら空の辞書（ゼロ件の挙動も忘れずテストする）"""
    assert summarize_by_rating([]) == {}


# ============================================================
# 6. fixture ─ テストの「準備」を共通化する
# ============================================================
# 複数のテストで同じ準備データを使うなら fixture にまとめる。
# テスト関数の引数に fixture 名を書くだけで、pytest が自動で渡してくれる。


@pytest.fixture
def sample_books() -> list[dict]:
    """テスト用の書籍データ（各テストのたびに新しく作られる）"""
    return [
        {"title": "Book A", "rating": 4, "price": 10.0},
        {"title": "Book B", "rating": 4, "price": 20.0},
        {"title": "Book C", "rating": 2, "price": 30.0},
    ]


def test_summarize_with_fixture(sample_books: list[dict]):
    counts = summarize_by_rating(sample_books)
    assert counts[4] == 2
    assert counts[2] == 1


def test_fixture_gives_fresh_data(sample_books: list[dict]):
    """fixture はテストごとに作り直されるので、他のテストの変更に影響されない"""
    sample_books.clear()  # このテスト内で壊しても…
    assert sample_books == []  # （他のテストの sample_books は無事）
