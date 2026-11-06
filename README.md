# BRUS-AI

BRUS-AI includes a FastAPI service for browser and cloud use, alongside the
original desktop assistant.

## Web app

The browser UI is served at `/`. The API health check is `/api/health`, the
interactive API documentation is `/api/docs`, and `POST /api/chat` accepts JSON
such as:

```json
{
  "message": "What is new in Python?",
  "provider": "groq",
  "web_search": true,
  "history": []
}
```

The response contains `response`, `provider`, and `sources`. Set `web_search`
to `true` to add Google search result snippets as model context. Conversation
history is supplied by the browser per request and stays in the current page
session. The API validates Auth0 access tokens; the browser obtains them through
Auth0's SPA SDK and keeps them in memory.

## Deploy to Render

The included `render.yaml` configures Gunicorn with Uvicorn's worker and
`/api/health` as the health check. Set `GROQ_API_KEY` in Render to enable the
default provider; `COHERE_API_KEY` is optional.

### Auth0 and rate limiting

1. In Auth0, create a single-page application and an API. Set the API identifier
   to the value used for `AUTH0_AUDIENCE`.
2. Add your Render service URL (for example,
   `https://your-service.onrender.com`) to the Auth0 application's **Allowed
   Callback URLs**, **Allowed Logout URLs**, and **Allowed Web Origins**.
3. Set `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, and `AUTH0_AUDIENCE` in Render. These
   are public identifiers, not credentials.
4. Provision a Redis instance reachable by the web service and set `REDIS_URL`
   in Render. Chat is limited to 60 requests per authenticated user per minute
   by default. The API fails closed with `503` if Redis is unavailable, rather
   than bypassing the shared limit.
5. Keep provider API keys as Render secrets. Never commit `.env` or put
   provider keys or a server-side API token in frontend code.

Any user who can authenticate with the configured Auth0 application can use the
chat API. Configure signup and connections in Auth0 according to your access
policy.

## Run locally

Use Python 3.11 or newer. Install web dependencies and prepare local settings:

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn web_main:app --reload
```

For chat locally, configure Auth0 and Redis as above, or supply those settings
through environment variables. `/api/docs` contains the interactive API docs.

## Legacy desktop assistant

The Windows desktop interface and OS automation are not loaded by the web
service. To install its dependencies separately, use
`python -m pip install -r requirements-desktop.txt`; run it with
`python main.py` on a supported desktop environment.
