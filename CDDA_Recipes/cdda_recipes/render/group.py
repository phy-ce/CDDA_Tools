from ..state import get_index, get_translator
from ..i18n import T
from ..loot import _subtype_and_raw, _norm_entries, group_loot, _loc_base
from ..htmlutil import (h, entries_html, pct_html, a_item, a_group, a_monster,
                        item_url, _more_list, _more_chips)
from ..assets import page

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

    g = idx.group_def.get(gid)
    if g is not None:
        st, raw = _subtype_and_raw(g)
        note = T(ctx, "g_note_coll" if st == "collection" else "g_note_dist")
        qsuf = "ver=%d&lang=%s%s" % (ctx["ver"], h(ctx["lang"]),
                                     "&mods=1" if ctx["mods"] else "")
        parts.append('<div class="mechnote">%s &nbsp;<a href="/mechanics?%s">%s</a></div>'
                     % (h(note), qsuf, h(T(ctx, "learn_more"))))
        rows = entries_html(idx, ctx, raw, st)
        if rows:
            n = len(_norm_entries(raw, st))
            parts.append('<details class="treebox"><summary class="section">%s</summary>'
                         '<ul class="problist">%s</ul></details>'
                         % (h(T(ctx, "g_contents", n=n)), rows))
        # flattened: what you actually get, per final item (chance + avg count)
        loot = group_loot(idx, g)
        if loot:
            top = sorted(loot.items(), key=lambda kv: (-kv[1][1], -kv[1][0]))
            lis = []
            for iid, (p, ex) in top:
                avg = ("%.2f" % ex) if ex < 10 else str(round(ex))
                lis.append('<li><span class="prob">%s</span><div class="ent">%s'
                           ' <span class="locq">%s %s</span></div></li>'
                           % (pct_html(p), a_item(idx, iid, ctx),
                              h(T(ctx, "avg_label")), h(avg)))
            parts.append('<div class="section">%s</div>%s'
                         % (h(T(ctx, "expected_yield", n=len(loot))), _more_list(lis)))
    else:
        # fallback: older set-based view (no raw def captured)
        items = sorted(idx.group_items.get(gid, ()), key=lambda x: idx.name(x).lower())
        if items:
            section("g_contains", "".join(
                '<a class="chip" href="%s">%s</a>' % (item_url(it, ctx), h(idx.name(it)))
                for it in items), len(items))
        subs = sorted(idx.group_subgroups.get(gid, ()))
        if subs:
            section("g_includes", "".join(a_group(s, ctx) for s in subs), len(subs))

    # where/when it triggers: monster death drops + map placements
    drops = sorted(idx.group_dropped_by.get(gid, ()), key=lambda x: idx.name(x).lower())
    if drops:
        section("dropped_by", "".join(a_monster(idx, d, ctx) for d in drops), len(drops))
    places = idx.group_places.get(gid) or {}
    if places:
        # resolve each location to its readable place name (variants like
        # house_20 / house_24 share a name and collapse), keeping the best chance
        agg = {}
        for loc, ic in places.items():
            label = idx.loc_name(loc) or _loc_base(loc)
            cur = agg.get(label)
            if cur is None or ic[0] > cur[0]:
                agg[label] = ic

        def loc_chip(name, ic):
            return ('<span class="chip loc">%s <span class="locq">%s</span></span>'
                    % (h(name), pct_html(ic[0])))
        # most-likely places first, then alphabetical
        rows = sorted(agg.items(), key=lambda kv: (-kv[1][0], kv[0].lower()))
        chiplist = [loc_chip(l, c) for l, c in rows]
        # ubiquitous groups (trash, etc.): lead with a plain-language summary
        lead = ('<span class="muted" style="font-size:13px">%s</span> '
                % h(T(ctx, "very_common")) if len(rows) > 60 else "")
        parts.append('<div class="section">%s</div>%s%s'
                     % (h(T(ctx, "placed_in", n=len(rows))), lead, _more_chips(chiplist, 24)))

    parents = sorted(idx.group_parents.get(gid, ()))
    if parents:
        section("g_partof", "".join(a_group(p, ctx) for p in parents), len(parents))
    return page("%s — CDDA Recipes" % gid, "".join(parts), ctx, nav="loot")

