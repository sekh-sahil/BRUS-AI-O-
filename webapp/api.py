"""FastAPI routes for BRUS-AI."""

import logging
import os
import secrets
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from webapp.assistant import (
    AssistantConfigurationError,
    AssistantServiceError,
    get_assistant_response,
)

load_dotenv()
logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)

app = FastAPI(
    title="BRUS-AI API",
    description="A web API for the BRUS-AI conversational assistant.",
    version="1.0.0",
)


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message content cannot be blank.")
        return value


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=4000)
    provider: Literal["groq", "cohere"] = "groq"
    web_search: bool = False
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be blank.")
        return value


class ChatResponse(BaseModel):
    response: str
    provider: Literal["groq", "cohere"]
    sources: list[dict[str, str]]


@app.get("/")
async def health_check() -> dict[str, str]:
    return {"service": "BRUS-AI API", "status": "ok"}


async def require_api_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> None:
    expected_token = os.getenv("API_ACCESS_TOKEN")
    if not expected_token:
        logger.error("API access token is not configured.")
        raise HTTPException(
            status_code=503,
            detail="API access is not configured.",
        )
    if credentials is None or not secrets.compare_digest(
        credentials.credentials,
        expected_token,
    ):
        raise HTTPException(
            status_code=401,
            detail="A valid bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    _: None = Depends(require_api_token),
) -> ChatResponse:
    try:
        answer, sources = await get_assistant_response(
            message=request.message,
            history=[message.model_dump() for message in request.history],
            provider=request.provider,
            web_search=request.web_search,
        )
    except AssistantConfigurationError as exc:
        logger.warning("Assistant provider configuration is incomplete.")
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AssistantServiceError as exc:
        logger.warning("Assistant request could not be completed.")
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(
        response=answer,
        provider=request.provider,
        sources=sources,
    )
