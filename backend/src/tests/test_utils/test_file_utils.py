from src.utils.file_utils import file_hash


def test_file_hash_consistent():
    content = b"Hello World"
    hash1 = file_hash(content)
    hash2 = file_hash(content)
    assert hash1 == hash2


def test_file_hash_different():
    content1 = b"Hello World"
    content2 = b"Hello World!"
    assert file_hash(content1) != file_hash(content2)


def test_file_hash_format():
    content = b"test"
    hash_value = file_hash(content)
    assert len(hash_value) == 32  # MD5 hex digest length
    assert all(c in "0123456789abcdef" for c in hash_value)
