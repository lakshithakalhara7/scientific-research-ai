"""Offline document-scoped HTTP and agent checks using fake cloud records."""

from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import main
from app.agents import retrieval_agent
from app.core.config import SupabaseConfigurationError
from app.services import retrieval_index_service as index
from app.services.database_service import DocumentChunkRecord, DocumentRecord


FIRST_ID = UUID(int=101)
SECOND_ID = UUID(int=102)
MISSING_ID = UUID(int=103)
DUMMY_PRIVATE_VALUE = "offline-private-error-detail-must-not-leak"


def document(identifier: UUID) -> DocumentRecord:
    return DocumentRecord(
        id=identifier, original_filename="same.pdf", category="test",
        storage_path=f"documents/{identifier}/same.pdf", status="indexed",
        page_count=1, created_at=datetime.now(timezone.utc),
    )


def chunk(parent: DocumentRecord, identifier: int, text: str) -> DocumentChunkRecord:
    return DocumentChunkRecord(
        id=UUID(int=identifier), document_id=parent.id,
        page_number=1, chunk_number=1, chunk_text=text,
        processed_text=text, token_count=len(text.split()),
        created_at=datetime.now(timezone.utc),
    )


class DocumentRetrievalApiTests(unittest.TestCase):
    def setUp(self) -> None:
        index.clear_retrieval_cache()
        self.addCleanup(index.clear_retrieval_cache)
        first, second = document(FIRST_ID), document(SECOND_ID)
        self.documents = {str(row.id): row for row in (first, second)}
        self.chunks = {
            str(first.id): [chunk(first, 201, "quartz nebula first evidence")],
            str(second.id): [chunk(second, 202, "quartz nebula second evidence")],
        }
        self.database = Mock()
        self.database.get_document.side_effect = lambda identifier: self.documents.get(str(identifier))
        self.database.get_document_chunks.side_effect = lambda identifier: self.chunks[str(identifier)]
        self.database.get_indexed_documents.side_effect = lambda: list(self.documents.values())
        factory = patch.object(index, "DatabaseService", return_value=self.database)
        self.factory = factory.start()
        self.addCleanup(factory.stop)
        local = patch.object(index, "load_all_research_papers", return_value=[{
            "filename": "local.pdf", "category": "local",
            "pages": [{"page_number": 1, "text": "quartz local baseline evidence"}],
        }])
        self.local = local.start()
        self.addCleanup(local.stop)
        self.client = TestClient(main.app)
        self.addCleanup(self.client.close)

    def retrieve(self, document_id=FIRST_ID, query="quartz nebula"):
        return self.client.post("/agents/retrieve", json={
            "query": query, "document_id": str(document_id) if document_id is not None else None,
        })

    def assert_safe_error(self, response, status_code: int) -> None:
        self.assertEqual(response.status_code, status_code)
        self.assertIsInstance(response.json()["detail"], str)
        self.assertNotIn(DUMMY_PRIVATE_VALUE, response.text)

    def test_scoped_request_returns_only_requested_uuid_with_original_evidence_fields(self) -> None:
        response = self.retrieve()
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(set(payload), {
            "agent", "status", "original_query", "processed_query", "total_results", "results",
        })
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["total_results"], 1)
        result = payload["results"][0]
        self.assertEqual(result["document_id"], str(FIRST_ID))
        self.assertEqual(result["chunk_id"], str(UUID(int=201)))
        self.assertEqual(result["filename"], "same.pdf")
        self.assertEqual(result["page_number"], 1)
        self.assertEqual(result["chunk_number"], 1)
        self.assertGreater(result["score"], 0)
        self.assertEqual(result["matched_terms"], ["nebula", "quartz"])
        self.assertEqual(result["text"], "quartz nebula first evidence")
        self.database.get_indexed_documents.assert_not_called()
        self.local.assert_not_called()

    def test_scoping_by_uuid_keeps_same_filename_documents_separate(self) -> None:
        first = self.retrieve(FIRST_ID).json()
        second = self.retrieve(SECOND_ID).json()
        self.assertEqual({row["document_id"] for row in first["results"]}, {str(FIRST_ID)})
        self.assertEqual({row["document_id"] for row in second["results"]}, {str(SECOND_ID)})
        self.assertNotEqual(first["results"][0]["chunk_id"], second["results"][0]["chunk_id"])
        self.local.assert_not_called()

    def test_missing_scope_preserves_whole_corpus_retrieval(self) -> None:
        response = self.client.post("/agents/retrieve", json={"query": "quartz"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual({row["document_id"] for row in response.json()["results"]}, {
            str(FIRST_ID), str(SECOND_ID),
        })
        self.local.assert_not_called()

    def test_null_scope_matches_omitted_scope(self) -> None:
        omitted = self.client.post("/agents/retrieve", json={"query": "quartz nebula"})
        explicit_null = self.retrieve(document_id=None)
        self.assertEqual(explicit_null.status_code, 200)
        self.assertEqual(explicit_null.json(), omitted.json())

    def test_invalid_uuid_returns_422_before_any_cloud_access(self) -> None:
        for identifier in ("not-a-uuid", "", 17, {"id": str(FIRST_ID)}):
            with self.subTest(identifier=identifier):
                response = self.client.post("/agents/retrieve", json={
                    "query": "quartz", "document_id": identifier,
                })
                self.assertEqual(response.status_code, 422)
        self.factory.assert_not_called()
        self.local.assert_not_called()

    def test_missing_or_invalid_query_returns_422_before_any_cloud_access(self) -> None:
        cases = [{"document_id": str(FIRST_ID)}]
        cases.extend({"query": value, "document_id": str(FIRST_ID)} for value in (None, 7, [], {}))
        for payload in cases:
            with self.subTest(payload=payload):
                response = self.client.post("/agents/retrieve", json=payload)
                self.assertEqual(response.status_code, 422)
        self.factory.assert_not_called()
        self.local.assert_not_called()

    def test_unknown_document_returns_404_even_with_warm_whole_corpus_index(self) -> None:
        self.assertEqual(self.retrieve(document_id=None).status_code, 200)
        response = self.retrieve(MISSING_ID)
        self.assert_safe_error(response, 404)
        self.local.assert_not_called()

    def test_nonindexed_document_returns_409_for_each_lifecycle_state(self) -> None:
        for status in ("uploaded", "processing", "failed"):
            with self.subTest(status=status):
                self.documents[str(FIRST_ID)] = self.documents[str(FIRST_ID)].model_copy(update={"status": status})
                response = self.retrieve()
                self.assert_safe_error(response, 409)
        self.database.get_document_chunks.assert_not_called()
        self.local.assert_not_called()

    def test_indexed_document_without_chunks_returns_409(self) -> None:
        self.chunks[str(FIRST_ID)] = []
        response = self.retrieve()
        self.assert_safe_error(response, 409)
        self.local.assert_not_called()

    def test_indexed_document_without_searchable_chunks_returns_409(self) -> None:
        record = self.chunks[str(FIRST_ID)][0]
        cases = [
            record.model_copy(update={"chunk_text": " \n\t"}),
            record.model_copy(update={"processed_text": " \n\t"}),
            record.model_copy(update={"chunk_text": "the and or", "processed_text": None}),
        ]
        for evidence in cases:
            with self.subTest(evidence=evidence):
                index.clear_retrieval_cache()
                self.chunks[str(FIRST_ID)] = [evidence]
                self.assert_safe_error(self.retrieve(), 409)
        self.local.assert_not_called()

    def test_searchable_document_with_no_query_matches_returns_empty_success(self) -> None:
        response = self.retrieve(query="volcano")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(response.json()["total_results"], 0)
        self.assertEqual(response.json()["results"], [])

    def test_document_lookup_failure_returns_sanitized_503(self) -> None:
        self.database.get_document.side_effect = RuntimeError(DUMMY_PRIVATE_VALUE)
        self.assert_safe_error(self.retrieve(), 503)
        self.database.get_document_chunks.assert_not_called()
        self.local.assert_not_called()

    def test_document_chunk_read_failure_returns_sanitized_503(self) -> None:
        self.database.get_document_chunks.side_effect = RuntimeError(DUMMY_PRIVATE_VALUE)
        self.assert_safe_error(self.retrieve(), 503)
        self.local.assert_not_called()

    def test_missing_configuration_returns_503_for_requested_document(self) -> None:
        self.factory.side_effect = SupabaseConfigurationError(DUMMY_PRIVATE_VALUE)
        self.assert_safe_error(self.retrieve(), 503)
        self.local.assert_not_called()

    def test_unscoped_missing_configuration_keeps_local_fallback(self) -> None:
        self.factory.side_effect = SupabaseConfigurationError("Supabase configuration is unavailable.")
        response = self.retrieve(document_id=None, query="baseline")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["chunk_id"], "local.pdf_p1_c1")
        self.assertNotIn("document_id", response.json()["results"][0])

    def test_unexpected_retrieval_failure_returns_safe_500_and_safe_log(self) -> None:
        with patch.object(retrieval_agent, "search_documents", side_effect=RuntimeError(DUMMY_PRIVATE_VALUE)):
            with self.assertLogs(main.logger, level="ERROR") as captured:
                response = self.retrieve()
        self.assert_safe_error(response, 500)
        self.assertEqual(response.json(), {"detail": "Research retrieval failed."})
        self.assertNotIn(DUMMY_PRIVATE_VALUE, " ".join(captured.output))

    def test_empty_query_keeps_existing_agent_validation_response(self) -> None:
        response = self.retrieve(query="   ")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "agent": "Retrieval Agent", "status": "error",
            "message": "Research query cannot be empty.", "results": [],
        })
        self.factory.assert_not_called()

    def test_stopword_query_keeps_existing_agent_validation_response(self) -> None:
        response = self.retrieve(query="  the and or  ")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "agent": "Retrieval Agent", "status": "no_valid_terms",
            "original_query": "the and or", "processed_query": [], "results": [],
        })
        self.factory.assert_not_called()

    def test_direct_agent_accepts_string_scope_and_preserves_top_k(self) -> None:
        original = self.chunks[str(FIRST_ID)][0]
        self.chunks[str(FIRST_ID)].append(original.model_copy(update={
            "id": UUID(int=203), "chunk_number": 2,
        }))
        result = retrieval_agent.RetrievalAgent().run(" quartz ", top_k=1, document_id=str(FIRST_ID))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["original_query"], "quartz")
        self.assertEqual(result["total_results"], 1)
        self.assertEqual(result["results"][0]["document_id"], str(FIRST_ID))
        self.local.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
