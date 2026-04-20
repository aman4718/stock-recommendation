"""
main.py — Groww MF/ETF/Stock FAQ Assistant (RAG + Groq)
Facts-only. Refuses investment advice. Cites source on every answer.
"""

import os
import re
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from groq import AuthenticationError, Groq, RateLimitError
from loguru import logger
from pydantic import BaseModel

load_dotenv()

import rag

# ── Prompts ───────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are a facts-only mutual fund and investment FAQ assistant for Groww users.

Rules (follow strictly):
1. Answer ONLY using the provided Context below — do not use outside knowledge.
2. Keep answers concise (3–6 sentences max).
3. Always end your answer with: Source: <URL from context>
4. If the answer is NOT in the context, reply exactly:
   "I don't have verified information on this. Please check groww.in for accurate details."
5. NEVER give investment advice, recommendations, or opinions on whether to buy/sell any fund/stock.
6. If the user asks for recommendations, portfolio advice, or "best fund", reply exactly:
   "I only provide factual information, not investment advice. For personalised guidance, consult a SEBI-registered advisor. Learn more: https://groww.in/blog/how-to-choose-mutual-fund"
"""

_GROQ_MODEL = "llama-3.1-8b-instant"

# ── Opinion/advice query detection ───────────────────────────────
_ADVICE_PATTERNS = re.compile(
    r"\b(should i|shall i|can i invest|best fund|top fund|recommend|which fund|"
    r"buy|sell|portfolio|where to invest|good fund|safe fund|suggest|better fund|"
    r"worth investing|worth buying)\b",
    re.IGNORECASE,
)

_REFUSAL = (
    "I only provide factual information, not investment advice. "
    "For personalised guidance, please consult a SEBI-registered investment advisor. "
    "Learn more: https://groww.in/blog/how-to-choose-mutual-fund"
)

# ── Groq client ───────────────────────────────────────────────────
_groq_client: Groq | None = None


def get_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        key = os.getenv("GROQ_API_KEY", "")
        if not key:
            raise RuntimeError("GROQ_API_KEY not set.")
        _groq_client = Groq(api_key=key)
    return _groq_client


# ── Lifespan ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — loading RAG engine ...")
    rag.load()
    logger.success("RAG engine ready.")
    yield
    logger.info("Shutting down.")


# ── App ───────────────────────────────────────────────────────────
app = FastAPI(
    title="Groww FAQ Assistant",
    description="Facts-only MF/ETF/Stock FAQ chatbot. No investment advice.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer:   str
    sources:  list[str]
    refused:  bool = False


# ── Routes ────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def serve_ui():
    html_path = Path(__file__).parent / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found.")
    return FileResponse(str(html_path), media_type="text/html")


@app.get("/health")
def health():
    return {"status": "healthy", "service": "groww-faq-assistant"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    query = req.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"Query: '{query}'")

    # Refuse opinion / advice queries immediately
    if _ADVICE_PATTERNS.search(query):
        logger.info("Refused opinion query.")
        return ChatResponse(
            answer=_REFUSAL,
            sources=["https://groww.in/blog/how-to-choose-mutual-fund"],
            refused=True,
        )

    # Retrieve top-3 relevant chunks
    hits = rag.retrieve(query, top_k=3)

    # Build context for LLM
    context_parts = []
    for i, h in enumerate(hits, 1):
        context_parts.append(
            f"[Source {i}]\nTitle: {h['title']}\nURL: {h['url']}\n{h['text']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # Call Groq
    try:
        resp = get_client().chat.completions.create(
            model=_GROQ_MODEL,
            max_tokens=512,
            temperature=0.1,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": f"Context:\n{context}\n\nQuestion: {query}"},
            ],
        )
        answer = resp.choices[0].message.content or "I don't have verified information on this."
    except AuthenticationError:
        logger.error("Invalid GROQ_API_KEY.")
        raise HTTPException(status_code=500, detail="LLM authentication failed.")
    except RateLimitError:
        logger.warning("Groq rate limit hit.")
        raise HTTPException(status_code=429, detail="Rate limit reached. Please retry shortly.")
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    sources = list(dict.fromkeys(h["url"] for h in hits))
    logger.success(f"Answered | sources={sources}")
    return ChatResponse(answer=answer, sources=sources)
