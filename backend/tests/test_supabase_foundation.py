"""Offline foundation checks; dummy settings and mocked HTTP never use backend/.env.

Run from the repository root:
    backend/.venv/Scripts/python.exe -m unittest discover -s backend/tests -p test_supabase_foundation.py -v
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

import httpx
from pydantic import ValidationError
from supabase import create_client
from supabase.client import ClientOptions


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core import config, supabase_client
from app.services.database_service import (
    DatabaseService,
    DocumentChunkCreate,
    DocumentCreate,
)
from app.services.storage_service import MAX_PDF_SIZE_BYTES, StorageService


DOCUMENT_ID = UUID("00000000-0000-0000-0000-000000000001")
DUMMY_URL = "https://offline-test.invalid"
DUMMY_KEY = "offline-test-key"


class ConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        config.get_settings.cache_clear()
        supabase_client.get_supabase_client.cache_clear()
        self.addCleanup(config.get_settings.cache_clear)
        self.addCleanup(supabase_client.get_supabase_client.cache_clear)
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.settings = patch.dict(config.SupabaseSettings.model_config, {"env_file": None})
        self.settings.start()
        self.addCleanup(self.settings.stop)

    def set_dummy_environment(self) -> None:
        os.environ.update(SUPABASE_URL=DUMMY_URL, SUPABASE_SECRET_KEY=DUMMY_KEY)

    def test_missing_settings_have_actionable_error(self) -> None:
        with self.assertRaises(config.SupabaseConfigurationError) as caught:
            config.get_settings()
        message = str(caught.exception)
        self.assertIn("SUPABASE_URL", message)
        self.assertIn("SUPABASE_SECRET_KEY", message)
        self.assertIn("backend/.env", message)

    def test_invalid_configuration_does_not_disclose_values(self) -> None:
        invalid_url = "https://user:dummy-private-password@offline-test.invalid"
        os.environ.update(SUPABASE_URL=invalid_url, SUPABASE_SECRET_KEY=DUMMY_KEY)
        with self.assertRaises(config.SupabaseConfigurationError) as caught:
            config.get_settings()
        self.assertNotIn("dummy-private-password", str(caught.exception))
        self.assertNotIn(DUMMY_KEY, str(caught.exception))
        self.assertTrue(caught.exception.__suppress_context__)

    def test_environment_overrides_dotenv_from_another_working_directory(self) -> None:
        self.assertTrue(config.BACKEND_ENV_FILE.is_absolute())
        self.assertEqual(config.BACKEND_ENV_FILE.parent.name, "backend")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            fixture = directory / ".env"
            fixture.write_text(
                "SUPABASE_URL=https://dotenv-test.invalid\n"
                "SUPABASE_SECRET_KEY=dotenv-dummy-key\n",
                encoding="utf-8-sig",
            )
            other_directory = directory / "other"
            other_directory.mkdir()
            previous_directory = Path.cwd()
            try:
                os.chdir(other_directory)
                os.environ["SUPABASE_SECRET_KEY"] = DUMMY_KEY
                with patch.dict(config.SupabaseSettings.model_config, {"env_file": fixture}):
                    settings = config.get_settings()
            finally:
                os.chdir(previous_directory)
        self.assertEqual(str(settings.supabase_url), "https://dotenv-test.invalid/")
        self.assertEqual(settings.supabase_secret_key.get_secret_value(), DUMMY_KEY)
        self.assertNotIn(DUMMY_KEY, repr(settings))

    def test_client_is_cached_with_server_session_options(self) -> None:
        self.set_dummy_environment()
        with patch.object(supabase_client, "create_client") as factory:
            first = supabase_client.get_supabase_client()
            self.assertIs(first, supabase_client.get_supabase_client())
        factory.assert_called_once()
        self.assertEqual(factory.call_args.args, (DUMMY_URL, DUMMY_KEY))
        options = factory.call_args.kwargs["options"]
        self.assertFalse(options.auto_refresh_token)
        self.assertFalse(options.persist_session)
        self.assertEqual(options.schema, "public")

    def test_client_initialization_errors_are_sanitized(self) -> None:
        self.set_dummy_environment()
        with patch.object(supabase_client, "create_client", side_effect=ValueError(DUMMY_KEY)):
            with self.assertRaises(config.SupabaseConfigurationError) as caught:
                supabase_client.get_supabase_client()
        self.assertNotIn(DUMMY_KEY, str(caught.exception))
        self.assertTrue(caught.exception.__suppress_context__)


class DatabaseTests(unittest.TestCase):
    """Exercise actual PostgREST serialization with no network transport."""

    def setUp(self) -> None:
        self.requests: list[httpx.Request] = []
        self.handler = lambda request: httpx.Response(200, json=[])

        def dispatch(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            return self.handler(request)

        transport = httpx.MockTransport(dispatch)
        http_client = httpx.Client(transport=transport)
        self.addCleanup(http_client.close)
        client = create_client(
            DUMMY_URL,
            DUMMY_KEY,
            options=ClientOptions(
                httpx_client=http_client,
                persist_session=False,
                auto_refresh_token=False,
            ),
        )
        self.database = DatabaseService(client=client)

    def test_create_document_returns_typed_metadata(self) -> None:
        document = DocumentCreate(original_filename="paper.pdf", storage_path="example/paper.pdf")
        record = {
            **document.model_dump(mode="json"),
            "id": str(DOCUMENT_ID),
            "status": "uploaded",
            "created_at": "2026-01-01T00:00:00Z",
        }
        self.handler = lambda request: httpx.Response(201, json=[record])
        created = self.database.create_document(document)
        self.assertEqual(created.id, DOCUMENT_ID)
        self.assertEqual(created.status, "uploaded")
        request = self.requests[0]
        self.assertEqual(request.url.path, "/rest/v1/documents")
        self.assertEqual(json.loads(request.content), document.model_dump(mode="json"))

    def test_get_document_serializes_uuid_and_handles_missing_row(self) -> None:
        self.assertIsNone(self.database.get_document(DOCUMENT_ID))
        request = self.requests[0]
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.url.params["id"], f"eq.{DOCUMENT_ID}")
        self.assertEqual(request.url.params["limit"], "1")

    def test_chunk_read_continues_below_requested_server_cap(self) -> None:
        rows = [
            {
                "id": str(UUID(int=index + 10)),
                "document_id": str(DOCUMENT_ID),
                "page_number": 1 + index // 2,
                "chunk_number": 1 + index % 2,
                "chunk_text": f"Evidence {index}",
                "created_at": "2026-01-01T00:00:00Z",
            }
            for index in range(5)
        ]
        offsets = []

        def paginated(request: httpx.Request) -> httpx.Response:
            offset = int(request.url.params["offset"])
            offsets.append(offset)
            self.assertEqual(request.url.params["limit"], "1000")
            self.assertEqual(request.url.params["order"], "page_number.asc,chunk_number.asc")
            self.assertEqual(request.url.params["document_id"], f"eq.{DOCUMENT_ID}")
            return httpx.Response(200, json=rows[offset:offset + 2])

        self.handler = paginated
        result = self.database.get_document_chunks(DOCUMENT_ID)
        self.assertEqual(offsets, [0, 2, 4, 5])
        self.assertEqual([chunk.chunk_text for chunk in result], [row["chunk_text"] for row in rows])

    def test_chunk_insert_requests_minimal_response_and_serializes_uuid(self) -> None:
        self.handler = lambda request: httpx.Response(201)
        chunks = [DocumentChunkCreate(page_number=1, chunk_number=1, chunk_text="Evidence")]
        self.assertIsNone(self.database.create_document_chunks(DOCUMENT_ID, chunks))
        self.assertEqual(len(self.requests), 1)
        request = self.requests[0]
        self.assertIn("return=minimal", request.headers["prefer"])
        self.assertEqual(json.loads(request.content)[0]["document_id"], str(DOCUMENT_ID))
        self.database.create_document_chunks(DOCUMENT_ID, [])
        self.assertEqual(len(self.requests), 1)

    def test_invalid_status_ids_and_batches_do_not_send_requests(self) -> None:
        with self.assertRaises(ValueError):
            self.database.update_document_status(DOCUMENT_ID, "unknown")
        with self.assertRaises(ValueError):
            self.database.get_document("invalid-id")
        valid = DocumentChunkCreate(page_number=1, chunk_number=1, chunk_text="Evidence")
        with self.assertRaises(ValueError):
            self.database.create_document_chunks(DOCUMENT_ID, [valid, valid])
        invalid = valid.model_copy(update={"page_number": 0})
        with self.assertRaises(ValidationError):
            self.database.create_document_chunks(DOCUMENT_ID, [valid, invalid])
        self.assertEqual(self.requests, [])


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = Mock()
        self.bucket = self.client.storage.from_.return_value
        self.storage = StorageService(client=self.client)

    def test_upload_uses_private_bucket_pdf_type_and_prevents_overwrite(self) -> None:
        content = b"%PDF-1.7\nOffline fixture"
        self.assertEqual(self.storage.upload_pdf("example/paper.pdf", content), "example/paper.pdf")
        self.client.storage.from_.assert_called_once_with("research-papers")
        self.bucket.upload.assert_called_once_with(
            path="example/paper.pdf",
            file=content,
            file_options={"content-type": "application/pdf", "upsert": "false"},
        )

    def test_invalid_paths_and_content_do_not_contact_storage(self) -> None:
        for path in ("../paper.pdf", "/paper.pdf", "folder/../paper.pdf", "paper.txt", "folder\\paper.pdf"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.storage.upload_pdf(path, b"%PDF-1.7")
        with self.assertRaises(ValueError):
            self.storage.upload_pdf("paper.pdf", b"not a PDF")
        with self.assertRaises(TypeError):
            self.storage.upload_pdf("paper.pdf", "not bytes")
        with self.assertRaises(ValueError):
            self.storage.upload_pdf("paper.pdf", b"%PDF-" + b"x" * (MAX_PDF_SIZE_BYTES - 4))
        self.client.storage.from_.assert_not_called()

    def test_download_and_delete_target_only_requested_object(self) -> None:
        self.bucket.download.return_value = b"%PDF-1.7"
        self.assertEqual(self.storage.download_pdf("example/paper.pdf"), b"%PDF-1.7")
        self.bucket.download.assert_called_once_with("example/paper.pdf")
        self.storage.delete_pdf("example/paper.pdf")
        self.bucket.remove.assert_called_once_with(["example/paper.pdf"])
        self.assertEqual(self.client.storage.from_.call_count, 2)


class ConnectionReportingTests(unittest.TestCase):
    def test_live_test_failure_output_never_includes_raw_sdk_error(self) -> None:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        try:
            import test_supabase_connection
        finally:
            sys.path.pop(0)
        client = Mock()
        client.table.return_value.select.return_value.limit.return_value.execute.side_effect = (
            RuntimeError(f"Simulated SDK error containing {DUMMY_KEY}")
        )
        result = unittest.TestResult()
        live_test = test_supabase_connection.SupabaseConnectionTest("test_documents_read_only")
        with patch.object(test_supabase_connection, "get_settings"), patch.object(
            supabase_client, "get_supabase_client", return_value=client
        ):
            live_test.run(result)
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.errors, [])
        rendered_failure = result.failures[0][1]
        self.assertIn("Supabase documents query failed", rendered_failure)
        self.assertNotIn(DUMMY_KEY, rendered_failure)


if __name__ == "__main__":
    unittest.main(verbosity=2)
