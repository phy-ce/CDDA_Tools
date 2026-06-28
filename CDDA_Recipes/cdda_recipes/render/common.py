import json
import re

from ..i18n import T
from ..htmlutil import (h, a_item, item_url, a_skill, a_quality, flag_url,
                        _to_ml, _to_g)

_META_KEYS = {"type", "id", "abstract", "copy-from", "extend", "delete",
              "relative", "proportional", "name", "description", "looks_like",
              "picture", "ascii_picture"}


_ASCII_COLORS = {
    "black": "#3a3f47", "white": "#e6e8eb", "light_gray": "#b8bfc7",
    "dark_gray": "#7e8893", "red": "#d23a2e", "light_red": "#ff6b5e",
    "green": "#2b8a3e", "light_green": "#5cc777", "blue": "#3b6fd6",
    "light_blue": "#6ea8ff", "cyan": "#1797a8", "light_cyan": "#4fd0e0",
    "magenta": "#b5179e", "light_magenta": "#e85ad0", "brown": "#9a6a23",
    "yellow": "#d6a400", "pink": "#ff8fc6"}


def _ascii_html(lines):
    out = []
    for ln in lines:
        buf = []
        for p in re.split(r'(<color_[a-z_0-9]+>|</color>)', ln):
            if p.startswith("<color_"):
                buf.append('<span style="color:%s">' % _ASCII_COLORS.get(p[7:-1], "inherit"))
            elif p == "</color>":
                buf.append("</span>")
            else:
                buf.append(h(p))
        out.append("".join(buf))
    return '<pre class="ascii">%s</pre>' % "\n".join(out)


def tile_html(idx, ctx, eid):
    """A CSS-cropped sprite from the active tileset, or '' if the id has none."""
    t = idx.tile_of(eid)
    if not t:
        return ""
    fn, x, y, w, h_ = t
    url = "/gfx?f=%s&ver=%d" % (fn, ctx["ver"])
    return ('<span class="tile" title="%s" style="width:%dpx;height:%dpx;'
            'background-image:url(%s);background-position:-%dpx -%dpx"></span>'
            % (h(fn), w, h_, h(url), x, y))


def picture_html(idx, ctx, eid):
    """The entity's ASCII-art picture (inline `picture` or an `ascii_picture`
    reference), rendered with its colors."""
    res = _resolved(idx, eid)
    pic = res.get("picture")
    if not isinstance(pic, list):
        ref = res.get("ascii_picture")
        pic = idx.ascii_art.get(ref) if isinstance(ref, str) else None
    if isinstance(pic, list) and pic:
        return _ascii_html([x for x in pic if isinstance(x, str)])
    return ""


def _resolved(idx, eid):
    """Merge an entry with its copy-from ancestors (child overrides parent)."""
    out = {}
    for e in reversed(idx._chain(eid)):
        if isinstance(e, dict):
            out.update(e)
    return out


def raw_fields_html(idx, ctx, eid, shown, skip_prefixes=("//",)):
    """Collapsible dump of every resolved JSON field not already shown, so no
    data is silently omitted."""
    res = _resolved(idx, eid)
    skip = set(shown) | _META_KEYS
    rows = []
    for k in sorted(res):
        if k in skip or any(k.startswith(p) for p in skip_prefixes):
            continue
        val = json.dumps(res[k], ensure_ascii=False)
        if len(val) > 240:
            val = val[:240] + " …"
        rows.append('<div class="f"><span class="k">%s</span>'
                    '<span class="v"><code>%s</code></span></div>' % (h(k), h(val)))
    if not rows:
        return ""
    return ('<details class="rawbox"><summary class="section">%s</summary>'
            '<div class="rawfields">%s</div></details>'
            % (h(T(ctx, "raw_fields", n=len(rows))), "".join(rows)))


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



def _otree_node(idx, group, ctx, depth, seen, budget):
    """One ingredient group -> one compact box node in the org-chart tree. The
    box shows a single representative item (the craftable one we expand, else
    the first) + qty, with a '+N' badge when the group has OR alternatives. The
    representative's sub-recipe branches into child boxes below it."""
    entries = [e for e in group if isinstance(e, list) and e]
    if not entries:
        return '<li><div class="node">?</div></li>'
    follow = next((e for e in entries
                   if not (len(e) > 2 and e[2] == "LIST")
                   and e[0] in idx.by_result and e[0] not in seen), None)
    primary = follow or entries[0]
    pid = primary[0]
    cnt = primary[1] if len(primary) > 1 else 1
    is_list = len(primary) > 2 and primary[2] == "LIST"
    label = h(idx.name(pid)) if is_list else a_item(idx, pid, ctx)
    qty = "" if is_list else ' <span class="qty">×%s</span>' % h(cnt)
    alts = len(entries) - 1
    badge = ""
    if alts > 0:
        def alt_label(e):
            nm = idx.name(e[0])
            if len(e) > 2 and e[2] == "LIST":
                return nm
            return "%s ×%s" % (nm, e[1] if len(e) > 1 else 1)
        others = ", ".join(alt_label(e) for e in entries if e is not primary)
        altdata = [{"label": alt_label(e),
                    "url": "" if (len(e) > 2 and e[2] == "LIST") else item_url(e[0], ctx)}
                   for e in entries if e is not primary]
        badge = (' <span class="alt" title="%s" data-alts="%s">+%d</span>'
                 % (h(others), h(json.dumps(altdata, ensure_ascii=False)), alts))
    box = '<div class="node">%s%s%s</div>' % (label, qty, badge)
    kids = ""
    if follow and depth > 0 and budget[0] > 0:
        budget[0] -= 1
        comps = _recipe_comps(idx, idx.by_result[pid][0])
        kids = "<ul>%s</ul>" % "".join(
            _otree_node(idx, g, ctx, depth - 1, seen | {pid}, budget)
            for g in comps if isinstance(g, list))
    return "<li>%s%s</li>" % (box, kids)



