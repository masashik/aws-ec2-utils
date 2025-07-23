from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
import os

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

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


@app.post("/generate")
async def generate_text(q: Query):
    backend = getattr(q, "backend", "ollama")  # default if not present
    instruction = "The output answer should be limited to 500 characters."
    if q.backend == "ollama":
        REQUEST_COUNT.labels(backend=backend).inc()
        start_time = time.time()

        payload = {
            "model": "llama3.1",
            "prompt": f"{q.prompt.strip()}\n\n{instruction}",
            "stream": False
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            res = await client.post(OLLAMA_API_URL, json=payload)
            res.raise_for_status()
            response = res.json()
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(backend=backend).observe(duration)
            return {"output": response.get("response", "No response")}

    elif q.backend == "openai":
        REQUEST_COUNT.labels(backend=backend).inc()
        start_time = time.time()

        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        payload = {
          "model": "gpt-3.5-turbo",
          "messages": [
              {"role": "user", "content": f"{q.prompt.strip()}\n\n{instruction}"}
          ]
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            res = await client.post(OPENAI_API_URL, headers=headers, json=payload)
            res.raise_for_status()
            response = res.json()
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(backend=backend).observe(duration)
            return {"output": response["choices"][0]["message"]["content"]}

    else:
        return {"error": "Unsupported backend"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
