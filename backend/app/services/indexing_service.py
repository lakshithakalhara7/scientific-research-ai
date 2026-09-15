from collections import defaultdict, Counter
from typing import List, Dict

from .nlp_service import preprocess_text


def build_inverted_index(
    chunks: List[Dict]
):
    """
    Build an inverted index from research paper chunks.

    Structure:

    term
        -> chunk_id
            -> term frequency

    Example:

    "cancer"
        -> paper1_p1_c1 : 5
        -> paper1_p2_c1 : 3

    Returns:
        inverted_index
        chunk_store
    """

    inverted_index = defaultdict(dict)

    chunk_store = {}

    for chunk in chunks:

        chunk_id = chunk["chunk_id"]

        # ------------------------------------------
        # NLP preprocessing
        # ------------------------------------------

        processed_tokens = preprocess_text(
            chunk["text"]
        )

        # Count how many times each term
        # appears inside this chunk
        term_frequencies = Counter(
            processed_tokens
        )

        # ------------------------------------------
        # Store original chunk + processed tokens
        # ------------------------------------------

        chunk_store[chunk_id] = {
            **chunk,
            "processed_tokens": processed_tokens
        }

        # ------------------------------------------
        # Build inverted index
        # ------------------------------------------

        for term, frequency in term_frequencies.items():

            inverted_index[term][chunk_id] = frequency

    return (
        dict(inverted_index),
        chunk_store
    )