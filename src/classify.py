import re
from collections import Counter
from .config import EXTERNAL_TAGGER

TOPICS_KEYWORDS={
 'AI':['openai','llama','gpt','huggingface','langchain','transformer'],
 'Coding':['stackoverflow','github','python','javascript','rust','golang'],
 'News':['nytimes','bbc','cnn','reuters','bloomberg','washingtonpost'],
 'Shopping':['amazon.','ebay','bestbuy','shopping','checkout','cart'],
 'Video':['youtube','vimeo','watch','video'],
 'Reference':['wikipedia.org','wikihow','docs','developer.mozilla','mdn'],
 'Social':['twitter.com','x.com','facebook.com','instagram.com'],
 'Cloud/Infra':['aws.amazon','azure','gcp','docker','kubernetes'],
}

TAGS_KEYWORDS={
 'Troubleshooting':['error','fix','issue','exception','stacktrace'],
 'Programming':['tutorial','example','library','programming'],
 'Research':['paper','arxiv','study'],
 'Reference':['docs','documentation','api'],
 'Shopping':['price','buy','coupon'],
 'Video':['youtube','watch','video'],
}

SEARCH_PATTERNS={
 'google': re.compile(r"https?://.*google\..*/search\?.*[?&]q=(?P<q>[^&]+)"),
 'bing': re.compile(r"https?://.*bing\.com/search\?.*q=(?P<q>[^&]+)"),
 'duckduckgo': re.compile(r"https?://.*duckduckgo\.com/\?.*q=(?P<q>[^&]+)"),
 'youtube': re.compile(r"https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)(?P<q>[^&/]+)"),
}

def extract_search_query(url):
    for eng,p in SEARCH_PATTERNS.items():
        m=p.search(url)
        if m: return eng, m.group('q')
    return None,None

def classify_topic(text,url):
    t=(text or '').lower(); u=(url or '').lower()
    scores=Counter()
    for topic,kws in TOPICS_KEYWORDS.items():
        for kw in kws:
            if kw in t or kw in u: scores[topic]+=1
    return max(scores,key=scores.get) if scores else 'Misc'

def classify_tags(text,url):
    tags=set()
    if EXTERNAL_TAGGER:
        ext=EXTERNAL_TAGGER(text,url,{})
        if ext: tags.update(ext)
    t=(text or '').lower(); u=(url or '').lower()
    for tag,kws in TAGS_KEYWORDS.items():
        for kw in kws:
            if kw in t or kw in u: tags.add(tag)
    return sorted(tags)
