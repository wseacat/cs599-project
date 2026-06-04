import pytest
from src.agents.planner import get_llm, _extract_text


def test_extract_text_string():
    assert _extract_text("Hello") == "Hello"


def test_extract_text_list():
    content = [{"text": "Hello"}]
    assert _extract_text(content) == "Hello"


def test_extract_text_list_with_attr():
    class Block:
        text = "Hello"
    assert _extract_text([Block()]) == "Hello"


def test_extract_text_empty():
    assert _extract_text("") == ""
    assert _extract_text([]) == ""
    assert _extract_text(None) == ""


def test_get_llm():
    llm = get_llm()
    assert llm is not None
    assert llm.model == "mimo-v2.5-pro"
