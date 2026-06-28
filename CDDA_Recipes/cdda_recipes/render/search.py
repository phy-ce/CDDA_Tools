import json

from ..state import get_index, get_translator
from ..i18n import T
from ..htmlutil import (h, item_url, group_url, skill_url, quality_url,
                        flag_url, monster_url, entity_url)
from ..config import BROWSE_TYPES
from ..assets import page

def _result_section(label, total, links, ctx):
    shown = links[:400]
    more = ("<p class='muted'>%s</p>" % h(T(ctx, "more", n=total - len(shown)))
            if total > len(shown) else "")
    return ('<div class="section">%s · %d</div><div class="results">%s</div>%s'
            % (h(label), total, "".join(shown), more))



def _rank(q, *cands):
    """0 = prefix match, 1 = word-start match, 2 = substring; None = no match."""
    best = None
    for c in cands:
        if not c:
            continue
        cl = c.lower()
        if cl.startswith(q):
            r = 0
        elif (" " + q) in cl:
            r = 1
        elif q in cl:
            r = 2
        else:
            continue
        if best is None or r < best:
            best = r
    return best



def search_categories(idx, ctx, q):
    """Ranked matches across every kind of page. Returns [(string-key, rows)]
    where rows = [(rank, label, href), ...]."""
    q = q.strip().lower()
    if not q:
        return []
    cats = []

    def add(key, rows):
        if rows:
            rows.sort(key=lambda t: (t[0], t[1].lower()))
            cats.append((key, rows))

    rows = [(r, lab, item_url(iid, ctx))
            for lab, iid in idx.item_pairs()
            for r in (_rank(q, lab, idx.raw_name(iid), iid),) if r is not None]
    add("nav_items", rows)

    rows = [(r, gid.replace("_", " "), group_url(gid, ctx))
            for gid in idx.group_def
            for r in (_rank(q, gid.replace("_", " "), gid),) if r is not None]
    add("nav_loot", rows)

    rows = [(r, lab, skill_url(sid, ctx))
            for lab, sid in idx.all_skills()
            for r in (_rank(q, lab, idx.raw_name(sid), sid),) if r is not None]
    add("skill_single", rows)

    rows = [(r, idx.tr(nm), quality_url(qid, ctx))
            for qid, nm in idx.quals.items()
            for r in (_rank(q, idx.tr(nm), nm, qid),) if r is not None]
    add("quality_single", rows)

    rows = [(r, f, flag_url(f, ctx))
            for f in idx.all_flags()
            for r in (_rank(q, f, idx.flag_desc(f) or ""),) if r is not None]
    add("flag_single", rows)

    rows = [(r, lab, monster_url(mid, ctx))
            for lab, mid in idx.all_monsters()
            for r in (_rank(q, lab, idx.raw_name(mid), mid),) if r is not None]
    add("monster_single", rows)

    for typ, nav_key, _icon, _route in BROWSE_TYPES:
        rows = [(r, idx.name(eid), entity_url(eid, ctx))
                for eid in idx.by_type.get(typ, [])
                for r in (_rank(q, idx.name(eid), idx.raw_name(eid), eid),) if r is not None]
        add(nav_key, rows)
    return cats



def render_search(ctx, q):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    if not q.strip():
        craft = idx.craftable()
        body = '<p class="hint">%s</p>' % h(T(ctx, "hint", n=len(craft), r=len(idx.recipes)))
        return page(T(ctx, "brand"), body, ctx, q, nav="items")
    sections = []
    for key, rows in search_categories(idx, ctx, q):
        links = ['<a href="%s">%s</a>' % (href, h(label)) for _, label, href in rows]
        sections.append(_result_section(T(ctx, key), len(rows), links, ctx))
    body = "".join(sections) or "<p class='muted'>%s</p>" % h(T(ctx, "no_match"))
    return page("%s — CDDA Recipes" % q, body, ctx, q, nav="items")



def suggest_json(ctx, q):
    """Flat top matches across all categories, for the search-box dropdown."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    flat = []
    for key, rows in search_categories(idx, ctx, q):
        kind = T(ctx, key)
        for r, label, href in rows[:8]:
            flat.append((r, label, href, kind))
    flat.sort(key=lambda t: (t[0], t[1].lower()))
    out = [{"label": label, "kind": kind, "url": href}
           for _, label, href, kind in flat[:10]]
    return json.dumps(out, ensure_ascii=False)

