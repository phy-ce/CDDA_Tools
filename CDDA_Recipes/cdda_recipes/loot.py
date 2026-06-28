def _subtype_and_raw(node):
    """(subtype, raw-entry-list) for either a group def or an inline
    distribution/collection node."""
    if isinstance(node.get("distribution"), list):
        return "distribution", node["distribution"]
    if isinstance(node.get("collection"), list):
        return "collection", node["collection"]
    st = node.get("subtype")
    if st not in ("collection", "distribution"):
        st = "collection"          # default / legacy "old" behaves like a collection
    raw = node.get("entries")
    if raw is None:
        raw = node.get("items")
    return st, (raw if isinstance(raw, list) else [])



def _norm_entries(raw, subtype):
    """Normalize an entry list and attach each entry's spawn 'frac' per the
    parent subtype. An inline distribution/collection keeps its child list in
    'inline' = (subtype, raw) so the caller can recurse and expand it."""
    out = []
    if not isinstance(raw, list):
        return out
    for e in raw:
        if isinstance(e, list) and e and isinstance(e[0], str):
            prob = e[1] if len(e) > 1 and isinstance(e[1], (int, float)) else 100
            out.append({"kind": "item", "id": e[0], "prob": prob, "count": None, "inline": None})
        elif isinstance(e, dict):
            prob = e.get("prob", 100)
            if not isinstance(prob, (int, float)):
                prob = 100
            if isinstance(e.get("item"), str):
                out.append({"kind": "item", "id": e["item"], "prob": prob,
                            "count": e.get("count") or e.get("charges"), "inline": None})
            elif isinstance(e.get("group"), str):
                out.append({"kind": "group", "id": e["group"], "prob": prob,
                            "count": None, "inline": None})
            elif isinstance(e.get("distribution"), list):
                out.append({"kind": "inline", "id": None, "prob": prob, "count": None,
                            "inline": ("distribution", e["distribution"])})
            elif isinstance(e.get("collection"), list):
                out.append({"kind": "inline", "id": None, "prob": prob, "count": None,
                            "inline": ("collection", e["collection"])})
    if subtype == "distribution":
        total = sum(max(0, x["prob"]) for x in out) or 1
        for x in out:
            x["frac"] = max(0, x["prob"]) / total
    else:
        for x in out:
            x["frac"] = min(max(x["prob"], 0), 100) / 100.0
    return out



_LOC_DROP = {"basement", "roof", "first", "second", "third", "ground", "upper",
             "lower", "north", "south", "east", "west", "ne", "nw", "se", "sw",
             "open", "closed", "interior", "entrance"}



def _loc_base(loc):
    """Collapse a mapgen om_terrain id to its base place: drop variant tokens
    (numbers, single letters, floor/direction qualifiers) so house_20 /
    house_24_roof -> 'house'."""
    loc = loc.replace("palette:", "")
    toks = [t for t in loc.split("_")
            if t and not t.isdigit() and len(t) > 1 and t.lower() not in _LOC_DROP]
    return " ".join(toks) if toks else loc.replace("_", " ")



# ---------------------------------------------------------------------------
# Loot probability engine.  Each item carries (prob, expected):
#   prob     = probability of getting >= 1   (a "chance"; capped at 1.0)
#   expected = expected count (the average; uncapped, so a >100% chance reads as
#              "more than one expected", not "more than certain")
# Derived from CDDA's own item_group rules (collection = independent rolls,
# distribution = weighted pick-one).
# ---------------------------------------------------------------------------
def _avg_count(c):
    if isinstance(c, list) and len(c) == 2:
        try:
            return (float(c[0]) + float(c[1])) / 2.0
        except (TypeError, ValueError):
            return 1.0
    if isinstance(c, (int, float)):
        return float(c)
    return 1.0



def _chance_ic(chance):
    p = chance / 100.0
    return (min(1.0, p), p)



def _or_ic(a, b):       # two independent rolls (collection)
    return (1.0 - (1.0 - a[0]) * (1.0 - b[0]), a[1] + b[1])



def _add_ic(a, b):      # mutually exclusive options (distribution)
    return (min(1.0, a[0] + b[0]), a[1] + b[1])



def _normalize_repeat(r):
    if isinstance(r, (int, float)):
        return (int(r), int(r))
    if isinstance(r, list) and r:
        a = r[0]
        b = r[1] if len(r) > 1 else r[0]
        return (int(a), int(b)) if a <= b else (int(b), int(a))
    return (1, 1)



def _repeat_ic(ic, repeat):
    """A placement tried `repeat` (range) times: prob = avg(1-(1-p)^r),
    expected scales by the average repeat count."""
    n0, n1 = _normalize_repeat(repeat)
    if n0 <= 1 and n1 <= 1:
        return ic
    p, ex = ic
    total, cnt = 0.0, 0
    for r in range(max(0, n0), n1 + 1):
        total += 1.0 - (1.0 - p) ** r
        cnt += 1
    prob = total / cnt if cnt else p
    return (min(1.0, prob), ex * (n0 + n1) / 2.0)



def _entry_loot(idx, e, parent_st, seen, depth):
    cnt = _avg_count(e.get("count"))
    if e["kind"] == "item":
        base = _chance_ic(e["prob"]) if parent_st == "collection" else (1.0, 1.0)
        return {e["id"]: (base[0], base[1] * cnt)}
    if e["kind"] == "group":
        gid = e["id"]
        if gid in seen:
            return {}
        d = idx.group_def.get(gid)
        if not d:
            return {}
        sub = group_loot(idx, d, seen | {gid}, depth + 1)
    else:                                   # inline distribution/collection
        st2, raw2 = e["inline"]
        sub = group_loot(idx, {"subtype": st2, "entries": raw2}, seen, depth + 1)
    if parent_st == "collection":           # the sub-group fires with prob%
        m = e["prob"] / 100.0
        sub = {k: (min(1.0, p * m), ex * m) for k, (p, ex) in sub.items()}
    return sub



def group_loot(idx, g, seen=None, depth=0):
    """Flatten an item_group to {item_id: (prob, expected)} over its whole tree."""
    seen = set() if seen is None else seen
    if depth > 12:
        return {}
    st, raw = _subtype_and_raw(g)
    entries = _norm_entries(raw, st)
    loot = {}
    if st == "distribution":
        total = sum(max(0, e["prob"]) for e in entries) or 1
        for e in entries:
            t = max(0, e["prob"]) / total
            for iid, ic in _entry_loot(idx, e, st, seen, depth).items():
                sc = (min(1.0, ic[0] * t), ic[1] * t)
                loot[iid] = sc if iid not in loot else _add_ic(loot[iid], sc)
    else:                                   # collection
        for e in entries:
            for iid, ic in _entry_loot(idx, e, st, seen, depth).items():
                loot[iid] = ic if iid not in loot else _or_ic(loot[iid], ic)
    return loot

