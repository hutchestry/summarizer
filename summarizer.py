#!/usr/bin/env python3
"""
browser_history_to_markdown.py

Supports macOS Brave, Chrome, Safari, Firefox.
Creates:
  - Daily Markdown summary with topics and tags
  - Weekly merged summary
  - Optional Obsidian vault integration
"""

import os
import sqlite3
import datetime
import shutil
import re
from pathlib import Path
from collections import defaultdict, Counter
import urllib.parse
import glob

# -------------------------
# CONFIGURATION
# -------------------------
BASE_OUTPUT = Path.home() / "browser-summaries"
DAILY_DIR = BASE_OUTPUT / "daily"
WEEKLY_DIR = BASE_OUTPUT / "weekly"
DAILY_DIR.mkdir(parents=True, exist_ok=True)
WEEKLY_DIR.mkdir(parents=True, exist_ok=True)

OBSIDIAN_VAULT = None   # e.g. Path.home() / "Documents/Obsidian/MyVault"

DAYS_FOR_DAILY = 1
DAYS_FOR_WEEKLY = 7

EXTERNAL_TAGGER = None  # optional hook: EXTERNAL_TAGGER(text, url) -> [tags...]

# -------------------------
# TOPIC/TAG KEYWORDS
# -------------------------
TOPICS_KEYWORDS = {
    "AI": ["openai", "llama", "gpt", "huggingface", "langchain", "transformer"],
    "Coding": ["stackoverflow", "github", "python", "javascript", "rust", "golang"],
    "News": ["nytimes", "bbc", "cnn", "reuters", "bloomberg", "washingtonpost"],
    "Shopping": ["amazon.", "ebay", "bestbuy", "shopping", "checkout", "cart"],
    "Video": ["youtube", "vimeo", "watch", "video"],
    "Reference": ["wikipedia.org", "wikihow", "docs", "developer.mozilla", "mdn"],
    "Social": ["twitter.com", "x.com", "facebook.com", "instagram.com"],
    "Cloud/Infra": ["aws.amazon", "azure", "gcp", "docker", "kubernetes"],
}

TAGS_KEYWORDS = {
    "Troubleshooting": ["error", "fix", "issue", "exception", "stacktrace"],
    "Programming": ["tutorial", "example", "library", "programming"],
    "Research": ["paper", "arxiv", "study"],
    "Reference": ["docs", "documentation", "api"],
    "Shopping": ["price", "buy", "coupon"],
    "Video": ["youtube", "watch", "video"],
}

SEARCH_PATTERNS = {
    "google": re.compile(r"https?://.*google\..*/search\?.*[?&]q=(?P<q>[^&]+)"),
    "bing": re.compile(r"https?://.*bing\.com/search\?.*q=(?P<q>[^&]+)"),
    "duckduckgo": re.compile(r"https?://.*duckduckgo\.com/\?.*q=(?P<q>[^&]+)"),
    "youtube": re.compile(r"https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)(?P<q>[^&/]+)"),
}

# -------------------------
# UTILITIES
# -------------------------
def safari_history_path():
    return Path.home() / "Library/Safari/History.db"

def chrome_history_path():
    return Path.home() / "Library/Application Support/Google/Chrome/Default/History"

def brave_history_path():
    return Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser/Default/History"

def firefox_history_path():
    base = Path.home() / "Library/Application Support/Firefox/Profiles"
    profiles = list(base.glob("*.default*"))
    if profiles:
        return profiles[0] / "places.sqlite"
    return None

def safe_copy(src: Path, dst: Path):
    try:
        shutil.copy(src, dst)
        return True
    except Exception:
        return False


# Convert Chrome/Safari time to normal datetime
def chrome_time_to_dt(chrome_ts):
    if chrome_ts is None:
        return None
    epoch = datetime.datetime(1601, 1, 1)
    return epoch + datetime.timedelta(microseconds=chrome_ts)


def extract_search_query(url):
    for engine, pattern in SEARCH_PATTERNS.items():
        m = pattern.search(url)
        if m:
            q = m.group("q")
            return engine, urllib.parse.unquote_plus(q)
    return None, None


