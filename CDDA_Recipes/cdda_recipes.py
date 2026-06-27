#!/usr/bin/env python
"""CDDA Recipe Helper — offline crafting assistant for Cataclysm: DDA / BN.

A small local web app (standard library only). It reads the installed game's
data/json (optionally including added mods), indexes items + recipes +
requirements, and serves a browser UI that answers:

  - "How do I craft X?"  (ingredients, tools, qualities, skills, how to learn)
  - "What can I make with X?"  (reverse: recipes that use X)

Every item reference is a real hyperlink, so you can click an ingredient to see
its own recipe (forward link) or follow the "used as an ingredient in" list
(back link). Names are localized via the game's own gettext files (EN / 한국어 /
日本語 / …). Run it and your browser opens automatically.
"""
import os
import glob
import json
import html
import gettext
import socket
import threading
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse, quote
from http.server import BaseHTTPRequestHandler, HTTPServer

HOME = os.path.expanduser("~")
GAMES_ROOT = os.path.join(HOME, "Games")
GAME_SUBDIRS = ["Cataclysm-DDA", "Cataclysm-BN"]

LOCALE_NAMES = {
    "en": "English", "ko": "한국어", "ja": "日本語",
    "zh_CN": "简体中文", "zh_TW": "繁體中文", "ru_RU": "Русский",
    "de": "Deutsch", "fr": "Français", "es_ES": "Español", "es_AR": "Español (AR)",
    "pt_BR": "Português (BR)", "it_IT": "Italiano", "pl_PL": "Polski",
}

# UI labels (the app's own chrome). Item/recipe *content* is localized from the
# game files; these are the surrounding labels. Falls back to English.
UI_STRINGS = {
    "en": {
        "brand": "CDDA Recipes", "search_ph": "search item name…", "mods": "mods",
        "hint": "{n} craftable items · {r} recipes. Type an item name above, or open "
                "one from a recipe to start clicking around.",
        "no_match": "No match.", "more": "… {n} more, refine your search.",
        "recipe": "Recipe", "skill": "Skill", "difficulty": "difficulty",
        "also_needs": "Also needs", "time": "Time", "learn": "Learn",
        "autolearn": "auto-learned", "books": "Books", "toolq": "Tool quality",
        "tools": "Tools", "ingredients": "Ingredients",
        "no_ing": "(no listed ingredients — may be gathered/disassembled)",
        "not_craftable": "Not craftable here — no recipe.",
        "used_in": "Used as an ingredient in ({n})",
        "disassembles": "Disassembles into", "tree": "Crafting tree",
        "weight": "Weight", "volume": "Volume", "material": "Material", "melee": "Melee",
        "categories": "Categories", "all_skills": "All skills", "max_lv": "Max level",
        "lv": "Lv", "found": "Found in (loot groups)", "all_cats": "← All categories",
        "items_n": "{n} items", "item_col": "Item", "browse_hint":
        "Pick a category to browse, or search by name above.",
        "settings": "Settings", "saved": "Saved.",
        "npc_loot": "Show NPC-inventory sources",
        "npc_loot_help": "Include groups carried by NPCs (NC_*) in 'Found in'. Off by default — they're noisy.",
        "group": "Loot group", "g_contains": "Can contain ({n})",
        "g_includes": "Includes groups ({n})", "g_partof": "Part of ({n})",
    },
    "ko": {
        "brand": "CDDA 레시피", "search_ph": "아이템 이름 검색…", "mods": "모드",
        "hint": "제작 가능 {n}개 · 레시피 {r}개. 위에 아이템 이름을 입력하거나, "
                "레시피에서 아이템을 열어 클릭하며 탐색하세요.",
        "no_match": "검색 결과 없음.", "more": "… 외 {n}개, 검색어를 좁히세요.",
        "recipe": "레시피", "skill": "스킬", "difficulty": "난이도",
        "also_needs": "추가 요구", "time": "시간", "learn": "습득",
        "autolearn": "자동 습득", "books": "책", "toolq": "도구 품질",
        "tools": "도구", "ingredients": "재료",
        "no_ing": "(표시된 재료 없음 — 채집/분해로 얻을 수 있음)",
        "not_craftable": "여기서는 제작 불가 — 레시피 없음.",
        "used_in": "이 아이템이 쓰이는 곳 ({n})",
        "disassembles": "분해 시 나오는 것", "tree": "제작 트리",
        "weight": "무게", "volume": "부피", "material": "재질", "melee": "근접",
        "categories": "카테고리", "all_skills": "모든 스킬", "max_lv": "최대 레벨",
        "lv": "Lv", "found": "입수 (루트 그룹)", "all_cats": "← 전체 카테고리",
        "items_n": "{n}개", "item_col": "아이템", "browse_hint":
        "카테고리를 골라 둘러보거나, 위에서 이름으로 검색하세요.",
        "settings": "설정", "saved": "저장됨.",
        "npc_loot": "NPC 소지 입수원 표시",
        "npc_loot_help": "'입수'에 NPC가 소지한 그룹(NC_*)도 포함. 기본 꺼짐 — 노이즈가 많습니다.",
        "group": "루트 그룹", "g_contains": "나올 수 있는 아이템 ({n})",
        "g_includes": "하위 그룹 ({n})", "g_partof": "상위 그룹 ({n})",
    },
    "ja": {
        "brand": "CDDAレシピ", "search_ph": "アイテム名で検索…", "mods": "MOD",
        "hint": "製作可能 {n}件 · レシピ {r}件。上にアイテム名を入力するか、"
                "レシピからアイテムを開いてクリックで辿ってください。",
        "no_match": "該当なし。", "more": "… 他 {n}件、検索語を絞ってください。",
        "recipe": "レシピ", "skill": "スキル", "difficulty": "難易度",
        "also_needs": "追加要件", "time": "時間", "learn": "習得",
        "autolearn": "自動習得", "books": "書籍", "toolq": "道具品質",
        "tools": "道具", "ingredients": "材料",
        "no_ing": "（記載の材料なし — 採取/分解で入手）",
        "not_craftable": "ここでは製作不可 — レシピなし。",
        "used_in": "材料として使われるレシピ ({n})",
        "disassembles": "分解で得られる", "tree": "製作ツリー",
        "weight": "重量", "volume": "体積", "material": "材質", "melee": "近接",
        "categories": "カテゴリ", "all_skills": "全スキル", "max_lv": "最大レベル",
        "lv": "Lv", "found": "入手（ルートグループ）", "all_cats": "← 全カテゴリ",
        "items_n": "{n}件", "item_col": "アイテム", "browse_hint":
        "カテゴリを選んで閲覧するか、上で名前検索してください。",
        "settings": "設定", "saved": "保存しました。",
        "npc_loot": "NPC所持の入手元を表示",
        "npc_loot_help": "「入手」にNPC所持グループ（NC_*）も含める。既定はオフ — ノイズが多いです。",
        "group": "ルートグループ", "g_contains": "入りうるアイテム ({n})",
        "g_includes": "内包グループ ({n})", "g_partof": "上位グループ ({n})",
    },
}


