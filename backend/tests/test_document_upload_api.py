"""Offline upload endpoint checks with fake services and no Supabase requests."""

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

import pymupdf
from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient
from starlette.datastructures import Headers


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api import documents
from app.core.auth import get_current_user
from app.main import app
from app.services.database_service import DocumentRecord
from app.services.ingestion_service import IngestionError, IngestionService
from app.services.storage_service import MAX_PDF_SIZE_BYTES


DOCUMENT_ID = str(UUID(int=41))
PDF = b"%PDF-1.7\nOffline API fixture"
DUMMY_PRIVATE_VALUE = "offline-private-value-must-not-leak"
FAKE_USER = {"id": str(UUID(int=42)), "email": "upload-test@example.invalid"}


def success_result() -> dict:
    return {
        "status": "success",
        "document": {
            "id": DOCUMENT_ID,
            "title": "Uploaded paper",
            "original_filename": "paper.pdf",
            "category": "test",
            "status": "indexed",
            "page_count": 1,
            "chunk_count": 2,
        },
    }


class DocumentUploadApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = Mock(spec=IngestionService)
        self.service.ingest_pdf.return_value = success_result()
        overrides = patch.dict(app.dependency_overrides, {
            get_current_user: lambda: FAKE_USER.copy(),
            documents.get_ingestion_service: lambda: self.service,
        })
        overrides.start()
        self.addCleanup(overrides.stop)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def upload(self, filename="paper.pdf", content=PDF, content_type="application/pdf", **metadata):
        return self.client.post(
            "/documents/upload",
            files={"file": (filename, content, content_type)},
            data=metadata,
        )

    def test_success_returns_indexed_metadata_and_passes_optional_fields(self) -> None:
        metadata = {
            "category": "test",
            "title": "Uploaded paper",
            "doi": "10.1234/test",
            "source_url": "https://example.org/paper",
        }
        response = self.upload(**metadata)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), success_result())
        self.service.ingest_pdf.assert_called_once_with(
            filename="paper.pdf", content_type="application/pdf", content=PDF, **metadata
        )

    def test_optional_metadata_can_be_omitted(self) -> None:
        response = self.upload()
        self.assertEqual(response.status_code, 201)
        for field in ("category", "title", "doi", "source_url"):
            self.assertIsNone(self.service.ingest_pdf.call_args.kwargs[field])

    def test_public_response_excludes_internal_service_fields(self) -> None:
        result = success_result()
        result["internal_detail"] = DUMMY_PRIVATE_VALUE
        result["document"]["storage_path"] = "documents/private/paper.pdf"
        result["document"]["internal_detail"] = DUMMY_PRIVATE_VALUE
        self.service.ingest_pdf.return_value = result
        response = self.upload()
        self.assertEqual(response.status_code, 201)
        self.assertNotIn(DUMMY_PRIVATE_VALUE, response.text)
        self.assertNotIn("storage_path", response.text)

    def test_missing_file_returns_400(self) -> None:
        response = self.client.post("/documents/upload", data={"title": "Missing PDF"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("PDF file is required", response.json()["detail"])
        self.service.ingest_pdf.assert_not_called()

    def test_real_validation_errors_become_400_without_cloud_calls(self) -> None:
        database, storage = Mock(), Mock()
        service = IngestionService(database=database, storage=storage, index_refresher=Mock())
        app.dependency_overrides[documents.get_ingestion_service] = lambda: service
        cases = [
            ("paper.txt", PDF, "application/pdf"),
            ("paper.pdf", PDF, "text/plain"),
            ("paper.pdf", b"", "application/pdf"),
            ("paper.pdf", b"Not a PDF", "application/pdf"),
            ("../paper.pdf", PDF, "application/pdf"),
            ("folder/paper.pdf", PDF, "application/pdf"),
        ]
        for filename, content, content_type in cases:
            with self.subTest(filename=filename, content_type=content_type, length=len(content)):
                response = self.upload(filename, content, content_type)
                self.assertEqual(response.status_code, 400)
                self.assertIsInstance(response.json()["detail"], str)
        self.assertEqual(database.mock_calls, [])
        self.assertEqual(storage.mock_calls, [])

    def test_invalid_metadata_returns_400_without_cloud_calls(self) -> None:
        database, storage = Mock(), Mock()
        service = IngestionService(database=database, storage=storage, index_refresher=Mock())
        app.dependency_overrides[documents.get_ingestion_service] = lambda: service
        response = self.upload(source_url="javascript:alert(1)")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(database.mock_calls, [])
        self.assertEqual(storage.mock_calls, [])

    def test_missing_filename_returns_400_without_cloud_calls(self) -> None:
        database, storage = Mock(), Mock()
        service = IngestionService(database=database, storage=storage, index_refresher=Mock())
        stream = BytesIO(PDF)
        file = UploadFile(file=stream, headers=Headers({"content-type": "application/pdf"}))
        with self.assertRaises(HTTPException) as caught:
            documents.upload_document(service, current_user=FAKE_USER.copy(), file=file)
        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn("filename", caught.exception.detail)
        self.assertTrue(stream.closed)
        self.assertEqual(database.mock_calls, [])
        self.assertEqual(storage.mock_calls, [])

    def test_safe_service_errors_preserve_http_status(self) -> None:
        for status_code in (400, 409, 413, 500, 503):
            with self.subTest(status_code=status_code):
                self.service.ingest_pdf.side_effect = IngestionError(
                    status_code, "A safe service error.", DOCUMENT_ID
                )
                response = self.upload()
                self.assertEqual(response.status_code, status_code)
                self.assertEqual(response.json(), {"detail": "A safe service error."})

    def test_real_pdf_reaches_persistence_and_index_refresh_through_endpoint(self) -> None:
        with pymupdf.open() as pdf:
            pdf.new_page().insert_text((72, 72), "Original upload endpoint test evidence.")
            content = pdf.tobytes()
        database, storage = Mock(), Mock()
        records = {}
        transitions = []

        def create(metadata, *, document_id):
            record = DocumentRecord(
                **metadata.model_dump(), id=document_id, status="uploaded",
                created_at=datetime.now(timezone.utc),
            )
            records[document_id] = record
            transitions.append("uploaded")
            return record

        def update(document_id, status):
            records[document_id] = records[document_id].model_copy(update={"status": status})
            transitions.append(status)
            return records[document_id]

        database.create_document.side_effect = create
        database.update_document_status.side_effect = update
        index_refresher = Mock(side_effect=lambda **kwargs: kwargs["on_ready"]())
        service = IngestionService(
            database=database, storage=storage, index_refresher=index_refresher
        )
        app.dependency_overrides[documents.get_ingestion_service] = lambda: service
        with patch("app.services.ingestion_service.preprocess_text", return_value=["test", "evidence"]):
            response = self.upload(content=content, title="Test evidence", category="test")
        self.assertEqual(response.status_code, 201)
        document = response.json()["document"]
        document_id = UUID(document["id"])
        self.assertEqual(transitions, ["uploaded", "processing", "indexed"])
        self.assertEqual(document["status"], "indexed")
        self.assertEqual(document["page_count"], 1)
        self.assertGreater(document["chunk_count"], 0)
        self.assertEqual(document["title"], "Test evidence")
        storage.upload_pdf.assert_called_once_with(f"documents/{document_id}/paper.pdf", content)
        chunks = database.create_document_chunks.call_args.args
        self.assertEqual(chunks[0], document_id)
        self.assertIn("endpoint test evidence", chunks[1][0].chunk_text)
        self.assertEqual(chunks[1][0].processed_text, "test evidence")
        index_refresher.assert_called_once()
        self.assertEqual(index_refresher.call_args.kwargs["pending_document_id"], document_id)

    def test_real_service_database_failure_returns_sanitized_503(self) -> None:
        with pymupdf.open() as pdf:
            pdf.new_page().insert_text((72, 72), "Original offline service failure fixture.")
            content = pdf.tobytes()
        database, storage = Mock(), Mock()
        database.create_document.side_effect = RuntimeError(DUMMY_PRIVATE_VALUE)
        service = IngestionService(database=database, storage=storage, index_refresher=Mock())
        app.dependency_overrides[documents.get_ingestion_service] = lambda: service
        with self.assertLogs("app.services.ingestion_service", level="WARNING") as captured:
            response = self.upload(content=content)
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(DUMMY_PRIVATE_VALUE, response.text)
        self.assertNotIn(DUMMY_PRIVATE_VALUE, " ".join(captured.output))
        self.assertEqual(storage.mock_calls, [])

    def test_oversized_multipart_returns_413(self) -> None:
        # A small test limit exercises real multipart parsing without a 25 MB fixture.
        with patch.object(documents, "MAX_PDF_SIZE_BYTES", 32):
            response = self.upload(content=b"%PDF-" + b"x" * 28)
        self.assertEqual(response.status_code, 413)
        self.service.ingest_pdf.assert_not_called()

    def test_oversized_known_file_is_closed_without_reading(self) -> None:
        stream = Mock()
        file = UploadFile(
            file=stream,
            filename="paper.pdf",
            size=MAX_PDF_SIZE_BYTES + 1,
            headers=Headers({"content-type": "application/pdf"}),
        )
        with self.assertRaises(HTTPException) as caught:
            documents.upload_document(self.service, current_user=FAKE_USER.copy(), file=file)
        self.assertEqual(caught.exception.status_code, 413)
        stream.read.assert_not_called()
        stream.close.assert_called_once()
        self.service.ingest_pdf.assert_not_called()

    def test_unknown_size_read_is_bounded_and_file_is_closed(self) -> None:
        stream = Mock()
        stream.read.return_value = b"%PDF-" + b"x" * 28
        file = UploadFile(
            file=stream,
            filename="paper.pdf",
            headers=Headers({"content-type": "application/pdf"}),
        )
        with patch.object(documents, "MAX_PDF_SIZE_BYTES", 32):
            with self.assertRaises(HTTPException) as caught:
                documents.upload_document(self.service, current_user=FAKE_USER.copy(), file=file)
        self.assertEqual(caught.exception.status_code, 413)
        stream.read.assert_called_once_with(33)
        stream.close.assert_called_once()
        self.service.ingest_pdf.assert_not_called()

    def test_unexpected_service_failure_returns_safe_500_and_safe_log(self) -> None:
        self.service.ingest_pdf.side_effect = RuntimeError(DUMMY_PRIVATE_VALUE)
        with self.assertLogs(documents.logger, level="ERROR") as captured:
            response = self.upload()
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {"detail": "Document ingestion failed."})
        self.assertNotIn(DUMMY_PRIVATE_VALUE, " ".join(captured.output))

    def test_upload_file_is_closed_after_service_failure(self) -> None:
        self.service.ingest_pdf.side_effect = RuntimeError(DUMMY_PRIVATE_VALUE)
        stream = BytesIO(PDF)
        file = UploadFile(
            file=stream,
            filename="paper.pdf",
            headers=Headers({"content-type": "application/pdf"}),
        )
        with self.assertLogs(documents.logger, level="ERROR"):
            with self.assertRaises(HTTPException):
                documents.upload_document(self.service, current_user=FAKE_USER.copy(), file=file)
        self.assertTrue(stream.closed)

    def test_existing_health_route_still_works(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})
        self.service.ingest_pdf.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
