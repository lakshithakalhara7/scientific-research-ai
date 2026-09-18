"""Offline checks for document-scoped BM25 retrieval and shared-cache safety."""

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import SupabaseConfigurationError
from app.services import retrieval_index_service as index
from app.services import retrieval_service
from app.services.database_service import DatabaseService, DocumentChunkRecord, DocumentRecord
from app.services.indexing_service import build_inverted_index
from app.services.retrieval_service import search_documents


class DocumentRetrievalTests(unittest.TestCase):
    def setUp(self):
        index.clear_retrieval_cache()
        self.addCleanup(index.clear_retrieval_cache)
        self.documents: dict[UUID, DocumentRecord] = {}
        self.chunks: dict[UUID, list[DocumentChunkRecord]] = {}
        self.database = Mock(spec=DatabaseService)
        self.database.get_document.side_effect = lambda identifier: self.documents.get(UUID(str(identifier)))
        self.database.get_indexed_documents.side_effect = lambda: [
            item for item in self.documents.values() if item.status == "indexed"
        ]
        self.database.get_document_chunks.side_effect = lambda identifier: self.chunks[UUID(str(identifier))]
        factory = patch.object(index, "DatabaseService", return_value=self.database)
        self.factory = factory.start()
        self.addCleanup(factory.stop)
        local = patch.object(index, "load_all_research_papers", return_value=[{
            "filename": "local.pdf", "category": "local",
            "pages": [{"page_number": 1, "text": "baseline local evidence"}],
        }])
        self.local = local.start()
        self.addCleanup(local.stop)

    def add_document(self, *texts, status="indexed", filename="same.pdf"):
        identifier = uuid4()
        parent = DocumentRecord(
            id=identifier, original_filename=filename,
            storage_path=f"documents/{identifier}/{filename}",
            title="Synthetic evidence", category="test-science", status=status,
            page_count=len(texts), created_at=datetime.now(timezone.utc),
        )
        self.documents[identifier] = parent
        self.chunks[identifier] = [DocumentChunkRecord(
            id=uuid4(), document_id=identifier, page_number=position,
            chunk_number=1, chunk_text=text, processed_text=text,
            token_count=len(text.split()), created_at=datetime.now(timezone.utc),
        ) for position, text in enumerate(texts, start=1)]
        return parent

    def assert_scoped_error(self, document_id, status_code):
        with self.assertRaises(index.DocumentRetrievalError) as caught:
            search_documents("quartz", document_id=document_id)
        self.assertEqual(caught.exception.status_code, status_code)
        self.assertNotIn("private-sdk-detail", str(caught.exception))
        return caught.exception

    def test_document_below_global_top_five_is_still_retrieved_when_scoped(self):
        target = self.add_document("quartz " + "background " * 400)
        for number in range(6):
            self.add_document("quartz quartz quartz", filename=f"strong-{number}.pdf")
        global_results = search_documents("quartz", top_k=5)
        self.assertEqual(len(global_results), 5)
        self.assertNotIn(str(target.id), {row["document_id"] for row in global_results})
        selected = search_documents("quartz", top_k=5, document_id=target.id)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["document_id"], str(target.id))
        self.assertEqual(selected[0]["chunk_id"], str(self.chunks[target.id][0].id))

    def test_scoped_scores_equal_bm25_over_the_target_corpus_only(self):
        target = self.add_document(
            "quartz quartz nebula evidence", "quartz evidence", "unrelated astronomy evidence"
        )
        self.add_document("quartz " * 90)
        self.add_document("nebula background " * 50)
        target_corpus = [{
            "document_id": str(target.id), "chunk_id": str(record.id),
            "filename": target.original_filename, "category": target.category,
            "page_number": record.page_number, "chunk_number": record.chunk_number,
            "text": record.chunk_text, "processed_tokens": record.processed_text.split(),
        } for record in self.chunks[target.id]]
        target_resources = build_inverted_index(target_corpus)
        with patch.object(retrieval_service, "get_retrieval_resources", return_value=target_resources):
            expected = search_documents("quartz nebula")
        index.get_retrieval_resources()
        actual = search_documents("quartz nebula", document_id=target.id)
        self.assertEqual(actual, expected)
        self.assertGreater(actual[0]["score"], actual[1]["score"])

    def test_scoped_results_preserve_ids_positions_and_metadata(self):
        target = self.add_document("unrelated data", "quartz nebula evidence", filename="target.pdf")
        self.add_document("quartz competing evidence", filename="target.pdf")
        result = search_documents("quartz", document_id=str(target.id))[0]
        expected_chunk = self.chunks[target.id][1]
        self.assertEqual(result["document_id"], str(target.id))
        self.assertEqual(result["chunk_id"], str(expected_chunk.id))
        self.assertEqual(result["filename"], "target.pdf")
        self.assertEqual(result["category"], "test-science")
        self.assertEqual(result["page_number"], 2)
        self.assertEqual(result["chunk_number"], 1)
        self.assertEqual(result["text"], expected_chunk.chunk_text)
        self.assertEqual(result["matched_terms"], ["quartz"])
        self.assertGreater(result["score"], 0)

    def test_scoping_does_not_change_existing_unscoped_results(self):
        target = self.add_document("quartz nebula evidence")
        self.add_document("quartz quartz evidence")
        before = search_documents("quartz nebula")
        selected = search_documents("quartz nebula", document_id=target.id)
        after = search_documents("quartz nebula")
        self.assertEqual(before, after)
        self.assertTrue(selected)
        self.assertTrue(all(row["document_id"] == str(target.id) for row in selected))

    def test_no_match_in_selected_document_does_not_return_another_document(self):
        target = self.add_document("galaxy background evidence")
        self.add_document("quartz competing evidence")
        self.assertTrue(search_documents("quartz"))
        self.assertEqual(search_documents("quartz", document_id=target.id), [])
        self.local.assert_not_called()

    def test_cached_scoped_view_reuses_index_and_preserves_global_snapshot(self):
        target = self.add_document("quartz nebula evidence")
        self.add_document("quartz competing evidence", "other background")
        original = index.get_retrieval_resources()
        saved = deepcopy(original)
        self.database.get_document_chunks.reset_mock()
        self.database.get_indexed_documents.reset_mock()
        with patch.object(index, "build_inverted_index", side_effect=AssertionError("Unexpected index rebuild")):
            first = search_documents("quartz", document_id=target.id)
            second = search_documents("quartz", document_id=str(target.id))
        self.assertEqual(first, second)
        self.assertIs(index.get_retrieval_resources(), original)
        self.assertEqual(original, saved)
        self.assertEqual(self.database.get_document.call_count, 2)
        self.database.get_document_chunks.assert_not_called()
        self.database.get_indexed_documents.assert_not_called()
        self.local.assert_not_called()

    def test_scoped_store_and_postings_exclude_every_other_document(self):
        target = self.add_document("quartz nebula")
        other = self.add_document("quartz competitor")
        index.get_retrieval_resources()
        inverted, store = index.get_document_retrieval_resources(target.id)
        target_ids = {str(row.id) for row in self.chunks[target.id]}
        other_ids = {str(row.id) for row in self.chunks[other.id]}
        self.assertEqual(set(store), target_ids)
        self.assertTrue(all(set(postings) <= target_ids for postings in inverted.values()))
        self.assertTrue(all(not (set(postings) & other_ids) for postings in inverted.values()))

    def test_cold_scoped_query_reads_only_selected_document_without_global_cache(self):
        target = self.add_document("quartz nebula evidence")
        self.add_document("quartz competing evidence")
        self.database.get_indexed_documents.side_effect = AssertionError("Unexpected corpus read")
        result = search_documents("quartz", document_id=target.id)
        self.assertEqual(result[0]["document_id"], str(target.id))
        self.assertEqual(self.database.get_document_chunks.call_count, 1)
        self.assertEqual(UUID(str(self.database.get_document_chunks.call_args.args[0])), target.id)
        self.database.get_indexed_documents.assert_not_called()
        self.database.create_document.assert_not_called()
        self.database.create_document_chunks.assert_not_called()
        self.database.update_document_status.assert_not_called()
        self.local.assert_not_called()
        self.assertIsNone(index._resources)

    def test_scoped_query_leaves_a_local_fallback_snapshot_unchanged(self):
        original = index.get_retrieval_resources()
        saved = deepcopy(original)
        target = self.add_document("quartz nebula evidence")
        selected = search_documents("quartz", document_id=target.id)
        self.assertEqual(selected[0]["document_id"], str(target.id))
        self.assertIs(index.get_retrieval_resources(), original)
        self.assertEqual(original, saved)
        self.assertEqual(search_documents("baseline")[0]["chunk_id"], "local.pdf_p1_c1")
        self.local.assert_called_once()

    def test_uncached_selected_document_does_not_replace_other_cloud_snapshot(self):
        existing = self.add_document("galaxy existing evidence")
        original = index.get_retrieval_resources()
        target = self.add_document("quartz new evidence")
        selected = search_documents("quartz", document_id=target.id)
        self.assertEqual(selected[0]["document_id"], str(target.id))
        self.assertIs(index.get_retrieval_resources(), original)
        self.assertEqual({row["document_id"] for row in original[1].values()}, {str(existing.id)})
        self.assertEqual(search_documents("quartz"), [])
        self.local.assert_not_called()

    def test_refresh_makes_new_document_immediately_searchable_in_scoped_view(self):
        self.add_document("galaxy existing evidence")
        index.get_retrieval_resources()
        pending = self.add_document("quartz new ingestion evidence", status="processing")

        def finish():
            self.documents[pending.id] = pending.model_copy(update={"status": "indexed"})

        index.refresh_retrieval_index(database=self.database, pending_document_id=pending.id, on_ready=finish)
        published = index.get_retrieval_resources()
        self.database.get_document_chunks.reset_mock()
        with patch.object(index, "build_inverted_index", side_effect=AssertionError("Unexpected index rebuild")):
            selected = search_documents("quartz", document_id=pending.id)
        self.assertEqual(selected[0]["document_id"], str(pending.id))
        self.assertIs(index.get_retrieval_resources(), published)
        self.database.get_document_chunks.assert_not_called()

    def test_invalid_uuid_is_422_without_client_setup(self):
        self.assert_scoped_error("not-a-document-uuid", 422)
        self.factory.assert_not_called()
        self.local.assert_not_called()

    def test_unknown_document_is_404_without_local_fallback(self):
        self.assert_scoped_error(uuid4(), 404)
        self.database.get_document_chunks.assert_not_called()
        self.database.get_indexed_documents.assert_not_called()
        self.local.assert_not_called()

    def test_nonindexed_documents_are_409_without_reading_chunks(self):
        for status in ("uploaded", "processing", "failed"):
            with self.subTest(status=status):
                parent = self.add_document("quartz evidence", status=status)
                self.assert_scoped_error(parent.id, 409)
        self.database.get_document_chunks.assert_not_called()
        self.local.assert_not_called()

    def test_cached_evidence_cannot_bypass_current_document_status_or_deletion(self):
        target = self.add_document("quartz evidence")
        original = index.get_retrieval_resources()
        self.documents[target.id] = target.model_copy(update={"status": "failed"})
        self.assert_scoped_error(target.id, 409)
        del self.documents[target.id]
        self.assert_scoped_error(target.id, 404)
        self.assertIs(index.get_retrieval_resources(), original)
        self.local.assert_not_called()

    def test_cloud_metadata_failure_is_safe_503_even_with_cached_evidence(self):
        target = self.add_document("quartz evidence")
        original = index.get_retrieval_resources()
        self.database.get_document.side_effect = RuntimeError("private-sdk-detail")
        error = self.assert_scoped_error(target.id, 503)
        self.assertTrue(error.__suppress_context__)
        self.assertIs(index.get_retrieval_resources(), original)
        self.local.assert_not_called()

    def test_cloud_chunk_failure_is_safe_503_without_local_fallback(self):
        target = self.add_document("quartz evidence")
        self.database.get_document_chunks.side_effect = RuntimeError("private-sdk-detail")
        error = self.assert_scoped_error(target.id, 503)
        self.assertTrue(error.__suppress_context__)
        self.database.get_indexed_documents.assert_not_called()
        self.local.assert_not_called()
        self.assertIsNone(index._resources)

    def test_missing_configuration_is_503_for_scoped_requests(self):
        self.factory.side_effect = SupabaseConfigurationError("private-sdk-detail")
        self.assert_scoped_error(uuid4(), 503)
        self.local.assert_not_called()

    def test_inconsistent_metadata_or_chunk_ownership_never_leaks_another_document(self):
        target = self.add_document("quartz selected evidence")
        other = self.add_document("quartz private competing evidence")
        self.database.get_document.side_effect = lambda identifier: other
        self.assert_scoped_error(target.id, 503)
        self.database.get_document_chunks.assert_not_called()
        self.database.get_document.side_effect = lambda identifier: target
        self.database.get_document_chunks.side_effect = lambda identifier: self.chunks[other.id]
        self.assert_scoped_error(target.id, 503)
        self.assertIsNone(index._resources)
        self.local.assert_not_called()

    def test_empty_or_unusable_selected_chunks_are_409_without_local_fallback(self):
        target = self.add_document("quartz evidence")
        original_chunk = self.chunks[target.id][0]
        cases = [
            [],
            [original_chunk.model_copy(update={"processed_text": ""})],
            [original_chunk.model_copy(update={"chunk_text": " \n\t"})],
            [original_chunk.model_copy(update={"chunk_text": "and the or", "processed_text": None})],
        ]
        for rows in cases:
            with self.subTest(rows=len(rows)):
                self.chunks[target.id] = rows
                self.assert_scoped_error(target.id, 409)
        self.local.assert_not_called()
        self.assertIsNone(index._resources)

    def test_cold_scoped_load_deduplicates_records_and_reuses_existing_nlp(self):
        target = self.add_document("quartz nebula evidence")
        row = self.chunks[target.id][0].model_copy(update={"processed_text": None})
        self.chunks[target.id] = [row, row]
        results = search_documents("quartz nebula", document_id=target.id)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["chunk_id"], str(row.id))
        self.assertEqual(results[0]["matched_terms"], ["nebula", "quartz"])
        self.local.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