def T(ctx, key, **kw):
    s = UI_STRINGS.get(ctx["lang"], UI_STRINGS["en"]).get(key) or UI_STRINGS["en"][key]
    return s.format(**kw) if kw else s


# recipe category codes -> readable names. Order = how they're listed.
CAT_NAMES = {
    "CC_WEAPON": {"en": "Weapons", "ko": "무기", "ja": "武器"},
    "CC_AMMO": {"en": "Ammo", "ko": "탄약", "ja": "弾薬"},
    "CC_ARMOR": {"en": "Armor / Clothing", "ko": "방어구 / 의류", "ja": "防具 / 衣類"},
    "CC_FOOD": {"en": "Food & Drink", "ko": "음식 / 음료", "ja": "食料 / 飲料"},
    "CC_CHEM": {"en": "Chemistry", "ko": "화학", "ja": "化学"},
    "CC_ELECTRONIC": {"en": "Electronics", "ko": "전자기기", "ja": "電子機器"},
    "CC_ANIMALS": {"en": "Animals", "ko": "동물", "ja": "動物"},
    "CC_OTHER": {"en": "Other", "ko": "기타", "ja": "その他"},
}


def cat_name(code, lang):
    d = CAT_NAMES.get(code)
    if not d:
        return code.replace("CC_", "").replace("_", " ").title()
    return d.get(lang) or d["en"]


# in-memory app settings (single local user). Set from the Settings page.
SETTINGS = {"npc_loot": False}


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


