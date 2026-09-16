"""Offline checks for persistent retrieval, UUID identity, and atomic refresh."""

from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services import retrieval_index_service as index
from app.services.database_service import DocumentChunkRecord, DocumentRecord
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
        factory.start()
        self.addCleanup(factory.stop)
        local = patch.object(index, "load_all_research_papers", return_value=[{
            "filename": "local.pdf", "category": "local",
            "pages": [{"page_number": 1, "text": "baseline local research corpus"}],
        }])
        local.start()
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
        old = index.get_retrieval_resources()
        self.database.get_indexed_documents.side_effect = RuntimeError("dummy-secret-value")
        with self.assertRaises(index.RetrievalSourceError) as error:
            index.refresh_retrieval_index(database=self.database)
        self.assertNotIn("dummy-secret-value", str(error.exception))
        self.assertTrue(error.exception.__suppress_context__)
        self.assertIs(index.get_retrieval_resources(), old)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
