from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


SUPPORTED_SUFFIXES = {".pdf", ".txt", ".md", ".markdown"}


def load_document(path: str | Path) -> list[Document]:
    file_path = Path(path).resolve()
    if not file_path.is_file():
        raise FileNotFoundError(f"Document does not exist: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_SUFFIXES))
        raise ValueError(f"Unsupported document type {suffix!r}. Supported: {supported}")

    if suffix == ".pdf":
        return _load_pdf(file_path)
    return _load_text(file_path)


def _load_pdf(path: Path) -> list[Document]:
    documents = []
    reader = PdfReader(str(path))
    for page_number, page in enumerate(reader.pages):
        content = (page.extract_text() or "").strip()
        if not content:
            continue
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": path.name,
                    "source_path": str(path),
                    "page": page_number,
                },
            )
        )
    if not documents:
        raise ValueError(f"No extractable text found in PDF: {path.name}")
    return documents


def _load_text(path: Path) -> list[Document]:
    content = path.read_text(encoding="utf-8-sig").strip()
    if not content:
        raise ValueError(f"Document is empty: {path.name}")
    return [
        Document(
            page_content=content,
            metadata={"source": path.name, "source_path": str(path)},
        )
    ]

