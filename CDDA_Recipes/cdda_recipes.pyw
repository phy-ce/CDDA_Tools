#!/usr/bin/env python
"""CDDA Recipe Helper — offline crafting assistant for Cataclysm: DDA / BN.

Reads the installed game's data/json (and optionally added mods), indexes
items + recipes + requirements, and answers two questions:
  - "How do I craft X?"  (ingredients, tools, qualities, skills, how to learn)
  - "What can I make with X?"  (reverse: recipes that use X as a component)

Everything is parsed from the local install, so it always matches your exact
version and mods. No network, no API key.
"""
import os
import glob
import json
import gettext
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

HOME = os.path.expanduser("~")
GAMES_ROOT = os.path.join(HOME, "Games")
GAME_SUBDIRS = ["Cataclysm-DDA", "Cataclysm-BN"]
MOD_MARKER = ".cdda_added"     # same marker CDDA_Installer uses for added content

# friendly labels for the locale codes CDDA ships under lang/mo/
LOCALE_NAMES = {
    "en": "English", "ko": "한국어", "ja": "日本語",
    "zh_CN": "简体中文", "zh_TW": "繁體中文", "ru_RU": "Русский",
    "de": "Deutsch", "fr": "Français", "es_ES": "Español", "es_AR": "Español (AR)",
    "pt_BR": "Português (BR)", "it_IT": "Italiano", "pl_PL": "Polski",
}


# ---------------------------------------------------------------------------
# Localization — translate English item names via the game's own gettext .mo
# ---------------------------------------------------------------------------
class Translator:
    """Maps an English item name to its translation in one locale.

    Falls back to English when a string has no translation. Also handles
    strings the game tagged with a msgctxt (stored as "ctx\\x04msgid")."""
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


def find_locales(json_dir):
    """{locale_code: mo_path} for an install's lang/mo folder (always incl. 'en')."""
    out = {"en": None}
    install_root = os.path.dirname(os.path.dirname(json_dir))   # .../<ver>/data/json -> <ver>
    modir = os.path.join(install_root, "lang", "mo")
    if os.path.isdir(modir):
        for loc in sorted(os.listdir(modir)):
            mos = glob.glob(os.path.join(modir, loc, "LC_MESSAGES", "*.mo"))
            if mos:
                out[loc] = mos[0]
    return out


# ---------------------------------------------------------------------------
# Install discovery (mirrors CDDA_Installer's folder conventions)
# ---------------------------------------------------------------------------
def find_json_dir(base):
    """Return the data/json folder under an install (or None)."""
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
    """Scan ~/Games/Cataclysm-* for version folders that contain data/json."""
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


# ---------------------------------------------------------------------------
# Helpers for the CDDA JSON shapes
# ---------------------------------------------------------------------------
def name_str(nm):
    """CDDA names are str, {"str": ...}, or a list. Return a display string."""
    if nm is None:
        return None
    if isinstance(nm, str):
        return nm
    if isinstance(nm, dict):
        return nm.get("str") or nm.get("str_sp") or nm.get("str_pl")
    if isinstance(nm, list) and nm:
        return name_str(nm[0])
    return None


