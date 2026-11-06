import asyncio
import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi.security import HTTPAuthorizationCredentials

from webapp.api import (
    app,
    enforce_chat_rate_limit,
    require_auth0_user,
)


class ChatApiTests(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides.clear()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_root_serves_frontend(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome back", response.text)

    def test_health_check_is_public_and_prefixed(self) -> None:
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_api_docs_are_prefixed(self) -> None:
        response = self.client.get("/api/docs")

        self.assertEqual(response.status_code, 200)

    def test_chat_requires_bearer_token(self) -> None:
        with patch.dict(os.environ, {"AUTH0_DOMAIN": ""}):
            response = self.client.post(
                "/api/chat",
                json={"message": "Hello"},
            )

        self.assertEqual(response.status_code, 401)

    def test_chat_returns_structured_response(self) -> None:
        assistant_response = AsyncMock(return_value=("Hello!", []))
        with patch(
            "webapp.api.get_assistant_response",
            new=assistant_response,
        ):
            app.dependency_overrides[enforce_chat_rate_limit] = (
                lambda: "auth0|test-user"
            )
            response = self.client.post(
                "/api/chat",
                headers={"Authorization": "Bearer test-token"},
                json={"message": "Hello"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"response": "Hello!", "provider": "groq", "sources": []},
        )
        assistant_response.assert_awaited_once()

    def test_blank_message_is_rejected(self) -> None:
        app.dependency_overrides[enforce_chat_rate_limit] = (
            lambda: "auth0|test-user"
        )
        with patch.dict(os.environ, {"AUTH0_DOMAIN": ""}):
            response = self.client.post(
                "/api/chat",
                headers={"Authorization": "Bearer test-token"},
                json={"message": "   "},
            )

        self.assertEqual(response.status_code, 422)

    def test_auth0_configuration_is_required_for_frontend(self) -> None:
        with patch.dict(
            os.environ,
            {
                "AUTH0_DOMAIN": "",
                "AUTH0_CLIENT_ID": "",
                "AUTH0_AUDIENCE": "",
            },
        ):
            response = self.client.get("/api/config")

        self.assertEqual(response.status_code, 503)

    def test_auth0_user_is_resolved_from_verified_subject(self) -> None:
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test-token",
        )
        with (
            patch.dict(
                os.environ,
                {
                    "AUTH0_DOMAIN": "example.auth0.com",
                    "AUTH0_CLIENT_ID": "public-client-id",
                    "AUTH0_AUDIENCE": "https://api.example.com",
                },
            ),
            patch(
                "webapp.api._decode_auth0_token",
                return_value={"sub": "auth0|test-user"},
            ) as decode,
        ):
            subject = asyncio.run(require_auth0_user(credentials))

        self.assertEqual(subject, "auth0|test-user")
        decode.assert_called_once_with(
            "test-token",
            "example.auth0.com",
            "https://api.example.com",
        )

    def test_rate_limit_blocks_requests_after_configured_limit(self) -> None:
        redis_client = AsyncMock()
        redis_client.eval.side_effect = [[60, 30], [61, 12]]
        request = SimpleNamespace(
            app=SimpleNamespace(
                state=SimpleNamespace(redis=redis_client),
            ),
        )
        with patch.dict(os.environ, {"CHAT_RATE_LIMIT_PER_MINUTE": "60"}):
            subject = asyncio.run(enforce_chat_rate_limit(request, "auth0|user"))
            self.assertEqual(subject, "auth0|user")
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(enforce_chat_rate_limit(request, "auth0|user"))

        self.assertEqual(raised.exception.status_code, 429)
        self.assertEqual(raised.exception.headers["Retry-After"], "12")
        self.assertEqual(redis_client.eval.await_count, 2)


if __name__ == "__main__":
    unittest.main()