# ---------------------------------------------------------------------------
# Data index
# ---------------------------------------------------------------------------
class DataIndex:
    def __init__(self):
        self.by_id = {}
        self.reqs = {}
        self.quals = {}
        self.recipes = []
        self.by_result = {}
        self.used_in = {}
        self.uncrafts = {}       # item id -> [uncraft entry, ...]
        self.cat_of = {}         # result id -> recipe category code (e.g. CC_WEAPON)
        self.by_cat = {}         # category code -> [result id, ...]
        self.item_groups_of = {}  # item id -> set(group id) it appears in (direct)
        self.group_parents = {}   # child group id -> set(parent group id)
        self.group_items = {}     # group id -> set(item id) it can spawn (direct)
        self.group_subgroups = {}  # group id -> set(child group id)
        self._groups = []        # raw item_group defs, processed after load
        self._namecache = {}
        self._desccache = {}
        self.tr = lambda s: s

    def load(self, json_dirs):
        for d in json_dirs:
            for dirpath, _, files in os.walk(d):
                for f in files:
                    if f.endswith(".json"):
                        self._load_file(os.path.join(dirpath, f))
        self._index_recipes()

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
            elif t == "uncraft" and isinstance(e.get("result"), str):
                self.uncrafts.setdefault(e["result"], []).append(e)
            elif t == "item_group" and isinstance(eid, str):
                self._groups.append(e)
            elif t == "requirement" and isinstance(eid, str):
                self.reqs[eid] = e
            elif t == "tool_quality" and isinstance(eid, str):
                self.quals[eid] = name_str(e.get("name")) or eid
            if isinstance(eid, str):
                self.by_id.setdefault(eid, e)

    def _index_recipes(self):
        for r in self.recipes:
            res = r.get("result")
            if not isinstance(res, str):
                continue
            self.by_result.setdefault(res, []).append(r)
            if res not in self.cat_of and r.get("category"):
                self.cat_of[res] = r["category"]
            for iid in self._recipe_component_ids(r):
                self.used_in.setdefault(iid, set()).add(res)
        for res, cat in self.cat_of.items():
            self.by_cat.setdefault(cat, []).append(res)
        self._index_groups()

    def _index_groups(self):
        for g in self._groups:
            gid = g.get("id") or g.get("abstract")
            if not isinstance(gid, str):
                continue
            items, subgroups = self._group_members(g)
            self.group_items.setdefault(gid, set()).update(items)
            self.group_subgroups.setdefault(gid, set()).update(subgroups)
            for it in items:
                self.item_groups_of.setdefault(it, set()).add(gid)
            for sg in subgroups:
                self.group_parents.setdefault(sg, set()).add(gid)
        self._groups = []

    @staticmethod
    def _group_members(g):
        """Item ids and child-group ids referenced by an item_group def."""
        items, groups = set(), set()

        def walk(node):
            if isinstance(node, list):
                for x in node:
                    if isinstance(x, list) and x and isinstance(x[0], str):
                        items.add(x[0])              # ["id", prob]
                    elif isinstance(x, dict):
                        walk(x)
                    elif isinstance(x, str):
                        items.add(x)
            elif isinstance(node, dict):
                if isinstance(node.get("item"), str):
                    items.add(node["item"])
                if isinstance(node.get("group"), str):
                    groups.add(node["group"])
                for key in ("entries", "items", "distribution", "collection"):
                    if key in node:
                        walk(node[key])

        for key in ("entries", "items", "distribution", "collection"):
            if key in g:
                walk(g[key])
        return items, groups

    def found_in(self, iid):
        """All loot/item groups this item appears in (direct + a couple levels up)."""
        groups = set(self.item_groups_of.get(iid, ()))
        frontier = set(groups)
        for _ in range(2):
            nxt = set()
            for g in frontier:
                nxt |= self.group_parents.get(g, set())
            nxt -= groups
            groups |= nxt
            frontier = nxt
            if not frontier:
                break
        # NPC-inventory groups (NC_*) are noisy; hidden unless enabled in Settings
        if not SETTINGS.get("npc_loot"):
            groups = [g for g in groups if not g.startswith("NC_")]
        return sorted(groups, key=str.lower)

    def raw_name(self, eid, _seen=None):
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
        return self.tr(self.raw_name(eid))

    def raw_desc(self, eid, _seen=None):
        """English description (cached), following copy-from inheritance."""
        if not isinstance(eid, str):
            return None
        if eid in self._desccache:
            return self._desccache[eid]
        seen = _seen or set()
        if eid in seen:
            return None
        seen.add(eid)
        e = self.by_id.get(eid)
        if not e:
            return None
        d = name_str(e.get("description"))
        if d is None and isinstance(e.get("copy-from"), str):
            d = self.raw_desc(e["copy-from"], seen)
        self._desccache[eid] = d
        return d

    def desc(self, eid):
        d = self.raw_desc(eid)
        return self.tr(d) if d else None

    def stats(self, eid):
        """A few headline item stats, inherited via copy-from. Raw strings."""
        out, seen = {}, set()
        cur = eid
        keys = ("weight", "volume", "material", "to_hit", "bashing", "cutting")
        while isinstance(cur, str) and cur not in seen:
            seen.add(cur)
            e = self.by_id.get(cur)
            if not e:
                break
            for k in keys:
                if k not in out and e.get(k) is not None:
                    out[k] = e[k]
            cur = e.get("copy-from")
        return out

    def _recipe_component_ids(self, recipe, _depth=0):
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
        rows = [(self.name(rid), rid) for rid in self.by_result]
        rows.sort(key=lambda x: x[0].lower())
        return rows


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


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------
def h(s):
    return html.escape(str(s))


def item_url(iid, ctx):
    p = {"id": iid, "ver": ctx["ver"], "lang": ctx["lang"]}
    if ctx["mods"]:
        p["mods"] = 1
    return "/item?" + urlencode(p)


def a_item(idx, iid, ctx, label=None):
    return '<a class="item" href="%s">%s</a>' % (
        item_url(iid, ctx), h(label if label is not None else idx.name(iid)))


def group_url(gid, ctx):
    p = {"group": gid, "ver": ctx["ver"], "lang": ctx["lang"]}
    if ctx["mods"]:
        p["mods"] = 1
    return "/group?" + urlencode(p)


def a_group(gid, ctx):
    return '<a class="chip" href="%s">%s</a>' % (group_url(gid, ctx), h(gid.replace("_", " ")))


def group_html(idx, group, ctx, depth=0):
    alts = []
    for entry in group:
        if not isinstance(entry, list) or not entry:
            continue
        iid = entry[0]
        cnt = entry[1] if len(entry) > 1 else 1
        is_list = len(entry) > 2 and entry[2] == "LIST"
        if is_list and iid in idx.reqs and depth < 2:
            subs = idx.reqs[iid].get("components", [])
            inner = " <span class=amp>&amp;</span> ".join(
                group_html(idx, g, ctx, depth + 1) for g in subs)
            alts.append('<span class="listreq">%s: %s</span>' % (h(idx.name(iid)), inner))
        else:
            tail = "" if is_list else ' <span class=qty>×%s</span>' % h(cnt)
            alts.append(a_item(idx, iid, ctx) + tail)
    if not alts:
        return "?"
    return ' <span class="or">OR</span> '.join(alts)


def _recipe_comps(idx, recipe):
    """A recipe's components with `using` requirements merged in."""
    comps = list(recipe.get("components") or [])
    for use in recipe.get("using") or []:
        if isinstance(use, list) and use and use[0] in idx.reqs:
            comps += idx.reqs[use[0]].get("components") or []
    return comps


