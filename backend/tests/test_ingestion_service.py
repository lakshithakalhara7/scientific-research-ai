"""Offline ingestion checks: generated PDF bytes, fake persistence, no cloud writes."""

from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from uuid import UUID

import pymupdf


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services import ingestion_service as ingestion
from app.services.database_service import DocumentChunkCreate, DocumentRecord
from app.services.document_service import extract_text_from_pdf_bytes, inspect_pdf_bytes
from app.services.storage_service import MAX_PDF_SIZE_BYTES


def make_pdf(text: str = "Controlled ingestion evidence supports reproducible scientific research.", *, encrypted: bool = False) -> bytes:
    with pymupdf.open() as document:
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)
        if encrypted:
            return document.tobytes(
                encryption=pymupdf.PDF_ENCRYPT_AES_256,
                owner_pw="test-owner",
                user_pw="test-reader",
            )
        return document.tobytes()


class FakeDatabase:
    def __init__(self, events: list) -> None:
        self.events = events
        self.records: dict[UUID, DocumentRecord] = {}
        self.chunks: dict[UUID, list[DocumentChunkCreate]] = {}
        self.failure: str | None = None

    def create_document(self, document, *, document_id):
        self.events.append("create_document")
        if self.failure == "create_document":
            raise RuntimeError("private-sdk-detail")
        record = DocumentRecord(
            **document.model_dump(), id=document_id, status="uploaded",
            created_at=datetime.now(timezone.utc),
        )
        self.records[document_id] = record
        return record

    def update_document_status(self, document_id, status):
        self.events.append(status)
        if self.failure == status:
            raise RuntimeError("private-sdk-detail")
        if self.failure == f"missing_{status}":
            return None
        record = self.records[document_id].model_copy(update={"status": status})
        self.records[document_id] = record
        if status == "indexed" and self.failure == "indexed_commit_then_raise":
            raise RuntimeError("private-sdk-detail")
        return record

    def create_document_chunks(self, document_id, chunks):
        self.events.append("insert_chunks")
        if self.failure == "insert_chunks":
            raise RuntimeError("private-sdk-detail")
        self.chunks[document_id] = list(chunks)


class FakeStorage:
    def __init__(self, events: list) -> None:
        self.events = events
        self.objects: dict[str, bytes] = {}
        self.failure: str | None = None

    def upload_pdf(self, storage_path, content):
        self.events.append("upload")
        if self.failure == "upload":
            raise RuntimeError("private-sdk-detail")
        self.objects[storage_path] = content
        return storage_path

    def delete_pdf(self, storage_path):
        self.events.append("delete_pdf")
        if self.failure == "delete_pdf":
            raise RuntimeError("private-sdk-detail")
        self.objects.pop(storage_path, None)


class IngestionServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pdf = make_pdf()

    def setUp(self) -> None:
        self.events: list = []
        self.database = FakeDatabase(self.events)
        self.storage = FakeStorage(self.events)
        self.service = ingestion.IngestionService(
            self.database, self.storage, self.refresh,
        )
        self.preprocess = patch.object(
            ingestion, "preprocess_text", side_effect=lambda text: text.lower().split()
        )
        self.preprocess.start()
        self.addCleanup(self.preprocess.stop)

    def refresh(self, *, database, pending_document_id, on_ready):
        self.assertIs(database, self.database)
        self.assertIn(pending_document_id, database.chunks)
        self.assertEqual(database.records[pending_document_id].status, "processing")
        self.events.append("index_build")
        on_ready()
        self.events.append("index_publish")

    def ingest(self, **overrides):
        arguments = {"filename": "research.pdf", "content_type": "application/pdf", "content": self.pdf}
        arguments.update(overrides)
        return self.service.ingest_pdf(**arguments)

    def assert_invalid(self, code: int = 400, **overrides):
        with self.assertRaises(ingestion.IngestionError) as caught:
            self.ingest(**overrides)
        self.assertEqual(caught.exception.status_code, code)
        self.assertEqual(self.events, [])

    def test_valid_pdf_persists_evidence_then_publishes_index(self):
        result = self.ingest(title="Evidence study", category="testing", doi="10.1234/test", source_url="https://example.org/test")
        identifier = UUID(result["document"]["id"])
        record = self.database.records[identifier]
        self.assertEqual(result, {"status": "success", "document": {
            "id": str(identifier), "title": "Evidence study", "original_filename": "research.pdf",
            "category": "testing", "status": "indexed", "page_count": 1, "chunk_count": 1,
        }})
        self.assertEqual(self.events, ["create_document", "upload", "processing", "insert_chunks", "index_build", "indexed", "index_publish"])
        self.assertEqual(record.storage_path, f"documents/{identifier}/research.pdf")
        self.assertEqual(record.file_size_bytes, len(self.pdf))
        self.assertEqual(self.storage.objects[record.storage_path], self.pdf)
        chunk = self.database.chunks[identifier][0]
        self.assertEqual(chunk.page_number, 1)
        self.assertEqual(chunk.chunk_number, 1)
        self.assertIn("Controlled ingestion evidence", chunk.chunk_text)
        self.assertEqual(chunk.processed_text, chunk.chunk_text.lower())
        self.assertEqual(chunk.token_count, len(chunk.processed_text.split()))

    def test_service_construction_and_invalid_input_do_not_initialize_clients(self):
        with patch.object(ingestion, "DatabaseService") as database, patch.object(ingestion, "StorageService") as storage:
            service = ingestion.IngestionService()
            with self.assertRaises(ingestion.IngestionError):
                service.ingest_pdf(filename="bad.exe", content_type="application/pdf", content=b"wrong")
        database.assert_not_called()
        storage.assert_not_called()

    def test_missing_file(self):
        self.assert_invalid(content=None)

    def test_missing_filename(self):
        for filename in (None, "", "   ", ".pdf"):
            with self.subTest(filename=filename):
                self.assert_invalid(filename=filename)

    def test_invalid_extension(self):
        self.assert_invalid(filename="document.txt")

    def test_wrong_mime_type(self):
        for content_type in (None, "text/plain", "application/octet-stream"):
            with self.subTest(content_type=content_type):
                self.assert_invalid(content_type=content_type)

    def test_empty_file(self):
        self.assert_invalid(content=b"")

    def test_oversized_file(self):
        self.assert_invalid(413, content=b"%PDF-" + b"x" * (MAX_PDF_SIZE_BYTES - 4))

    def test_path_traversal_and_control_filenames_rejected(self):
        for filename in ("../evil.pdf", "..\\evil.pdf", "/paper.pdf", "folder/paper.pdf", "C:\\paper.pdf", "file:paper.pdf", "bad\nname.pdf", "bad\x00name.pdf", "bad\u202ename.pdf", "a" * 256 + ".pdf"):
            with self.subTest(filename=filename):
                self.assert_invalid(filename=filename)

    def test_non_pdf_header(self):
        self.assert_invalid(content=b"<!DOCTYPE html>not a PDF")

    def test_fake_pdf_header_is_not_enough(self):
        self.assert_invalid(content=b"%PDF-1.7\nThis is not an actual PDF.")

    def test_encrypted_pdf_rejected_before_cloud_writes(self):
        self.assert_invalid(content=make_pdf(encrypted=True))

    def test_unicode_and_space_filename_safely_normalized(self):
        result = self.ingest(filename="Résumé study.PDF", content_type="application/pdf; charset=binary")
        record = self.database.records[UUID(result["document"]["id"])]
        self.assertEqual(record.original_filename, "Résumé study.PDF")
        self.assertTrue(record.storage_path.endswith("/Resume_study.pdf"))

    def test_non_ascii_stem_uses_safe_fallback(self):
        result = self.ingest(filename="研究.pdf")
        record = self.database.records[UUID(result["document"]["id"])]
        self.assertTrue(record.storage_path.endswith("/document.pdf"))

    def test_optional_blank_metadata_normalized(self):
        result = self.ingest(category="  ", title="", doi=" ", source_url=" ")
        record = self.database.records[UUID(result["document"]["id"])]
        self.assertIsNone(record.category)
        self.assertIsNone(record.title)
        self.assertIsNone(record.doi)
        self.assertIsNone(record.source_url)

    def test_invalid_metadata_rejected_before_cloud_writes(self):
        cases = ({"title": "x" * 501}, {"category": "x" * 101}, {"doi": "x" * 256}, {"title": "bad\nmetadata"}, {"source_url": "javascript:alert(1)"}, {"source_url": "https://user:password@example.org"}, {"source_url": "x" * 2049})
        for metadata in cases:
            with self.subTest(metadata=list(metadata)):
                self.assert_invalid(**metadata)

    def test_database_creation_failure_never_uploads(self):
        self.database.failure = "create_document"
        with self.assertRaises(ingestion.IngestionError) as caught:
            self.ingest()
        self.assertEqual(caught.exception.status_code, 503)
        self.assertNotIn("private-sdk-detail", str(caught.exception))
        self.assertTrue(caught.exception.__suppress_context__)
        self.assertEqual(self.events, ["create_document"])

    def test_storage_failure_marks_failed_and_does_not_delete_an_unconfirmed_upload(self):
        self.storage.failure = "upload"
        with self.assertRaises(ingestion.IngestionError) as caught:
            self.ingest()
        self.assertEqual(caught.exception.status_code, 503)
        self.assertEqual(self.events, ["create_document", "upload", "failed"])
        self.assertEqual(next(iter(self.database.records.values())).status, "failed")

    def test_extraction_failure_marks_failed_and_cleans_uploaded_file(self):
        with patch.object(ingestion, "extract_text_from_pdf_bytes", side_effect=RuntimeError("private-sdk-detail")):
            with self.assertRaises(ingestion.IngestionError) as caught:
                self.ingest()
        self.assertEqual(caught.exception.status_code, 500)
        self.assertEqual(self.events, ["create_document", "upload", "processing", "failed", "delete_pdf"])
        self.assertEqual(self.storage.objects, {})
        self.assertEqual(self.database.chunks, {})

    def test_image_only_pdf_does_not_become_indexed(self):
        with self.assertRaises(ingestion.IngestionError) as caught:
            self.ingest(content=make_pdf(""))
        self.assertEqual(caught.exception.status_code, 400)
        self.assertNotIn("indexed", self.events)
        self.assertNotIn("index_publish", self.events)
        self.assertEqual(self.storage.objects, {})

    def test_no_searchable_tokens_does_not_become_indexed(self):
        with patch.object(ingestion, "preprocess_text", return_value=[]):
            with self.assertRaises(ingestion.IngestionError) as caught:
                self.ingest()
        self.assertEqual(caught.exception.status_code, 400)
        self.assertNotIn("insert_chunks", self.events)
        self.assertNotIn("indexed", self.events)

    def test_chunk_insertion_failure_marks_failed_without_refresh(self):
        self.database.failure = "insert_chunks"
        with self.assertRaises(ingestion.IngestionError) as caught:
            self.ingest()
        self.assertEqual(caught.exception.status_code, 503)
        self.assertNotIn("index_build", self.events)
        self.assertEqual(next(iter(self.database.records.values())).status, "failed")
        self.assertEqual(self.storage.objects, {})

    def test_preprocessing_failure_is_not_misreported_as_cloud_failure(self):
        with patch.object(ingestion, "preprocess_text", side_effect=LookupError("private-sdk-detail")):
            with self.assertRaises(ingestion.IngestionError) as caught:
                self.ingest()
        self.assertEqual(caught.exception.status_code, 500)
        self.assertNotIn("insert_chunks", self.events)
        self.assertEqual(next(iter(self.database.records.values())).status, "failed")

    def test_index_build_failure_does_not_mark_indexed(self):
        self.service._index_refresher = lambda **kwargs: (_ for _ in ()).throw(RuntimeError("private-sdk-detail"))
        with self.assertRaises(ingestion.IngestionError) as caught:
            self.ingest()
        self.assertEqual(caught.exception.status_code, 500)
        self.assertNotIn("indexed", self.events)
        self.assertEqual(next(iter(self.database.records.values())).status, "failed")
        self.assertEqual(self.storage.objects, {})

    def test_cloud_data_source_failure_during_refresh_is_503(self):
        from app.services.retrieval_index_service import RetrievalSourceError

        def unavailable(**kwargs):
            raise RetrievalSourceError("private-sdk-detail")

        self.service._index_refresher = unavailable
        with self.assertRaises(ingestion.IngestionError) as caught:
            self.ingest()
        self.assertEqual(caught.exception.status_code, 503)
        self.assertNotIn("private-sdk-detail", str(caught.exception))
        self.assertEqual(next(iter(self.database.records.values())).status, "failed")
        self.assertNotIn("indexed", self.events)
        self.assertEqual(self.storage.objects, {})

    def test_failure_status_outage_still_attempts_object_cleanup(self):
        self.database.failure = "failed"
        with patch.object(ingestion, "extract_text_from_pdf_bytes", side_effect=RuntimeError("private-sdk-detail")):
            with self.assertLogs(ingestion.logger, level="WARNING") as logs:
                with self.assertRaises(ingestion.IngestionError) as caught:
                    self.ingest()
        self.assertEqual(caught.exception.status_code, 500)
        self.assertEqual(next(iter(self.database.records.values())).status, "processing")
        self.assertEqual(self.storage.objects, {})
        self.assertNotIn("private-sdk-detail", " ".join(logs.output))
        self.assertNotIn("indexed", self.events)

    def test_final_status_failure_prevents_index_publication(self):
        self.database.failure = "indexed"
        with self.assertRaises(ingestion.IngestionError) as caught:
            self.ingest()
        self.assertEqual(caught.exception.status_code, 503)
        self.assertNotIn("index_publish", self.events)
        self.assertEqual(next(iter(self.database.records.values())).status, "failed")

    def test_missing_processing_record_prevents_processing(self):
        self.database.failure = "missing_processing"
        with self.assertRaises(ingestion.IngestionError) as caught:
            self.ingest()
        self.assertEqual(caught.exception.status_code, 503)
        self.assertNotIn("insert_chunks", self.events)
        self.assertEqual(self.storage.objects, {})

    def test_missing_indexed_record_prevents_publication(self):
        self.database.failure = "missing_indexed"
        with self.assertRaises(ingestion.IngestionError) as caught:
            self.ingest()
        self.assertEqual(caught.exception.status_code, 503)
        self.assertNotIn("index_publish", self.events)

    def test_final_status_failure_is_compensated_before_refresh_lock_releases(self):
        for failure in ("indexed", "missing_indexed", "indexed_commit_then_raise"):
            with self.subTest(failure=failure):
                self.events.clear()
                self.database.failure = failure

                def refresh_with_lock_boundary(**kwargs):
                    try:
                        self.refresh(**kwargs)
                    except ingestion.IngestionError:
                        self.events.append("refresh_lock_released")
                        raise

                self.service._index_refresher = refresh_with_lock_boundary
                with self.assertRaises(ingestion.IngestionError) as caught:
                    self.ingest()
                self.assertEqual(caught.exception.status_code, 503)
                self.assertLess(self.events.index("failed"), self.events.index("refresh_lock_released"))
                self.assertNotIn("index_publish", self.events)
                self.assertTrue(all(record.status == "failed" for record in self.database.records.values()))

    def test_cleanup_failure_does_not_expose_sdk_details(self):
        self.storage.failure = "delete_pdf"
        with patch.object(ingestion, "extract_text_from_pdf_bytes", side_effect=RuntimeError("private-sdk-detail")):
            with self.assertLogs(ingestion.logger, level="WARNING") as logs:
                with self.assertRaises(ingestion.IngestionError) as caught:
                    self.ingest()
        self.assertNotIn("private-sdk-detail", " ".join(logs.output))
        self.assertNotIn("private-sdk-detail", str(caught.exception))
        self.assertEqual(next(iter(self.database.records.values())).status, "failed")

    def test_duplicate_filenames_have_separate_uuids_paths_and_chunks(self):
        first = self.ingest()
        second = self.ingest()
        self.assertNotEqual(first["document"]["id"], second["document"]["id"])
        self.assertEqual(len(self.storage.objects), 2)
        self.assertEqual(len(self.database.chunks), 2)
        for record in self.database.records.values():
            self.assertIn(str(record.id), record.storage_path)

    def test_database_conflict_is_409_and_does_not_upload(self):
        class Conflict(Exception):
            code = "23505"
        with patch.object(self.database, "create_document", side_effect=Conflict("private-sdk-detail")):
            with self.assertRaises(ingestion.IngestionError) as caught:
                self.ingest()
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(self.storage.objects, {})

    def test_multi_page_pdf_preserves_page_positions(self):
        with pymupdf.open() as document:
            for text in ("First page evidence.", "Second page evidence."):
                document.new_page().insert_text((72, 72), text)
            content = document.tobytes()
        self.assertEqual(inspect_pdf_bytes(content), 2)
        self.assertEqual([page["page_number"] for page in extract_text_from_pdf_bytes(content)], [1, 2])
        result = self.ingest(content=content)
        chunks = self.database.chunks[UUID(result["document"]["id"])]
        self.assertEqual([(item.page_number, item.chunk_number) for item in chunks], [(1, 1), (2, 1)])
        self.assertEqual(result["document"]["page_count"], 2)
        self.assertEqual(result["document"]["chunk_count"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
