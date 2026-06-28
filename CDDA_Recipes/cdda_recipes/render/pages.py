from urllib.parse import quote

from ..state import get_index, get_translator
from ..config import SETTINGS, BROWSE_BY_ROUTE, BROWSE_BY_TYPE
from ..i18n import T, CAT_NAMES, cat_name, MECH_DOC
from ..htmlutil import (h, a_group, a_item, a_monster, item_url, flag_url,
                        monster_url, skill_url, quality_url, entity_url, pct_html,
                        _more_chips, _more_list)
from ..assets import page
from .common import _item_level, raw_fields_html, picture_html, tile_html

_MON_SHOWN = {
    "hp", "speed", "diff", "weight", "volume", "material", "symbol", "color",
    "melee_dice", "melee_dice_sides", "melee_cut", "melee_skill", "attack_cost",
    "special_attacks", "melee_damage", "monster_weapon", "starting_ammo",
    "special_when_hit", "aggression", "morale", "dodge", "regenerates", "bodytype",
    "categories", "vision_day", "vision_night", "species", "default_faction", "flags",
    "anger_triggers", "fear_triggers", "placate_triggers", "luminance", "emit_fields",
    "aggro_character", "harvest", "death_function", "upgrades", "reproduction",
    "burn_into", "fungalize_into", "zombify_into", "revert_to_itype", "death_drops",
    "petfood", "pet_training", "baby_flags",
}

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



def _browse_page(ctx, nav_key, pairs):
    """A browse landing: a sorted, clickable chip list of every entity of a kind."""
    chips = ['<a class="chip" href="%s">%s</a>' % (href, h(label)) for label, href in pairs]
    body = ('<h1 class="item">%s · %d</h1>%s'
            % (h(T(ctx, nav_key)), len(pairs), _more_chips(chips, 150)))
    return page(T(ctx, nav_key), body, ctx, nav=nav_key.replace("nav_", "", 1))


def render_monsters_list(ctx):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    pairs = sorted(((idx.name(m), monster_url(m, ctx)) for _n, m in idx.all_monsters()),
                   key=lambda x: x[0].lower())
    return _browse_page(ctx, "nav_monsters", pairs)


def render_skills_list(ctx):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    pairs = sorted(((idx.name(s), skill_url(s, ctx)) for _n, s in idx.all_skills()),
                   key=lambda x: x[0].lower())
    return _browse_page(ctx, "nav_skills", pairs)


def render_qualities_list(ctx):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    pairs = sorted(((idx.tr(nm), quality_url(qid, ctx)) for qid, nm in idx.quals.items()),
                   key=lambda x: x[0].lower())
    return _browse_page(ctx, "nav_qualities", pairs)


def render_flags_list(ctx):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    pairs = sorted(((f, flag_url(f, ctx)) for f in idx.all_flags()),
                   key=lambda x: x[0].lower())
    return _browse_page(ctx, "nav_flags", pairs)


def render_entity_list(ctx, route):
    """Generic browse landing for one of the BROWSE_TYPES."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    typ, nav_key = BROWSE_BY_ROUTE[route]
    pairs = sorted(((idx.name(i), entity_url(i, ctx)) for i in idx.by_type.get(typ, [])),
                   key=lambda x: x[0].lower())
    return _browse_page(ctx, nav_key, pairs)


def render_entity(ctx, eid):
    """Generic detail page: name + description + ASCII art + every JSON field."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    e = idx.by_id.get(eid) or {}
    typ = e.get("type")
    nav_key = BROWSE_BY_TYPE.get(typ, ("",))[0]
    nav = nav_key.replace("nav_", "", 1) if nav_key else None
    name = idx.name(eid)
    parts = ['<div class="idtag">%s</div><h1 class="item">%s</h1><div class="idtag">%s</div>'
             % (h(T(ctx, nav_key) if nav_key else (typ or "")), h(name), h(eid))]
    parts.append(tile_html(idx, ctx, eid))
    d = idx.desc(eid)
    if d:
        parts.append('<div class="desc">%s</div>' % h(d))
    parts.append(picture_html(idx, ctx, eid))
    parts.append(raw_fields_html(idx, ctx, eid, set()))
    return page("%s — CDDA Recipes" % name, "".join(parts), ctx, nav=nav)


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
    return page("%s — CDDA Recipes" % flag, "".join(parts), ctx, nav="flags")



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
    return page("%s — CDDA Recipes" % idx.name(skill), "".join(parts), ctx, nav="skills")



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
    return page("%s — CDDA Recipes" % title, "".join(parts), ctx, nav="qualities")



