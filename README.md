# BRUS-AI

BRUS-AI includes a FastAPI service for browser and cloud use, alongside the
original desktop assistant.

## Web API

Use Python 3.11 or newer. Install the web-compatible dependencies and configure
credentials in the hosting platform's environment settings:

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `GROQ_API_KEY` to enable the default Groq provider. `COHERE_API_KEY` enables
the optional Cohere provider. `API_ACCESS_TOKEN` is required to protect the
chat endpoint; generate a strong random value and send it as a bearer token.
`ASSISTANT_NAME` and `BRUS_USERNAME` customize the assistant prompt. Never
commit `.env`, expose the access token in browser code, or put provider
credentials in frontend code.

Start the ASGI service locally:

```powershell
uvicorn web_main:app --reload
```

`GET /` is a health check. `POST /api/chat` accepts JSON such as:

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
history is supplied by the client per request and is not stored on the server.
Interactive API documentation is available at `/docs`.

Send `Authorization: Bearer <API_ACCESS_TOKEN>` with each `POST /api/chat`
request. Keep this token on a trusted client/server rather than embedding it in
a public web page.

### Deploy

- **Render:** use the included `render.yaml`; it runs the FastAPI app with
  Gunicorn and Uvicorn's worker. Add API keys as environment variables in the
  Render dashboard.
- **Railway:** deploy from the repository; the included `Procfile` starts
  Uvicorn using Railway's `PORT`.
- **Vercel:** this ASGI configuration targets persistent web services such as
  Render and Railway. Vercel requires a serverless function adapter/configuration
  and is not configured by these deployment files.

## Legacy desktop assistant

The existing Windows desktop interface and OS automation are intentionally not
loaded by the web service. To install its original dependencies separately,
use `python -m pip install -r requirements-desktop.txt`; run it with
`python main.py` on a supported desktop environment.
#
