# Supabase setup and PDF ingestion

The backend now supports `POST /documents/upload`: validation, private PDF
storage, metadata and chunk persistence, and explicit refresh of the existing
BM25 index. Usable indexed Supabase chunks form the primary corpus; local PDF
retrieval remains a fallback when that corpus is empty or unavailable at first
load. The sources are not merged. No local corpus migration occurs automatically.

The existing project, tables, and private bucket can be reused as configured.
There are no new SQL migrations or database grants for this ingestion change.
Steps 1 and 2 below document initial setup for a new project; do not recreate
resources that already exist. All cloud provisioning remains manual.

## 1. Apply the database schema manually

1. Open the existing **scientific-research-ai** project in the Supabase dashboard.
2. Open **SQL Editor** and create a new query.
3. Review and paste the contents of
   [`backend/supabase/schema.sql`](../backend/supabase/schema.sql), then run it.
4. Confirm `public.documents` and `public.document_chunks` exist and have Row
   Level Security enabled. No public, anonymous, or frontend policies are needed.
5. In the project's Data API settings, confirm the Data API is enabled and
   `public` is an exposed schema. Keep **automatic table exposure disabled**.

The schema grants `service_role` only schema usage, document reads and inserts,
updates to `documents.status`, and chunk reads and inserts. It grants no database
deletes, chunk updates, or frontend access. PostgreSQL grants are required even
when the server role bypasses RLS. See
[Supabase Data API security](https://supabase.com/docs/guides/api/securing-your-api).

The SQL is transactional and can be rerun against tables created by this same
file. `CREATE TABLE IF NOT EXISTS` does **not** reconcile an existing table with a
different shape, remove pre-existing policies or column grants, or apply later
schema changes. Review any existing tables of these names first; future changes
need explicit migrations. The script does not change project-wide default grants
or other tables.

`storage_path` is the object key within the `research-papers` bucket, for example
`documents/<document-uuid>/paper.pdf`; it is neither a public URL nor a local file
path. PostgreSQL stores metadata and text only. The unique chunk key also indexes
document/page/chunk lookups.

## 2. Create the private PDF bucket manually

1. Open **Storage** in the dashboard and choose **New bucket**.
2. Set the bucket name to **research-papers**.
3. Leave the **Public bucket** option off, then create the bucket.
4. In its configuration, restrict allowed MIME types to **application/pdf** and
   set the suggested maximum file size to **25 MB** (25,000,000 bytes when entering
   a byte limit). The project-wide limit must allow this size.
5. Confirm the bucket is private. Do not add anonymous/public or frontend access
   policies during this foundation task.

Bucket creation and restrictions are dashboard operations. The backend service
expects this bucket to exist; it does not provision it. See the
[Storage quickstart](https://supabase.com/docs/guides/storage/quickstart),
[bucket restrictions](https://supabase.com/docs/guides/storage/buckets/creating-buckets),
and [file limits](https://supabase.com/docs/guides/storage/uploads/file-limits).

## 3. Configure backend credentials locally

Find the project URL in the project's **Connect** dialog or Data API settings.
Find the backend secret key under **Settings > API Keys**. Use the server secret
key for `SUPABASE_SECRET_KEY`; a publishable key is not suitable for these trusted
backend operations. The secret key uses `service_role` and bypasses RLS, so keep
it exclusively in controlled backend environments. See
[Supabase API keys](https://supabase.com/docs/guides/getting-started/api-keys).

If `backend/.env` already exists, preserve it. For a new checkout, copy
[`backend/.env.example`](../backend/.env.example) to `backend/.env`, then fill in
the two values locally:

```dotenv
SUPABASE_URL=
SUPABASE_SECRET_KEY=
```

The configuration loader reads that backend file using its absolute path and
allows process environment variables to take precedence. Missing or invalid
configuration produces a clear configuration error when Supabase is requested.
The first retrieval query attempts to load persistent indexed chunks, with local
corpus fallback when no searchable persistent chunks exist or configuration or
Supabase is unavailable. Uploads require working Supabase access. Settings and
the client are cached, so restart the backend after changing credentials.

Never paste actual keys or database passwords into source, documentation, logs,
screenshots, issue reports, or chat. Never commit `backend/.env`. Never place the
secret key in frontend code, frontend environment variables, or browser requests.
The variable names in this guide are safe; their real values must remain local.
Do not add research PDFs to Git either.

From the repository root, confirm the ignore rules without displaying contents:

```powershell
git check-ignore -v backend/.env
git check-ignore -v backend/app/data/research_papers/
```

## 4. Install and verify

Requirements pin `supabase==2.31.0` and `websockets==15.0.1`, because the
Supabase client's Realtime dependency requires `websockets>=11,<16`. All other
existing dependency pins are preserved. Do not bypass dependency resolution
with `--no-deps`.

Use the existing backend virtual environment. From the repository root:

```powershell
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\backend\.venv\Scripts\python.exe -m unittest discover -s backend/tests -p test_supabase_foundation.py -v
.\backend\.venv\Scripts\python.exe -m unittest discover -s backend/tests -p test_supabase_connection.py -v
.\backend\.venv\Scripts\python.exe -m unittest discover -s backend/tests -p test_ingestion*.py -v
.\backend\.venv\Scripts\python.exe -m unittest discover -s backend/tests -p test_document_upload_api.py -v
.\backend\.venv\Scripts\python.exe -m unittest discover -s backend/tests -p test_retrieval_index.py -v
.\backend\.venv\Scripts\python.exe test_pdf.py
.\backend\.venv\Scripts\python.exe test_retrieval_agent.py
.\backend\.venv\Scripts\python.exe -m pip check
```

The foundation, ingestion, upload API, and retrieval-index tests run offline with
fake cloud services. Their generated PDFs contain original test text; they do not
upload existing research papers. The connection test loads configuration,
initializes the official Supabase client, and queries `documents` without inserting
or deleting records. An empty table is valid. Missing credentials are reported
clearly as a skip; inspect the test output rather than treating a skip as proof of
a working connection. The connection test does not verify bucket configuration.

If the connection fails, confirm the project is reachable, the schema was applied,
the Data API is enabled, `public` is exposed, and the backend role has the grants
from the schema. Review credentials locally without printing them. A missing table
or permission error requires completing the dashboard setup, not adding permissive
frontend policies.

## 5. Upload one PDF through FastAPI

From the repository root, start one backend worker for the trusted local
prototype:

```powershell
.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

The upload endpoint has no application authentication yet. Keep this prototype
restricted to trusted local use until authentication and authorization are added.
Do not send the Supabase secret key in client requests. Frontend, Auth, other
agents, and deployment are separate tasks.

In another terminal, upload an original or permitted test PDF. Replace the sample
path below with that file's path; this example does not select a research-corpus
file automatically:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/documents/upload" -F "file=@C:\path\to\your-test.pdf;type=application/pdf" -F "category=test" -F "title=My test document"
```

The required multipart field is `file`; `category`, `title`, `doi`, and
`source_url` are optional form fields. Files must have a plain `.pdf` filename,
PDF MIME type, a valid PDF header and structure, and at most 25,000,000 bytes.
Optional `source_url` values must be HTTP(S) URLs without embedded credentials.
Password-protected PDFs and PDFs without searchable extracted text are rejected;
OCR is not part of this task.

The endpoint responds with HTTP 201 after chunk persistence and index publication:

```json
{
  "status": "success",
  "document": {
    "id": "00000000-0000-4000-8000-000000000001",
    "title": "My test document",
    "original_filename": "your-test.pdf",
    "category": "test",
    "status": "indexed",
    "page_count": 1,
    "chunk_count": 1
  }
}
```

The UUID above is illustrative. Each request receives a new `uuid4` primary key
inserted into PostgreSQL and confirmed from the returned document row. Storage
uses `documents/{document_id}/{sanitized_filename}`, so duplicate filenames do
not collide. Chunk UUIDs are assigned by PostgreSQL. Page count is measured before
the initial metadata insert; the existing status-only update grant is sufficient.

Query a distinctive phrase from the PDF through the existing agent endpoint:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/agents/retrieve" -ContentType "application/json" -Body '{"query":"distinctive phrase from your test PDF"}'
```

Evidence for uploaded sources includes `document_id`, chunk UUID, filename,
page/chunk position, score, matched terms, and extracted text. The existing custom
BM25 algorithm ranks the selected corpus: usable Supabase chunks, or the local
fallback. It does not merge local copies with persistent evidence. Changing the
corpus can change numeric scores through BM25's corpus statistics; the algorithm
is unchanged. Supabase provides persistence, not a replacement search algorithm.

| HTTP status | Meaning |
| --- | --- |
| 201 | Metadata and chunks persisted; document indexed and searchable in this process. |
| 400 | Missing/invalid PDF, unsafe filename, invalid metadata, or no searchable extracted text. |
| 413 | File exceeds the 25 MB limit. |
| 409 | Conflicting storage/database operation. |
| 500 | Processing or index build failed. |
| 503 | Configuration or Supabase persistence is unavailable. |

Malformed multipart fields can also receive FastAPI validation errors. Raw SDK
exceptions, configuration values, and secret keys are never returned by ingestion.

## 6. Index refresh and failures

Ingestion coordinates `uploaded -> processing -> indexed` through the database
and storage service abstractions. It uses the existing extraction, chunking, NLP,
inverted index, and BM25 services; `RetrievalAgent` does not call Supabase directly.

The index is built once on first retrieval and reused by subsequent queries.
Usable indexed Supabase chunks are the sole primary source. Each usable chunk
needs nonblank raw text and nonempty processed tokens; existing `processed_text`
is reused, and NLP runs only when that field is null. If no persistent chunks are
searchable, the index uses the local corpus. Local PDFs are not loaded when
usable Supabase chunks exist.

Repeated records are removed by `(document_id, chunk_id)` for Supabase or
`(filename, page_number, chunk_number)` for local chunks. Identifiers remain
unchanged, and separately identified documents are not deduplicated by their text.

Successful ingestion performs an explicit strict rebuild from persistent chunks,
including usable chunks from the pending document. It prepares the replacement
before marking that document `indexed`, then atomically publishes the snapshot
under a process lock. Failed reads, builds, or final status updates preserve the
old snapshot and surface a sanitized failure; strict refresh errors do not switch
to local fallback.

If the first retrieval load cannot reach Supabase, it falls back to local PDFs
and caches that snapshot until restart or explicit refresh. Database failures
other than missing/invalid configuration produce a sanitized warning. Run one
backend process; multiple workers or instances do not share refresh notifications.
A direct database edit or an upload made by another process requires refresh or
restart in each consumer.

On failure after metadata creation, ingestion attempts to mark the row `failed`
and delete only this attempt's successfully uploaded Storage object. Any already
persisted chunks stay attached to the failed document and are excluded from
retrieval. If cleanup cannot reach Supabase, incomplete rows or objects may remain
for manual review. Retry with a new upload to receive a new UUID; automatic row
deletion or in-place retry cleanup is not implemented. Existing backend grants
remain sufficient and no new delete grants are required.

If a final status write commits but its response times out, ingestion attempts a
compensating `failed` update. An ongoing outage can prevent that update, leaving
the cloud row `indexed` even though the current process retained its old index.
Inspect such incomplete attempts and manually set their status to `failed`
before reloading. This prototype has no distributed transaction across database,
Storage, and the in-memory index.

## 7. One explicitly enabled live integration test

`backend/tests/test_live_ingestion.py` is skipped during ordinary test discovery.
When explicitly enabled, it generates one small original PDF in memory, uploads
it through the API, verifies private Storage bytes, metadata, chunks and indexed
status, then retrieves its unique phrase through the Retrieval Agent. It also
checks retrieval after clearing the cache. Only the generated fixture is uploaded;
index rebuilding uses persistent chunks once usable Supabase data exists. A cold
index can use local fallback before any searchable cloud chunks exist. No local
research PDFs are uploaded and no cloud resources are created.

Each enabled run uploads one new test document, retained as `indexed` for dashboard
review. The test prints its document UUID, never credentials. Avoid repeatedly
enabling the live test during routine unit testing.

```powershell
$env:RUN_LIVE_SUPABASE_INGESTION = "1"
try {
    .\backend\.venv\Scripts\python.exe -m unittest discover -s backend/tests -p test_live_ingestion.py -v
} finally {
    Remove-Item Env:RUN_LIVE_SUPABASE_INGESTION
}
```

Missing credentials cause a clear skip. A failed private-bucket restriction check
or live operation requires reviewing the existing project configuration; the test
does not recreate tables/buckets or upload a fallback research paper. An existing
backend running separately must refresh/restart to see the retained test document.

See [architecture.md](architecture.md) for service boundaries, persistent IDs,
local fallback behavior, and the evidence handoff to future team agents.
