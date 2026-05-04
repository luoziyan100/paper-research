"""Input helpers for papers and benchmark reports."""

from __future__ import annotations

from pathlib import Path


def load_paper_text(path: Path) -> str:
    """Load paper text from txt/md files, with a helpful PDF message."""

    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        return _load_pdf_text(path)
    raise ValueError(f"Unsupported paper file type: {path.suffix}")


def _load_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "PDF input requires the optional 'pypdf' package. Convert the paper to "
            "txt/md or install pypdf before using PDF files."
        ) from exc

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    text = "\n".join(pages).strip()
    if not text:
        raise RuntimeError(f"No extractable text found in PDF: {path}")
    return text
