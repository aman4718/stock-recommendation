"""
scraper.py — Scrapes Groww blog/FAQ pages for MF, ETF, and stock education content.
Uses requests + BeautifulSoup with __NEXT_DATA__ extraction for Next.js pages.
"""

from __future__ import annotations

import json
import re
import time

import requests
from bs4 import BeautifulSoup
from loguru import logger

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}

# Groww blog posts covering MF, ETF, stock FAQ topics
GROWW_URLS = [
    "https://groww.in/blog/what-is-expense-ratio-in-mutual-fund",
    "https://groww.in/blog/exit-load-in-mutual-fund",
    "https://groww.in/blog/what-is-elss",
    "https://groww.in/blog/how-does-sip-work",
    "https://groww.in/blog/nav-mutual-fund",
    "https://groww.in/blog/direct-vs-regular-mutual-fund",
    "https://groww.in/blog/riskometer-mutual-fund",
    "https://groww.in/blog/capital-gains-statement",
    "https://groww.in/blog/swp-systematic-withdrawal-plan",
    "https://groww.in/blog/stp-systematic-transfer-plan",
    "https://groww.in/blog/what-is-aum",
    "https://groww.in/blog/mutual-fund-taxation",
    "https://groww.in/blog/what-is-etf",
    "https://groww.in/blog/index-funds-india",
    "https://groww.in/blog/kyc-for-mutual-funds",
    "https://groww.in/blog/consolidated-account-statement",
    "https://groww.in/blog/sip-lumpsum",
    "https://groww.in/blog/large-cap-vs-mid-cap-vs-small-cap-funds",
    "https://groww.in/blog/debt-mutual-funds",
    "https://groww.in/blog/what-is-benchmark-in-mutual-fund",
    "https://groww.in/blog/what-is-xirr-in-mutual-fund",
    "https://groww.in/blog/what-is-cagr",
    "https://groww.in/blog/dividend-option-vs-growth-option-mutual-fund",
    "https://groww.in/blog/elss-lock-in-period",
    "https://groww.in/blog/minimum-sip-amount",
    "https://groww.in/blog/how-to-redeem-mutual-funds-on-groww",
    "https://groww.in/blog/folio-number-in-mutual-fund",
    "https://groww.in/blog/what-is-alpha-in-mutual-fund",
    "https://groww.in/blog/sharpe-ratio-mutual-fund",
    "https://groww.in/blog/what-is-an-etf-exchange-traded-fund",
]

# AMFI / SEBI static pages (reliable fallback content)
AMFI_URLS = [
    "https://www.amfiindia.com/investor-corner/knowledge-center/expense-ratio.html",
    "https://www.amfiindia.com/investor-corner/knowledge-center/exit-load.html",
    "https://www.amfiindia.com/investor-corner/knowledge-center/nav.html",
    "https://www.amfiindia.com/investor-corner/knowledge-center/kyc.html",
]


def _extract_next_data(html: str) -> dict | None:
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except Exception:
        return None


def _text_from_next_data(data: dict) -> tuple[str, str]:
    """Return (title, content) extracted from Next.js page data."""
    try:
        pp = data.get("props", {}).get("pageProps", {})

        # Groww blog stores content under various keys
        for key in ["blogPostData", "post", "blog", "article", "data", "blogData"]:
            obj = pp.get(key)
            if not obj or not isinstance(obj, dict):
                continue

            title = (
                obj.get("title") or obj.get("heading") or obj.get("name") or ""
            )

            # Try HTML content fields
            for ckey in ["content", "body", "description", "article", "blogContent", "postContent"]:
                raw = obj.get(ckey, "")
                if raw and len(raw) > 200:
                    soup = BeautifulSoup(raw, "html.parser")
                    return title, soup.get_text(separator="\n", strip=True)

        return "", ""
    except Exception:
        return "", ""


def _text_from_html(html: str) -> tuple[str, str]:
    """BeautifulSoup fallback — extract title + main content."""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
        tag.decompose()

    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True).split("|")[0].strip()

    # Try to find main content area
    main = (
        soup.find("article")
        or soup.find(attrs={"class": re.compile(r"blog|post|content|article|body", re.I)})
        or soup.find("main")
        or soup.find("body")
    )

    if main:
        paras = main.find_all(["p", "h1", "h2", "h3", "h4", "h5", "li"])
        lines = [p.get_text(strip=True) for p in paras if p.get_text(strip=True)]
        return title, "\n".join(lines)

    return title, ""


def scrape_page(url: str) -> dict | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            logger.warning(f"HTTP {resp.status_code} — {url}")
            return None

        html = resp.text
        title, content = "", ""

        next_data = _extract_next_data(html)
        if next_data:
            title, content = _text_from_next_data(next_data)

        if not content or len(content) < 200:
            title_fb, content_fb = _text_from_html(html)
            if not title:
                title = title_fb
            if len(content_fb) > len(content):
                content = content_fb

        if not content or len(content) < 150:
            logger.warning(f"Skipping {url} — only {len(content)} chars")
            return None

        if not title:
            title = url.split("/")[-1].replace("-", " ").title()

        content = re.sub(r"\n{3,}", "\n\n", content).strip()
        logger.success(f"Scraped '{title[:50]}' — {len(content)} chars  [{url}]")
        return {"url": url, "title": title, "content": content}

    except Exception as exc:
        logger.error(f"Failed {url}: {exc}")
        return None


def scrape_all(urls: list[str] | None = None, delay: float = 1.5) -> list[dict]:
    all_urls = (urls or GROWW_URLS) + AMFI_URLS
    docs: list[dict] = []
    for url in all_urls:
        doc = scrape_page(url)
        if doc:
            docs.append(doc)
        time.sleep(delay)
    logger.info(f"Scraped {len(docs)}/{len(all_urls)} pages")
    return docs
