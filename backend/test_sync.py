import sys
import os
sys.path.append(os.getcwd())
from phase3.rag_pipeline import run_query
from loguru import logger

def test_recs():
    query = "low risk stocks"
    logger.info(f"Testing run_query with: {query}")
    res = run_query(query)
    logger.info("Recommendations returned:")
    for r in res["recommendations"]:
        logger.info(r)
    
    if len(res["recommendations"]) > 0 and isinstance(res["recommendations"][0], dict):
        logger.success("SUCCESS: Recommendations are objects!")
    else:
        logger.error("FAILURE: Recommendations are still strings!")

if __name__ == "__main__":
    test_recs()
