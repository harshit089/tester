"""Generate a short overview brief summarizing the whole digest run."""
import logging

from summarize import _call_groq, _client
from config import GROQ_MODEL_FALLBACK, GROQ_MODEL_PRIMARY

logger = logging.getLogger(__name__)

BRIEF_SYSTEM_PROMPT = """You are writing a short "today's brief" intro paragraph for a \
CAT exam prep news digest. You will be given category summaries. Write a tight 3-4 \
sentence overview connecting the most important 2-3 developments across categories. \
Plain English, no bullet points, no headers, no markdown -- just flowing prose. \
Do not editorialize."""


def _build_brief_input(summaries_by_category: dict[str, list[dict]]) -> str:
    parts = []
    for category, items in summaries_by_category.items():
        if not items:
            continue
        parts.append(f"\n{category}:")
        for item in items:
            parts.append(f"- {item.get('title', '')}: {item.get('summary', '')}")
    return "\n".join(parts)


def generate_brief(summaries_by_category: dict[str, list[dict]]) -> str:
    user_input = _build_brief_input(summaries_by_category)
    if not user_input.strip():
        return "No significant updates in this cycle."
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set")

    for model in (GROQ_MODEL_PRIMARY, GROQ_MODEL_FALLBACK):
        try:
            text = _call_groq(model, BRIEF_SYSTEM_PROMPT, user_input)
            return text.strip()
        except Exception as e:
            logger.warning("Brief generation failed with model %s: %s", model, e)
            continue

    logger.error("Both Groq models failed for brief generation")
    return "Brief unavailable this cycle due to a temporary error."
