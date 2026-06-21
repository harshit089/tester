"""Summarize and lightly rewrite news articles using Groq's chat completion API."""
import json
import logging

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL_FALLBACK, GROQ_MODEL_PRIMARY

logger = logging.getLogger(__name__)

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SYSTEM_PROMPT = """You are a news editor preparing a digest for MBA entrance exam (CAT) \
aspirants in India. You will be given a list of raw news articles (title + short \
description) for one category. For EACH article, write a crisp 2-3 sentence summary \
in plain English that captures why it matters -- suitable for someone building \
general awareness for exams and interviews. Do not editorialize or add opinions.

Respond with ONLY a JSON array, no markdown fences, no preamble. Each element:
{"title": "<original or lightly cleaned title>", "summary": "<your 2-3 sentence summary>", \
"source": "<source name as given>", "url": "<original url, unchanged>"}

If an article is too thin, promotional, or duplicate to be useful, omit it from the array \
entirely rather than including a low-quality entry."""


def _build_user_prompt(category: str, articles: list[dict]) -> str:
    lines = [f"Category: {category}", "Articles:"]
    for i, a in enumerate(articles, 1):
        title = a.get("title", "")
        desc = a.get("description", "") or ""
        source = (a.get("source") or {}).get("name", "Unknown")
        url = a.get("url", "")
        lines.append(f"\n{i}. Title: {title}\n   Description: {desc}\n   Source: {source}\n   URL: {url}")
    return "\n".join(lines)


def _call_groq(model: str, system: str, user: str) -> str:
    completion = _client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=2000,
    )
    return completion.choices[0].message.content


def _parse_json_array(raw: str) -> list[dict]:
    cleaned = raw.strip()
    # Strip accidental markdown fences if the model adds them anyway
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    return json.loads(cleaned)


def summarize_category(category: str, articles: list[dict]) -> list[dict]:
    """Summarize one category's articles. Returns list of {title, summary, source, url}.

    Tries the primary model first, falls back to the secondary model on any failure.
    Returns an empty list (never raises) if both attempts fail, so one bad category
    doesn't take down the whole digest.
    """
    if not articles:
        return []
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set")

    user_prompt = _build_user_prompt(category, articles)

    for model in (GROQ_MODEL_PRIMARY, GROQ_MODEL_FALLBACK):
        try:
            raw = _call_groq(model, SYSTEM_PROMPT, user_prompt)
            parsed = _parse_json_array(raw)
            if not isinstance(parsed, list):
                raise ValueError("Model did not return a JSON array")
            logger.info(
                "Summarized %d/%d articles for '%s' using %s",
                len(parsed), len(articles), category, model,
            )
            return parsed
        except Exception as e:
            logger.warning("Groq summarization failed with model %s for '%s': %s", model, category, e)
            continue

    logger.error("Both Groq models failed for category '%s'; skipping", category)
    return []


def summarize_all(articles_by_category: dict[str, list[dict]]) -> dict[str, list[dict]]:
    return {
        category: summarize_category(category, articles)
        for category, articles in articles_by_category.items()
    }
