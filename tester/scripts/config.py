import os

GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Groq models: try the high-quality one first, fall back to the fast one
# if the primary call fails (rate limit, transient error, etc.)
GROQ_MODEL_PRIMARY = "llama-3.3-70b-versatile"
GROQ_MODEL_FALLBACK = "llama-3.1-8b-instant"

# CAT-prep relevant categories. Each maps to a GNews query.
CATEGORIES = {
    "Geopolitics": "geopolitics OR international relations OR diplomacy OR war",
    "Economy": "India economy OR RBI OR inflation OR GDP OR fiscal policy",
    "Business": "India business OR corporate OR merger OR IPO OR startup funding",
    "National Affairs": "India government OR policy OR parliament OR supreme court",
}

ARTICLES_PER_CATEGORY = 6
GNEWS_LANG = "en"
GNEWS_COUNTRY = "in"

# How many past digests to keep visible in the history list
MAX_HISTORY = 28  # ~7 days at 4 runs/day

OUTPUT_DIR = "docs"
DATA_FILE = "docs/data/digests.json"
