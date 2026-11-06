"""FastAPI routes and static frontend for BRUS-AI."""

import asyncio
import hashlib
import logging
import os
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from typing import Literal

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientConnectionError, PyJWTError
from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.staticfiles import StaticFiles

from webapp.assistant import (
    AssistantConfigurationError,
    AssistantServiceError,
    get_assistant_response,
)

load_dotenv()
logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return {count, redis.call('TTL', KEYS[1])}
"""


@asynccontextmanager
async def lifespan(application: FastAPI):
    redis_url = os.getenv("REDIS_URL")
    application.state.redis = (
        Redis.from_url(redis_url, decode_responses=True) if redis_url else None
    )
    try:
        yield
    finally:
        if application.state.redis is not None:
            await application.state.redis.aclose()

app = FastAPI(
    title="BRUS-AI API",
    description="A web API for the BRUS-AI conversational assistant.",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
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


def _auth0_configuration() -> tuple[str, str, str]:
    domain = os.getenv("AUTH0_DOMAIN", "").strip().removeprefix("https://").rstrip("/")
    client_id = os.getenv("AUTH0_CLIENT_ID", "").strip()
    audience = os.getenv("AUTH0_AUDIENCE", "").strip()
    if not domain or "/" in domain or not client_id or not audience:
        raise HTTPException(
            status_code=503,
            detail="Auth0 is not configured. Set AUTH0_DOMAIN, AUTH0_CLIENT_ID, and AUTH0_AUDIENCE.",
        )
    return domain, client_id, audience


@lru_cache(maxsize=8)
def _jwks_client(domain: str) -> PyJWKClient:
    return PyJWKClient(f"https://{domain}/.well-known/jwks.json")


def _decode_auth0_token(token: str, domain: str, audience: str) -> dict:
    issuer = f"https://{domain}/"
    signing_key = _jwks_client(domain).get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=audience,
        issuer=issuer,
    )


@app.get("/api/config")
async def frontend_config() -> dict[str, str]:
    domain, client_id, audience = _auth0_configuration()
    return {
        "auth0_domain": domain,
        "auth0_client_id": client_id,
        "auth0_audience": audience,
        "assistant_name": os.getenv("ASSISTANT_NAME", "BRUS-AI"),
    }


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"service": "BRUS-AI API", "status": "ok"}


async def require_auth0_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="A valid Auth0 bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        domain, _, audience = _auth0_configuration()
    except HTTPException:
        logger.error("Auth0 API authentication is not configured.")
        raise
    try:
        claims = await asyncio.to_thread(
            _decode_auth0_token,
            credentials.credentials,
            domain,
            audience,
        )
    except PyJWKClientConnectionError as exc:
        logger.error("Auth0 signing keys could not be retrieved.")
        raise HTTPException(
            status_code=503,
            detail="Authentication service is temporarily unavailable.",
        ) from exc
    except PyJWTError as exc:
        raise HTTPException(
            status_code=401,
            detail="The Auth0 bearer token is invalid or expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    subject = claims.get("sub")
    if not isinstance(subject, str) or not subject:
        raise HTTPException(status_code=401, detail="The bearer token has no user identity.")
    return subject


async def enforce_chat_rate_limit(
    request: Request,
    subject: str = Depends(require_auth0_user),
) -> str:
    redis_client: Redis | None = getattr(request.app.state, "redis", None)
    if redis_client is None:
        logger.error("Redis is not configured for chat rate limiting.")
        raise HTTPException(
            status_code=503,
            detail="Chat is unavailable because rate limiting is not configured.",
        )
    try:
        limit = int(os.getenv("CHAT_RATE_LIMIT_PER_MINUTE", "60"))
        if limit < 1:
            raise ValueError
    except ValueError as exc:
        logger.error("CHAT_RATE_LIMIT_PER_MINUTE must be a positive integer.")
        raise HTTPException(
            status_code=503,
            detail="Chat rate limiting is misconfigured.",
        ) from exc
    key = f"chat-rate:{hashlib.sha256(subject.encode()).hexdigest()}"
    try:
        count, ttl = await redis_client.eval(
            RATE_LIMIT_SCRIPT,
            1,
            key,
            RATE_LIMIT_WINDOW_SECONDS,
        )
    except RedisError as exc:
        logger.error("Redis rate limiting failed (%s).", type(exc).__name__)
        raise HTTPException(
            status_code=503,
            detail="Chat is temporarily unavailable because rate limiting failed.",
        ) from exc
    if int(count) > limit:
        raise HTTPException(
            status_code=429,
            detail="Chat request limit reached. Try again shortly.",
            headers={"Retry-After": str(max(1, int(ttl)))},
        )
    return subject


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    _: str = Depends(enforce_chat_rate_limit),
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


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
