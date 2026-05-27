def truncate(text: str, max_length: int = 500) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def clean_text(text: str) -> str:
    import re
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"-\n", "", text)
    return text.strip()
