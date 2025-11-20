import shutil, datetime
def safe_copy(src,dst):
    try: shutil.copy(src,dst); return True
    except: return False
def chrome_time_to_dt(ts):
    if ts is None: return None
    epoch=datetime.datetime(1601,1,1)
    return epoch+datetime.timedelta(microseconds=ts)
