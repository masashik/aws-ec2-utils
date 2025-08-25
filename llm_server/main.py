from pydantic import BaseModel
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)
import time
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
import os
import signal
import threading
from typing import Optional
import logging
import httpx

# -----------------------------
# Config
# -----------------------------
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OLLAMA_API_URL = "http://host.docker.internal:11434/api/generate"
# OLLAMA_API_URL = "http://localhost:11434/api/generate"

logger = logging.getLogger("uvicorn")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_API_URL = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
logger.info(f"OLLAMA_HOST={OLLAMA_HOST} OLLAMA_API_URL={OLLAMA_API_URL}")
GRACEFUL_TIMEOUT = float(os.environ.get("GRACEFUL_TIMEOUT", "25"))

# -----------------------------
# App & Metrics
# -----------------------------
app = FastAPI()

_SHUTTING_DOWN = threading.Event()

REQUEST_COUNT = Counter(
    "llm_requests_total",
    "Total number of LLM requests",
    ["route", "backend"],
)

REQUEST_LATENCY = Histogram(
    "llm_request_latency_seconds",
    "LLM request latency (seconds)",
    buckets=(0.05, 0.1, 0.2, 0.4, 0.8, 1.5, 3, 6, 12),
)


# -----------------------------
# Models
# -----------------------------
class Query(BaseModel):
    prompt: str
    backend: str = "ollama"
    model: Optional[str] = None  # e.g., "llama3.1" or "gpt-4o-mini"


# -----------------------------
# Middleware for metrics
# -----------------------------
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
        return response
    finally:
        elapsed = time.perf_counter() - start
        route = request.url.path
        backend = request.headers.get("x-backend", "unknown")
        REQUEST_COUNT.labels(route=route, backend=backend).inc()
        REQUEST_LATENCY.observe(elapsed)


# -----------------------------
# Health & Metrics
# -----------------------------
@app.get("/healthz")
async def healthz():
    if _SHUTTING_DOWN.is_set():
        return Response(content="shutting_down", status_code=503)
    return JSONResponse({"status": "ok"})


@app.get("/ready")
async def ready():
    # Replace with dependency checks (DB, upstreams) if needed
    if _SHUTTING_DOWN.is_set():
        return Response(content="shutting_down", status_code=503)
    return JSONResponse({"ready": True})


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/infer")
async def generate_text(q: Query):
    backend = getattr(q, "backend", "ollama")  # default if not present
    instruction = "The output answer should be limited to 500 characters."
    if q.backend == "ollama":
        REQUEST_COUNT.labels(backend=backend).inc()
        start_time = time.time()

        OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": f"{q.prompt.strip()}\n\n{instruction}",
            "stream": False
        }

        try:

            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                res = await client.post(OLLAMA_API_URL, json=payload)
                res.raise_for_status()
                response = res.json()
                duration = time.time() - start_time
                REQUEST_LATENCY.labels(backend=backend).observe(duration)
                return {"output": response.get("response", "No response")}

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Upstream timeout")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

    elif q.backend == "openai":
        REQUEST_COUNT.labels(backend=backend).inc()
        start_time = time.time()

        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        payload = {
          "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
          "messages": [
              {"role": "user", "content": f"{q.prompt.strip()}\n\n{instruction}"},
          ]
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            res = await client.post(OPENAI_API_URL, headers=headers, json=payload)

        if res.status_code >= 400:
            raise HTTPException(status_code=res.status_code, detail=res.text[:500])

        data = res.json()
        if "error" in data:
            raise HTTPException(status_code=502, detail=str(data["error"]))

        choices = data.get("choices") or []
        if not choices or "message" not in choices[0]:
            raise HTTPException(status_code=502,
                                detail=f"Unexpected response: keys={list(data.keys())}")

        text = choices[0]["message"]["content"]

        return {"output": text}

    else:
        return {"error": "Unsupported backend"}


# -----------------------------
# Graceful shutdown (SIGTERM)
# -----------------------------
def _handle_sigterm(signum, frame):
    _SHUTTING_DOWN.set()
    # Allow in-flight requests to drain
    time.sleep(GRACEFUL_TIMEOUT)
    # Exit process to let systemd/docker handle restart/stop
    os._exit(0)


signal.signal(signal.SIGTERM, _handle_sigterm)