def _vtree_node(idx, group, ctx, depth, seen, budget):
    """One ingredient group -> one <li> in the visual tree. The group's OR
    alternatives are shown inline (reusing group_html); the first craftable
    alternative is expanded as indented children, so you follow a real tree."""
    label = group_html(idx, group, ctx)
    follow = None
    for entry in group:
        if isinstance(entry, list) and entry:
            iid = entry[0]
            is_list = len(entry) > 2 and entry[2] == "LIST"
            if not is_list and iid in idx.by_result and iid not in seen:
                follow = iid
                break
    kids = ""
    if follow and depth > 0 and budget[0] > 0:
        budget[0] -= 1
        comps = _recipe_comps(idx, idx.by_result[follow][0])
        kids = "<ul class=\"vtree\">%s</ul>" % "".join(
            _vtree_node(idx, g, ctx, depth - 1, seen | {follow}, budget)
            for g in comps if isinstance(g, list))
    return "<li>%s%s</li>" % (label, kids)


def tree_block(idx, recipe, ctx):
    ids = idx._recipe_component_ids(recipe)
    if not any(i in idx.by_result for i in ids):
        return ""   # nothing craftable to expand
    budget = [200]
    body = "".join(_vtree_node(idx, g, ctx, 5, set(), budget)
                   for g in _recipe_comps(idx, recipe) if isinstance(g, list))
    return ('<details class="treebox" open><summary>🌳 %s</summary>'
            '<ul class="vtree root">%s</ul></details>' % (h(T(ctx, "tree")), body))


def recipe_html(idx, recipe, ctx, n=None):
    rows = []

    def field(label, value_html):
        rows.append('<div class="f"><span class="k">%s</span>'
                    '<span class="v">%s</span></div>' % (label, value_html))

    skill = recipe.get("skill_used")
    diff = recipe.get("difficulty")
    if skill or diff is not None:
        s = h(idx.name(skill)) if skill else "?"
        if diff is not None:
            s += ' <span class="diff">%s %s</span>' % (h(T(ctx, "difficulty")), h(diff))
        field(h(T(ctx, "skill")), s)
    req = recipe.get("skills_required")
    if req:
        pairs = req if (req and isinstance(req[0], list)) else [req]
        field(h(T(ctx, "also_needs")), ", ".join("%s&nbsp;%s" % (h(idx.name(p[0])), h(p[1]))
                                                  for p in pairs if isinstance(p, list)))
    if recipe.get("time"):
        field(h(T(ctx, "time")), h(recipe["time"]))

    learn = []
    al = recipe.get("autolearn")
    if al is True:
        learn.append(h(T(ctx, "autolearn")))
    elif isinstance(al, list):
        learn.append(h(T(ctx, "autolearn")) + " (" +
                     ", ".join("%s %s" % (h(p[0]), h(p[1])) for p in al) + ")")
    if learn:
        field(h(T(ctx, "learn")), "; ".join(learn))
    books = [b for b in (recipe.get("book_learn") or []) if isinstance(b, list) and b]
    if books:
        field(h(T(ctx, "books")), ", ".join(a_item(idx, b[0], ctx) for b in books))

    quals = list(recipe.get("qualities") or [])
    tools = list(recipe.get("tools") or [])
    for use in recipe.get("using") or []:
        if isinstance(use, list) and use and use[0] in idx.reqs:
            r = idx.reqs[use[0]]
            quals += r.get("qualities") or []
            tools += r.get("tools") or []

    if quals:
        qs = []
        for q in quals:
            if isinstance(q, dict):
                qs.append("%s&nbsp;%s" % (h(idx.tr(idx.quals.get(q.get("id"), q.get("id")))),
                                          h(q.get("level", 1))))
        if qs:
            field(h(T(ctx, "toolq")), ", ".join(qs))
    if tools:
        groups = []
        for group in tools:
            if not isinstance(group, list):
                continue
            opts = [e for e in group if isinstance(e, list) and e]
            if not opts:
                continue
            parts = []
            for e in opts:
                charges = e[1] if len(e) > 1 else -1
                t = a_item(idx, e[0], ctx)
                if isinstance(charges, int) and charges > 0:
                    t += ' <span class=qty>(%d)</span>' % charges
                parts.append(t)
            groups.append(' <span class="or">OR</span> '.join(parts))
        if groups:
            field(h(T(ctx, "tools")), ' <span class="semi">;</span> '.join(groups))

    comps = _recipe_comps(idx, recipe)
    ing = ""
    if comps:
        items = "".join("<li>%s</li>" % group_html(idx, g, ctx)
                        for g in comps if isinstance(g, list))
        ing = ('<div class="f"><span class="k">%s</span><span class="v">'
               '<ul class="ing">%s</ul></span></div>' % (h(T(ctx, "ingredients")), items))
    elif not tools and not quals:
        ing = '<div class="muted">%s</div>' % h(T(ctx, "no_ing"))

    title = h(T(ctx, "recipe")) + ("" if n is None else " #%d" % n)
    return ('<div class="recipe"><div class="rtitle">%s</div>%s%s%s</div>'
            % (title, "".join(rows), ing, tree_block(idx, recipe, ctx)))


