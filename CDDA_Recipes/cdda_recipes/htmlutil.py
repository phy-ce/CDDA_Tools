import html
import re

from urllib.parse import urlencode

from .i18n import T
from .loot import _norm_entries

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



def _kv_url(path, key, val, ctx):
    p = {key: val, "ver": ctx["ver"], "lang": ctx["lang"]}
    if ctx["mods"]:
        p["mods"] = 1
    return path + "?" + urlencode(p)



def flag_url(flag, ctx):
    return _kv_url("/flag", "flag", flag, ctx)



def skill_url(skill, ctx):
    return _kv_url("/skill", "id", skill, ctx)



def quality_url(qid, ctx):
    return _kv_url("/quality", "id", qid, ctx)



def monster_url(mid, ctx):
    return _kv_url("/monster", "id", mid, ctx)


def entity_url(eid, ctx):
    return _kv_url("/entity", "id", eid, ctx)



def a_skill(idx, skill, ctx):
    return '<a class="item" href="%s">%s</a>' % (skill_url(skill, ctx), h(idx.name(skill)))



def a_quality(idx, qid, ctx):
    return '<a class="item" href="%s">%s</a>' % (
        quality_url(qid, ctx), h(idx.tr(idx.quals.get(qid, qid))))



def a_monster(idx, mid, ctx):
    return '<a class="chip" href="%s">%s</a>' % (monster_url(mid, ctx), h(idx.name(mid)))



def _more_chips(chips, cap=24):
    """A chips row; anything past `cap` is hidden behind a click-to-expand +N."""
    if len(chips) <= cap:
        return '<div class="chips">%s</div>' % "".join(chips)
    return ('<div class="chips">%s</div>'
            '<details class="morechips"><summary class="chip loc">+%d</summary>'
            '<div class="chips">%s</div></details>'
            % ("".join(chips[:cap]), len(chips) - cap, "".join(chips[cap:])))



def _more_list(lis, cap=60):
    """A problist <ul>; rows past `cap` collapse behind a click-to-expand +N."""
    if len(lis) <= cap:
        return '<ul class="problist">%s</ul>' % "".join(lis)
    return ('<ul class="problist">%s</ul>'
            '<details class="morechips"><summary class="chip loc">+%d</summary>'
            '<ul class="problist">%s</ul></details>'
            % ("".join(lis[:cap]), len(lis) - cap, "".join(lis[cap:])))



def pct_html(frac):
    p = frac * 100
    if p >= 99.5:
        return "100%"
    if p >= 1:
        return "~%d%%" % round(p)
    if p > 0:
        return "<1%"
    return "0%"



def _count_html(c):
    if not c:
        return ""
    shown = "%s–%s" % (c[0], c[1]) if isinstance(c, list) and len(c) == 2 else c
    return ' <span class="qty">×%s</span>' % h(shown)



def _to_ml(v):
    m = re.match(r"\s*([\d.]+)\s*([a-zA-Z]*)", str(v))
    if not m:
        return None
    try:
        n = float(m.group(1))
    except ValueError:
        return None
    return n * 1000 if m.group(2).lower() == "l" else n



def _to_g(v):
    m = re.match(r"\s*([\d.]+)\s*([a-zA-Z]*)", str(v))
    if not m:
        return None
    try:
        n = float(m.group(1))
    except ValueError:
        return None
    u = m.group(2).lower()
    return n * 1000 if u == "kg" else (n / 1000 if u == "mg" else n)



def entries_html(idx, ctx, raw, subtype, depth=0):
    """Recursive <li> rows for a group's entries. Inline anonymous groups are
    expanded in place (labelled 'pick 1 of' / 'all of'), so nothing is opaque."""
    rows = []
    for e in _norm_entries(raw, subtype):
        if e["kind"] == "item":
            label, sub = a_item(idx, e["id"], ctx), ""
        elif e["kind"] == "group":
            label, sub = a_group(e["id"], ctx), ""
        else:
            sub_st, sub_raw = e["inline"]
            label = '<span class="slot">%s</span>' % h(
                T(ctx, "pick_one" if sub_st == "distribution" else "all_of"))
            sub = ("" if depth >= 6 else
                   '<ul class="problist sub">%s</ul>'
                   % entries_html(idx, ctx, sub_raw, sub_st, depth + 1))
        rows.append('<li><span class="prob">%s</span><div class="ent">%s%s%s</div></li>'
                    % (pct_html(e["frac"]), label, _count_html(e["count"]), sub))
    return "".join(rows)



def avg_html(expected):
    if expected >= 9.95:
        return "×%d" % round(expected)
    return "×%.1f" % expected

