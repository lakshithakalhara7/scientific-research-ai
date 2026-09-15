from pathlib import Path
import pymupdf


BASE_DIR = Path(__file__).resolve().parent.parent

RESEARCH_PAPERS_DIR = BASE_DIR / "data" / "research_papers"


def extract_text_from_pdf(pdf_path: Path):
    """
    Extract text from a single PDF page by page.
    """

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document):
        text = page.get_text()

        pages.append({
            "page_number": page_number + 1,
            "text": text
        })

    document.close()

    return pages


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