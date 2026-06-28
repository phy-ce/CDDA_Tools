from urllib.parse import quote

from ..state import get_index, get_translator
from ..config import SETTINGS
from ..i18n import T, CAT_NAMES, cat_name, MECH_DOC
from ..htmlutil import (h, a_group, a_item, item_url, pct_html,
                        _more_chips, _more_list)
from ..assets import page
from .common import _item_level

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
    return page(T(ctx, "brand"), body, ctx, nav="items")



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
    return page("%s — CDDA Recipes" % cat_name(cat, ctx["lang"]),
                head + filters + table, ctx, nav="items")



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
    return page("%s — CDDA Recipes" % T(ctx, "settings"), body, ctx, nav="settings")



def render_loot(ctx):
    """Browse loot from the top: root groups (not nested under any other group)
    are the entry points mapgen actually places. Click to drill down."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    roots = [gid for gid in idx.group_def if not idx.group_parents.get(gid)]
    if not SETTINGS.get("npc_loot"):
        roots = [g for g in roots if not g.startswith("NC_")]
    roots.sort(key=str.lower)
    chips = "".join(a_group(g, ctx) for g in roots)
    body = ('<h1 class="item">%s</h1><p class="hint">%s</p><div class="chips">%s</div>'
            % (h(T(ctx, "loot_title")), h(T(ctx, "loot_hint", n=len(roots))), chips))
    return page(T(ctx, "loot_title"), body, ctx, nav="loot")



def render_mechanics(ctx):
    doc = MECH_DOC.get(ctx["lang"]) or MECH_DOC["en"]
    secs = "".join("<h2>%s</h2>%s" % (h(head), body) for head, body in doc)
    body = ('<h1 class="item">%s</h1><div class="mech">%s</div>'
            % (h(T(ctx, "mech_title")), secs))
    return page(T(ctx, "mech_title"), body, ctx, nav="mechanics")



def render_flag(ctx, flag):
    """A flag's own page: its description and every item that carries it."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    parts = ['<div class="idtag">%s</div><h1 class="item">%s</h1>'
             % (h(T(ctx, "flag_single")), h(flag))]
    desc = idx.flag_desc(flag)
    if desc:
        parts.append('<div class="desc">%s</div>' % h(desc))
    items = sorted(idx.items_with_flag(flag), key=lambda x: idx.name(x).lower())
    if items:
        chips = ['<a class="chip" href="%s">%s</a>' % (item_url(i, ctx), h(idx.name(i)))
                 for i in items]
        parts.append('<div class="section">%s</div>%s'
                     % (h(T(ctx, "items_with_flag", n=len(items))), _more_chips(chips, 80)))
    return page("%s — CDDA Recipes" % flag, "".join(parts), ctx, nav="items")



def render_skill(ctx, skill):
    """A skill page: recipes that use it (by difficulty) and books that train it."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    parts = ['<div class="idtag">%s</div><h1 class="item">%s</h1><div class="idtag">%s</div>'
             % (h(T(ctx, "skill_single")), h(idx.name(skill)), h(skill))]
    d = idx.desc(skill)
    if d:
        parts.append('<div class="desc">%s</div>' % h(d))
    recs = sorted(set(idx.skill_recipes.get(skill, ())),
                  key=lambda rid: (_item_level(idx, rid)[0], idx.name(rid).lower()))
    if recs:
        chips = ['<a class="chip" href="%s">%s <span class="locq">%s %s</span></a>'
                 % (item_url(rid, ctx), h(idx.name(rid)), h(T(ctx, "lv")),
                    h(_item_level(idx, rid)[0])) for rid in recs]
        parts.append('<div class="section">%s</div>%s'
                     % (h(T(ctx, "skill_recipes_label", n=len(recs))), _more_chips(chips, 80)))
    books = sorted(idx.books_for_skill(skill), key=lambda x: idx.name(x).lower())
    if books:
        chips = ['<a class="chip" href="%s">%s</a>' % (item_url(b, ctx), h(idx.name(b)))
                 for b in books]
        parts.append('<div class="section">%s</div>%s'
                     % (h(T(ctx, "skill_books_label", n=len(books))), _more_chips(chips, 80)))
    return page("%s — CDDA Recipes" % idx.name(skill), "".join(parts), ctx, nav="items")



def render_quality(ctx, qid):
    """A tool-quality page: items that provide it, ranked by level."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    title = idx.tr(idx.quals.get(qid, qid))
    parts = ['<div class="idtag">%s</div><h1 class="item">%s</h1><div class="idtag">%s</div>'
             % (h(T(ctx, "quality_single")), h(title), h(qid))]
    items = sorted(idx.items_with_quality(qid),
                   key=lambda t: (-(t[1] or 0), idx.name(t[0]).lower()))
    if items:
        chips = ['<a class="chip" href="%s">%s <span class="locq">%s %s</span></a>'
                 % (item_url(iid, ctx), h(idx.name(iid)), h(T(ctx, "lv")), h(lv))
                 for iid, lv in items]
        parts.append('<div class="section">%s</div>%s'
                     % (h(T(ctx, "quality_items_label", n=len(items))), _more_chips(chips, 80)))
    return page("%s — CDDA Recipes" % title, "".join(parts), ctx, nav="items")



def render_monster(ctx, mid):
    """A monster page: its description and what it drops on death."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    e = idx.by_id.get(mid) or {}
    parts = ['<div class="idtag">%s</div><h1 class="item">%s</h1><div class="idtag">%s</div>'
             % (h(T(ctx, "monster_single")), h(idx.name(mid)), h(mid))]
    d = idx.desc(mid)
    if d:
        parts.append('<div class="desc">%s</div>' % h(d))
    dd = e.get("death_drops")
    if isinstance(dd, str) and dd in idx.group_def:
        parts.append('<div class="section">%s</div><div class="chips">%s</div>'
                     % (h(T(ctx, "monster_drop_group")), a_group(dd, ctx)))
        loot = idx.loot_of(dd)
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
                         % (h(T(ctx, "monster_drops", n=len(loot))), _more_list(lis)))
    return page("%s — CDDA Recipes" % idx.name(mid), "".join(parts), ctx)