# -------------------------
# CLASSIFICATION
# -------------------------
def classify_topic(text, url):
    text_l = (text or "").lower()
    url_l = (url or "").lower()
    scores = Counter()

    for topic, keywords in TOPICS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_l or kw in url_l:
                scores[topic] += 1

    if not scores:
        return "Misc"

    top_score = scores.most_common(1)[0][1]
    return ", ".join([t for t, s in scores.items() if s == top_score])


def classify_tags(text, url):
    tags = set()
    text_l = (text or "").lower()
    url_l = (url or "").lower()

    if EXTERNAL_TAGGER:
        ext = EXTERNAL_TAGGER(text, url)
        if ext:
            tags.update(ext)

    for tag, kws in TAGS_KEYWORDS.items():
        for kw in kws:
            if kw in text_l or kw in url_l:
                tags.add(tag)

    return sorted(tags)


# -------------------------
# BROWSER EXTRACTORS
# -------------------------
def extract_chrome_like(name, history_path):
    if not history_path or not history_path.exists():
        return []

    dst = history_path.parent / f"{name}_history_copy"
    if not safe_copy(history_path, dst):
        return []

    conn = sqlite3.connect(str(dst))
    cur = conn.cursor()

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=DAYS_FOR_WEEKLY)
    chrome_epoch = datetime.datetime(1601, 1, 1)
    cutoff_ts = int((cutoff - chrome_epoch).total_seconds() * 1_000_000)

    cur.execute("""
        SELECT url, title, last_visit_time
        FROM urls
        WHERE last_visit_time > ?
    """, (cutoff_ts,))

    rows = cur.fetchall()
    conn.close()

    try:
        dst.unlink()
    except:
        pass

    results = []
    for url, title, ts in rows:
        results.append({
            "browser": name,
            "url": url,
            "title": title or "",
            "last_visit": chrome_time_to_dt(ts)
        })
    return results


def extract_safari():
    p = safari_history_path()
    if not p.exists():
        return []

    dst = p.parent / "History_copy_safari.db"
    if not safe_copy(p, dst):
        return []

    conn = sqlite3.connect(str(dst))
    cur = conn.cursor()

    cutoff = datetime.datetime.now() - datetime.timedelta(days=DAYS_FOR_WEEKLY)
    cutoff_ts = cutoff.timestamp()

    cur.execute("""
        SELECT history_items.url, history_visits.title, history_visits.visit_time
        FROM history_items
        JOIN history_visits ON history_items.id = history_visits.history_item
        WHERE history_visits.visit_time > ?
    """, (cutoff_ts,))

    rows = cur.fetchall()
    conn.close()

    try:
        dst.unlink()
    except:
        pass

    results = []
    for url, title, ts in rows:
        dt = datetime.datetime.fromtimestamp(ts)
        results.append({
            "browser": "Safari",
            "url": url,
            "title": title or "",
            "last_visit": dt
        })
    return results


def extract_firefox():
    fp = firefox_history_path()
    if not fp or not fp.exists():
        return []

    dst = fp.parent / "places_copy.sqlite"
    if not safe_copy(fp, dst):
        return []

    conn = sqlite3.connect(str(dst))
    cur = conn.cursor()

    cutoff = (datetime.datetime.utcnow() -
              datetime.timedelta(days=DAYS_FOR_WEEKLY)).timestamp()

    cur.execute("""
        SELECT url, title, last_visit_date
        FROM moz_places
        WHERE last_visit_date > ?
    """, (cutoff * 1_000_000,))

    rows = cur.fetchall()
    conn.close()

    try:
        dst.unlink()
    except:
        pass

    results = []
    for url, title, ts in rows:
        dt = datetime.datetime.fromtimestamp(ts / 1_000_000)
        results.append({
            "browser": "Firefox",
            "url": url,
            "title": title or "",
            "last_visit": dt
        })
    return results


# -------------------------
# MERGE DATA
# -------------------------
def get_all_entries():
    entries = []
    entries += extract_chrome_like("Brave", brave_history_path())
    entries += extract_chrome_like("Chrome", chrome_history_path())
    entries += extract_safari()
    entries += extract_firefox()

    return sorted(entries, key=lambda e: e["last_visit"], reverse=True)


