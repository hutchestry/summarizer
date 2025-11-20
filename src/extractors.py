import sqlite3, datetime, glob
from pathlib import Path
from .utils import safe_copy, chrome_time_to_dt
from .config import DAYS_FOR_WEEKLY

def safari_history_path(): return Path.home()/ 'Library/Safari/History.db'
def chrome_history_path(): return Path.home()/ 'Library/Application Support/Google/Chrome/Default/History'
def brave_history_path(): return Path.home()/ 'Library/Application Support/BraveSoftware/Brave-Browser/Default/History'
def firefox_history_path():
    base=Path.home()/ 'Library/Application Support/Firefox/Profiles'
    prof=list(base.glob('*.default*'))
    return prof[0]/'places.sqlite' if prof else None

def extract_chrome_like(name, path):
    if not path or not path.exists(): return []
    dst=path.parent/f"{name}_copy"
    if not safe_copy(path,dst): return []
    conn=sqlite3.connect(dst); cur=conn.cursor()
    cutoff=datetime.datetime.utcnow()-datetime.timedelta(days=DAYS_FOR_WEEKLY)
    chrome_epoch=datetime.datetime(1601,1,1)
    cutoff_ts=int((cutoff-chrome_epoch).total_seconds()*1_000_000)
    cur.execute("SELECT url,title,last_visit_time FROM urls WHERE last_visit_time>?",(cutoff_ts,))
    rows=cur.fetchall(); conn.close(); dst.unlink(missing_ok=True)
    return [{"browser":name,"url":u,"title":t or "","last_visit":chrome_time_to_dt(ts)} for u,t,ts in rows]

def extract_safari():
    p=safari_history_path()
    if not p.exists(): return []
    dst=p.parent/'History_copy'
    if not safe_copy(p,dst): return []
    conn=sqlite3.connect(dst); cur=conn.cursor()
    cutoff=datetime.datetime.now()-datetime.timedelta(days=DAYS_FOR_WEEKLY)
    cur.execute("SELECT history_items.url, history_visits.title, history_visits.visit_time FROM history_items JOIN history_visits ON history_items.id=history_visits.history_item WHERE visit_time> ?",(cutoff.timestamp(),))
    rows=cur.fetchall(); conn.close(); dst.unlink(missing_ok=True)
    return [{"browser":"Safari","url":u,"title":t or "","last_visit":datetime.datetime.fromtimestamp(ts)} for u,t,ts in rows]

def extract_firefox():
    fp=firefox_history_path()
    if not fp or not fp.exists(): return []
    dst=fp.parent/'places_copy.sqlite'
    if not safe_copy(fp,dst): return []
    conn=sqlite3.connect(dst); cur=conn.cursor()
    cutoff=(datetime.datetime.utcnow()-datetime.timedelta(days=DAYS_FOR_WEEKLY)).timestamp()*1_000_000
    cur.execute("SELECT url,title,last_visit_date FROM moz_places WHERE last_visit_date>?",(cutoff,))
    rows=cur.fetchall(); conn.close(); dst.unlink(missing_ok=True)
    return [{"browser":"Firefox","url":u,"title":t or "","last_visit":datetime.datetime.fromtimestamp(ts/1_000_000)} for u,t,ts in rows]

def get_all_entries():
    ents=[]
    ents+=extract_chrome_like('Brave', brave_history_path())
    ents+=extract_chrome_like('Chrome', chrome_history_path())
    ents+=extract_safari()
    ents+=extract_firefox()
    return sorted(ents, key=lambda e:e['last_visit'], reverse=True)
