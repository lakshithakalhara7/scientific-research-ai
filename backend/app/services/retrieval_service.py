from pathlib import Path

from app.services.nlp_service import preprocess_text


PAPERS_FOLDER = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "papers"
)


def load_documents():
    documents = {}

    for file_path in PAPERS_FOLDER.glob("*.txt"):
        content = file_path.read_text(encoding="utf-8")
        documents[file_path.name] = content

    return documents


def build_inverted_index(documents):
    inverted_index = {}

    for document_name, content in documents.items():

        tokens = preprocess_text(content)

        for token in tokens:

            if token not in inverted_index:
                inverted_index[token] = []

            if document_name not in inverted_index[token]:
                inverted_index[token].append(document_name)

    return inverted_index


def search_documents(query: str):

    documents = load_documents()

    inverted_index = build_inverted_index(documents)

    query_tokens = preprocess_text(query)

    scores = {}

    for token in query_tokens:

        matching_documents = inverted_index.get(token, [])

        for document_name in matching_documents:

            if document_name not in scores:
                scores[document_name] = 0

            scores[document_name] += 1

    ranked_documents = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for document_name, score in ranked_documents:

        results.append({
            "document": document_name,
            "score": score,
            "content": documents[document_name]
        })

    return results