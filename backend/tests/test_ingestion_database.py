"""Offline tests for ingestion-specific database operations using real SDK requests."""

import json
from pathlib import Path
import sys
import unittest
from uuid import UUID

import httpx
from postgrest.exceptions import APIError
from pydantic import ValidationError
from supabase import create_client
from supabase.client import ClientOptions

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.database_service import DatabaseService, DocumentChunkCreate, DocumentCreate


class IngestionDatabaseTests(unittest.TestCase):
    def client(self, handler):
        http = httpx.Client(transport=httpx.MockTransport(handler))
        self.addCleanup(http.close)
        return DatabaseService(create_client(
            "https://offline-test.invalid", "offline-test-key",
            options=ClientOptions(httpx_client=http, persist_session=False, auto_refresh_token=False),
        ))

    def test_insert_preserves_allocated_primary_key_and_storage_path(self):
        identifier = UUID(int=1)
        metadata = DocumentCreate(
            original_filename="paper.pdf", storage_path=f"documents/{identifier}/paper.pdf",
            page_count=1,
        )

        def handle(request):
            payload = json.loads(request.content)
            self.assertEqual(payload["id"], str(identifier))
            self.assertEqual(payload["storage_path"], metadata.storage_path)
            return httpx.Response(201, json=[{
                **payload, "status": "uploaded", "created_at": "2026-01-01T00:00:00Z",
            }])

        record = self.client(handle).create_document(metadata, document_id=identifier)
        self.assertEqual(record.id, identifier)

    def test_indexed_documents_read_paginates_under_lower_server_cap(self):
        offsets = []

        def handle(request):
            self.assertEqual(request.url.params["status"], "eq.indexed")
            self.assertEqual(request.url.params["order"], "id.asc")
            offset = int(request.url.params["offset"])
            offsets.append(offset)
            rows = [] if offset == 2 else [{
                "id": str(UUID(int=offset + 1)), "original_filename": "paper.pdf",
                "storage_path": f"example/{offset}.pdf", "status": "indexed",
                "created_at": "2026-01-01T00:00:00Z",
            }]
            return httpx.Response(200, json=rows)

        self.assertEqual(len(self.client(handle).get_indexed_documents()), 2)
        self.assertEqual(offsets, [0, 1, 2])

    def test_realistic_bulk_insert_normalizes_nul_and_preserves_scientific_unicode(self):
        rows = [
            DocumentChunkCreate(
                page_number=page, chunk_number=number,
                chunk_text=("Scientific \u03b2 evidence \u2264 threshold " * 45) + (
                    "matrix\x00value\x00term\x00" if page == 5 and number == 1 else "valid text"
                ),
                processed_text="scientific \u03b2 evidence \u2264 threshold matrix\x00value",
                token_count=6,
            )
            for page in range(1, 24)
            for number in range(1, 3 if page <= 21 else 2)
        ]
        requests = []

        def handle(request):
            requests.append(request)
            payload = json.loads(request.content)
            self.assertEqual(len(payload), 44)
            self.assertGreater(len(request.content), 60_000)
            self.assertIn("return=minimal", request.headers["prefer"])
            self.assertEqual(len({(row['document_id'], row['page_number'], row['chunk_number']) for row in payload}), 44)
            for row in payload:
                for field in ("chunk_text", "processed_text"):
                    self.assertNotIn("\x00", row[field])
                    self.assertIn("\u03b2", row[field])
                    self.assertIn("\u2264", row[field])
                for field in ("page_number", "chunk_number", "token_count"):
                    self.assertIs(type(row[field]), int)
                self.assertTrue(all(value is not None for value in row.values()))
            return httpx.Response(201)

        self.client(handle).create_document_chunks(UUID(int=1), rows)
        self.assertEqual(len(requests), 1, "Keep the existing atomic insert; batching does not fix NUL.")

    def test_nul_only_required_text_is_rejected_after_normalization(self):
        with self.assertRaises(ValidationError):
            DocumentChunkCreate(page_number=1, chunk_number=1, chunk_text="\x00\x00")
        chunk = DocumentChunkCreate(page_number=1, chunk_number=1, chunk_text="valid", processed_text=None)
        self.assertIsNone(chunk.processed_text)

    def test_insert_error_diagnostics_exclude_sdk_message_details_and_credentials(self):
        private = "offline-private-value-must-not-leak"
        rows = [DocumentChunkCreate(page_number=1, chunk_number=1, chunk_text="valid")]
        for code in ("22P05", "42501", private):
            with self.subTest(code_is_sqlstate=code != private):
                def handle(request):
                    return httpx.Response(400, json={
                        "code": code, "message": private, "details": private,
                        "hint": "Authorization: Bearer " + private,
                    })

                with self.assertLogs("app.services.database_service", level="WARNING") as logs:
                    with self.assertRaises(APIError):
                        self.client(handle).create_document_chunks(UUID(int=1), rows)
                rendered = " ".join(logs.output)
                self.assertIn("type=APIError", rendered)
                self.assertIn("code=" + (code if code != private else "unknown"), rendered)
                self.assertNotIn(private, rendered)
                self.assertNotIn("Authorization", rendered)
                if code == "22P05":
                    self.assertIn("unsupported Unicode escape sequence", rendered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
