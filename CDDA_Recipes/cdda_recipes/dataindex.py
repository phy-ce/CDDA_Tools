import os
import re
import json

from .config import ITEM_TYPES, SETTINGS, TYPE_CAT
from .installs import name_str
from .loot import group_loot, _chance_ic, _or_ic, _repeat_ic, _loc_base

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
        self.tool_recipes = {}   # tool item id -> set(recipe result id) using it as a tool
        self.quality_recipes = {}  # tool quality id -> set(recipe result id) requiring it
        self.uncrafts = {}       # item id -> [uncraft entry, ...]
        self.uncraft_from = {}   # yielded item id -> set(source item id) to disassemble
        self.book_recipes = {}   # book id -> [(recipe result, level), ...]
        self._loot_cache = {}    # group id -> flattened {item: (prob, expected)}
        self.skill_recipes = {}  # skill id -> [recipe result id, ...]
        # reverse item indexes, built together on first demand
        self._flag_items = {}    # flag -> set(item id)
        self._quality_items = {}  # tool quality id -> [(item id, level), ...]
        self._skill_books = {}   # skill id -> set(book item id)
        self._item_idx_built = False
        self._skill_ids = []     # all skill ids (for search), built lazily
        self._monster_ids = []   # all monster ids (for search), built lazily
        self._ent_built = False
        self.flag_info = {}      # flag id -> info text (json_flag)
        self.action_names = {}   # item_action id -> readable name
        self.ascii_art = {}      # ascii_art id -> picture (list of lines)
        self.by_type = {}        # json type -> [entity id, ...] (for browse)
        self.gfx_dir = ""        # install's gfx folder (set by get_index)
        self._tileset = None     # parsed active tileset (lazy)
        self._tileset_built = False
        self.item_ids = []       # ids whose type is a real item (for search)
        self.by_itemcat = {}     # item_category id -> [item id, ...] (lazy)
        self._itemcat_built = False
        self.item_groups_of = {}  # item id -> set(group id) it appears in (direct)
        self.group_parents = {}   # child group id -> set(parent group id)
        self.group_items = {}     # group id -> set(item id) it can spawn (direct)
        self.group_subgroups = {}  # group id -> set(child group id)
        self.group_def = {}      # group id -> raw def (kept for probabilities)
        self.group_dropped_by = {}  # group id -> set(monster id) (death_drops)
        self.group_places = {}   # group id -> {location: chance or None} (mapgen)
        self._groups = []        # raw item_group defs, processed after load
        self._monsters = []      # MONSTER defs with death_drops, processed after load
        self._mapgens = []       # mapgen defs, processed after load
        self._palettes = []      # palette defs, processed after load
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
            elif t == "json_flag" and isinstance(eid, str):
                if isinstance(e.get("info"), str):
                    self.flag_info[eid] = e["info"]
            elif t == "item_action" and isinstance(eid, str):
                nm = name_str(e.get("name"))
                if nm:
                    self.action_names[eid] = nm
            elif t == "ascii_art" and isinstance(eid, str):
                if isinstance(e.get("picture"), list):
                    self.ascii_art[eid] = e["picture"]
            elif t == "MONSTER" and e.get("death_drops") is not None:
                self._monsters.append(e)
            elif t == "mapgen":
                self._mapgens.append(e)
            elif t == "palette":
                self._palettes.append(e)
            if isinstance(eid, str):
                # real entities win id collisions over cosmetic ascii_art pictures
                cur = self.by_id.get(eid)
                if cur is None or (cur.get("type") == "ascii_art" and t != "ascii_art"):
                    self.by_id[eid] = e

    def _index_recipes(self):
        for r in self.recipes:
            res = r.get("result")
            if not isinstance(res, str):
                continue
            self.by_result.setdefault(res, []).append(r)
            for iid in self._recipe_component_ids(r):
                self.used_in.setdefault(iid, set()).add(res)
            tools, quals = self._recipe_tools_quals(r)
            for tid in self._tool_item_ids(tools):
                self.tool_recipes.setdefault(tid, set()).add(res)
            for qid in self._quality_ids(quals):
                self.quality_recipes.setdefault(qid, set()).add(res)
            sk = r.get("skill_used")
            if isinstance(sk, str):
                self.skill_recipes.setdefault(sk, []).append(res)
            self._index_book_learn(r, res)
        self.item_ids = [eid for eid, e in self.by_id.items()
                         if isinstance(e, dict) and e.get("type") in ITEM_TYPES]
        for eid, e in self.by_id.items():
            if isinstance(e, dict):
                self.by_type.setdefault(e.get("type"), []).append(eid)
        for src, entries in self.uncrafts.items():       # reverse: yield -> source
            for un in entries:
                for group in (un.get("components") or []):
                    if not isinstance(group, list):
                        continue
                    for e in group:
                        if isinstance(e, list) and e and isinstance(e[0], str):
                            self.uncraft_from.setdefault(e[0], set()).add(src)
        self._index_groups()

    def _index_book_learn(self, recipe, res):
        """Reverse a recipe's book_learn so each book lists the recipes it teaches."""
        def add(bid, lvl):
            if isinstance(bid, str):
                self.book_recipes.setdefault(bid, []).append((res, lvl))
        bl = recipe.get("book_learn")
        if isinstance(bl, list):
            for b in bl:
                if isinstance(b, list) and b:
                    add(b[0], b[1] if len(b) > 1 else None)
                elif isinstance(b, str):
                    add(b, None)
        elif isinstance(bl, dict):
            for bid, v in bl.items():
                add(bid, v.get("skill_level") if isinstance(v, dict) else None)

    def _index_groups(self):
        for g in self._groups:
            gid = g.get("id") or g.get("abstract")
            if not isinstance(gid, str):
                continue
            self.group_def[gid] = g
            items, subgroups = self._group_members(g)
            self.group_items.setdefault(gid, set()).update(items)
            self.group_subgroups.setdefault(gid, set()).update(subgroups)
            for it in items:
                self.item_groups_of.setdefault(it, set()).add(gid)
            for sg in subgroups:
                self.group_parents.setdefault(sg, set()).add(gid)
        self._groups = []
        self._index_sources()

    _REF_KEYS = ("item", "group", "item_group", "groups")

    def _group_refs(self, node, out=None):
        """(gid, chance, repeat) for every known item-group id referenced under a
        reference key anywhere inside node. `chance`/`repeat` come from the dict
        directly holding the ref. A ref-key string that isn't a known group
        (e.g. a plain item id) is ignored."""
        if out is None:
            out = []
        if isinstance(node, dict):
            ch = node.get("chance")
            rp = node.get("repeat")
            for k, v in node.items():
                if k in self._REF_KEYS:
                    for x in (v if isinstance(v, list) else [v]):
                        if isinstance(x, str) and x in self.group_def:
                            out.append((x, ch, rp))
                        elif isinstance(x, (dict, list)):
                            self._group_refs(x, out)
                elif isinstance(v, (dict, list)):
                    self._group_refs(v, out)
        elif isinstance(node, list):
            for x in node:
                self._group_refs(x, out)
        return out

    def _index_sources(self):
        """Reverse index: which monsters drop a group on death, and which map
        locations place it — each location with a placement ItemChance
        (prob, expected) from the mapgen chance + repeat, spots combined."""
        def locs_of(mg):
            # only real overmap places; nested-mapgen chunks have no location and
            # would show as cryptic ids (e.g. 4x4_cr1), so they're left out
            labels = []

            def flat(x):
                if isinstance(x, str):
                    labels.append(x)
                elif isinstance(x, list):
                    for y in x:
                        flat(y)
            flat(mg.get("om_terrain"))
            return labels

        for mon in self._monsters:
            mid = mon.get("id")
            if not isinstance(mid, str):
                continue
            dd = mon.get("death_drops")
            if isinstance(dd, str):                      # direct group reference
                refs = [(dd, None, None)] if dd in self.group_def else []
            else:                                        # inline group object
                refs = self._group_refs(dd)
            for gid, _ch, _rp in refs:
                self.group_dropped_by.setdefault(gid, set()).add(mid)

        # palette id -> set(locations) of the mapgens that pull it in
        pal_locs = {}
        for mg in self._mapgens:
            obj = mg.get("object") or {}
            for p in (obj.get("palettes") or []):
                if isinstance(p, str):
                    pal_locs.setdefault(p, set()).update(locs_of(mg))

        def add_place(gid, loc, chance, repeat):
            if not loc:
                return
            ic = _repeat_ic(_chance_ic(chance if chance is not None else 100), repeat)
            d = self.group_places.setdefault(gid, {})
            d[loc] = ic if loc not in d else _or_ic(d[loc], ic)

        for mg in self._mapgens:
            labels = locs_of(mg)
            for gid, ch, rp in self._group_refs(mg.get("object")):
                for loc in labels:
                    add_place(gid, loc, ch, rp)

        for pal in self._palettes:
            pid = pal.get("id")
            refs = self._group_refs(pal)
            if not refs:
                continue
            targets = pal_locs.get(pid)
            if targets:                       # only attribute to real places
                for gid, ch, rp in refs:
                    for loc in targets:
                        add_place(gid, loc, ch, rp)

        self._monsters = []
        self._mapgens = []
        self._palettes = []

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

    def groups_with_item(self, iid):
        """Every group that can yield the item, directly or through any depth of
        nesting (the transitive set of ancestors)."""
        seen = set(self.item_groups_of.get(iid, ()))
        frontier = set(seen)
        while frontier:
            nxt = set()
            for g in frontier:
                nxt |= self.group_parents.get(g, set())
            nxt -= seen
            seen |= nxt
            frontier = nxt
        return seen

    def loot_of(self, gid):
        """Flattened {item: (prob, expected)} for a named group, memoized."""
        lc = self._loot_cache.get(gid)
        if lc is None:
            d = self.group_def.get(gid)
            lc = group_loot(self, d) if d else {}
            self._loot_cache[gid] = lc
        return lc

    def item_loot_locations(self, iid):
        """place label -> (prob, expected) of finding the item there, combining
        the item's chance inside each placed group with that group's placement."""
        agg = {}
        for g in self.groups_with_item(iid):
            places = self.group_places.get(g)
            if not places:
                continue
            item_ic = self.loot_of(g).get(iid)
            if not item_ic:
                continue
            for loc, pl in places.items():
                label = self.loc_name(loc) or _loc_base(loc)
                combo = (pl[0] * item_ic[0], pl[1] * item_ic[1])
                cur = agg.get(label)
                if cur is None or combo[0] > cur[0]:   # max across variants
                    agg[label] = combo
        return agg

    def item_drop_monsters(self, iid):
        """Monsters that can drop the item via a death-drop group."""
        mons = set()
        for g in self.groups_with_item(iid):
            if g in self.group_dropped_by and iid in self.loot_of(g):
                mons |= self.group_dropped_by[g]
        return mons

    def loc_name(self, loc):
        """Readable, localized place name for an om_terrain/city_building id, or
        None if it has no name (caller falls back to a cleaned id)."""
        e = self.by_id.get(loc)
        if e:
            nm = name_str(e.get("name"))
            if nm:
                return self.tr(nm)
        return None

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

    def _recipe_tools_quals(self, recipe, _depth=0):
        """A recipe's tool groups and quality requirements, with `using`
        requirements expanded (tools/qualities can be hidden behind a
        requirement reference such as `forging_standard`)."""
        tools = list(recipe.get("tools") or [])
        quals = list(recipe.get("qualities") or [])
        for use in recipe.get("using") or []:
            if isinstance(use, list) and use and use[0] in self.reqs and _depth < 3:
                t2, q2 = self._recipe_tools_quals(self.reqs[use[0]], _depth + 1)
                tools += t2
                quals += q2
        return tools, quals

    @staticmethod
    def _tool_item_ids(tools):
        """Item ids referenced as tools (each group is a list of [id, charges]
        OR-alternatives, or bare id strings)."""
        ids = set()
        for group in tools:
            if not isinstance(group, list):
                continue
            for e in group:
                if isinstance(e, list) and e and isinstance(e[0], str):
                    ids.add(e[0])
                elif isinstance(e, str):
                    ids.add(e)
        return ids

    @staticmethod
    def _quality_ids(quals):
        """Quality ids required (dict `{"id":..,"level":..}` or list `["id",lv]`)."""
        ids = set()
        for q in quals:
            if isinstance(q, dict) and isinstance(q.get("id"), str):
                ids.add(q["id"])
            elif isinstance(q, list) and q and isinstance(q[0], str):
                ids.add(q[0])
        return ids

    def recipes_using_tool(self, iid):
        """Recipe results that need this item to craft: directly as a tool, or
        through any tool quality the item provides (e.g. a forge required as a
        tool, an anvil required via its ANVIL quality)."""
        out = set(self.tool_recipes.get(iid, ()))
        for q, _lv in self.qualities_of(iid):
            out |= self.quality_recipes.get(q, set())
        return out

    def recipes_requiring_quality(self, qid):
        """Recipe results that require this tool quality."""
        return self.quality_recipes.get(qid, set())

    def craftable(self):
        rows = [(self.name(rid), rid) for rid in self.by_result]
        rows.sort(key=lambda x: x[0].lower())
        return rows

    def all_items(self):
        rows = [(self.name(i), i) for i in self.item_ids]
        rows.sort(key=lambda x: x[0].lower())
        return rows

    def item_pairs(self):           # unsorted (name, id), for search
        return [(self.name(i), i) for i in self.item_ids]

    def item_category(self, iid):
        """An item's in-game item_category id: its explicit `category` (inherited
        via copy-from), else the engine default for its type."""
        for e in self._chain(iid):
            c = e.get("category")
            if isinstance(c, str):
                return c
        e = self.by_id.get(iid) or {}
        return TYPE_CAT.get(e.get("type"), "other")

    def item_categories(self):
        """Lazy {item_category id -> [item id, ...]} over every real item."""
        if not self._itemcat_built:
            for iid in self.item_ids:
                self.by_itemcat.setdefault(self.item_category(iid), []).append(iid)
            self._itemcat_built = True
        return self.by_itemcat

    def _build_entities(self):
        if self._ent_built:
            return
        for eid, e in self.by_id.items():
            if not isinstance(e, dict):
                continue
            t = e.get("type")
            if t == "skill":
                self._skill_ids.append(eid)
            elif t == "MONSTER":
                self._monster_ids.append(eid)
        self._ent_built = True

    def all_skills(self):
        self._build_entities()
        return [(self.name(s), s) for s in self._skill_ids]

    def all_monsters(self):
        self._build_entities()
        return [(self.name(m), m) for m in self._monster_ids]

    def all_flags(self):
        self._build_item_indexes()
        return sorted(set(self._flag_items) | set(self.flag_info))

    def book_info(self, rid):
        """If rid (following copy-from) is a BOOK, the skill it trains and the
        level range; else None. Novels etc. return {} (a book, but no skill)."""
        seen, info, is_book = set(), {}, False
        cur = rid
        while isinstance(cur, str) and cur not in seen:
            seen.add(cur)
            e = self.by_id.get(cur)
            if not e:
                break
            if e.get("type") == "BOOK":
                is_book = True
            for k in ("skill", "max_level", "required_level"):
                if k not in info and e.get(k) is not None:
                    info[k] = e[k]
            cur = e.get("copy-from")
        return info if is_book else None

    def _chain(self, rid):
        """The item def + its copy-from ancestors, most-derived first."""
        out, seen, cur = [], set(), rid
        while isinstance(cur, str) and cur not in seen:
            seen.add(cur)
            e = self.by_id.get(cur)
            if not e:
                break
            out.append(e)
            cur = e.get("copy-from")
        return out

    def flags_of(self, rid):
        """Flags on an item, merging copy-from + extend, minus delete."""
        flags = set()
        for e in reversed(self._chain(rid)):   # parents first so child can delete
            for f in (e.get("flags") or []):
                if isinstance(f, str):
                    flags.add(f)
            ext = e.get("extend")
            if isinstance(ext, dict):
                for f in (ext.get("flags") or []):
                    if isinstance(f, str):
                        flags.add(f)
            dl = e.get("delete")
            if isinstance(dl, dict):
                for f in (dl.get("flags") or []):
                    flags.discard(f)
        return flags

    _ARMOR_TYPES = ("ARMOR", "TOOL_ARMOR", "PET_ARMOR")

    @staticmethod
    def _mat_ids(val):
        """Material ids from an item's `material` (string, list of strings, or
        list of `{type, portion}` dicts)."""
        out = []
        for m in (val if isinstance(val, list) else [val]):
            if isinstance(m, str):
                out.append(m)
            elif isinstance(m, dict) and isinstance(m.get("type"), str):
                out.append(m["type"])
        return out

    def _mat_resist(self, mat_id, key):
        e = self.by_id.get(mat_id)
        if isinstance(e, dict) and e.get("type") == "material":
            v = e.get(key)
            return float(v) if isinstance(v, (int, float)) else 0.0
        return 0.0

    def armor_protection(self, iid):
        """Derived armor resistances for an item, following the BN engine
        formula (item.cpp `phys_resist` / `acid_resist` / `fire_resist`, build
        sha 426991f): average of each material's *_resist × thickness; stab =
        0.8·cut; acid/fire scaled by env/10 when env<10. Computed for an
        undamaged item with no clothing mods. Returns a dict of the resist
        values (plus env/thickness) or None when the item is not armor.

        See CDDA_Recipes/docs/combat-formulas.md."""
        merged = {}
        for e in reversed(self._chain(iid)):
            if isinstance(e, dict):
                merged.update(e)
        if merged.get("type") not in self._ARMOR_TYPES:
            return None
        mats = self._mat_ids(merged.get("material"))
        thick = merged.get("material_thickness")
        thick = float(thick) if isinstance(thick, (int, float)) else 0.0
        env = merged.get("environmental_protection") or 0
        env = float(env) if isinstance(env, (int, float)) else 0.0

        def avg(key):
            return (sum(self._mat_resist(m, key) for m in mats) / len(mats)) if mats else 0.0

        bash = round(avg("bash_resist") * thick)
        cut = round(avg("cut_resist") * thick)
        bullet = round(avg("bullet_resist") * thick)
        env_scale = 1.0 if env >= 10 else env / 10.0
        acid = round(avg("acid_resist") * env_scale)
        fire = round(avg("fire_resist") * env_scale)
        return {"bash": bash, "cut": cut, "stab": int(0.8 * cut), "bullet": bullet,
                "acid": acid, "fire": fire, "env": int(env), "thickness": thick}

    def qualities_of(self, rid):
        for e in self._chain(rid):
            q = e.get("qualities")
            if q:
                return [(it[0], it[1] if len(it) > 1 else 1)
                        for it in q if isinstance(it, list) and it]
        return []

    def techniques_of(self, rid):
        for e in self._chain(rid):
            t = e.get("techniques")
            if t:
                return [x for x in t if isinstance(x, str)]
        return []

    def actions_of(self, rid):
        """Readable labels for an item's use_action(s)."""
        for e in self._chain(rid):
            ua = e.get("use_action")
            if ua is not None:
                out, seen = [], set()
                for x in (ua if isinstance(ua, list) else [ua]):
                    lbl = None
                    if isinstance(x, str):
                        lbl = self.action_names.get(x) or x.replace("_", " ").lower()
                    elif isinstance(x, dict):
                        lbl = (name_str(x.get("name")) or name_str(x.get("menu_text"))
                               or (x.get("type") or "").replace("_", " "))
                    if lbl:
                        lbl = self.tr(lbl)
                        if lbl not in seen:
                            seen.add(lbl)
                            out.append(lbl)
                return out
        return []

    def flag_desc(self, flag):
        info = self.flag_info.get(flag)
        if not info:
            return None
        return self.tr(re.sub(r"<[^>]+>", "", info)).strip()

    def tileset(self):
        if not self._tileset_built:
            self._tileset_built = True
            from . import tiles
            self._tileset = tiles.build_tileset(self.gfx_dir)
        return self._tileset

    def tile_of(self, eid):
        """(file_rel, x, y, w, h) sprite for an id in the active tileset, or None."""
        ts = self.tileset()
        if not ts:
            return None
        s = ts["id2s"].get(eid)
        if s is None:
            return None
        from . import tiles
        return tiles.sprite_pos(ts, s)

    def _build_item_indexes(self):
        """One pass over items to build reverse flag / quality / book-skill maps."""
        if self._item_idx_built:
            return
        for iid in self.item_ids:
            for f in self.flags_of(iid):
                self._flag_items.setdefault(f, set()).add(iid)
            for q, lv in self.qualities_of(iid):
                self._quality_items.setdefault(q, []).append((iid, lv))
            bi = self.book_info(iid)
            if bi and bi.get("skill"):
                self._skill_books.setdefault(bi["skill"], set()).add(iid)
        self._item_idx_built = True

    def items_with_flag(self, flag):
        self._build_item_indexes()
        return self._flag_items.get(flag, set())

    def items_with_quality(self, qid):
        self._build_item_indexes()
        return self._quality_items.get(qid, [])

    def books_for_skill(self, skill):
        self._build_item_indexes()
        return self._skill_books.get(skill, set())

