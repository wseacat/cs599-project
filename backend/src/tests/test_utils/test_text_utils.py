from src.utils.text_utils import truncate, clean_text


def test_truncate_short_text():
    text = "Hello World"
    assert truncate(text, 20) == "Hello World"


def test_truncate_long_text():
    text = "A" * 100
    result = truncate(text, 50)
    assert len(result) == 53  # 50 + "..."
    assert result.endswith("...")


def test_truncate_exact_length():
    text = "A" * 50
    assert truncate(text, 50) == text


def test_clean_text_whitespace():
    text = "  Hello   World  "
    assert clean_text(text) == "Hello World"


def test_clean_text_newlines():
    text = "Hello\n\nWorld"
    assert clean_text(text) == "Hello World"


def test_clean_text_hyphen_newline():
    text = "Hello-\nWorld"
    assert clean_text(text) == "HelloWorld"
