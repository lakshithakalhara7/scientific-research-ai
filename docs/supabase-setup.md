# Supabase foundation setup

The existing local PDF retrieval pipeline continues to run independently of
Supabase. This foundation adds configuration, isolated database and storage
services, and a read-only connection test. It creates no cloud resources
automatically and adds no upload or retrieval endpoints. Actual ingestion
migration requires separate approval.

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
`diabetes/<document-uuid>/paper.pdf`; it is neither a public URL nor a local file
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
configuration produces a clear configuration error when Supabase is requested;
the existing retrieval path does not initialize Supabase. Settings and the client
are cached, so restart the backend after changing credentials.

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

## 4. Install and verify the foundation

Requirements pin `supabase==2.31.0` and `websockets==15.0.1`, because the
Supabase client's Realtime dependency requires `websockets>=11,<16`. All other
existing dependency pins are preserved. Do not bypass dependency resolution
with `--no-deps`.

Use the existing backend virtual environment. From the repository root:

```powershell
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\backend\.venv\Scripts\python.exe -m unittest discover -s backend/tests -p test_supabase_foundation.py -v
.\backend\.venv\Scripts\python.exe -m unittest discover -s backend/tests -p test_supabase_connection.py -v
```

The foundation tests run offline. The connection test loads configuration,
initializes the official Supabase client, and queries `documents` without inserting
or deleting records. An empty table is valid. Missing credentials are reported
clearly as a skip; inspect the test output rather than treating a skip as proof of
a working connection. The connection test does not verify bucket configuration.

If the connection fails, confirm the project is reachable, the schema was applied,
the Data API is enabled, `public` is exposed, and the backend role has the grants
from the schema. Review credentials locally without printing them. A missing table
or permission error requires completing the dashboard setup, not adding permissive
frontend policies.

The new service methods remain disconnected from `RetrievalAgent`. Do not switch
the local ingestion source or migrate research PDFs until the foundation has been
reviewed and the next task approved.