# -------------------------
# MARKDOWN GENERATION
# -------------------------
def write_daily(date, entries):
    iso = date.isoformat()
    md_path = DAILY_DIR / f"{iso}.md"

    searches = []
    topics = defaultdict(list)

    for e in entries:
        engine, q = extract_search_query(e["url"])
        if engine and q:
            topic = classify_topic(q, e["url"])
            tags = classify_tags(q, e["url"])
            searches.append((engine, q, e["url"], e["last_visit"]))
            topics[topic].append({
                "title": f"Search: {q}",
                "url": e["url"],
                "time": e["last_visit"],
                "tags": tags
            })
        else:
            topic = classify_topic(e["title"], e["url"])
            tags = classify_tags(e["title"], e["url"])
            topics[topic].append({
                "title": e["title"] or "(Untitled)",
                "url": e["url"],
                "time": e["last_visit"],
                "tags": tags
            })

    # YAML frontmatter
    all_tags = {t for items in topics.values() for entry in items for t in entry["tags"]}

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f"date: {iso}\n")
        f.write(f"tags: [{', '.join(sorted(all_tags))}]\n")
        f.write("type: browser-activity\n")
        f.write("---\n\n")

        f.write(f"# Browser Activity — {iso}\n\n")

        f.write("## 🔍 Searches\n")
        if searches:
            for engine, q, url, t in searches:
                f.write(f"- {t.strftime('%H:%M')} — **{engine}**: {q}\n")
                f.write(f"  - [{url}]({url})\n")
        else:
            f.write("_No searches_\n")
        f.write("\n")

        # Topics
        for topic, items in sorted(topics.items(), key=lambda kv: -len(kv[1])):
            f.write(f"## {topic} ({len(items)})\n")
            for it in items:
                t = it["time"].strftime("%H:%M") if it["time"] else ""
                tag_str = " ".join(f"`{x}`" for x in it["tags"])
                title = it["title"]
                f.write(f"- {t} — [{title}]({it['url']}) {tag_str}\n")
            f.write("\n")

    # copy to Obsidian
    if OBSIDIAN_VAULT:
        try:
            shutil.copy(md_path, OBSIDIAN_VAULT / f"{iso}.md")
        except Exception as e:
            print("Failed to write to Obsidian:", e)

    return md_path


def write_weekly(start_date, end_date, entries):
    iso = f"{start_date.isoformat()}_to_{end_date.isoformat()}"
    md_path = WEEKLY_DIR / f"weekly-summary-{iso}.md"

    topics = defaultdict(list)
    for e in entries:
        topic = classify_topic(e["title"], e["url"])
        tags = classify_tags(e["title"], e["url"])
        topics[topic].append({**e, "tags": tags})

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Weekly Browser Summary — {iso}\n\n")
        for topic, items in sorted(topics.items(), key=lambda kv: -len(kv[1])):
            f.write(f"## {topic} — {len(items)} items\n")
            domain_counts = Counter(
                urllib.parse.urlparse(e["url"]).netloc for e in items
            )
            f.write("**Top domains:** " +
                    ", ".join(f"{d} ({c})" for d, c in domain_counts.most_common(5))
                    + "\n\n")

            for e in items[:200]:
                t = e["last_visit"].strftime("%Y-%m-%d %H:%M")
                tags = ", ".join(e["tags"])
                f.write(f"- {t} — [{e['title']}]({e['url']}) — `{tags}`\n")
            f.write("\n")

    return md_path


# -------------------------
# MAIN
# -------------------------
def main():
    today = datetime.date.today()
    all_entries = get_all_entries()

    # DAILY
    daily_entries = [
        e for e in all_entries
        if e["last_visit"].date() == today
    ]
    if not daily_entries:
        daily_entries = all_entries[:1000]  # fallback

    daily_path = write_daily(today, daily_entries)
    print("Daily written:", daily_path)

    # WEEKLY
    start = today - datetime.timedelta(days=DAYS_FOR_WEEKLY - 1)
    weekly_entries = [
        e for e in all_entries
        if start <= e["last_visit"].date() <= today
    ]
    weekly_path = write_weekly(start, today, weekly_entries)
    print("Weekly written:", weekly_path)


if __name__ == "__main__":
    main()