PAGE_CSS = """
/* one palette, two themes — every colour is a variable so light AND dark
   stay consistent (the OS 'prefers-color-scheme' picks which) */
:root {
  color-scheme: light dark;
  --bg:#f4f5f7; --fg:#1c1f23; --panel:#ffffff; --panel2:#fff;
  --border:#e2e6ea; --border2:#cdd2d8; --muted:#6b7280; --faint:#8a929c;
  --link:#1558d6; --red:#d23a2e; --green:#2b8a3e;
  --pill-bg:#9aa3ad; --pill-fg:#ffffff; --hover:#e9edf2;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg:#16181d; --fg:#e6e8eb; --panel:#232730; --panel2:#2a2f3a;
    --border:#363b45; --border2:#3a4150; --muted:#9aa3ad; --faint:#7e8893;
    --link:#6ea8ff; --red:#ff8478; --green:#5cc777;
    --pill-bg:#4a515c; --pill-fg:#eef1f5; --hover:#2a2f3a;
  }
}
* { box-sizing: border-box; }
body { font-family: "Segoe UI", system-ui, sans-serif; margin: 0;
       background: var(--bg); color: var(--fg); }
header { position: sticky; top: 0; background: var(--panel);
         border-bottom: 1px solid var(--border);
         padding: 10px 16px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; z-index: 5; }
header .brand { font-weight: 700; margin-right: 6px; white-space: nowrap; }
header select, header input[type=search] { padding: 6px 8px; border: 1px solid var(--border2);
         border-radius: 7px; font-size: 14px; background: var(--panel2); color: var(--fg); }
header input[type=search] { min-width: 220px; flex: 1; }
header label { font-size: 13px; color: var(--muted); display: flex; align-items: center; gap: 4px; }
.wrap { max-width: 920px; margin: 18px auto; padding: 0 16px; }
h1.item { font-size: 22px; margin: 0 0 2px; }
.idtag { font: 12px ui-monospace, Consolas, monospace; color: var(--faint); }
.recipe { background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
          padding: 12px 14px; margin: 14px 0; }
.rtitle { font-weight: 700; color: var(--red); margin-bottom: 8px; }
.f { display: flex; gap: 8px; padding: 2px 0; }
.f .k { color: var(--muted); min-width: 110px; flex: none; font-size: 13px; padding-top:1px; }
.f .v { flex: 1; }
.diff { color: var(--faint); font-size:12px; } .semi{ color: var(--faint); } .amp{ color: var(--faint); }
.or { font-size: 11px; color: var(--pill-fg); background: var(--pill-bg); border-radius: 4px;
      padding: 0 5px; margin: 0 2px; vertical-align: 1px; }
.qty { color: var(--muted); } .listreq { color: inherit; }
a.item { color: var(--link); text-decoration: none; }
a.item:hover { text-decoration: underline; }
ul.ing { margin: 6px 0 0; padding-left: 20px; } ul.ing li { padding: 2px 0; }
.muted { color: var(--faint); }
.section { margin-top: 18px; font-weight: 600; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.chip { background: var(--panel); border: 1px solid var(--border2); border-radius: 999px;
        padding: 3px 11px; font-size: 13px; text-decoration: none; color: var(--link); }
.chip:hover { border-color: var(--link); }
.chip.loc { color: var(--muted); cursor: default; }
.chip.loc:hover { border-color: var(--border2); }
details.foundbox { margin-top: 0; }
details.foundbox > summary { cursor: pointer; list-style-position: inside; }
.results a { display: block; padding: 7px 10px; border-radius: 8px; color: inherit;
             text-decoration: none; }
.results a:hover { background: var(--hover); }
.results .rid { color: var(--faint); font: 11px ui-monospace, monospace; margin-left: 6px; }
.hint { color: var(--muted); margin-top: 24px; }
a.brand { text-decoration: none; color: inherit; }
a.gear { text-decoration: none; color: var(--muted); font-size: 18px; padding: 2px 6px; }
a.gear:hover { color: var(--fg); }
.desc { color: var(--muted); font-style: italic; margin: 6px 0 2px; }
.stats { color: var(--muted); font-size: 13px; margin: 2px 0 4px; }
details.treebox { margin-top: 10px; }
details.treebox > summary { cursor: pointer; color: var(--green); font-weight: 600; }
/* the real indented tree, with connector lines */
ul.vtree { list-style: none; margin: 4px 0 0; padding-left: 22px; }
ul.vtree.root { padding-left: 4px; margin-top: 6px; }
ul.vtree li { position: relative; padding: 1px 0 1px 16px; line-height: 1.55; }
ul.vtree li::before { content: ""; position: absolute; left: 0; top: 0;
        height: 100%; border-left: 1px solid var(--border2); }
ul.vtree li:last-child::before { height: 0.95em; }
ul.vtree li::after { content: ""; position: absolute; left: 0; top: 0.95em;
        width: 11px; border-top: 1px solid var(--border2); }
ul.vtree.root > li { padding-left: 0; }
ul.vtree.root > li::before, ul.vtree.root > li::after { display: none; }
/* category grid + listing table + settings */
.catgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 10px; margin-top: 14px; }
.catcard { display: block; text-decoration: none; color: inherit; background: var(--panel);
        border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
.catcard:hover { border-color: var(--link); }
.catcard b { font-size: 16px; } .catcard span { color: var(--muted); font-size: 13px; }
table.cat { border-collapse: collapse; width: 100%; margin-top: 12px; }
table.cat th, table.cat td { text-align: left; padding: 6px 10px; border-bottom: 1px solid var(--border); }
table.cat th { color: var(--muted); font-weight: 600; font-size: 13px; }
table.cat td.lv, table.cat th.lv { text-align: right; color: var(--muted); width: 4em; }
table.cat tr:hover td { background: var(--hover); }
.filters { display: flex; gap: 10px; align-items: center; margin-top: 10px; flex-wrap: wrap; }
.filters select, .filters input { padding: 5px 8px; border: 1px solid var(--border2);
        border-radius: 7px; background: var(--panel2); color: var(--fg); }
.setrow { display: flex; gap: 10px; align-items: flex-start; margin: 14px 0; }
.setrow .help { color: var(--muted); font-size: 13px; }
.saved { color: var(--green); margin-left: 8px; }
"""


