from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import get_settings

_text_splitter: RecursiveCharacterTextSplitter | None = None


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    global _text_splitter
    if _text_splitter is None:
        settings = get_settings()
        _text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", ".", " ", ""],
            length_function=len,
        )
    return _text_splitter


def chunk_text(text: str, metadata: dict | None = None) -> list[dict]:
    splitter = get_text_splitter()
    chunks = splitter.create_documents([text], metadatas=[metadata or {}])
    return [
        {
            "content": chunk.page_content,
            "metadata": chunk.metadata,
            "chunk_index": i,
        }
        for i, chunk in enumerate(chunks)
    ]
