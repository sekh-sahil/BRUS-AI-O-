import os
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from webapp.api import app


class ChatApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_check_is_public(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_chat_requires_bearer_token(self) -> None:
        with patch.dict(os.environ, {"API_ACCESS_TOKEN": "test-token"}):
            response = self.client.post(
                "/api/chat",
                json={"message": "Hello"},
            )

        self.assertEqual(response.status_code, 401)

    def test_chat_returns_structured_response(self) -> None:
        assistant_response = AsyncMock(return_value=("Hello!", []))
        with (
            patch.dict(os.environ, {"API_ACCESS_TOKEN": "test-token"}),
            patch(
                "webapp.api.get_assistant_response",
                new=assistant_response,
            ),
        ):
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
        with patch.dict(os.environ, {"API_ACCESS_TOKEN": "test-token"}):
            response = self.client.post(
                "/api/chat",
                headers={"Authorization": "Bearer test-token"},
                json={"message": "   "},
            )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