def page(title, body, ctx, q=""):
    locs = locales_for(ctx["ver"])
    order = ["en", "ko", "ja"]
    codes = sorted(locs.keys(), key=lambda c: (order.index(c) if c in order else 99, c))
    vers = "".join('<option value="%d"%s>%s</option>'
                   % (i, " selected" if i == ctx["ver"] else "", h(inst["label"]))
                   for i, inst in enumerate(INSTALLS))
    langs = "".join('<option value="%s"%s>%s</option>'
                    % (c, " selected" if c == ctx["lang"] else "", h(LOCALE_NAMES.get(c, c)))
                    for c in codes)
    mods_chk = " checked" if ctx["mods"] else ""
    # settings form reloads the current page; search form goes to "/"
    if ctx.get("item_id"):
        action = "/item"
        hidden = '<input type=hidden name=id value="%s">' % h(ctx["item_id"])
    elif ctx.get("group_id"):
        action = "/group"
        hidden = '<input type=hidden name=group value="%s">' % h(ctx["group_id"])
    else:
        action, hidden = "/", ""
    header = """
<header>
  <a class="brand" href="/?ver=%(ver)d&lang=%(lang)s%(mods_q)s">🔧 %(brand)s</a>
  <form method="get" action="%(action)s" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0;">
    %(hidden)s
    <select name="ver" onchange="this.form.submit()">%(vers)s</select>
    <select name="lang" onchange="this.form.submit()">%(langs)s</select>
    <label><input type=checkbox name="mods" value="1"%(mods_chk)s onchange="this.form.submit()"> %(mods_label)s</label>
  </form>
  <form method="get" action="/" style="display:flex;flex:1;gap:8px;margin:0;">
    <input type=hidden name="ver" value="%(ver)d">
    <input type=hidden name="lang" value="%(lang)s">
    %(mods_hidden)s
    <input type=search name="q" value="%(q)s" placeholder="%(search_ph)s" autofocus>
  </form>
  <a class="gear" href="/settings?ver=%(ver)d&lang=%(lang)s%(mods_q)s" title="%(settings)s">⚙</a>
</header>""" % {
        "action": action, "hidden": hidden, "vers": vers, "langs": langs,
        "mods_chk": mods_chk, "ver": ctx["ver"], "lang": h(ctx["lang"]),
        "mods_q": "&mods=1" if ctx["mods"] else "",
        "mods_hidden": '<input type=hidden name="mods" value="1">' if ctx["mods"] else "",
        "brand": h(T(ctx, "brand")), "mods_label": h(T(ctx, "mods")),
        "search_ph": h(T(ctx, "search_ph")), "q": h(q), "settings": h(T(ctx, "settings"))}
    return ("<!doctype html><html><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>%s</title><style>%s</style></head><body>%s<div class='wrap'>%s</div></body></html>"
            % (h(title), PAGE_CSS, header, body))


def render_search(ctx, q):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    rows = idx.craftable()
    if not q.strip():
        body = '<p class="hint">%s</p>' % h(T(ctx, "hint", n=len(rows), r=len(idx.recipes)))
        return page(T(ctx, "brand"), body, ctx, q)
    ql = q.strip().lower()
    # cross-language: match the localized name, the English name, or the id
    rows = [(disp, rid) for disp, rid in rows
            if ql in disp.lower() or ql in idx.raw_name(rid).lower() or ql in rid.lower()]
    shown = rows[:500]
    lst = "".join('<a href="%s">%s<span class="rid">%s</span></a>'
                  % (item_url(rid, ctx), h(disp), h(rid)) for disp, rid in shown)
    more = ("<p class='muted'>%s</p>" % h(T(ctx, "more", n=len(rows) - len(shown)))
            if len(rows) > len(shown) else "")
    body = ('<div class="results">%s</div>%s'
            % (lst or "<p class='muted'>%s</p>" % h(T(ctx, "no_match")), more))
    return page("%s — CDDA Recipes" % q, body, ctx, q)


def _stats_html(idx, ctx, rid):
    st = idx.stats(rid)
    if not st:
        return ""
    bits = []
    if st.get("weight"):
        bits.append("%s %s" % (h(T(ctx, "weight")), h(st["weight"])))
    if st.get("volume"):
        bits.append("%s %s" % (h(T(ctx, "volume")), h(st["volume"])))
    mat = st.get("material")
    if mat:
        mats = mat if isinstance(mat, list) else [mat]
        names = [h(idx.name(m if isinstance(m, str) else m.get("type", "")))
                 for m in mats if m]
        if names:
            bits.append("%s %s" % (h(T(ctx, "material")), ", ".join(names)))
    dmg = st.get("bashing") or st.get("cutting")
    if dmg:
        bits.append("%s %s" % (h(T(ctx, "melee")), h(dmg)))
    if not bits:
        return ""
    return '<div class="stats">%s</div>' % "  ·  ".join(bits)


