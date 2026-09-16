"""Offline tests for ingestion-specific database operations using real SDK requests."""

import json
from pathlib import Path
import sys
import unittest
from uuid import UUID

import httpx
from supabase import create_client
from supabase.client import ClientOptions

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.database_service import DatabaseService, DocumentCreate


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
