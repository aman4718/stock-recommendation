"""
main.py — Phase 4: Root FastAPI Interface for the RAG Chatbot
"""

from typing import List, Optional, Dict, Any
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

# ── App Setup ────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Stock RAG Chatbot API",
    description="REST API for querying stock recommendations using ChromaDB and Groq.",
    version="1.0.0"
)

# ── Env Validation ──────────────────────────────────────────────────
import os
from phase3.settings import GROQ_API_KEY, CHROMA_API_KEY
logger.info("Checking Environment Variables...")
logger.info(f"GROQ_API_KEY exists: {bool(GROQ_API_KEY)}")
logger.info(f"CHROMA_API_KEY exists: {bool(CHROMA_API_KEY)}")
logger.info(f"APP_ENV: {os.getenv('APP_ENV', 'not set')}")

# ── Import RAG Pipeline ──────────────────────────────────────────────
run_query = None
try:
    from phase3.rag_pipeline import run_query as rag_run_query
    run_query = rag_run_query
    logger.success("Successfully imported RAG pipeline from phase3.")
except Exception as e:
    logger.error(f"CRITICAL: Failed to import run_query from phase3: {e}")
    # We define a fallback or just let the endpoints check for None

# Allow CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Models ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str

class StockRecommendation(BaseModel):
    ticker: str
    name: str
    sector: str
    industry: str
    price: float
    pe_ratio: Optional[float] = None
    market_cap: str
    one_month_change: str
    risk_level: str
    valuation_category: str
    description: str
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    eps: Optional[float] = None
    revenue_growth: str
    profit_margin: str
    yahoo_finance_url: str

class ChatResponse(BaseModel):
    answer: str
    recommendations: List[StockRecommendation]

# ── Endpoints ────────────────────────────────────────────────────────

@app.get("/", tags=["System"])
def root():
    """Root endpoint to verify the API is live."""
    return {
        "status": "online",
        "message": "AI Stock RAG Chatbot API is running.",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["System"])
def health_check():
    """Verify that the API is up and running."""
    return {"status": "healthy", "service": "stock_rag_chatbot"}

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
def chat_endpoint(request: ChatRequest):
    """
    RAG Chat Endpoint.
    Accepts a user query, triggers retrieval from Chroma, and generates an LLM response.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    logger.info(f"API received query: '{request.query}'")
    
    try:
        # Check if run_query is available
        if run_query is None:
            raise RuntimeError("RAG Pipeline (run_query) was not loaded correctly during startup.")

        # Run pipeline
        res = run_query(request.query)
        
        return ChatResponse(
            answer=res["answer"],
            recommendations=res["recommendations"]
        )
    except Exception as e:
        error_msg = traceback.format_exc()
        logger.error(f"Error processing chat request:\n{error_msg}")
        # Return detailed error for debugging in production
        raise HTTPException(
            status_code=500, 
            detail=f"RAG Processing Error: {str(e)} | See logs for full traceback."
        )

# For local testing convenience
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
