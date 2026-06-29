"""Sortable / filterable item table: all items in one place, with columns for
their characteristics (weight, volume, melee, plus type-specific armor / food /
gun stats and an optional tool-quality level). Sorting is done client-side by
clicking a column header (see the table script in ``assets``)."""
from collections import Counter

from ..state import get_index, get_translator
from ..i18n import T, type_name, itemcat_name
from ..htmlutil import h, a_item, _to_g, _to_ml
from ..assets import page
from .common import _resolved

ARMOR_TYPES = {"ARMOR", "TOOL_ARMOR", "PET_ARMOR"}


def _num(v):
    return float(v) if isinstance(v, (int, float)) else None


def _f_weight(v):
    return ("%.2f kg" % (v / 1000)) if v >= 1000 else ("%g g" % v)


def _f_vol(v):
    return ("%.2f L" % (v / 1000)) if v >= 1000 else ("%g ml" % v)


def _f_int(v):
    return "%g" % v


def _attrs(idx, iid):
    """Numeric characteristics of an item, resolved through copy-from."""
    r = _resolved(idx, iid)
    return {
        "type": r.get("type"),
        "weight": _to_g(r.get("weight")), "volume": _to_ml(r.get("volume")),
        "bash": _num(r.get("bashing")), "cut": _num(r.get("cutting")),
        "tohit": _num(r.get("to_hit")),
        "enc": _num(r.get("encumbrance")), "cov": _num(r.get("coverage")),
        "warmth": _num(r.get("warmth")), "thick": _num(r.get("material_thickness")),
        "cal": _num(r.get("calories")), "quench": _num(r.get("quench")),
        "healthy": _num(r.get("healthy")), "fun": _num(r.get("fun")),
        "range": _num(r.get("range")), "disp": _num(r.get("dispersion")),
        "quals": dict(idx.qualities_of(iid)),
        "armor": idx.armor_protection(iid),
    }


# ---------------------------------------------------------------------------
# columns: each is {label, numeric, cell}. cell(idx, ctx, iid, a) returns
# (data_value_for_sorting, inner_html). An empty data value sorts to the end.
# ---------------------------------------------------------------------------
def _name_col(ctx):
    return {"label": T(ctx, "item_col"), "numeric": False,
            "cell": lambda idx, ctx, iid, a: (idx.name(iid).lower(),
                                              a_item(idx, iid, ctx))}


def _type_col(ctx):
    def cell(idx, ctx, iid, a):
        nm = type_name(a.get("type"), ctx["lang"])
        return (nm.lower(), h(nm))
    return {"label": T(ctx, "type_col"), "numeric": False, "cell": cell}


def _stat_col(label, key, fmt):
    def cell(idx, ctx, iid, a):
        v = a.get(key)
        return ("", "") if v is None else ("%s" % v, h(fmt(v)))
    return {"label": label, "numeric": True, "cell": cell}


def _armor_col(ctx, dmgkey, key):
    """A derived armor-resistance column (value pulled from a['armor'])."""
    label = "🛡 " + T(ctx, dmgkey)

    def cell(idx, ctx, iid, a):
        ar = a.get("armor")
        v = ar.get(key) if ar else None
        return ("", "") if v is None else ("%s" % v, h(_f_int(v)))
    return {"label": label, "numeric": True, "cell": cell}


def _armor_env_col(ctx):
    def cell(idx, ctx, iid, a):
        ar = a.get("armor")
        v = ar.get("env") if ar else None
        return ("", "") if v is None else ("%s" % v, h(_f_int(v)))
    return {"label": T(ctx, "col_env"), "numeric": True, "cell": cell}


def _qual_col(ctx, qid, qname):
    def cell(idx, ctx, iid, a):
        lv = a["quals"].get(qid)
        return ("", "") if lv is None else ("%s" % lv, h(lv))
    return {"label": T(ctx, "qual_lv", q=qname), "numeric": True, "cell": cell}


def _base_cols(ctx, typ=None):
    cols = [_name_col(ctx), _type_col(ctx),
            _stat_col(T(ctx, "weight"), "weight", _f_weight),
            _stat_col(T(ctx, "volume"), "volume", _f_vol)]
    # melee attack columns are noise on an armor table — only show them elsewhere
    if typ not in ARMOR_TYPES:
        cols += [_stat_col(T(ctx, "col_bash"), "bash", _f_int),
                 _stat_col(T(ctx, "col_cut"), "cut", _f_int),
                 _stat_col(T(ctx, "col_tohit"), "tohit", _f_int)]
    return cols


