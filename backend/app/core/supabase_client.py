"""Lazy server client; never imported or called by the local retrieval pipeline."""

from functools import lru_cache

from supabase import Client, create_client
from supabase.client import ClientOptions

from .config import SupabaseConfigurationError, get_settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Create one backend client without signing in users or persisting sessions."""
    settings = get_settings()
    try:
        return create_client(
            str(settings.supabase_url).rstrip("/"),
            settings.supabase_secret_key.get_secret_value(),
            options=ClientOptions(
                schema="public",
                auto_refresh_token=False,
                persist_session=False,
                postgrest_client_timeout=10,
                storage_client_timeout=30,
            ),
        )
    except Exception:
        # SDK exceptions may contain request details; do not expose them to logs.
        raise SupabaseConfigurationError(
            "Supabase client initialization failed. Check backend settings and "
            "install backend/requirements.txt in the existing virtual environment."
        ) from None
