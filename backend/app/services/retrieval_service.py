import math
from typing import Dict, List
from uuid import UUID

from .nlp_service import preprocess_text
from .retrieval_index_service import (
    clear_retrieval_cache,
    get_document_retrieval_resources,
    get_retrieval_resources,
    refresh_retrieval_index,
)


# --------------------------------------------------
# Retrieval resources are built once and explicitly refreshed after ingestion.
# --------------------------------------------------

# --------------------------------------------------
# Detect reference-heavy chunks
# --------------------------------------------------

def get_reference_penalty(text: str) -> float:

    text_lower = text.lower()

    # Strong sign that this is a reference section
    if "references" in text_lower[:250]:
        return 0.25

    citation_count = (
        text_lower.count(" et al")
        + text_lower.count("http")
        + text_lower.count("www.")
        + text_lower.count(" doi")
    )

    # Likely bibliography/reference-heavy content
    if citation_count >= 5:
        return 0.35

    if citation_count >= 3:
        return 0.60

    return 1.0


# --------------------------------------------------
# BM25 Search
# --------------------------------------------------

def search_documents(
    query: str,
    top_k: int = 5,
    *,
    document_id: UUID | str | None = None,
) -> List[Dict]:

    inverted_index, chunk_store = (
        get_retrieval_resources() if document_id is None
        else get_document_retrieval_resources(document_id)
    )

    # ----------------------------------------------
    # Process query
    # ----------------------------------------------

    query_tokens = preprocess_text(query)

    # Remove duplicates from query terms
    query_terms = list(
        dict.fromkeys(query_tokens)
    )

    if not query_terms:
        return []

    # ----------------------------------------------
    # BM25 settings
    # ----------------------------------------------

    k1 = 1.5
    b = 0.75

    total_chunks = len(chunk_store)

    document_lengths = {
        chunk_id: len(
            chunk["processed_tokens"]
        )
        for chunk_id, chunk
        in chunk_store.items()
    }

    average_document_length = (
        sum(document_lengths.values())
        / total_chunks
        if total_chunks > 0
        else 0
    )

    scores = {}
    matched_terms = {}

    # ----------------------------------------------
    # Calculate BM25 score
    # ----------------------------------------------

    for term in query_terms:

        postings = inverted_index.get(
            term,
            {}
        )

        document_frequency = len(postings)

        if document_frequency == 0:
            continue

        idf = math.log(
            1
            +
            (
                total_chunks
                - document_frequency
                + 0.5
            )
            /
            (
                document_frequency
                + 0.5
            )
        )

        for chunk_id, term_frequency in postings.items():

            document_length = (
                document_lengths[chunk_id]
            )

            denominator = (
                term_frequency
                +
                k1
                *
                (
                    1
                    - b
                    +
                    b
                    * (
                        document_length
                        / average_document_length
                    )
                )
            )

            term_score = (
                idf
                *
                (
                    term_frequency
                    * (k1 + 1)
                )
                / denominator
            )

            if chunk_id not in scores:
                scores[chunk_id] = 0.0
                matched_terms[chunk_id] = set()

            scores[chunk_id] += term_score

            matched_terms[
                chunk_id
            ].add(term)

    # ----------------------------------------------
    # Apply query coverage bonus
    # ----------------------------------------------

    for chunk_id in scores:

        coverage = (
            len(matched_terms[chunk_id])
            / len(query_terms)
        )

        scores[chunk_id] *= (
            1.0
            + 0.30 * coverage
        )

        # ------------------------------------------
        # Penalize reference-heavy chunks
        # ------------------------------------------

        text = chunk_store[
            chunk_id
        ]["text"]

        penalty = get_reference_penalty(
            text
        )

        scores[chunk_id] *= penalty

    # ----------------------------------------------
    # Rank
    # ----------------------------------------------

    ranked_chunks = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # ----------------------------------------------
    # Diversify results
    #
    # Maximum 2 chunks from the same paper
    # ----------------------------------------------

    results = []

    paper_counts = {}

    for chunk_id, score in ranked_chunks:

        chunk = chunk_store[
            chunk_id
        ]

        filename = chunk[
            "filename"
        ]

        paper_id = chunk.get("document_id", filename)

        current_count = paper_counts.get(
            paper_id,
            0
        )

        if current_count >= 2:
            continue

        results.append({
            **({"document_id": chunk["document_id"]} if "document_id" in chunk else {}),
            "chunk_id": chunk_id,
            "filename": filename,
            "category": chunk["category"],
            "page_number": chunk["page_number"],
            "chunk_number": chunk["chunk_number"],
            "score": round(score, 4),
            "matched_terms": sorted(
                matched_terms[chunk_id]
            ),
            "text": chunk["text"]
        })

        paper_counts[
            paper_id
        ] = current_count + 1

        if len(results) >= top_k:
            break

    return results