def _extra_cols(ctx, typ):
    if typ in ARMOR_TYPES:
        return [_armor_col(ctx, "dmg_bash", "bash"),
                _armor_col(ctx, "dmg_cut", "cut"),
                _armor_col(ctx, "dmg_bullet", "bullet"),
                _armor_col(ctx, "dmg_acid", "acid"),
                _armor_col(ctx, "dmg_fire", "fire"),
                _armor_env_col(ctx),
                _stat_col(T(ctx, "col_enc"), "enc", _f_int),
                _stat_col(T(ctx, "col_cov"), "cov", _f_int),
                _stat_col(T(ctx, "col_warmth"), "warmth", _f_int),
                _stat_col(T(ctx, "col_thick"), "thick", _f_int)]
    if typ == "COMESTIBLE":
        return [_stat_col(T(ctx, "col_cal"), "cal", _f_int),
                _stat_col(T(ctx, "col_quench"), "quench", _f_int),
                _stat_col(T(ctx, "col_healthy"), "healthy", _f_int),
                _stat_col(T(ctx, "col_fun"), "fun", _f_int)]
    if typ == "GUN":
        return [_stat_col(T(ctx, "col_range"), "range", _f_int),
                _stat_col(T(ctx, "col_disp"), "disp", _f_int)]
    return []


def attr_table(ctx, idx, ids, cols):
    """Render a sortable table of `ids` using the given column specs."""
    head = "".join('<th class="%s">%s<span class="ar"></span></th>'
                   % ("num" if c["numeric"] else "", h(c["label"])) for c in cols)
    body = []
    for iid in ids:
        a = _attrs(idx, iid)
        tds = []
        for c in cols:
            dv, inner = c["cell"](idx, ctx, iid, a)
            tds.append('<td class="%s" data-v="%s">%s</td>'
                       % ("num" if c["numeric"] else "", h(dv), inner))
        body.append("<tr>%s</tr>" % "".join(tds))
    return ('<div class="tablewrap"><table class="cat sortable">'
            '<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (head, "".join(body)))


def _dominant_type(idx, ids):
    """Most common json item-type among ids (drives the type-specific columns)."""
    c = Counter((idx.by_id.get(i) or {}).get("type") for i in ids)
    return c.most_common(1)[0][0] if c else None


def _filters_html(ctx, idx, cat, qual):
    base = ('<input type=hidden name="ver" value="%d">'
            '<input type=hidden name="lang" value="%s">%s'
            % (ctx["ver"], h(ctx["lang"]),
               '<input type=hidden name="mods" value="1">' if ctx["mods"] else ""))
    cats = idx.item_categories()
    copts = ['<option value="">%s</option>' % h(T(ctx, "cat_any"))]
    for c in sorted(cats, key=lambda c: itemcat_name(c, ctx["lang"]).lower()):
        copts.append('<option value="%s"%s>%s (%d)</option>'
                     % (h(c), " selected" if c == cat else "",
                        h(itemcat_name(c, ctx["lang"])), len(cats[c])))
    qopts = ['<option value="">%s</option>' % h(T(ctx, "none_quality"))]
    for qid, nm in sorted(idx.quals.items(), key=lambda kv: idx.tr(kv[1]).lower()):
        qopts.append('<option value="%s"%s>%s</option>'
                     % (h(qid), " selected" if qid == qual else "", h(idx.tr(nm))))
    return (
        '<form class="filters" method="get" action="/items">%s'
        '<select name="cat" onchange="this.form.submit()">%s</select>'
        '<select name="qual" onchange="this.form.submit()">%s</select>'
        '<input class="tfilter" placeholder="%s" autocomplete="off">'
        '</form>'
        % (base, "".join(copts), "".join(qopts), h(T(ctx, "tfilter_ph"))))


def render_items_table(ctx, cat, qual):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    cats = idx.item_categories()
    if cat and cat in cats:
        ids = list(cats[cat])
        title = itemcat_name(cat, ctx["lang"])
    else:
        cat, ids, title = "", list(idx.item_ids), T(ctx, "all_items")
    # type-specific stat columns follow the category's dominant item type
    dom = _dominant_type(idx, ids)
    cols = _base_cols(ctx, dom) + _extra_cols(ctx, dom)
    if qual and qual in idx.quals:
        cols.append(_qual_col(ctx, qual, idx.tr(idx.quals[qual])))
    else:
        qual = ""
    ids = sorted(ids, key=lambda i: idx.name(i).lower())
    qsuf = "ver=%d&lang=%s%s" % (ctx["ver"], h(ctx["lang"]), "&mods=1" if ctx["mods"] else "")
    head = ('<a class="item" href="/?%s">%s</a>'
            '<h1 class="item">%s <span class="idtag">(%s)</span></h1>'
            '<p class="hint" style="margin-top:6px">%s</p>'
            % (qsuf, h(T(ctx, "all_cats")), h(title), h(T(ctx, "items_n", n=len(ids))),
               h(T(ctx, "table_hint"))))
    body = head + _filters_html(ctx, idx, cat, qual) + attr_table(ctx, idx, ids, cols)
    return page("%s — CDDA Recipes" % title, body, ctx, nav="items")
