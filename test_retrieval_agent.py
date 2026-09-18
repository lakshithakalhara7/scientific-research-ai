import sys
from pathlib import Path


# Add backend folder to Python path
BACKEND_DIR = Path(__file__).resolve().parent / "backend"

sys.path.insert(
    0,
    str(BACKEND_DIR)
)


from app.agents.retrieval_agent import RetrievalAgent


print("\n================================")
print("RETRIEVAL AGENT TEST")
print("================================\n")


agent = RetrievalAgent()


query = (
    "machine learning methods "
    "for breast cancer detection"
)


response = agent.run(
    query=query,
    top_k=5
)


print(
    "Agent:",
    response["agent"]
)

print(
    "Status:",
    response["status"]
)

print(
    "Original Query:",
    response["original_query"]
)

print(
    "Processed Query:",
    response["processed_query"]
)

print(
    "Total Results:",
    response["total_results"]
)


print("\n================================")
print("RETRIEVED EVIDENCE")
print("================================\n")


for number, result in enumerate(
    response["results"],
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
        "Score:",
        result["score"]
    )

    print(
        "Matched Terms:",
        result["matched_terms"]
    )

    print(
        "\nText Preview:\n",
        result["text"][:500]
    )

    print(
        "\n--------------------------------\n"
    )