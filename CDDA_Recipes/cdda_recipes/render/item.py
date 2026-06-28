from ..state import get_index, get_translator
from ..i18n import T
from ..htmlutil import (h, a_skill, a_monster, a_group, item_url, pct_html,
                        _more_chips)
from ..assets import page
from .common import (_stats_html, _abilities_html, recipe_html, group_html,
                     _resolved, raw_fields_html, picture_html)

# item fields already surfaced by the curated sections above (everything else
# lands in the "all JSON fields" box so nothing is omitted)
_ITEM_SHOWN = {"weight", "volume", "material", "to_hit", "bashing", "cutting",
               "flags", "qualities", "techniques", "use_action", "category",
               "symbol", "color", "skill", "max_level", "required_level"}

# the game auto-assigns an item_category by type when none is set
_TYPE_CAT = {"GUN": "guns", "GUNMOD": "mods", "MAGAZINE": "magazines", "AMMO": "ammo",
             "TOOL": "tools", "TOOL_ARMOR": "clothing", "ARMOR": "clothing",
             "COMESTIBLE": "food", "BOOK": "books", "BIONIC_ITEM": "bionics",
             "PET_ARMOR": "clothing", "BATTERY": "tools", "ENGINE": "veh_parts",
             "WHEEL": "veh_parts", "CONTAINER": "container", "GENERIC": "other"}


def render_item(ctx):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    rid = ctx["item_id"]
    title = idx.name(rid)
    parts = ['<h1 class="item">%s</h1><div class="idtag">%s</div>' % (h(title), h(rid))]
    res = _resolved(idx, rid)
    cat = res.get("category") or _TYPE_CAT.get(res.get("type"))
    if cat:
        parts[-1] = parts[-1][:-len('</div>')] + (
            ' · <span class="cat">%s %s</span></div>' % (h(T(ctx, "category")), h(cat)))
    desc = idx.desc(rid)
    if desc:
        parts.append('<div class="desc">%s</div>' % h(desc))
    parts.append(picture_html(idx, ctx, rid))
    parts.append(_stats_html(idx, ctx, rid))
    parts.append(_abilities_html(idx, ctx, rid))

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

    # if this item is a book: the skill it trains + the recipes it teaches
    bi = idx.book_info(rid)
    if bi is not None:
        rows = []
        sk = bi.get("skill")
        if sk:
            lo = bi.get("required_level") or 0
            hi = bi.get("max_level")
            lvl = (" <span class=\"diff\">%s %s–%s</span>" % (h(T(ctx, "lv")), h(lo), h(hi))
                   if hi is not None else "")
            rows.append('<div class="f"><span class="k">%s</span>'
                        '<span class="v">%s%s</span></div>'
                        % (h(T(ctx, "book_skill")), a_skill(idx, sk, ctx), lvl))
        learn, seen = [], set()
        for resv, _lv in sorted(idx.book_recipes.get(rid, ()),
                                key=lambda x: idx.name(x[0]).lower()):
            if resv not in seen:
                seen.add(resv)
                learn.append('<a class="chip" href="%s">%s</a>'
                             % (item_url(resv, ctx), h(idx.name(resv))))
        if rows or learn:
            box = "".join(rows)
            if learn:
                box += ('<div class="section">%s</div><div class="chips">%s</div>'
                        % (h(T(ctx, "book_recipes", n=len(learn))), "".join(learn)))
            parts.append('<div class="recipe"><div class="rtitle">📖 %s</div>%s</div>'
                         % (h(T(ctx, "book")), box))

    # how to obtain it: disassembly source, loot locations (chance/avg), monster drops
    obtain = []

    df = sorted(idx.uncraft_from.get(rid, ()), key=lambda x: idx.name(x).lower())
    if df:
        chips = "".join('<a class="chip" href="%s">%s</a>' % (item_url(d, ctx), h(idx.name(d)))
                        for d in df)
        obtain.append('<div class="section">%s</div><div class="chips">%s</div>'
                      % (h(T(ctx, "disassemble_from", n=len(df))), chips))

    iloc = idx.item_loot_locations(rid)
    if iloc:
        rows = sorted(iloc.items(), key=lambda kv: -kv[1][0])
        chips = []
        for label, (p, ex) in rows:
            avg = ("%.2f" % ex) if ex < 10 else str(round(ex))
            chips.append('<span class="chip loc">%s <span class="locq">%s · %s %s</span></span>'
                         % (h(label), pct_html(p), h(T(ctx, "avg_label")), h(avg)))
        lead = ('<span class="muted" style="font-size:13px">%s</span> '
                % h(T(ctx, "very_common")) if len(rows) > 60 else "")
        obtain.append('<div class="section">%s</div>%s%s'
                      % (h(T(ctx, "loot_at", n=len(rows))), lead, _more_chips(chips, 24)))

    mons = sorted(idx.item_drop_monsters(rid), key=lambda x: idx.name(x).lower())
    if mons:
        chips = "".join(a_monster(idx, mid, ctx) for mid in mons)
        obtain.append('<div class="section">%s</div><div class="chips">%s</div>'
                      % (h(T(ctx, "dropped_by", n=len(mons))), chips))

    glist = idx.found_in(rid)
    if glist:
        chips = "".join(a_group(g, ctx) for g in glist)
        obtain.append('<details class="foundbox"><summary class="section">%s · %d</summary>'
                      '<div class="chips">%s</div></details>'
                      % (h(T(ctx, "found")), len(glist), chips))

    if obtain:
        parts.append('<div class="recipe"><div class="rtitle">📥 %s</div>%s</div>'
                     % (h(T(ctx, "obtain")), "".join(obtain)))

    users = sorted(idx.used_in.get(rid, ()), key=lambda x: idx.name(x).lower())
    if users:
        chips = "".join('<a class="chip" href="%s">%s</a>' % (item_url(u, ctx), h(idx.name(u)))
                        for u in users)
        parts.append('<div class="section">%s</div><div class="chips">%s</div>'
                     % (h(T(ctx, "used_in", n=len(users))), chips))

    parts.append(raw_fields_html(idx, ctx, rid, _ITEM_SHOWN))
    return page("%s — CDDA Recipes" % title, "".join(parts), ctx, nav="items")

