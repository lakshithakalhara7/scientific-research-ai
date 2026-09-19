"""Read-only live check: configuration, client, then SELECT on documents.

Run from the repository root:
    backend/.venv/Scripts/python.exe -m unittest discover -s backend/tests -p test_supabase_connection.py -v
"""

from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import SupabaseConfigurationError, get_settings


class SupabaseConnectionTest(unittest.TestCase):
    def test_documents_read_only(self) -> None:
        try:
            get_settings()
        except SupabaseConfigurationError as error:
            self.skipTest(str(error))

        try:
            from app.core.supabase_client import get_supabase_client
        except ImportError:
            self.fail("Supabase dependency is unavailable; install backend/requirements.txt.")

        try:
            client = get_supabase_client()
        except SupabaseConfigurationError as error:
            self.fail(str(error))

        try:
            response = client.table("documents").select("id").limit(1).execute()
        except Exception as error:
            # Never print the raw exception, request headers, URL, or credentials.
            code = getattr(error, "code", None)
            status = getattr(getattr(error, "response", None), "status_code", None)
            if code in ("PGRST205", "42P01"):
                reason = (
                    "documents is unavailable in the Data API. Run backend/supabase/schema.sql "
                    "in the dashboard and check that the Data API exposes public."
                )
            elif code in ("42501", "PGRST301", "PGRST302", "PGRST303") or status in (401, 403):
                reason = (
                    "Supabase rejected access. Check the backend secret key and the explicit "
                    "service_role grants in backend/supabase/schema.sql."
                )
            else:
                reason = (
                    "Supabase documents query failed. Check network access, project health, "
                    "backend credentials, Data API settings, and schema grants. "
                    "Request details are intentionally omitted."
                )
            raise self.failureException(reason) from None

        self.assertIsInstance(response.data, list)
        print("Supabase configuration, client initialization, and documents SELECT: PASS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