# ---------------------------------------------------------------------------
# The data index
# ---------------------------------------------------------------------------
class DataIndex:
    def __init__(self):
        self.by_id = {}          # id -> raw entry (items, abstracts, ...)
        self.reqs = {}           # requirement id -> entry
        self.quals = {}          # tool_quality id -> display name
        self.recipes = []        # non-obsolete recipe entries
        self.by_result = {}      # result item id -> [recipe, ...]
        self.used_in = {}        # component item id -> set(result item id)
        self._namecache = {}
        self.tr = lambda s: s    # active translator (English by default)

    # -- loading -----------------------------------------------------------
    def load(self, json_dirs, progress=None):
        nfiles = 0
        for d in json_dirs:
            for dirpath, _, files in os.walk(d):
                for f in files:
                    if not f.endswith(".json"):
                        continue
                    nfiles += 1
                    if progress and nfiles % 200 == 0:
                        progress(nfiles)
                    self._load_file(os.path.join(dirpath, f))
        self._index_recipes()
        return nfiles

    def _load_file(self, path):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except Exception:
            return
        for e in (data if isinstance(data, list) else [data]):
            if not isinstance(e, dict):
                continue
            t = e.get("type")
            eid = e.get("id") or e.get("abstract")
            if t == "recipe":
                if not e.get("obsolete"):
                    self.recipes.append(e)
            elif t == "requirement" and isinstance(eid, str):
                self.reqs[eid] = e
            elif t == "tool_quality" and isinstance(eid, str):
                self.quals[eid] = name_str(e.get("name")) or eid
            # store anything with an id so component/result names resolve
            if isinstance(eid, str):
                self.by_id.setdefault(eid, e)

    def _index_recipes(self):
        for r in self.recipes:
            res = r.get("result")
            if not isinstance(res, str):
                continue
            self.by_result.setdefault(res, []).append(r)
            for iid in self._recipe_component_ids(r):
                self.used_in.setdefault(iid, set()).add(res)

    # -- name resolution (follows copy-from) -------------------------------
    def raw_name(self, eid, _seen=None):
        """English display name (cached), following copy-from inheritance."""
        if not isinstance(eid, str):
            return str(eid)
        if eid in self._namecache:
            return self._namecache[eid]
        seen = _seen or set()
        if eid in seen:
            return eid
        seen.add(eid)
        e = self.by_id.get(eid)
        if not e:
            return eid
        nm = name_str(e.get("name"))
        if nm is None and isinstance(e.get("copy-from"), str):
            nm = self.raw_name(e["copy-from"], seen)
        if nm is None:
            nm = eid
        self._namecache[eid] = nm
        return nm

    def name(self, eid):
        """Localized display name (English name run through the active translator)."""
        return self.tr(self.raw_name(eid))

    # -- component extraction ---------------------------------------------
    def _recipe_component_ids(self, recipe, _depth=0):
        """Flat set of concrete item ids referenced by a recipe (LIST/using
        requirements resolved one level deep)."""
        ids = set()
        groups = list(recipe.get("components", []))
        for use in recipe.get("using", []):
            if isinstance(use, list) and use and use[0] in self.reqs:
                groups += self.reqs[use[0]].get("components", [])
        for group in groups:
            if not isinstance(group, list):
                continue
            for entry in group:
                if not isinstance(entry, list) or not entry:
                    continue
                iid = entry[0]
                is_list = len(entry) > 2 and entry[2] == "LIST"
                if is_list and iid in self.reqs and _depth < 3:
                    ids |= self._recipe_component_ids(
                        {"components": self.reqs[iid].get("components", [])}, _depth + 1)
                elif isinstance(iid, str):
                    ids.add(iid)
        return ids

    def craftable(self):
        """Sorted list of (display_name, result_id) for everything craftable."""
        rows = [(self.name(rid), rid) for rid in self.by_result]
        rows.sort(key=lambda x: x[0].lower())
        return rows


# ---------------------------------------------------------------------------
# Rendering a recipe to readable text
# ---------------------------------------------------------------------------
def _fmt_group(idx, group, idx_data, depth=0):
    """One OR-group -> 'A x2  OR  B x1'."""
    alts = []
    for entry in group:
        if not isinstance(entry, list) or not entry:
            continue
        iid = entry[0]
        cnt = entry[1] if len(entry) > 1 else 1
        is_list = len(entry) > 2 and entry[2] == "LIST"
        if is_list and iid in idx_data.reqs and depth < 2:
            inner = []
            for g in idx_data.reqs[iid].get("components", []):
                inner.append(_fmt_group(0, g, idx_data, depth + 1))
            alts.append("({}: {})".format(idx_data.name(iid), "  &  ".join(inner)))
        else:
            alts.append("{} x{}".format(idx_data.name(iid), cnt))
    return "  OR  ".join(alts) if alts else "?"