_ARMOR_TYPES = [("armor_bash", "dmg_bash"), ("armor_cut", "dmg_cut"),
                ("armor_stab", "dmg_stab"), ("armor_bullet", "dmg_bullet"),
                ("armor_acid", "dmg_acid"), ("armor_fire", "dmg_fire"),
                ("armor_cold", "dmg_cold"), ("armor_elec", "dmg_elec")]

_DMG_LABEL = {"bash": "dmg_bash", "cut": "dmg_cut", "stab": "dmg_stab",
              "bullet": "dmg_bullet", "acid": "dmg_acid", "heat": "dmg_fire",
              "cold": "dmg_cold", "electric": "dmg_elec"}

_COLOR_HEX = {"red": "#d23a2e", "light_red": "#ff6b5e", "green": "#2b8a3e",
              "light_green": "#5cc777", "blue": "#1558d6", "light_blue": "#6ea8ff",
              "cyan": "#1797a8", "light_cyan": "#4fd0e0", "magenta": "#b5179e",
              "light_magenta": "#e85ad0", "brown": "#9a6a23", "light_brown": "#c08a3e",
              "yellow": "#d6a400", "white": "#e6e8eb", "light_gray": "#b8bfc7",
              "dark_gray": "#7e8893", "black": "#5a606a", "pink": "#ff8fc6"}


def _dmg_name(ctx, dt):
    k = _DMG_LABEL.get(dt)
    return T(ctx, k) if k else (dt or "")


def _trigger_rows(ctx, idx, mid, field):
    out = []
    for key, lab in (("anger_triggers", "m_anger"), ("fear_triggers", "m_fear"),
                     ("placate_triggers", "m_placate")):
        tg = _mf(idx, mid, key)
        if tg:
            tgs = tg if isinstance(tg, list) else [tg]
            out.append(field(T(ctx, lab), ", ".join(h(x) for x in tgs if isinstance(x, str))))
    return out


def _mf(idx, mid, key, default=None):
    """A monster field, resolved through copy-from (most-derived wins)."""
    for e in idx._chain(mid):
        if e.get(key) is not None:
            return e[key]
    return default


def _mlink(idx, ctx, ident):
    """Link an id to a monster or group page, else plain text."""
    if ident in idx.by_id and idx.by_id[ident].get("type") == "MONSTER":
        return a_monster(idx, ident, ctx)
    if ident in idx.group_def:
        return a_group(ident, ctx)
    return h(ident)


