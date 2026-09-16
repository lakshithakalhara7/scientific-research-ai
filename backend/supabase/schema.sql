-- Apply manually in the Supabase SQL Editor for scientific-research-ai.
-- This foundation stores PDF metadata and extracted text, never PDF binaries.
-- IF NOT EXISTS supports rerunning this initial schema; it does not migrate
-- existing tables with different columns, constraints, policies, or grants.

begin;

create table if not exists public.documents (
    id uuid primary key default gen_random_uuid(),
    title text,
    original_filename text not null,
    category text,
    doi text,
    source_url text,
    storage_path text not null unique,
    mime_type text not null default 'application/pdf',
    file_size_bytes bigint check (file_size_bytes >= 0),
    status text not null default 'uploaded'
        check (status in ('uploaded', 'processing', 'indexed', 'failed')),
    page_count integer check (page_count >= 0),
    created_at timestamptz not null default now()
);

create table if not exists public.document_chunks (
    id uuid primary key default gen_random_uuid(),
    document_id uuid not null references public.documents(id) on delete cascade,
    page_number integer not null check (page_number > 0),
    chunk_number integer not null check (chunk_number > 0),
    chunk_text text not null,
    processed_text text,
    token_count integer check (token_count >= 0),
    created_at timestamptz not null default now(),
    unique (document_id, page_number, chunk_number)
);

alter table public.documents enable row level security;
alter table public.document_chunks enable row level security;

-- Limit changes to these two tables. Keep automatic table exposure disabled.
-- No anonymous, authenticated-user, or frontend access is granted.
revoke all privileges on table public.documents, public.document_chunks
    from public, anon, authenticated, service_role;

-- The trusted backend's secret key uses service_role, which bypasses RLS but
-- still requires PostgreSQL grants. Grant only operations implemented here.
grant usage on schema public to service_role;
grant select, insert on table public.documents to service_role;
grant update (status) on table public.documents to service_role;
grant select, insert on table public.document_chunks to service_role;

-- UUID defaults need no sequence grants. No RLS policies are created.
commit;