def tree_block(idx, recipe, ctx):
    ids = idx._recipe_component_ids(recipe)
    if not any(i in idx.by_result for i in ids):
        return ""   # nothing craftable to expand
    budget = [80]
    children = "".join(_otree_node(idx, g, ctx, 2, set(), budget)
                       for g in _recipe_comps(idx, recipe) if isinstance(g, list))
    root = a_item(idx, recipe.get("result", ""), ctx)
    tree = ('<ul class="otree"><li><div class="node root">%s</div>'
            '<ul>%s</ul></li></ul>' % (root, children))
    return ('<details class="treebox" open><summary>🌳 %s</summary>'
            '<div class="treescroll">%s</div></details>' % (h(T(ctx, "tree")), tree))



def recipe_html(idx, recipe, ctx, n=None):
    rows = []

    def field(label, value_html):
        rows.append('<div class="f"><span class="k">%s</span>'
                    '<span class="v">%s</span></div>' % (label, value_html))

    skill = recipe.get("skill_used")
    diff = recipe.get("difficulty")
    if skill or diff is not None:
        s = a_skill(idx, skill, ctx) if skill else "?"
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
                qs.append("%s&nbsp;%s" % (a_quality(idx, q.get("id"), ctx),
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
        # melee attack time from the weapon base cost (65 + volume/62.5mL + weight/60g);
        # range = base/2 (skill 15) .. base (skill 0), before Dex / encumbrance
        vol, wt = _to_ml(st.get("volume")), _to_g(st.get("weight"))
        if vol and wt:
            base = 65 + vol / 62.5 + wt / 60.0
            bm = base / 2.0
            bits.append('<span class="atk" title="%s">%s</span>'
                        % (h(T(ctx, "atk_tip")),
                           h(T(ctx, "atk_time_fmt", a="%.1f" % (bm / 100.0),
                              b="%.1f" % (base / 100.0),
                              m0=int(round(bm)), m1=int(round(base))))))
    if not bits:
        return ""
    return ('<div class="stats">%s</div>'
            % "".join('<span class="pill">%s</span>' % b for b in bits))



def _abilities_html(idx, ctx, rid):
    """What you can do with the item: tool qualities, use actions, melee
    techniques, and its flags (with descriptions on hover)."""
    def field(label, value_html):
        return ('<div class="f"><span class="k">%s</span><span class="v">%s</span></div>'
                % (h(label), value_html))

    rows = []
    quals = idx.qualities_of(rid)
    if quals:
        rows.append(field(T(ctx, "toolq"), ", ".join(
            "%s&nbsp;%s" % (a_quality(idx, q, ctx), h(lv)) for q, lv in quals)))
    acts = idx.actions_of(rid)
    if acts:
        rows.append(field(T(ctx, "actions"), ", ".join(h(a) for a in acts)))
    techs = idx.techniques_of(rid)
    if techs:
        rows.append(field(T(ctx, "techniques"),
                          ", ".join(h(idx.name(t)) for t in techs)))
    flags = sorted(idx.flags_of(rid))
    flag_html = ""
    if flags:
        chips = []
        for f in flags:
            d = idx.flag_desc(f)
            tip = ' title="%s"' % h(d) if d else ""
            chips.append('<a class="chip flag" href="%s"%s>%s</a>'
                         % (flag_url(f, ctx), tip, h(f)))
        flag_html = ('<div class="f"><span class="k">%s</span>'
                     '<span class="v"><div class="chips">%s</div></span></div>'
                     % (h(T(ctx, "flags")), "".join(chips)))
    if not rows and not flag_html:
        return ""
    return ('<div class="recipe"><div class="rtitle">🛠 %s</div>%s%s</div>'
            % (h(T(ctx, "abilities")), "".join(rows), flag_html))



def _item_level(idx, rid):
    """Lowest crafting difficulty across this item's recipes, and the skill."""
    recs = idx.by_result.get(rid, [])
    diffs = [r.get("difficulty") for r in recs if isinstance(r.get("difficulty"), int)]
    lv = min(diffs) if diffs else 0
    skill = next((r.get("skill_used") for r in recs if r.get("skill_used")), None)
    return lv, skill

