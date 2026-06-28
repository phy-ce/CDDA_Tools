import os
import threading

from .installs import find_locales, Translator
from .dataindex import DataIndex

# ---------------------------------------------------------------------------
# Caches: one index per (version, include-mods); one translator per (ver, loc)
# ---------------------------------------------------------------------------
INSTALLS = []



_index_cache = {}



_tr_cache = {}



_lock = threading.Lock()



def get_index(ver, mods):
    key = (ver, mods)
    with _lock:
        idx = _index_cache.get(key)
        if idx is None:
            inst = INSTALLS[ver]
            dirs = [inst["json_dir"]]
            if mods and os.path.isdir(inst["mods_dir"]):
                dirs.append(inst["mods_dir"])
            idx = DataIndex()
            idx.load(dirs)
            _index_cache[key] = idx
        return idx



def get_translator(ver, loc):
    key = (ver, loc)
    tr = _tr_cache.get(key)
    if tr is None:
        locs = find_locales(INSTALLS[ver]["json_dir"])
        tr = Translator(locs.get(loc))
        _tr_cache[key] = tr
    return tr



def locales_for(ver):
    return find_locales(INSTALLS[ver]["json_dir"])

