"""Offline checks for persistent retrieval, UUID identity, and atomic refresh."""

from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services import retrieval_index_service as index
from app.services import retrieval_service
from app.core.config import SupabaseConfigurationError
from app.services.database_service import DocumentChunkRecord, DocumentRecord
from app.services.indexing_service import build_inverted_index
from app.services.retrieval_service import search_documents


def document(status="indexed", filename="same.pdf"):
    return DocumentRecord(
        id=uuid4(), original_filename=filename, storage_path=f"tests/{uuid4()}.pdf",
        status=status, created_at=datetime.now(timezone.utc),
    )


def chunk(parent, number=1, text="quartz nebula evidence"):
    return DocumentChunkRecord(
        id=uuid4(), document_id=parent.id, page_number=1, chunk_number=number,
        chunk_text=text, processed_text=text, token_count=len(text.split()),
        created_at=datetime.now(timezone.utc),
    )


class RetrievalIndexTests(unittest.TestCase):
    def setUp(self):
        index.clear_retrieval_cache()
        self.addCleanup(index.clear_retrieval_cache)
        self.database = Mock()
        self.database.get_indexed_documents.return_value = []
        factory = patch.object(index, "DatabaseService", return_value=self.database)
        self.factory = factory.start()
        self.addCleanup(factory.stop)
        local = patch.object(index, "load_all_research_papers", return_value=[{
            "filename": "local.pdf", "category": "local",
            "pages": [{"page_number": 1, "text": "baseline local research corpus"}],
        }])
        self.local = local.start()
        self.addCleanup(local.stop)

    def test_queries_reuse_snapshot_without_reading_cloud_again(self):
        self.assertTrue(search_documents("baseline"))
        self.assertTrue(search_documents("baseline"))
        self.database.get_indexed_documents.assert_called_once()

    def test_cloud_failure_uses_local_corpus_without_logging_raw_error(self):
        self.database.get_indexed_documents.side_effect = RuntimeError("dummy-secret-value")
        with self.assertLogs(index.logger, level="WARNING") as captured:
            self.assertTrue(search_documents("baseline"))
        self.assertNotIn("dummy-secret-value", " ".join(captured.output))

    def test_refresh_publishes_after_status_callback_and_survives_reload(self):
        old = index.get_retrieval_resources()
        pending = document(status="processing")
        evidence = chunk(pending)
        self.database.get_document.return_value = pending
        self.database.get_document_chunks.return_value = [evidence]

        def finish():
            self.assertIs(index.get_retrieval_resources(), old)
            self.assertNotIn(str(evidence.id), old[1])
            self.database.get_indexed_documents.return_value = [
                pending.model_copy(update={"status": "indexed"})
            ]

        index.refresh_retrieval_index(
            database=self.database, pending_document_id=pending.id, on_ready=finish
        )
        results = search_documents("quartz nebula")
        self.assertEqual(results[0]["document_id"], str(pending.id))
        self.assertEqual(results[0]["chunk_id"], str(evidence.id))
        self.assertEqual(set(index.get_retrieval_resources()[1]), {str(evidence.id)})
        self.assertEqual(search_documents("baseline"), [])
        self.local.assert_called_once()
        index.clear_retrieval_cache()
        self.assertEqual(search_documents("quartz")[0]["document_id"], str(pending.id))

    def test_failed_final_status_update_preserves_previous_snapshot(self):
        old = index.get_retrieval_resources()
        pending = document(status="processing")
        self.database.get_document.return_value = pending
        self.database.get_document_chunks.return_value = [chunk(pending)]
        with self.assertRaises(RuntimeError):
            index.refresh_retrieval_index(
                database=self.database, pending_document_id=pending.id,
                on_ready=Mock(side_effect=RuntimeError("status update failed")),
            )
        self.assertIs(index.get_retrieval_resources(), old)
        self.assertEqual(search_documents("quartz"), [])

    def test_failed_rebuild_never_calls_completion_or_discards_snapshot(self):
        old = index.get_retrieval_resources()
        complete = Mock()
        with patch.object(index, "build_inverted_index", side_effect=RuntimeError("build failed")):
            with self.assertRaises(RuntimeError):
                index.refresh_retrieval_index(database=self.database, on_ready=complete)
        complete.assert_not_called()
        self.assertIs(index.get_retrieval_resources(), old)

    def test_failed_strict_refresh_cannot_silently_publish_local_only_snapshot(self):
        parent = document()
        evidence = chunk(parent)
        self.database.get_indexed_documents.return_value = [parent]
        self.database.get_document_chunks.return_value = [evidence]
        old = index.get_retrieval_resources()
        self.database.get_indexed_documents.side_effect = RuntimeError("dummy-secret-value")
        with self.assertRaises(index.RetrievalSourceError) as error:
            index.refresh_retrieval_index(database=self.database)
        self.assertNotIn("dummy-secret-value", str(error.exception))
        self.assertTrue(error.exception.__suppress_context__)
        self.assertIs(index.get_retrieval_resources(), old)
        self.assertEqual(search_documents("quartz")[0]["chunk_id"], str(evidence.id))
        self.local.assert_not_called()

    def test_unfinished_documents_are_excluded_from_regular_retrieval(self):
        self.database.get_indexed_documents.return_value = [
            document(status="processing"), document(status="failed"), document(status="uploaded")
        ]
        self.assertEqual(search_documents("quartz"), [])
        self.database.get_document_chunks.assert_not_called()

    def test_duplicate_filenames_have_independent_paper_limits_and_chunk_ids(self):
        first, second = document(), document()
        self.database.get_indexed_documents.return_value = [first, second]
        self.database.get_document_chunks.side_effect = lambda identifier: [
            chunk(first if identifier == first.id else second, number=number)
            for number in (1, 2, 3)
        ]
        results = search_documents("quartz nebula", top_k=6)
        self.assertEqual(len(results), 4)
        self.assertEqual(len({row["chunk_id"] for row in results}), 4)
        for parent in (first, second):
            self.assertEqual(sum(row["document_id"] == str(parent.id) for row in results), 2)
        self.assertTrue(all(row["score"] > 0 for row in results))

    def test_pending_document_requires_completion_callback_and_persisted_chunks(self):
        pending = document(status="processing")
        with self.assertRaises(ValueError):
            index.refresh_retrieval_index(database=self.database, pending_document_id=pending.id)
        self.database.get_document.return_value = pending
        self.database.get_document_chunks.return_value = []
        complete = Mock()
        with self.assertRaises(index.RetrievalSourceError):
            index.refresh_retrieval_index(
                database=self.database, pending_document_id=pending.id, on_ready=complete
            )
        complete.assert_not_called()

    def test_usable_cloud_chunks_do_not_load_or_index_the_local_corpus(self):
        parent = document()
        evidence = chunk(parent)
        self.database.get_indexed_documents.return_value = [parent]
        self.database.get_document_chunks.return_value = [evidence]
        results = search_documents("quartz")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["document_id"], str(parent.id))
        self.assertEqual(results[0]["chunk_id"], str(evidence.id))
        self.assertEqual(set(index.get_retrieval_resources()[1]), {str(evidence.id)})
        self.assertEqual(search_documents("baseline"), [])
        self.local.assert_not_called()

    def test_same_pdf_in_cloud_and_local_folder_returns_only_its_cloud_evidence(self):
        parent = document(filename="local.pdf")
        evidence = chunk(parent, text="baseline local research corpus")
        self.database.get_indexed_documents.return_value = [parent]
        self.database.get_document_chunks.return_value = [evidence]
        results = search_documents("baseline research", top_k=5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["filename"], "local.pdf")
        self.assertEqual(results[0]["document_id"], str(parent.id))
        self.assertEqual(results[0]["chunk_id"], str(evidence.id))
        self.assertNotIn("local.pdf_p1_c1", index.get_retrieval_resources()[1])
        self.local.assert_not_called()

    def test_empty_cloud_corpus_keeps_original_local_chunk_ids(self):
        results = search_documents("baseline")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["chunk_id"], "local.pdf_p1_c1")
        self.assertNotIn("document_id", results[0])
        self.local.assert_called_once()

    def test_indexed_document_without_chunks_falls_back_to_local(self):
        self.database.get_indexed_documents.return_value = [document()]
        self.database.get_document_chunks.return_value = []
        results = search_documents("baseline")
        self.assertEqual(results[0]["chunk_id"], "local.pdf_p1_c1")
        self.assertNotIn("document_id", results[0])

    def test_missing_configuration_preserves_offline_local_retrieval(self):
        self.factory.side_effect = SupabaseConfigurationError("Supabase configuration is missing.")
        results = search_documents("baseline")
        self.assertEqual(results[0]["chunk_id"], "local.pdf_p1_c1")
        self.assertNotIn("document_id", results[0])
        self.database.get_indexed_documents.assert_not_called()

    def test_unusable_persisted_text_and_tokens_fall_back_to_local(self):
        parent = document()
        cases = [
            chunk(parent, text=" \t\n").model_copy(update={"processed_text": "quartz"}),
            chunk(parent).model_copy(update={"processed_text": " \t\n"}),
            chunk(parent, text="the and or").model_copy(update={"processed_text": None}),
        ]
        for evidence in cases:
            with self.subTest(chunk_id=evidence.id):
                index.clear_retrieval_cache()
                self.database.get_indexed_documents.return_value = [parent]
                self.database.get_document_chunks.return_value = [evidence]
                results = search_documents("baseline")
                self.assertEqual(results[0]["chunk_id"], "local.pdf_p1_c1")
                self.assertNotIn(str(evidence.id), index.get_retrieval_resources()[1])

    def test_missing_processed_text_uses_existing_nlp_and_cloud_only(self):
        parent = document()
        evidence = chunk(parent).model_copy(update={"processed_text": None})
        self.database.get_indexed_documents.return_value = [parent]
        self.database.get_document_chunks.return_value = [evidence]
        result = search_documents("quartz nebula")[0]
        self.assertEqual(result["document_id"], str(parent.id))
        self.assertEqual(result["chunk_id"], str(evidence.id))
        self.assertEqual(result["matched_terms"], ["nebula", "quartz"])
        self.local.assert_not_called()

    def test_cloud_nlp_failure_is_not_hidden_by_local_fallback(self):
        parent = document()
        evidence = chunk(parent).model_copy(update={"processed_text": None})
        self.database.get_indexed_documents.return_value = [parent]
        self.database.get_document_chunks.return_value = [evidence]
        with patch.object(index, "preprocess_text", side_effect=LookupError("NLP resource unavailable")):
            with self.assertRaises(LookupError):
                index.get_retrieval_resources()
        self.local.assert_not_called()
        # A failed initial build must not cache a partial/local snapshot.
        self.assertEqual(search_documents("quartz")[0]["chunk_id"], str(evidence.id))

    def test_usable_cloud_evidence_excludes_unusable_rows_and_local_data(self):
        parent = document()
        valid = chunk(parent)
        unusable = chunk(parent, number=2).model_copy(update={"processed_text": ""})
        self.database.get_indexed_documents.return_value = [parent]
        self.database.get_document_chunks.return_value = [unusable, valid]
        self.assertEqual(len(search_documents("quartz", top_k=5)), 1)
        self.assertEqual(set(index.get_retrieval_resources()[1]), {str(valid.id)})
        self.local.assert_not_called()

    def test_exact_cloud_record_duplicates_are_removed_before_indexing(self):
        parent = document()
        first, second = chunk(parent), chunk(parent, number=2, text="quartz second finding")
        self.database.get_indexed_documents.return_value = [parent, parent]
        self.database.get_document_chunks.return_value = [first, first, second]
        with patch.object(index, "build_inverted_index", wraps=build_inverted_index) as build:
            results = search_documents("quartz")
        supplied = build.call_args.args[0]
        self.assertEqual(len(supplied), 2)
        self.assertEqual({item["chunk_id"] for item in supplied}, {str(first.id), str(second.id)})
        self.assertEqual(len(results), 2)
        self.local.assert_not_called()

    def test_exact_local_position_duplicates_are_removed_before_indexing(self):
        self.local.return_value *= 2
        with patch.object(index, "build_inverted_index", wraps=build_inverted_index) as build:
            results = search_documents("baseline")
        supplied = build.call_args.args[0]
        self.assertEqual(len(supplied), 1)
        self.assertEqual(supplied[0]["chunk_id"], "local.pdf_p1_c1")
        self.assertEqual(len(results), 1)

    def test_same_text_in_distinct_cloud_documents_is_preserved(self):
        first, second = document(), document()
        first_chunk, second_chunk = chunk(first), chunk(second)
        self.database.get_indexed_documents.return_value = [first, second]
        records = {first.id: [first_chunk], second.id: [second_chunk]}
        self.database.get_document_chunks.side_effect = records.__getitem__
        results = search_documents("quartz nebula")
        self.assertEqual(len(results), 2)
        self.assertEqual({row["document_id"] for row in results}, {str(first.id), str(second.id)})
        self.assertEqual({row["chunk_id"] for row in results}, {str(first_chunk.id), str(second_chunk.id)})

    def test_cloud_source_preserves_bm25_scores_for_the_same_fixed_corpus(self):
        parents = [document(filename=f"paper-{number}.pdf") for number in range(3)]
        records = {
            parents[0].id: [chunk(parents[0], text="quartz quartz nebula evidence")],
            parents[1].id: [chunk(parents[1], text="quartz evidence")],
            parents[2].id: [chunk(parents[2], text="unrelated astronomy method evidence")],
        }
        fixed_corpus = [{
            "chunk_id": str(item.id), "document_id": str(parent.id),
            "filename": parent.original_filename, "category": "uncategorized",
            "page_number": item.page_number, "chunk_number": item.chunk_number,
            "text": item.chunk_text, "processed_tokens": item.processed_text.split(),
        } for parent in parents for item in records[parent.id]]
        # Independently supply the exact corpus to the unchanged BM25 scorer.
        # This catches accidental local data affecting IDF or average length.
        baseline = build_inverted_index(fixed_corpus)
        with patch.object(retrieval_service, "get_retrieval_resources", return_value=baseline):
            expected = search_documents("quartz nebula")
        self.database.get_indexed_documents.return_value = parents
        self.database.get_document_chunks.side_effect = records.__getitem__
        actual = search_documents("quartz nebula")
        self.assertEqual(actual, expected)
        self.assertGreater(actual[0]["score"], actual[1]["score"])
        self.local.assert_not_called()

    def test_unusable_pending_document_never_completes_or_replaces_snapshot(self):
        old = index.get_retrieval_resources()
        pending = document(status="processing")
        existing = document()
        existing_evidence = chunk(existing)
        self.database.get_indexed_documents.return_value = [existing]
        self.database.get_document.return_value = pending
        cases = [
            chunk(pending).model_copy(update={"processed_text": ""}),
            chunk(pending, text=" \n").model_copy(update={"processed_text": "quartz"}),
            chunk(pending, text="and the or").model_copy(update={"processed_text": None}),
        ]
        for evidence in cases:
            with self.subTest(chunk_id=evidence.id):
                self.database.get_document_chunks.side_effect = (
                    lambda identifier: [evidence] if identifier == pending.id else [existing_evidence]
                )
                complete = Mock()
                with self.assertRaises(index.RetrievalSourceError):
                    index.refresh_retrieval_index(
                        database=self.database, pending_document_id=pending.id, on_ready=complete,
                    )
                complete.assert_not_called()
                self.assertIs(index.get_retrieval_resources(), old)
                self.assertEqual(search_documents("quartz"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
