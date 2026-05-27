import hashlib


def file_hash(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()