def render_monster(ctx, mid):
    """A monster page: full stat block from its JSON (combat, defense, senses,
    lifecycle/butchering) plus death drops."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    e = idx.by_id.get(mid) or {}
    name = idx.name(mid)
    parts = ['<div class="idtag">%s</div><h1 class="item">%s</h1><div class="idtag">%s</div>'
             % (h(T(ctx, "monster_single")), h(name), h(mid))]
    parts.append(tile_html(idx, ctx, mid))
    d = idx.desc(mid)
    if d:
        parts.append('<div class="desc">%s</div>' % h(d))
    parts.append(picture_html(idx, ctx, mid))

    def mf(k, dflt=None):
        return _mf(idx, mid, k, dflt)

    def field(label, value_html):
        return ('<div class="f"><span class="k">%s</span><span class="v">%s</span></div>'
                % (h(label), value_html))

    def box(title, rows):
        rows = [r for r in rows if r]
        if rows:
            parts.append('<div class="recipe"><div class="rtitle">%s</div>%s</div>'
                         % (h(title), "".join(rows)))

    # headline stats inline
    bits = []
    sym, col = mf("symbol"), mf("color")
    if sym:
        cname = col[0] if isinstance(col, list) and col else (col if isinstance(col, str) else "")
        bits.append('<span style="color:%s;font-weight:700">%s</span>'
                    % (_COLOR_HEX.get(cname, "var(--muted)"), h(sym)))
    if mf("hp") is not None:
        bits.append("HP %s" % h(mf("hp")))
    if mf("speed") is not None:
        bits.append("%s %s" % (h(T(ctx, "speed")), h(mf("speed"))))
    if mf("diff") is not None:
        bits.append("%s %s" % (h(T(ctx, "difficulty")), h(mf("diff"))))
    if mf("weight"):
        bits.append("%s %s" % (h(T(ctx, "weight")), h(mf("weight"))))
    if mf("volume"):
        bits.append("%s %s" % (h(T(ctx, "volume")), h(mf("volume"))))
    mat = mf("material")
    if mat:
        mats = mat if isinstance(mat, list) else [mat]
        bits.append("%s %s" % (h(T(ctx, "material")),
                               ", ".join(h(idx.name(m)) for m in mats if m)))
    if bits:
        parts.append('<div class="stats">%s</div>'
                     % "".join('<span class="pill">%s</span>' % b for b in bits))

    # combat (offense)
    rows = []
    dice, sides, cut = mf("melee_dice"), mf("melee_dice_sides"), mf("melee_cut", 0)
    if dice and sides:
        avg = dice * (sides + 1) / 2.0
        s = "%dd%d (~%d) %s" % (dice, sides, round(avg), h(T(ctx, "dmg_bash")))
        if cut:
            s += " + %d %s" % (cut, h(T(ctx, "dmg_cut")))
        if mf("melee_skill") is not None:
            s += ' <span class="diff">%s %s</span>' % (h(T(ctx, "skill")), h(mf("melee_skill")))
        rows.append(field(T(ctx, "melee"), s))
    if mf("attack_cost") is not None:
        rows.append(field(T(ctx, "m_atkcost"), h(mf("attack_cost"))))
    sp = mf("special_attacks")
    if sp:
        names = []
        for s in sp:
            if isinstance(s, list) and s:
                names.append(h(s[0]) + (" (%s)" % h(s[1]) if len(s) > 1 else ""))
            elif isinstance(s, dict) and s.get("type"):
                names.append(h(s.get("id") or s["type"]))
            elif isinstance(s, str):
                names.append(h(s))
        if names:
            rows.append(field(T(ctx, "m_special"), ", ".join(names)))
    md = mf("melee_damage")
    if isinstance(md, list) and md:
        seg = ", ".join("%s %s" % (h(_dmg_name(ctx, u.get("damage_type"))), h(u.get("amount")))
                        for u in md if isinstance(u, dict) and u.get("amount"))
        if seg:
            rows.append(field(T(ctx, "m_extra_dmg"), seg))
    mw = mf("monster_weapon")
    if isinstance(mw, str):
        rows.append(field(T(ctx, "m_weapon"),
                          a_item(idx, mw, ctx) if mw in idx.by_id else h(mw)))
    sa = mf("starting_ammo")
    if isinstance(sa, dict) and sa:
        rows.append(field(T(ctx, "m_ammo"), ", ".join(
            "%s×%s" % (a_item(idx, k, ctx) if k in idx.by_id else h(k), h(v))
            for k, v in sa.items())))
    swh = mf("special_when_hit")
    if isinstance(swh, list) and swh:
        rows.append(field(T(ctx, "m_when_hit"),
                          h(swh[0]) + (" (%s%%)" % h(swh[1]) if len(swh) > 1 else "")))
    if mf("aggression") is not None:
        rows.append(field(T(ctx, "aggression"), h(mf("aggression"))))
    if mf("morale") is not None:
        rows.append(field(T(ctx, "morale"), h(mf("morale"))))
    box(T(ctx, "m_combat"), rows)

    # defense
    rows = []
    if mf("dodge") is not None:
        rows.append(field(T(ctx, "dodge"), h(mf("dodge"))))
    arm = [(T(ctx, lab), mf(k)) for k, lab in _ARMOR_TYPES if mf(k)]
    if arm:
        rows.append(field(T(ctx, "armor"),
                          "  ·  ".join("%s %s" % (h(l), h(v)) for l, v in arm)))
    if mf("regenerates"):
        rows.append(field(T(ctx, "m_regen"), h(mf("regenerates"))))
    box(T(ctx, "m_defense"), rows)

    # senses & behavior
    rows = []
    if mf("bodytype"):
        rows.append(field(T(ctx, "bodytype"), h(mf("bodytype"))))
    cats = mf("categories")
    if cats:
        catl = cats if isinstance(cats, list) else [cats]
        rows.append(field(T(ctx, "category"), ", ".join(h(x) for x in catl)))
    vd, vn = mf("vision_day"), mf("vision_night")
    if vd is not None or vn is not None:
        rows.append(field(T(ctx, "vision"), "%s / %s"
                          % (h(vd if vd is not None else "—"), h(vn if vn is not None else "—"))))
    spc = mf("species")
    if spc:
        spcs = spc if isinstance(spc, list) else [spc]
        rows.append(field(T(ctx, "species"), ", ".join(h(x) for x in spcs)))
    if mf("default_faction"):
        rows.append(field(T(ctx, "faction"), h(mf("default_faction"))))
    flags = sorted(idx.flags_of(mid))
    if flags:
        chips = []
        for f in flags:
            fd = idx.flag_desc(f)
            tip = ' title="%s"' % h(fd) if fd else ""
            chips.append('<a class="chip flag" href="%s"%s>%s</a>' % (flag_url(f, ctx), tip, h(f)))
        rows.append(field(T(ctx, "flags"), '<div class="chips">%s</div>' % "".join(chips)))
    rows.extend(_trigger_rows(ctx, idx, mid, field))
    if mf("luminance"):
        rows.append(field(T(ctx, "m_glow"), h(mf("luminance"))))
    em = mf("emit_fields")
    if em:
        eml = em if isinstance(em, list) else [em]
        rows.append(field(T(ctx, "m_emit"), ", ".join(h(x) for x in eml if isinstance(x, str))))
    if mf("aggro_character"):
        rows.append(field(T(ctx, "m_aggro"), "✓"))
    box(T(ctx, "m_senses"), rows)

    # lifecycle & butchering
    rows = []
    if mf("harvest"):
        rows.append(field(T(ctx, "m_harvest"), h(mf("harvest"))))
    df = mf("death_function")
    if df:
        dfs = df if isinstance(df, list) else [df]
        rows.append(field(T(ctx, "m_death"), ", ".join(h(x) for x in dfs if isinstance(x, str))))
    up = mf("upgrades")
    if isinstance(up, dict):
        tgt = up.get("into") or up.get("into_group")
        seg = _mlink(idx, ctx, tgt) if tgt else ""
        if up.get("half_life"):
            seg += ' <span class="diff">half-life %s</span>' % h(up["half_life"])
        if seg:
            rows.append(field(T(ctx, "m_upgrades"), seg))
    rep = mf("reproduction")
    if isinstance(rep, dict):
        baby = rep.get("baby_monster") or rep.get("baby_egg")
        if baby:
            rows.append(field(T(ctx, "m_reproduces"), _mlink(idx, ctx, baby)))
    for k in ("burn_into", "fungalize_into"):
        v = mf(k)
        if v:
            rows.append(field(T(ctx, "m_becomes"), _mlink(idx, ctx, v)))
    zi = mf("zombify_into")
    if zi:
        rows.append(field(T(ctx, "m_zombify"), _mlink(idx, ctx, zi)))
    rv = mf("revert_to_itype")
    if rv:
        rows.append(field(T(ctx, "m_revert"), a_item(idx, rv, ctx) if rv in idx.by_id else h(rv)))
    pf = mf("petfood")
    if isinstance(pf, dict) and pf.get("food"):
        foods = pf["food"]
        rows.append(field(T(ctx, "m_food"),
                          ", ".join(h(x) for x in (foods if isinstance(foods, list) else [foods]))))
    pt = mf("pet_training")
    if isinstance(pt, dict) and pt:
        rows.append(field(T(ctx, "m_pettrain"),
                          " · ".join("%s ×%s" % (h(k), h(v)) for k, v in pt.items())))
    bf = mf("baby_flags")
    if bf:
        rows.append(field(T(ctx, "m_seasons"),
                          ", ".join(h(x) for x in (bf if isinstance(bf, list) else [bf]))))
    box(T(ctx, "m_life"), rows)

    dd = e.get("death_drops") or mf("death_drops")
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

    parts.append(raw_fields_html(idx, ctx, mid, _MON_SHOWN, skip_prefixes=("//", "armor_")))
    return page("%s — CDDA Recipes" % idx.name(mid), "".join(parts), ctx, nav="monsters")