def render_item(ctx):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    rid = ctx["item_id"]
    title = idx.name(rid)
    parts = ['<h1 class="item">%s</h1><div class="idtag">%s</div>' % (h(title), h(rid))]
    desc = idx.desc(rid)
    if desc:
        parts.append('<div class="desc">%s</div>' % h(desc))
    parts.append(_stats_html(idx, ctx, rid))

    recipes = idx.by_result.get(rid, [])
    if recipes:
        for i, r in enumerate(recipes, 1):
            parts.append(recipe_html(idx, r, ctx, i if len(recipes) > 1 else None))
    else:
        parts.append('<div class="recipe muted">%s</div>' % h(T(ctx, "not_craftable")))

    # disassembly (uncraft)
    for un in idx.uncrafts.get(rid, []):
        comps = un.get("components") or []
        if not comps:
            continue
        items = "".join("<li>%s</li>" % group_html(idx, g, ctx)
                        for g in comps if isinstance(g, list))
        parts.append('<div class="recipe"><div class="rtitle">%s</div>'
                     '<ul class="ing">%s</ul></div>'
                     % (h(T(ctx, "disassembles")), items))

    # where it's found (loot/item groups) — clickable, like items; collapse if long
    locs = idx.found_in(rid)
    if locs:
        chips = "".join(a_group(g, ctx) for g in locs)
        hdr = "%s · %d" % (h(T(ctx, "found")), len(locs))
        if len(locs) > 30:
            parts.append('<details class="foundbox"><summary class="section">%s</summary>'
                         '<div class="chips">%s</div></details>' % (hdr, chips))
        else:
            parts.append('<div class="section">%s</div><div class="chips">%s</div>' % (hdr, chips))

    users = sorted(idx.used_in.get(rid, ()), key=lambda x: idx.name(x).lower())
    if users:
        chips = "".join('<a class="chip" href="%s">%s</a>' % (item_url(u, ctx), h(idx.name(u)))
                        for u in users)
        parts.append('<div class="section">%s</div><div class="chips">%s</div>'
                     % (h(T(ctx, "used_in", n=len(users))), chips))
    return page("%s — CDDA Recipes" % title, "".join(parts), ctx)


def render_group(ctx, gid):
    """A loot/item group shown like an item page: what it can spawn, the groups
    it includes, and the groups it's part of — all clickable."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    ctx["group_id"] = gid
    parts = ['<div class="idtag">%s</div><h1 class="item">%s</h1><div class="idtag">%s</div>'
             % (h(T(ctx, "group")), h(gid.replace("_", " ")), h(gid))]

    def section(key, chips_html, n):
        parts.append('<div class="section">%s</div><div class="chips">%s</div>'
                     % (h(T(ctx, key, n=n)), chips_html))

    items = sorted(idx.group_items.get(gid, ()), key=lambda x: idx.name(x).lower())
    if items:
        section("g_contains", "".join(
            '<a class="chip" href="%s">%s</a>' % (item_url(it, ctx), h(idx.name(it)))
            for it in items), len(items))
    subs = sorted(idx.group_subgroups.get(gid, ()))
    if subs:
        section("g_includes", "".join(a_group(s, ctx) for s in subs), len(subs))
    parents = sorted(idx.group_parents.get(gid, ()))
    if parents:
        section("g_partof", "".join(a_group(p, ctx) for p in parents), len(parents))
    return page("%s — CDDA Recipes" % gid, "".join(parts), ctx)


def render_landing(ctx):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    order = list(CAT_NAMES.keys())
    cats = sorted(idx.by_cat.keys(), key=lambda c: (order.index(c) if c in order else 99, c))
    cards = []
    for c in cats:
        cards.append('<a class="catcard" href="/?cat=%s&ver=%d&lang=%s%s">'
                     '<b>%s</b><br><span>%s</span></a>'
                     % (quote(c), ctx["ver"], h(ctx["lang"]), "&mods=1" if ctx["mods"] else "",
                        h(cat_name(c, ctx["lang"])), h(T(ctx, "items_n", n=len(idx.by_cat[c])))))
    body = ('<p class="hint">%s</p><div class="catgrid">%s</div>'
            % (h(T(ctx, "browse_hint")), "".join(cards)))
    return page(T(ctx, "brand"), body, ctx)


def _item_level(idx, rid):
    """Lowest crafting difficulty across this item's recipes, and the skill."""
    recs = idx.by_result.get(rid, [])
    diffs = [r.get("difficulty") for r in recs if isinstance(r.get("difficulty"), int)]
    lv = min(diffs) if diffs else 0
    skill = next((r.get("skill_used") for r in recs if r.get("skill_used")), None)
    return lv, skill


