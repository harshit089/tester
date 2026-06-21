"""Fetch recent news articles from GNews for each configured category."""
import logging
import time

import requests

from config import ARTICLES_PER_CATEGORY, CATEGORIES, GNEWS_API_KEY, GNEWS_COUNTRY, GNEWS_LANG

logger = logging.getLogger(__name__)

GNEWS_URL = "https://gnews.io/api/v4/search"


def fetch_category(category: str, query: str) -> list[dict]:
    """Fetch articles for a single category. Returns a list of raw GNews article dicts."""
    params = {
        "q": query,
        "lang": GNEWS_LANG,
        "country": GNEWS_COUNTRY,
        "max": ARTICLES_PER_CATEGORY,
        "sortby": "publishedAt",
        "apikey": GNEWS_API_KEY,
    }
    try:
        resp = requests.get(GNEWS_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])
        logger.info("Fetched %d articles for category '%s'", len(articles), category)
        return articles
    except requests.exceptions.RequestException as e:
        logger.error("GNews fetch failed for category '%s': %s", category, e)
        return []


def fetch_all() -> dict[str, list[dict]]:
    """Fetch articles for every configured category.

    Returns: {category_name: [raw_article, ...]}
    """
    if not GNEWS_API_KEY:
        raise RuntimeError("GNEWS_API_KEY is not set")

    results = {}
    for category, query in CATEGORIES.items():
        results[category] = fetch_category(category, query)
        time.sleep(1)  # be polite to the free-tier rate limit
    return results
