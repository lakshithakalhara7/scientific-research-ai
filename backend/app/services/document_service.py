from pathlib import Path
from typing import TypedDict
import pymupdf


BASE_DIR = Path(__file__).resolve().parent.parent

RESEARCH_PAPERS_DIR = BASE_DIR / "data" / "research_papers"


class PDFPage(TypedDict):
    page_number: int
    text: str


class PDFValidationError(ValueError):
    """Unreadable, encrypted, or empty PDF, with a safe public message."""


def _extract_pages(document: pymupdf.Document) -> list[PDFPage]:
    return [
        {"page_number": page_number + 1, "text": page.get_text()}
        for page_number, page in enumerate(document)
    ]


def inspect_pdf_bytes(content: bytes) -> int:
    """Parse uploaded bytes without creating files or contacting Supabase."""
    try:
        with pymupdf.open(stream=content, filetype="pdf") as document:
            if not document.is_pdf or document.needs_pass or document.is_encrypted:
                raise PDFValidationError("Upload an unencrypted, readable PDF.")
            if document.page_count < 1:
                raise PDFValidationError("The PDF must contain at least one page.")
            # Loading each page also catches broken page trees before cloud writes.
            for page_number in range(document.page_count):
                document.load_page(page_number)
            return document.page_count
    except PDFValidationError:
        raise
    except Exception:
        raise PDFValidationError("The file is not a readable PDF.") from None


def extract_text_from_pdf_bytes(content: bytes) -> list[PDFPage]:
    """Reuse page extraction for uploads, keeping PDF bytes only in memory."""
    with pymupdf.open(stream=content, filetype="pdf") as document:
        if document.needs_pass or document.is_encrypted:
            raise PDFValidationError("Upload an unencrypted, readable PDF.")
        return _extract_pages(document)


def extract_text_from_pdf(pdf_path: Path) -> list[PDFPage]:
    """Extract a local PDF page by page; preserve the existing local API."""
    with pymupdf.open(pdf_path) as document:
        return _extract_pages(document)


def load_all_research_papers():
    """
    Load all PDF files inside the research_papers folder.

    Expected structure:

    research_papers/
        cancer/
        cardiovascular/
        diabetes/
    """

    documents = []

    pdf_files = list(
        RESEARCH_PAPERS_DIR.rglob("*.pdf")
    )

    for pdf_file in pdf_files:
        category = pdf_file.parent.name

        try:
            pages = extract_text_from_pdf(pdf_file)

            documents.append({
                "filename": pdf_file.name,
                "category": category,
                "path": str(pdf_file),
                "total_pages": len(pages),
                "pages": pages
            })

        except Exception as error:
            print(
                f"Error reading {pdf_file.name}: {error}"
            )

    return documents