def render_category(ctx, cat, skill, maxlv):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    ids = idx.by_cat.get(cat, [])
    rows = []
    skills = set()
    for rid in ids:
        lv, sk = _item_level(idx, rid)
        if sk:
            skills.add(sk)
        rows.append((idx.name(rid), rid, lv, sk))
    if skill:
        rows = [r for r in rows if r[3] == skill]
    if maxlv is not None:
        rows = [r for r in rows if r[2] <= maxlv]
    rows.sort(key=lambda r: (r[2], r[0].lower()))

    skopts = '<option value="">%s</option>' % h(T(ctx, "all_skills"))
    for sk in sorted(skills, key=lambda s: idx.name(s).lower()):
        skopts += '<option value="%s"%s>%s</option>' % (
            h(sk), " selected" if sk == skill else "", h(idx.name(sk)))
    base = 'ver=%d&lang=%s%s' % (ctx["ver"], h(ctx["lang"]), "&mods=1" if ctx["mods"] else "")
    filters = (
        '<form class="filters" method="get" action="/">'
        '<input type=hidden name="cat" value="%s">'
        '<input type=hidden name="ver" value="%d"><input type=hidden name="lang" value="%s">%s'
        '<select name="skill" onchange="this.form.submit()">%s</select>'
        '<input type=number name="maxlv" min="0" placeholder="%s" value="%s" '
        'style="width:6em" onchange="this.form.submit()">'
        '</form>'
        % (h(cat), ctx["ver"], h(ctx["lang"]),
           '<input type=hidden name="mods" value="1">' if ctx["mods"] else "",
           skopts, h(T(ctx, "max_lv")), "" if maxlv is None else h(maxlv)))

    trs = "".join(
        '<tr><td><a class="item" href="%s">%s</a></td><td>%s</td><td class="lv">%s</td></tr>'
        % (item_url(rid, ctx), h(name), h(idx.name(sk)) if sk else "", lv)
        for name, rid, lv, sk in rows)
    table = ('<table class="cat"><tr><th>%s</th><th>%s</th><th class="lv">%s</th></tr>%s</table>'
             % (h(T(ctx, "item_col")), h(T(ctx, "skill")), h(T(ctx, "lv")), trs))
    head = ('<a class="item" href="/?%s">%s</a><h1 class="item">%s <span class="idtag">(%s)</span></h1>'
            % (base, h(T(ctx, "all_cats")), h(cat_name(cat, ctx["lang"])),
               h(T(ctx, "items_n", n=len(rows)))))
    return page("%s — CDDA Recipes" % cat_name(cat, ctx["lang"]), head + filters + table, ctx)


def render_settings(ctx, saved):
    npc = SETTINGS.get("npc_loot")
    saved_tag = ' <span class="saved">%s</span>' % h(T(ctx, "saved")) if saved else ""
    body = (
        '<h1 class="item">%s%s</h1>'
        '<form method="get" action="/settings">'
        '<input type=hidden name="save" value="1">'
        '<input type=hidden name="ver" value="%d"><input type=hidden name="lang" value="%s">%s'
        '<div class="setrow"><label><input type=checkbox name="npc_loot" value="1"%s '
        'onchange="this.form.submit()"> %s</label></div>'
        '<div class="help">%s</div>'
        '</form>'
        % (h(T(ctx, "settings")), saved_tag, ctx["ver"], h(ctx["lang"]),
           '<input type=hidden name="mods" value="1">' if ctx["mods"] else "",
           " checked" if npc else "", h(T(ctx, "npc_loot")), h(T(ctx, "npc_loot_help"))))
    return page("%s — CDDA Recipes" % T(ctx, "settings"), body, ctx)


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------
def parse_ctx(qs):
    def first(k, d=""):
        v = qs.get(k)
        return v[0] if v else d
    try:
        ver = int(first("ver", "0"))
    except ValueError:
        ver = 0
    ver = max(0, min(ver, len(INSTALLS) - 1))
    return {"ver": ver, "lang": first("lang", "en") or "en",
            "mods": first("mods", "") in ("1", "true", "on"),
            "item_id": first("id", "")}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, status=200):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        ctx = parse_ctx(qs)

        def first(k, d=""):
            v = qs.get(k)
            return v[0] if v else d

        try:
            if u.path == "/item" and ctx["item_id"]:
                self._send(render_item(ctx))
            elif u.path == "/group" and first("group"):
                self._send(render_group(ctx, first("group")))
            elif u.path == "/settings":
                saved = first("save") == "1"
                if saved:                       # checkbox absent => unchecked
                    SETTINGS["npc_loot"] = first("npc_loot") in ("1", "true", "on")
                self._send(render_settings(ctx, saved))
            elif first("cat"):
                maxlv = first("maxlv")
                maxlv = int(maxlv) if maxlv.isdigit() else None
                self._send(render_category(ctx, first("cat"), first("skill"), maxlv))
            elif first("q"):
                self._send(render_search(ctx, first("q")))
            else:
                self._send(render_landing(ctx))
        except Exception as e:
            self._send("<pre>error: %s</pre>" % h(e), 500)


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def main():
    global INSTALLS
    INSTALLS = find_installs()
    if not INSTALLS:
        print("No CDDA installs found under ~/Games/Cataclysm-DDA|BN.")
        print("Install a version with CDDA_Installer first.")
        return
    print("Indexing %s …" % INSTALLS[0]["label"].strip())
    get_index(0, False)          # preload default so the first page is instant
    port = _free_port()
    url = "http://127.0.0.1:%d/" % port
    httpd = HTTPServer(("127.0.0.1", port), Handler)
    threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    print("CDDA Recipe Helper running at %s" % url)
    print("To stop: close this window, or press Ctrl+C.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    print("stopped.")


if __name__ == "__main__":
    main()
