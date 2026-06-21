# The Briefing — CAT Prep News Digest

An automated news digest covering **Geopolitics, Economy, Business, and National Affairs**,
refreshed every 6 hours. Built for CAT exam preparation (general awareness / GK).

- **Source**: [GNews API](https://gnews.io)
- **Summarization**: [Groq](https://groq.com) running Llama 3.3 70B (falls back to Llama 3.1 8B
  if the primary model call fails)
- **Hosting**: GitHub Pages, served from `/docs`
- **Scheduling**: GitHub Actions cron, every 6 hours

---

## How it works

1. `scripts/fetch_news.py` pulls recent articles from GNews for each category in
   `scripts/config.py`.
2. `scripts/summarize.py` sends each category's articles to Groq, which returns clean
   2-3 sentence summaries as structured JSON. If Groq fails or returns bad data for a
   category, that category is skipped rather than crashing the whole run.
3. `scripts/brief.py` generates a short 3-4 sentence overview tying the run together.
4. `scripts/run_digest.py` orchestrates the above and prepends the result to
   `docs/data/digests.json` (keeping the most recent 28 runs — about a week of history).
5. `docs/index.html` is a static page that fetches `data/digests.json` client-side and
   renders the latest digest, with a dropdown to browse past runs.
6. `.github/workflows/update-digest.yml` runs the whole pipeline every 6 hours and commits
   the updated JSON back to the repo, which GitHub Pages then serves automatically.

No build step, no server to maintain — it's a static site updated by a scheduled bot.

---

## Setup

### 1. Get your API keys
- **GNews**: sign up at [gnews.io](https://gnews.io) (free tier: 100 requests/day, which
  is comfortably enough for 4 categories × 4 runs/day = 16 requests/day)
- **Groq**: get a key at [console.groq.com](https://console.groq.com/keys) (free tier is
  generous and Llama 3.3 70B is very fast on Groq's hardware)

### 2. Push this repo to GitHub
```bash
cd cat-news-bot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

### 3. Add your API keys as repository secrets
In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**
- Add `GNEWS_API_KEY`
- Add `GROQ_API_KEY`

### 4. Enable GitHub Pages
**Settings → Pages → Source**: Deploy from a branch → Branch: `main`, Folder: `/docs` → Save.

Your site will be live at `https://<your-username>.github.io/<repo-name>/`.

### 5. Trigger the first run manually
Don't wait 6 hours for the first digest. Go to **Actions → Update News Digest → Run workflow**
to trigger it immediately. After it finishes (~1-2 minutes), refresh your Pages URL.

---

## Customizing

- **Categories / search queries**: edit `CATEGORIES` in `scripts/config.py`
- **Articles per category**: edit `ARTICLES_PER_CATEGORY` in `scripts/config.py`
- **Schedule**: edit the `cron` line in `.github/workflows/update-digest.yml`
  (current: `0 0,6,12,18 * * *` — every 6 hours, UTC)
- **History length**: edit `MAX_HISTORY` in `scripts/config.py`
- **Model**: edit `GROQ_MODEL_PRIMARY` / `GROQ_MODEL_FALLBACK` in `scripts/config.py`

## Running locally

```bash
pip install -r requirements.txt
export GNEWS_API_KEY=your_key
export GROQ_API_KEY=your_key
cd scripts
python run_digest.py
```

Then open `docs/index.html` in a browser (or run a local server, e.g.
`python -m http.server` from inside `docs/`, since `fetch()` can be blocked on `file://`
in some browsers).
