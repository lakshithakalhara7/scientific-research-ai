"""Offline auth regressions: real dependencies, fake Auth SDK and business services."""

from contextlib import ExitStack
import importlib
import os
from pathlib import Path
import subprocess
import sys
import textwrap
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import UUID

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient


BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.core import auth
from app.services import auth_service


DUMMY_URL = "https://offline-auth-test.invalid"
DUMMY_KEY = "offline-publishable-key"
DUMMY_TOKEN = "offline-test-token-not-a-jwt"
PRIVATE_DETAIL = "offline-private-error-detail-must-not-leak"
USER_ID = UUID(int=31)
FAKE_USER = {"id": str(USER_ID), "email": "offline@example.invalid"}
ANALYSIS = {
    "summary": "Evidence summary.", "key_findings": ["A finding."],
    "methods": ["An experiment."], "conclusion": "Further study is needed.",
}
RETRIEVAL = {"results": [{"text": "Scientific evidence from a test paper."}]}
ENVIRONMENT = {"SUPABASE_URL": DUMMY_URL, "SUPABASE_PUBLISHABLE_KEY": DUMMY_KEY}


class AuthServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.stack = self.enterContext(ExitStack())
        self.stack.enter_context(patch.dict(os.environ, ENVIRONMENT, clear=True))
        self.dotenv = self.stack.enter_context(patch.object(auth_service, "load_dotenv"))
        self.client = Mock()
        self.factory = self.stack.enter_context(
            patch.object(auth_service, "create_client", return_value=self.client)
        )
        self.service = auth_service.AuthService()

    def test_constructor_uses_publishable_key_for_auth_client(self) -> None:
        self.dotenv.assert_called_once_with()
        self.factory.assert_called_once_with(DUMMY_URL, DUMMY_KEY)

    def test_missing_auth_settings_fail_without_constructing_client(self) -> None:
        for missing in ENVIRONMENT:
            with self.subTest(missing=missing):
                environment = {key: value for key, value in ENVIRONMENT.items() if key != missing}
                # The server secret cannot substitute for a missing publishable key.
                environment["SUPABASE_SECRET_KEY"] = "offline-server-secret"
                with patch.dict(os.environ, environment, clear=True):
                    self.factory.reset_mock()
                    with self.assertRaises(RuntimeError):
                        auth_service.AuthService()
                    self.factory.assert_not_called()

    def test_empty_token_is_rejected_without_auth_request(self) -> None:
        for token in (None, ""):
            with self.subTest(token=token):
                self.assertEqual(self.service.verify_access_token(token), {
                    "authenticated": False, "user": None,
                    "reason": "Access token is missing.",
                })
        self.client.auth.get_user.assert_not_called()

    def test_verified_user_maps_id_and_email_only(self) -> None:
        self.client.auth.get_user.return_value = SimpleNamespace(user=SimpleNamespace(
            id=USER_ID, email=FAKE_USER["email"], private_metadata=PRIVATE_DETAIL,
        ))
        self.assertEqual(self.service.verify_access_token(DUMMY_TOKEN), {
            "authenticated": True, "user": FAKE_USER, "reason": None,
        })
        self.client.auth.get_user.assert_called_once_with(DUMMY_TOKEN)

    def test_response_without_user_is_rejected(self) -> None:
        self.client.auth.get_user.return_value = SimpleNamespace(user=None)
        self.assertEqual(self.service.verify_access_token(DUMMY_TOKEN), {
            "authenticated": False, "user": None,
            "reason": "Invalid authentication token.",
        })

    def test_sdk_error_is_sanitized(self) -> None:
        self.client.auth.get_user.side_effect = RuntimeError(PRIVATE_DETAIL)
        result = self.service.verify_access_token(DUMMY_TOKEN)
        self.assertEqual(result, {
            "authenticated": False, "user": None,
            "reason": "Authentication failed or the token is invalid.",
        })
        self.assertNotIn(PRIVATE_DETAIL, str(result))


class ProtectedRouteAuthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Unrelated eager Gemini setup is outside this auth test's scope.
        with patch("dotenv.load_dotenv"), patch("google.genai.Client"), patch("nltk.download"):
            cls.main = importlib.import_module("app.main")
        cls.documents = importlib.import_module("app.api.documents")

    def setUp(self) -> None:
        auth.get_auth_service.cache_clear()
        self.addCleanup(auth.get_auth_service.cache_clear)
        self.stack = self.enterContext(ExitStack())
        self.stack.enter_context(patch.dict(os.environ, ENVIRONMENT, clear=True))
        self.dotenv = self.stack.enter_context(patch.object(auth_service, "load_dotenv"))
        self.auth_client = Mock()
        self.auth_client.auth.get_user.return_value = SimpleNamespace(user=SimpleNamespace(
            id=USER_ID, email=FAKE_USER["email"],
        ))
        self.auth_factory = self.stack.enter_context(
            patch.object(auth_service, "create_client", return_value=self.auth_client)
        )
        self.retrieval = self.stack.enter_context(
            patch.object(self.main.retrieval_agent, "run", return_value=RETRIEVAL)
        )
        self.analysis = self.stack.enter_context(
            patch.object(self.main.analysis_agent, "analyze", return_value=ANALYSIS)
        )
        self.verification = self.stack.enter_context(patch.object(
            self.main.verification_agent, "verify_analysis", return_value={"verified": True},
        ))
        self.security = self.stack.enter_context(patch.object(
            self.main.security_service, "prepare_safe_query",
            side_effect=lambda query: {"safe": True, "query": query},
        ))
        self.ingestion = Mock()
        self.ingestion.ingest_pdf.return_value = {
            "status": "success", "document": {
                "id": str(UUID(int=41)), "original_filename": "paper.pdf",
                "status": "indexed", "page_count": 1, "chunk_count": 1,
            },
        }
        self.stack.enter_context(patch.dict(self.main.app.dependency_overrides, {
            self.documents.get_ingestion_service: lambda: self.ingestion,
        }, clear=True))
        self.client = self.enterContext(TestClient(self.main.app))

    def protected_requests(self):
        return (
            ("/agents/retrieve", {"json": {"query": "Scientific evidence"}}, 200),
            ("/documents/upload", {"files": {
                "file": ("paper.pdf", b"%PDF-offline-fixture", "application/pdf"),
            }}, 201),
            ("/analyze", {"json": {"question": "Scientific evidence", "chunks": ["Evidence"]}}, 200),
            ("/verify", {"json": {"analysis": ANALYSIS, "retrieval_output": RETRIEVAL}}, 200),
            ("/research", {"json": {"question": "Scientific evidence"}}, 200),
        )

    def assert_no_business_calls(self) -> None:
        for service in (self.retrieval, self.analysis, self.verification, self.security):
            service.assert_not_called()
        self.ingestion.ingest_pdf.assert_not_called()

    def test_all_protected_routes_require_bearer_auth_without_loading_config(self) -> None:
        for path, kwargs, _ in self.protected_requests():
            with self.subTest(path=path):
                response = self.client.post(path, **kwargs)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.json(), {"detail": "Authentication is required."})
        self.dotenv.assert_not_called()
        self.auth_factory.assert_not_called()
        self.assert_no_business_calls()

    def test_malformed_authorization_is_rejected_before_auth_sdk(self) -> None:
        for header in ("Basic offline-value", "Bearer", "Bearer "):
            for path, kwargs, _ in self.protected_requests():
                with self.subTest(path=path, header=header):
                    response = self.client.post(path, headers={"Authorization": header}, **kwargs)
                    self.assertEqual(response.status_code, 401)
        self.auth_factory.assert_not_called()
        self.assert_no_business_calls()

    def test_invalid_token_is_rejected_safely_on_every_protected_route(self) -> None:
        self.auth_client.auth.get_user.side_effect = RuntimeError(PRIVATE_DETAIL)
        for path, kwargs, _ in self.protected_requests():
            with self.subTest(path=path):
                response = self.client.post(path, headers={"Authorization": f"Bearer {DUMMY_TOKEN}"}, **kwargs)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.json(), {
                    "detail": "Authentication failed or the token is invalid.",
                })
                self.assertNotIn(PRIVATE_DETAIL, response.text)
                self.assertNotIn(DUMMY_TOKEN, response.text)
        self.assertEqual(self.auth_client.auth.get_user.call_count, 5)
        self.assert_no_business_calls()

    def test_missing_verified_user_returns_401(self) -> None:
        self.auth_client.auth.get_user.return_value = SimpleNamespace(user=None)
        response = self.client.post("/agents/retrieve", json={"query": "Scientific evidence"},
                                    headers={"Authorization": f"Bearer {DUMMY_TOKEN}"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid authentication token."})
        self.assert_no_business_calls()

    def test_verified_token_reaches_all_secured_business_routes(self) -> None:
        for path, kwargs, expected in self.protected_requests():
            with self.subTest(path=path):
                response = self.client.post(path, headers={"Authorization": f"Bearer {DUMMY_TOKEN}"}, **kwargs)
                self.assertEqual(response.status_code, expected)
        self.assertEqual(self.auth_client.auth.get_user.call_count, 5)
        self.auth_factory.assert_called_once_with(DUMMY_URL, DUMMY_KEY)
        self.assertEqual(self.retrieval.call_count, 2)
        self.assertEqual(self.analysis.call_count, 2)
        self.assertEqual(self.verification.call_count, 2)
        self.ingestion.ingest_pdf.assert_called_once()

    def test_fake_dependency_reaches_secured_routes_and_cleanup_restores_auth(self) -> None:
        with patch.dict(self.main.app.dependency_overrides, {auth.get_current_user: lambda: dict(FAKE_USER)}):
            for path, kwargs, expected in self.protected_requests():
                with self.subTest(path=path):
                    self.assertEqual(self.client.post(path, **kwargs).status_code, expected)
        self.assertNotIn(auth.get_current_user, self.main.app.dependency_overrides)
        for path, kwargs, _ in self.protected_requests():
            with self.subTest(restored_auth_for=path):
                self.assertEqual(self.client.post(path, **kwargs).status_code, 401)
        self.auth_factory.assert_not_called()
        self.auth_client.auth.get_user.assert_not_called()

    def test_missing_configuration_returns_safe_503_only_when_auth_is_requested(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(self.client.get("/health").status_code, 200)
            self.assertEqual(self.client.get("/").status_code, 200)
            self.dotenv.assert_not_called()
            response = self.client.post("/agents/retrieve", json={"query": "Scientific evidence"},
                                        headers={"Authorization": f"Bearer {DUMMY_TOKEN}"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Authentication service is unavailable."})
        self.auth_factory.assert_not_called()
        self.assert_no_business_calls()

    def test_client_construction_failure_is_safe_and_later_request_can_retry(self) -> None:
        self.auth_factory.side_effect = RuntimeError(PRIVATE_DETAIL)
        kwargs = {"json": {"query": "Scientific evidence"},
                  "headers": {"Authorization": f"Bearer {DUMMY_TOKEN}"}}
        response = self.client.post("/agents/retrieve", **kwargs)
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Authentication service is unavailable."})
        self.assert_no_business_calls()
        self.auth_factory.side_effect = None
        self.assertEqual(self.client.post("/agents/retrieve", **kwargs).status_code, 200)
        self.assertEqual(self.auth_factory.call_count, 2)

    def test_current_user_returns_sdk_verified_identity(self) -> None:
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=DUMMY_TOKEN)
        self.assertEqual(auth.get_current_user(credentials), FAKE_USER)
        self.auth_client.auth.get_user.assert_called_once_with(DUMMY_TOKEN)

    def test_empty_credentials_are_rejected_without_constructing_auth_service(self) -> None:
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
        with self.assertRaises(HTTPException) as caught:
            auth.get_current_user(credentials)
        self.assertEqual(caught.exception.status_code, 401)
        self.assertEqual(caught.exception.detail, "Authentication token is missing.")
        self.auth_factory.assert_not_called()


class AuthImportTests(unittest.TestCase):
    def test_fresh_import_and_health_need_no_auth_settings_or_auth_client(self) -> None:
        script = textwrap.dedent("""
            import asyncio
            import os
            from types import SimpleNamespace
            from unittest.mock import patch

            for name in tuple(os.environ):
                if name.startswith("SUPABASE_") or name in (
                    "TEST_USER_EMAIL", "TEST_USER_PASSWORD", "GEMINI_API_KEY"
                ):
                    os.environ.pop(name)

            # Windows asyncio creates an internal loopback socketpair here.
            # Construct it before blocking sockets during app import and requests.
            event_loop = asyncio.new_event_loop()
            with patch("dotenv.load_dotenv") as dotenv, \\
                 patch("supabase.create_client") as client_factory, \\
                 patch("google.genai.Client"), \\
                 patch("nltk.data.find"), \\
                 patch("nltk.download"), \\
                 patch("nltk.corpus.stopwords", SimpleNamespace(words=lambda language: [])), \\
                 patch("socket.socket.connect", side_effect=AssertionError("Network is forbidden")):
                from app.core import auth
                from app.services import auth_service
                dotenv.assert_not_called()
                client_factory.assert_not_called()
                assert auth.get_auth_service.cache_info().currsize == 0

                from app.main import app
                from fastapi.testclient import TestClient
                with TestClient(app, backend_options={"loop_factory": lambda: event_loop}) as client:
                    assert client.get("/health").json() == {"status": "healthy"}
                    assert client.post("/agents/retrieve", json={"query": "evidence"}).status_code == 401
                client_factory.assert_not_called()
                assert auth.get_auth_service.cache_info().currsize == 0
            print("offline-auth-import-ok")
        """)
        result = subprocess.run(
            [sys.executable, "-c", script], cwd=BACKEND, text=True,
            capture_output=True, timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "offline-auth-import-ok")


if __name__ == "__main__":
    unittest.main(verbosity=2)
