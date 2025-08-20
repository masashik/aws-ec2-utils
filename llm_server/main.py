from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
import os
from fastapi import HTTPException

OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

#OLLAMA_API_URL = "http://host.docker.internal:11434/api/generate"
#OLLAMA_API_URL = "http://localhost:11434/api/generate"

import os, logging, httpx
logger = logging.getLogger("uvicorn")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_API_URL = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
logger.info(f"OLLAMA_HOST={OLLAMA_HOST} OLLAMA_API_URL={OLLAMA_API_URL}")


app = FastAPI()

REQUEST_COUNT = Counter(
    "llm_requests_total", "Total number of LLM requests", ["backend"]
)

REQUEST_LATENCY = Histogram(
    "llm_request_latency_seconds", "Latency of LLM requests in seconds", ["backend"]
)


class Query(BaseModel):
    prompt: str
    backend: str = "ollama"


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
          "model": os.getenv("OPENAI_MODEL","gpt-4o-mini"),
          "messages": [
              {"role": "user", "content": f"{q.prompt.strip()}\n\n{instruction}"}
          ]
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            res = await client.post(OPENAI_API_URL, headers=headers, json=payload)

        if res.status_code >= 400:
            status = "error"
            raise HTTPException(status_code=res.status_code, detail=res.text[:500])

        data = res.json()
        if "error" in data:
            status = "error"
            raise HTTPException(status_code=502, detail=str(data["error"]))

        choices = data.get("choices") or []
        if not choices or "message" not in choices[0]:
            status = "error"
            raise HTTPException(status_code=502, detail=f"Unexpected response: keys={list(data.keys())}")

        text = choices[0]["message"]["content"]

        #usage = data.get("usage", {})
        #TOKENS.labels(backend).inc(int(usage.get("completion_tokens", 0)))

        return {"output": text}
            #res.raise_for_status()
            #response = res.json()

            #duration = time.time() - start_time
            #REQUEST_LATENCY.labels(backend=backend).observe(duration)
            #return {"output": response["choices"][0]["message"]["content"]}

    else:
        return {"error": "Unsupported backend"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health(): return {"ok": True}

@app.get("/ready")
async def ready():  return {"ready": True}
