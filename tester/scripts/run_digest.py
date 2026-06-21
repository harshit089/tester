"""Main entry point: runs the full digest pipeline and updates docs/data/digests.json.

Run every 6 hours via GitHub Actions. Designed to fail loudly on setup problems
(missing API keys) but degrade gracefully on per-category fetch/summarize issues
so a single flaky category never blocks the whole digest from publishing.
"""
import json
import logging
import os
from datetime import datetime, timezone

from brief import generate_brief
from config import DATA_FILE, MAX_HISTORY
from fetch_news import fetch_all
from summarize import summarize_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_history() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Could not load existing history (%s); starting fresh", e)
        return []


def save_history(history: list[dict]) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def run() -> dict:
    logger.info("Starting digest run")

    raw_articles = fetch_all()
    total_raw = sum(len(v) for v in raw_articles.values())
    if total_raw == 0:
        raise RuntimeError("GNews returned zero articles across all categories; aborting run")

    summaries = summarize_all(raw_articles)
    total_summarized = sum(len(v) for v in summaries.values())
    if total_summarized == 0:
        raise RuntimeError("Groq summarization produced zero usable articles; aborting run")

    brief_text = generate_brief(summaries)

    digest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "brief": brief_text,
        "categories": summaries,
    }

    history = load_history()
    history.insert(0, digest)
    history = history[:MAX_HISTORY]
    save_history(history)

    logger.info(
        "Digest run complete: %d articles summarized across %d categories",
        total_summarized, len(summaries),
    )
    return digest


if __name__ == "__main__":
    run()
