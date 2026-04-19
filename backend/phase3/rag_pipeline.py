"""
rag_pipeline.py — Core orchestrator logic for RAG query processing.
"""

from typing import Dict, Any, List
from loguru import logger
from langchain_core.output_parsers import StrOutputParser
from phase3.retriever import retrieve_context, format_context_for_prompt
from phase3.llm import get_llm
from phase3.prompt import get_rag_prompt_template

def run_query(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Executes the full RAG pipeline for a given query.
    1. Embed & Retrieve
    2. Format Prompt
    3. LLM Generation
    4. Compile Result
    """
    logger.info(f"Processing query: '{query}'")
    
    # 1. Retrieval
    results = retrieve_context(query, top_k=top_k)
    
    # Extract unique recommendations logic (return metadata objects)
    recommendations = []
    seen_tickers = set()
    for res in results:
        meta = res.get("metadata", {})
        ticker = meta.get("ticker") or res.get("id") or "UNKNOWN"
        
        if ticker not in seen_tickers:
            # Safely handle numeric fields that might be strings or None
            try:
                price = float(meta.get("price") or 0.0)
            except (ValueError, TypeError):
                price = 0.0
                
            try:
                pe = meta.get("pe_ratio")
                pe_ratio = float(pe) if pe and str(pe).strip() else None
            except (ValueError, TypeError):
                pe_ratio = None

            def safe_float(v):
                if v == "" or v is None: return None
                try: return float(v)
                except: return None

            # Map metadata to consistent fields for frontend
            stock_data = {
                "ticker":           ticker,
                "name":             meta.get("name") or ticker,
                "sector":           meta.get("sector") or "N/A",
                "industry":         meta.get("industry") or "N/A",
                "price":            price,
                "pe_ratio":         pe_ratio,
                "market_cap":       str(meta.get("market_cap") or "N/A"),
                "one_month_change": str(meta.get("price_change_fmt") or meta.get("price_change_1mo") or "N/A"),
                "risk_level":       str(meta.get("risk_level") or "Unknown"),
                "valuation_category": str(meta.get("valuation") or "Unknown"),
                "description":      str(meta.get("description") or ""),
                "fifty_two_week_high": safe_float(meta.get("fifty_two_week_high")),
                "fifty_two_week_low":  safe_float(meta.get("fifty_two_week_low")),
                "eps":                 safe_float(meta.get("eps")),
                "revenue_growth":      str(meta.get("revenue_growth") or "N/A"),
                "profit_margin":       str(meta.get("profit_margin") or "N/A"),
                "yahoo_finance_url":   f"https://finance.yahoo.com/quote/{ticker}"
            }
            recommendations.append(stock_data)
            seen_tickers.add(ticker)
            logger.debug(f"Mapped recommendation: {ticker} -> {stock_data['name']} (${price})")
    
    # 2. Context Formatting
    context_str = format_context_for_prompt(results)
    
    # 3. Prompt Construction & 4. LLM Generation
    llm = get_llm()
    prompt_template = get_rag_prompt_template()
    output_parser = StrOutputParser()
    
    chain = prompt_template | llm | output_parser
    
    logger.info("Generating response from Groq LLM...")
    answer = chain.invoke({"context": context_str, "query": query})
    logger.success(f"Response generated with {len(recommendations)} recommendations.")
    
    # 5. Compile Result
    return {
        "answer": answer,
        "recommendations": recommendations,
        "context_used": len(results)
    }
