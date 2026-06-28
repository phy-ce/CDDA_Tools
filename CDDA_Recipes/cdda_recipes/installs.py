import os
import glob
import json
import gettext

from .config import GAMES_ROOT, GAME_SUBDIRS

# ---------------------------------------------------------------------------
# Install discovery + localization (same conventions as CDDA_Installer)
# ---------------------------------------------------------------------------
def name_str(nm):
    if nm is None:
        return None
    if isinstance(nm, str):
        return nm
    if isinstance(nm, dict):
        return nm.get("str") or nm.get("str_sp") or nm.get("str_pl")
    if isinstance(nm, list) and nm:
        return name_str(nm[0])
    return None



def find_json_dir(base):
    cand = os.path.join(base, "data", "json")
    if os.path.isdir(cand):
        return cand
    for dirpath, dirs, _ in os.walk(base):
        if os.path.basename(dirpath) == "data" and "json" in dirs:
            return os.path.join(dirpath, "json")
    return None



def read_meta(path):
    try:
        return json.load(open(os.path.join(path, ".cdda_meta.json"), encoding="utf-8"))
    except Exception:
        return {}



def find_installs():
    installs = []
    for sub in GAME_SUBDIRS:
        root = os.path.join(GAMES_ROOT, sub)
        if not os.path.isdir(root):
            continue
        for entry in sorted(os.listdir(root)):
            vpath = os.path.join(root, entry)
            if not os.path.isdir(vpath):
                continue
            jdir = find_json_dir(vpath)
            if not jdir:
                continue
            meta = read_meta(vpath)
            label = "{}  |  {}".format(meta.get("game", sub), meta.get("version", entry))
            installs.append({"label": label, "json_dir": jdir,
                             "mods_dir": os.path.join(os.path.dirname(jdir), "mods")})
    return installs



def find_locales(json_dir):
    out = {"en": None}
    install_root = os.path.dirname(os.path.dirname(json_dir))
    modir = os.path.join(install_root, "lang", "mo")
    if os.path.isdir(modir):
        for loc in sorted(os.listdir(modir)):
            mos = glob.glob(os.path.join(modir, loc, "LC_MESSAGES", "*.mo"))
            if mos:
                out[loc] = mos[0]
    return out



class Translator:
    def __init__(self, mo_path=None):
        self.gt = None
        self._ctx_fallback = {}
        if mo_path:
            try:
                self.gt = gettext.GNUTranslations(open(mo_path, "rb"))
                for k, v in self.gt._catalog.items():
                    if isinstance(k, str) and "\x04" in k:
                        self._ctx_fallback.setdefault(k.split("\x04", 1)[1], v)
            except Exception:
                self.gt = None

    def __call__(self, s):
        if not self.gt or not s:
            return s
        r = self.gt.gettext(s)
        if r != s:
            return r
        return self._ctx_fallback.get(s, s)