def render_recipe(idx_data, recipe, n=None):
    L = []
    head = "▼ Recipe" + ("" if n is None else " #%d" % n)
    L.append(head)

    skill = recipe.get("skill_used")
    diff = recipe.get("difficulty")
    if skill or diff is not None:
        L.append("  Skill: {}{}".format(
            idx_data.name(skill) if skill else "?",
            "  (difficulty %s)" % diff if diff is not None else ""))
    req = recipe.get("skills_required")
    if req:
        pairs = req if (req and isinstance(req[0], list)) else [req]
        L.append("  Also needs: " + ", ".join(
            "%s %s" % (idx_data.name(p[0]), p[1]) for p in pairs if isinstance(p, list)))
    if recipe.get("time"):
        L.append("  Time: {}".format(recipe["time"]))

    # how to learn
    learn = []
    al = recipe.get("autolearn")
    if al is True:
        learn.append("auto-learned")
    elif isinstance(al, list):
        learn.append("auto-learned (" + ", ".join("%s %s" % (p[0], p[1]) for p in al) + ")")
    for b in recipe.get("book_learn", []) or []:
        if isinstance(b, list) and b:
            learn.append("book: %s" % idx_data.name(b[0]))
    if learn:
        L.append("  Learn: " + "; ".join(learn))

    # tools / qualities (merge in `using` requirements)
    quals = list(recipe.get("qualities", []) or [])
    tools = list(recipe.get("tools", []) or [])
    extra_comp = []
    for use in recipe.get("using", []) or []:
        if isinstance(use, list) and use and use[0] in idx_data.reqs:
            r = idx_data.reqs[use[0]]
            quals += r.get("qualities", []) or []
            tools += r.get("tools", []) or []
            extra_comp += r.get("components", []) or []

    if quals:
        qs = []
        for q in quals:
            if isinstance(q, dict):
                qname = idx_data.tr(idx_data.quals.get(q.get("id"), q.get("id")))
                qs.append("%s %s" % (qname, q.get("level", 1)))
        if qs:
            L.append("  Tool quality: " + ", ".join(qs))
    if tools:
        ts = []
        for group in tools:
            if not isinstance(group, list):
                continue
            opts = []
            for entry in group:
                if isinstance(entry, list) and entry:
                    charges = entry[1] if len(entry) > 1 else -1
                    label = idx_data.name(entry[0])
                    if isinstance(charges, int) and charges > 0:
                        label += " (%d charges)" % charges
                    opts.append(label)
            if opts:
                ts.append("  OR  ".join(opts))
        if ts:
            L.append("  Tools: " + " ; ".join(ts))

    # components
    comps = list(recipe.get("components", []) or []) + extra_comp
    if comps:
        L.append("  Ingredients:")
        for i, group in enumerate(comps):
            if isinstance(group, list):
                L.append("    • " + _fmt_group(i, group, idx_data))
    if not comps and not tools and not quals:
        L.append("  (no listed ingredients — may be gathered/disassembled)")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("CDDA Recipe Helper")
        root.geometry("860x620")
        root.minsize(720, 520)

        self.idx = DataIndex()
        self.installs = find_installs()
        self.rows = []          # (display, result_id) currently shown
        self._all_rows = []

        # top bar -----------------------------------------------------------
        top = ttk.Frame(root, padding=(10, 8))
        top.pack(fill="x")
        ttk.Label(top, text="Version:").pack(side="left")
        self.ver = ttk.Combobox(top, state="readonly", width=34,
                                values=[i["label"] for i in self.installs])
        if self.installs:
            self.ver.current(0)
        self.ver.pack(side="left", padx=(6, 8))
        self.inc_mods = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Include mods", variable=self.inc_mods).pack(side="left")
        ttk.Button(top, text="Load", command=self.load).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Browse…", command=self.browse).pack(side="left", padx=(6, 0))

        ttk.Label(top, text="Lang:").pack(side="left", padx=(12, 0))
        self.locales = {"en": None}            # code -> mo path
        self._lang_codes = ["en"]
        self.cur_locale = "en"
        self.lang = ttk.Combobox(top, state="readonly", width=10, values=["English"])
        self.lang.current(0)
        self.lang.bind("<<ComboboxSelected>>", lambda *_: self.set_language())
        self.lang.pack(side="left", padx=(6, 0))

        self.status = ttk.Label(top, text="", foreground="#666")
        self.status.pack(side="left", padx=(12, 0))

        # search + split ----------------------------------------------------
        body = ttk.Frame(root, padding=(10, 0, 10, 10))
        body.pack(fill="both", expand=True)

        pane = ttk.Panedwindow(body, orient="horizontal")
        pane.pack(fill="both", expand=True)

        left = ttk.Frame(pane)
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *_: self.apply_filter())
        se = ttk.Entry(left, textvariable=self.search)
        se.pack(fill="x", pady=(0, 6))
        se.insert(0, "")
        self._placeholder(se, "search item name…")
        self.listbox = tk.Listbox(left, activestyle="none")
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", lambda *_: self.show_selected())
        pane.add(left, weight=1)

        right = ttk.Frame(pane)
        self.detail = tk.Text(right, wrap="word", state="disabled",
                              font=("Consolas", 10), padx=8, pady=8)
        self.detail.pack(fill="both", expand=True)
        pane.add(right, weight=2)

        self._manual_dir = None
        if self.installs:
            self.load()
        else:
            self._set_status("No installs found under ~/Games — use Browse…", "#a00")

    # -- small UI helpers --------------------------------------------------
    def _placeholder(self, entry, text):
        def on_in(_):
            if entry.get() == text:
                entry.delete(0, "end"); entry.config(foreground="black")
        def on_out(_):
            if not entry.get():
                entry.insert(0, text); entry.config(foreground="#999")
        entry.insert(0, text); entry.config(foreground="#999")
        entry.bind("<FocusIn>", on_in)
        entry.bind("<FocusOut>", on_out)
        self._ph_text = text

    def _set_status(self, msg, color="#666"):
        self.status.config(text=msg, foreground=color)

    def _set_detail(self, text):
        self.detail.config(state="normal")
        self.detail.delete("1.0", "end")
        self.detail.insert("1.0", text)
        self.detail.config(state="disabled")

    # -- loading -----------------------------------------------------------
    def browse(self):
        d = filedialog.askdirectory(title="Pick a CDDA install or data/json folder")
        if not d:
            return
        jdir = d if os.path.basename(d) == "json" else find_json_dir(d)
        if not jdir:
            messagebox.showerror("Not found", "No data/json folder found there.")
            return
        self._manual_dir = jdir
        self.load(manual=jdir)

    def load(self, manual=None):
        if manual:
            jdir = manual
            mods = os.path.join(os.path.dirname(jdir), "mods")
        else:
            if not self.installs:
                return
            inst = self.installs[self.ver.current()]
            jdir, mods = inst["json_dir"], inst["mods_dir"]
        dirs = [jdir]
        if self.inc_mods.get() and os.path.isdir(mods):
            dirs.append(mods)
        # discover which languages this install ships, refresh the selector
        self.locales = find_locales(jdir)
        self._refresh_lang_combo()
        mo_path = self.locales.get(self.cur_locale)
        self._set_status("Loading…")
        self.listbox.delete(0, "end")
        self._set_detail("")
        threading.Thread(target=self._load_worker, args=(dirs, mo_path), daemon=True).start()

    def _refresh_lang_combo(self):
        order = ["en", "ko", "ja"]
        codes = sorted(self.locales.keys(),
                       key=lambda c: (order.index(c) if c in order else 99, c))
        self._lang_codes = codes
        self.lang["values"] = [LOCALE_NAMES.get(c, c) for c in codes]
        if self.cur_locale not in codes:
            self.cur_locale = "en"
        self.lang.current(codes.index(self.cur_locale))

    def set_language(self):
        if not self._lang_codes:
            return
        self.cur_locale = self._lang_codes[self.lang.current()]
        self.idx.tr = Translator(self.locales.get(self.cur_locale))
        self._all_rows = self.idx.craftable()
        self.apply_filter()
        self._set_status("%d craftable items  |  %d recipes" %
                         (len(self._all_rows), len(self.idx.recipes)))

    def _load_worker(self, dirs, mo_path):
        idx = DataIndex()
        try:
            idx.load(dirs, progress=lambda n: self.root.after(
                0, self._set_status, "Loading… %d files" % n))
            idx.tr = Translator(mo_path)
            rows = idx.craftable()
        except Exception as e:
            self.root.after(0, self._set_status, "Load error: %s" % e, "#a00")
            return
        self.root.after(0, self._loaded, idx, rows)

    def _loaded(self, idx, rows):
        self.idx = idx
        self._all_rows = rows
        self._set_status("%d craftable items  |  %d recipes" % (len(rows), len(idx.recipes)))
        self.apply_filter()

    # -- filtering + display ----------------------------------------------
    def apply_filter(self):
        q = self.search.get().strip().lower()
        if q == getattr(self, "_ph_text", "").lower():
            q = ""
        self.rows = [r for r in self._all_rows if q in r[0].lower()] if q else self._all_rows
        self.listbox.delete(0, "end")
        for disp, _ in self.rows[:3000]:
            self.listbox.insert("end", disp)
        if len(self.rows) > 3000:
            self.listbox.insert("end", "… (%d more — refine search)" % (len(self.rows) - 3000))

    def show_selected(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] >= len(self.rows):
            return
        disp, rid = self.rows[sel[0]]
        out = ["%s    [%s]" % (disp, rid), "=" * 60, ""]
        recipes = self.idx.by_result.get(rid, [])
        if recipes:
            for i, r in enumerate(recipes, 1):
                out.append(render_recipe(self.idx, r, i if len(recipes) > 1 else None))
                out.append("")
        else:
            out.append("(no crafting recipe)")
            out.append("")
        # reverse: used in
        users = sorted(self.idx.used_in.get(rid, ()), key=lambda x: self.idx.name(x).lower())
        if users:
            out.append("─" * 60)
            out.append("Used as an ingredient in (%d):" % len(users))
            for u in users[:60]:
                out.append("    • %s" % self.idx.name(u))
            if len(users) > 60:
                out.append("    … and %d more" % (len(users) - 60))
        self._set_detail("\n".join(out))


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista")
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
