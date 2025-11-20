import datetime, shutil, urllib.parse
from pathlib import Path
from collections import defaultdict, Counter
from .classify import extract_search_query, classify_topic, classify_tags
from .config import DAILY_DIR, WEEKLY_DIR, OBSIDIAN_VAULT

def write_daily(date, entries):
    iso=date.isoformat()
    md=DAILY_DIR/f"{iso}.md"
    topics=defaultdict(list); searches=[]
    for e in entries:
        eng,q=extract_search_query(e['url'])
        if eng and q:
            topic=classify_topic(q,e['url'])
            tags=classify_tags(q,e['url'])
            searches.append((eng,q,e['url'],e['last_visit']))
            topics[topic].append({'title':f"Search: {q}", 'url':e['url'], 'time':e['last_visit'], 'tags':tags})
        else:
            topic=classify_topic(e['title'],e['url'])
            tags=classify_tags(e['title'],e['url'])
            topics[topic].append({'title':e['title'] or '(Untitled)', 'url':e['url'],'time':e['last_visit'],'tags':tags})
    all_tags=sorted({t for it in topics.values() for x in it for t in x['tags']})
    with open(md,'w') as f:
        f.write('---\n'); f.write(f"date: {iso}\n"); f.write(f"tags: [{', '.join(all_tags)}]\n"); f.write('type: browser-activity\n'); f.write('---\n\n')
        f.write(f"# Browser Activity — {iso}\n\n")
        f.write("## 🔍 Searches\n")
        if searches:
            for eng,q,url,t in searches:
                f.write(f"- {t.strftime('%H:%M')} — **{eng}**: {q}\n  - [{url}]({url})\n")
        else: f.write("_No searches_\n")
        f.write("\n")
        for topic,items in sorted(topics.items(), key=lambda kv:-len(kv[1])):
            f.write(f"## {topic} ({len(items)})\n")
            for it in items:
                ts=it['time'].strftime('%H:%M'); tag_str=' '.join(f"`{t}`" for t in it['tags'])
                f.write(f"- {ts} — [{it['title']}]({it['url']}) {tag_str}\n")
            f.write("\n")
    if OBSIDIAN_VAULT:
        try: shutil.copy(md, OBSIDIAN_VAULT/f"{iso}.md")
        except: pass
    return md

def write_weekly(start,end,entries):
    iso=f"{start.isoformat()}_to_{end.isoformat()}"
    md=WEEKLY_DIR/f"weekly-summary-{iso}.md"
    topics=defaultdict(list)
    for e in entries:
        topic=classify_topic(e['title'],e['url'])
        tags=classify_tags(e['title'],e['url'])
        topics[topic].append({**e,'tags':tags})
    with open(md,'w') as f:
        f.write(f"# Weekly Browser Summary — {iso}\n\n")
        for topic,items in sorted(topics.items(), key=lambda kv:-len(kv[1])):
            f.write(f"## {topic} — {len(items)} items\n")
            doms=Counter(urllib.parse.urlparse(e['url']).netloc for e in items)
            f.write(f"**Top domains:** "+", ".join(f"{d} ({c})" for d,c in doms.most_common(5))+"\n\n")
            for e in items[:200]:
                ts=e['last_visit'].strftime('%Y-%m-%d %H:%M'); tg=', '.join(e['tags'])
                f.write(f"- {ts} — [{e['title']}]({e['url']}) — `{tg}`\n")
            f.write("\n")
    return md
