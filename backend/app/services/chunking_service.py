from typing import List, Dict


def chunk_text(
    text: str,
    chunk_size: int = 250,
    overlap: int = 50
) -> List[str]:
    """
    Split text into word-based chunks.

    chunk_size:
        Maximum number of words in one chunk.

    overlap:
        Number of words repeated between consecutive chunks.
    """

    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk_words = words[start:end]

        chunk = " ".join(chunk_words)

        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def create_document_chunks(
    documents: List[Dict],
    chunk_size: int = 250,
    overlap: int = 50
) -> List[Dict]:
    """
    Convert extracted research paper pages
    into smaller searchable chunks.

    Keeps important metadata:
    - filename
    - category
    - page number
    - chunk number
    """

    all_chunks = []

    for document in documents:

        filename = document["filename"]
        category = document["category"]

        for page in document["pages"]:

            page_number = page["page_number"]

            page_text = page["text"]

            page_chunks = chunk_text(
                page_text,
                chunk_size=chunk_size,
                overlap=overlap
            )

            for chunk_number, chunk in enumerate(
                page_chunks,
                start=1
            ):

                chunk_id = (
                    f"{filename}"
                    f"_p{page_number}"
                    f"_c{chunk_number}"
                )

                all_chunks.append({
                    "chunk_id": chunk_id,
                    "filename": filename,
                    "category": category,
                    "page_number": page_number,
                    "chunk_number": chunk_number,
                    "text": chunk
                })

    return all_chunks