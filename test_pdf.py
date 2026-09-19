from backend.app.services.retrieval_service import (
    search_documents
)


print("\n================================")
print("RESEARCH RETRIEVAL TEST")
print("================================\n")


query = (
    "machine learning methods "
    "for breast cancer detection"
)


print(
    "Query:",
    query
)


results = search_documents(
    query,
    top_k=5
)


print(
    "\nTotal results:",
    len(results)
)


print("\n================================")
print("TOP RETRIEVED CHUNKS")
print("================================\n")


for number, result in enumerate(
    results,
    start=1
):

    print(
        f"RESULT {number}"
    )

    print(
        "File:",
        result["filename"]
    )

    print(
        "Category:",
        result["category"]
    )

    print(
        "Page:",
        result["page_number"]
    )

    print(
        "Chunk:",
        result["chunk_number"]
    )

    print(
        "Score:",
        result["score"]
    )

    print(
        "Matched Terms:",
        result["matched_terms"]
    )

    print(
        "\nText Preview:\n",
        result["text"][:700]
    )

    print(
        "\n--------------------------------\n"
    )