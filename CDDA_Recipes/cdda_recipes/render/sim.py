"""Combat simulator — melee and ranged. Replays the Bright Nights formulas (see
Mechanics → combat topics and docs/combat-formulas.md) via Monte-Carlo, and can
auto-fill stats by picking a weapon / gun / ammo / monster from the loaded game
index.

We model the common wielded-weapon path with full stamina, no encumbrance, two
working arms and no martial-arts / mutation buffs (noted on-page). Ranged shots
assume torso hits (severity capped at 1.5) and ignore aim-time / fire-rate, so
ranged results are per-shot.
"""
import math
import random

from ..state import get_index, get_translator
from ..i18n import T
from ..htmlutil import h, _to_ml, _to_g
from ..assets import page
from .common import _resolved

# size_melee_penalty (creature.cpp): subtracted from melee hit_spread
_SIZE_PEN = {"tiny": 30, "small": 15, "medium": 0, "large": -10, "huge": -20}
# occupied_tile_fraction (ranged.cpp): ranged target size
_OCC = {"tiny": 0.1, "small": 0.25, "medium": 0.5, "large": 0.75, "huge": 1.0}
_SIZES = ["tiny", "small", "medium", "large", "huge"]
_MS = {"MS_TINY": "tiny", "MS_SMALL": "small", "MS_MEDIUM": "medium",
       "MS_LARGE": "large", "MS_HUGE": "huge"}

_M_FIELDS = [
    ("str", 10, 1, 40), ("dex", 10, 1, 40), ("per", 8, 1, 40),
    ("sk_melee", 3, 0, 10), ("sk_weapon", 3, 0, 10),
    ("w_bash", 12, 0, 500), ("w_cut", 0, 0, 500), ("w_stab", 0, 0, 500),
    ("w_hit", 1, -10, 10), ("w_vol", 1000, 0, 200000), ("w_wt", 1200, 0, 200000),
    ("t_dodge", 3, 0, 40), ("a_bash", 2, 0, 200), ("a_cut", 2, 0, 200),
    ("a_stab", 2, 0, 200), ("t_hp", 80, 1, 100000),
]
_R_FIELDS = [
    ("dex", 10, 1, 40), ("per", 10, 1, 40), ("sk_gun", 3, 0, 10), ("sk_weapon", 3, 0, 10),
    ("gun_disp", 150, 0, 20000), ("recoil", 50, 0, 3000),
    ("rng_dmg", 25, 0, 2000), ("rng_pen", 2, 0, 2000), ("proj_speed", 1000, 1, 5000),
    ("range", 6, 1, 60),
    ("t_dodge", 3, 0, 40), ("a_bullet", 2, 0, 200), ("t_hp", 80, 1, 100000),
]
_INT_KEYS = {"str", "dex", "per", "sk_melee", "sk_weapon", "sk_gun", "w_bash",
             "w_cut", "w_stab", "w_hit", "a_bash", "a_cut", "a_stab", "a_bullet",
             "t_hp", "t_dodge", "rng_dmg", "rng_pen", "proj_speed", "range"}

_TRIALS = 20000


def _phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _cl(v, lo, hi):
    return max(lo, min(hi, v))


# ---------------------------------------------------------------------------
# index lookups for auto-fill
# ---------------------------------------------------------------------------
def _opt_ids(idx, kind):
    """Cached id list for a picker kind (language-independent)."""
    attr = "_sim_ids_" + kind
    cached = getattr(idx, attr, None)
    if cached is not None:
        return cached
    if kind == "weapon":
        ids = [i for i in idx.item_ids if _has_melee(idx, i)]
    else:
        ids = list(idx.by_type.get(kind.upper(), []))
    setattr(idx, attr, ids)
    return ids


def _opts(idx, kind):
    """(name, id) options, sorted by name in the *current* language each call —
    names are not cached, so the dropdown follows the selected language."""
    return sorted(((idx.name(i), i) for i in _opt_ids(idx, kind)),
                  key=lambda x: x[0].lower())


def _name_to_id(idx, kind, typed):
    """Resolve a typed item/monster name (case-insensitive, current language)
    back to its id, or '' if there's no exact match."""
    if not typed:
        return ""
    t = typed.strip().lower()
    for i in _opt_ids(idx, kind):
        if idx.name(i).lower() == t:
            return i
    return ""


def _has_melee(idx, iid):
    r = _resolved(idx, iid)
    return bool(r.get("bashing")) or bool(r.get("cutting"))


def _weapon_stats(idx, iid):
    r = _resolved(idx, iid)
    flags = idx.flags_of(iid)
    bash = int(r.get("bashing") or 0)
    cut = int(r.get("cutting") or 0)
    stab = 0
    if "STAB" in flags:          # finalize_pre swaps cut<->stab for STAB items
        stab, cut = cut, 0
    th = r.get("to_hit")
    th = int(th) if isinstance(th, (int, float)) else 0
    return {"w_bash": bash, "w_cut": cut, "w_stab": stab, "w_hit": th,
            "w_vol": int(_to_ml(r.get("volume")) or 0),
            "w_wt": int(_to_g(r.get("weight")) or 0)}


def _monster_stats(idx, mid):
    r = _resolved(idx, mid)
    sz = r.get("size")
    size = _MS.get(sz, (sz or "").lower() if (sz or "").lower() in _OCC else "medium")
    return {"t_dodge": int(r.get("dodge") or 0), "t_hp": int(r.get("hp") or 1),
            "a_bash": int(r.get("armor_bash") or 0), "a_cut": int(r.get("armor_cut") or 0),
            "a_stab": int(r.get("armor_stab") or 0), "a_bullet": int(r.get("armor_bullet") or 0),
            "size": size}


def _gun_stats(idx, gid):
    r = _resolved(idx, gid)
    return {"gun_disp": int(r.get("dispersion") or 0)}


def _ammo_stats(idx, aid):
    r = _resolved(idx, aid)
    dmg = r.get("damage")
    amt = pen = 0
    if isinstance(dmg, dict):
        amt = int(dmg.get("amount") or 0)
        pen = int(dmg.get("armor_penetration") or 0)
    elif isinstance(dmg, (int, float)):
        amt = int(dmg)
    return {"rng_dmg": amt, "rng_pen": pen}


# ---------------------------------------------------------------------------
# melee model (transcribed from melee.cpp)
# ---------------------------------------------------------------------------
def _crit_chance(p, hit_roll, tdodge5):
    ath = p["w_hit"]
    wcc = 0.5
    if ath > 0:
        wcc = max(wcc, 0.5 + 0.1 * ath)
    elif ath < 0:
        wcc += 0.1 * ath
    wcc = _cl(wcc, 0.0, 1.0)
    scc = _cl(0.25 + 0.01 * p["dex"] + 0.02 * p["per"], 0.0, 1.0)
    sk = p["sk_weapon"] + p["sk_melee"] / 2.5
    kcc = _cl(0.25 + 0.025 * sk, 0.0, 1.0)
    triple = wcc * scc * kcc
    if hit_roll > tdodge5 * 1.5:
        return triple + 0.5 * (wcc * scc + scc * kcc + wcc * kcc - 3 * triple)
    return triple


def _roll_units(rng, p, crit):
    units = []
    # bash
    skill, stat = p["sk_weapon"], p["str"]
    stat_bonus = rng.uniform(stat / 2.0, stat)
    wd = p["w_bash"] + stat_bonus
    cap = 2 * stat + 2 * skill
    mul = 0.8 + 0.08 * skill if skill < 5 else 0.96 + 0.04 * skill
    if cap < wd and p["w_bash"] > 0:
        mul *= (1.0 + cap / wd) / 2.0
    bmin = min(1.0, stat / 20.0) * wd
    wd = rng.uniform(bmin, wd)
    amult, arpen = 1.0, 0.0
    if crit:
        mul *= 1.5
        amult *= 0.5
    units.append((wd, arpen, amult, mul, p["a_bash"]))
    # cut
    if p["w_cut"] > 0:
        s = p["sk_weapon"]
        m = 0.8 + 0.08 * s if s < 5 else 0.96 + 0.04 * s
        amult, arpen = 1.0, 0.0
        if crit:
            m *= 1.25
            arpen += 5
            amult = 0.75
        units.append((p["w_cut"], arpen, amult, m, p["a_cut"]))
    # stab
    if p["w_stab"] > 0:
        s = p["sk_weapon"]
        m = 0.66 + 0.1 * s if s <= 5 else 0.86 + 0.06 * s
        amult, arpen = 1.0, 0.0
        if crit:
            m *= 1.0 + s / 10.0
            amult *= 0.66
        units.append((p["w_stab"], arpen, amult, m, p["a_stab"]))
    return units


def _resolve_dmg(units):
    total = 0
    for amount, res_pen, res_mult, dmg_mult, arm in units:
        eff = max(arm - res_pen, 0.0) * res_mult
        total += int(max(0.0, amount - eff) * dmg_mult)
    return total


def _attack_cost(p):
    base = 65 + p["w_vol"] / 62.5 + p["w_wt"] / 60.0
    b = base / 2.0
    move = b + b * (15 - p["sk_melee"]) / 15.0 - p["dex"]
    return max(25.0, move)


def _melee_sim(p):
    hit_val = p["dex"] / 4.0 + (p["sk_weapon"] / 3.0 + p["sk_melee"] / 2.0 + p["w_hit"])
    tdodge5 = p["t_dodge"] * 5.0
    size_pen = _SIZE_PEN[p["size"]]
    hit_chance = _phi((hit_val * 5.0 - tdodge5 - size_pen) / 25.0)
    rng = random.Random(_seed(p))
    hits = crits = 0
    swings = []
    for _ in range(_TRIALS):
        # one hit roll, reused for both the hit/miss test and the crit high-roll
        # bonus (engine: Character::melee_attack rolls hit_roll once, melee.cpp)
        hit_roll = rng.gauss(hit_val * 5.0, 25.0)
        if hit_roll - tdodge5 - size_pen < 0:
            swings.append(0)
            continue
        hits += 1
        crit = rng.random() < _crit_chance(p, hit_roll, tdodge5)
        crits += crit
        swings.append(_resolve_dmg(_roll_units(rng, p, crit)))
    avg_swing = sum(swings) / len(swings)
    move = _attack_cost(p)
    aps = 100.0 / move
    dps = avg_swing * aps
    return {
        "hit_chance": hit_chance, "crit": (crits / hits) if hits else 0.0,
        "avg_hit": (sum(swings) / hits) if hits else 0.0, "avg_swing": avg_swing,
        "move": move, "aps": aps, "dps": dps, "extra": hit_val,
        "ttk": (p["t_hp"] / dps) if dps > 0 else float("inf"), "dist": swings,
    }


# ---------------------------------------------------------------------------
# ranged model (transcribed from ranged.cpp / ballistics.cpp / creature.cpp)
# ---------------------------------------------------------------------------
def _disp_from_skill(s, wd):
    if s >= 10:
        return 0.0
    pen = 3 * (10 - s)
    if s >= 5:
        return pen + wd * (10 - s) * 1.25 / 5.0
    return pen + wd * (1.25 + (5 - s) * 3.75 / 5.0)


def _rng_normal(rng, hi):
    if hi <= 0:
        return 0.0
    return _cl(rng.gauss(hi / 2.0, hi / 4.0), 0.0, hi)


def _ranged_sim(p):
    wd = p["gun_disp"]
    avg_skill = min(10.0, (p["sk_gun"] + p["sk_weapon"]) / 2.0)
    linear = [max((20 - p["dex"]) * 0.5, 0.0), _disp_from_skill(avg_skill, wd), p["recoil"]]
    frac = _OCC[p["size"]]
    rng = random.Random(_seed(p))
    hits = aimed = 0
    disp_sum = 0.0
    shots = []
    for _ in range(_TRIALS):
        disp = sum(rng.uniform(0.0, L) for L in linear) + _rng_normal(rng, wd)
        disp_sum += disp
        tiles = 2.0 * p["range"] * math.sin(math.radians(disp / 60.0) / 2.0)
        missed_by = min(1.0, tiles / frac) if frac > 0 else 1.0
        if missed_by >= 1.0:
            shots.append(0)
            continue
        diff = sum(rng.randint(1, int(p["proj_speed"])) for _ in range(10))
        dadj = p["t_dodge"] * 5.0 / diff if diff > 0 else 0.0
        if dadj < 0.01:
            dadj = 0.0
        goodhit = missed_by + _cl(dadj, 0.0, 1.0)
        if goodhit >= 1.0:
            shots.append(0)
            continue
        hits += 1
        if goodhit > 0.8:
            sev = max(0.01, 4.0 * (1.0 - goodhit))
        elif goodhit > 0.5:
            sev = 1.6 - goodhit
        elif goodhit > 0.2:
            sev = 1.766 - goodhit * 4.0 / 3.0
        else:
            sev = 1.5
            aimed += 1
        amount, mult = float(p["rng_dmg"]), 1.0
        if goodhit > 0.8:            # graze: multiply before armor
            amount *= sev
        else:
            mult *= sev
        eff = max(p["a_bullet"] - p["rng_pen"], 0.0)
        shots.append(int(max(0.0, amount - eff) * mult))
    avg_shot = sum(shots) / len(shots)
    return {
        "hit_chance": hits / _TRIALS, "crit": (aimed / hits) if hits else 0.0,
        "avg_hit": (sum(shots) / hits) if hits else 0.0, "avg_swing": avg_shot,
        "stk": (p["t_hp"] / avg_shot) if avg_shot > 0 else float("inf"),
        "avg_disp": disp_sum / _TRIALS, "dist": shots,
    }


def _seed(p):
    return abs(hash(tuple(sorted((k, p[k]) for k in p)))) % (2 ** 31)


def _histogram(vals, bins=10):
    mx = max(vals) if vals else 0
    if mx <= 0:
        return [("0", len(vals), 1.0, 1.0)]
    width = max(1, math.ceil((mx + 1) / bins))
    counts = [0] * (bins + 1)
    for d in vals:
        counts[min(bins, int(d) // width)] += 1
    n = len(vals)
    peak = max(counts) or 1
    out = []
    for i, c in enumerate(counts):
        if c == 0 and i > mx // width:
            continue
        lo = i * width
        label = "0" if (i == 0 and width == 1) else ("%d–%d" % (lo, lo + width - 1))
        out.append((label, c, c / n, c / peak))
    return out


# ---------------------------------------------------------------------------
# page
# ---------------------------------------------------------------------------
def render_sim(ctx, qs):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])

    def first(k, d=""):
        v = qs.get(k)
        return v[0] if v else d

    mode = first("mode", "melee")
    if mode not in ("melee", "ranged"):
        mode = "melee"
    fields = _M_FIELDS if mode == "melee" else _R_FIELDS

    p = {}
    for key, dflt, lo, hi in fields:
        try:
            p[key] = float(first(key, dflt))
        except ValueError:
            p[key] = float(dflt)
    szv = first("size")
    p["size"] = szv if szv in _OCC else "medium"

    # auto-fill from a freshly chosen item / monster (prev_* lets you then tweak).
    # the pickers are searchable text inputs holding the *name*; resolve to id.
    weapon = _name_to_id(idx, "weapon", first("weapon"))
    gun = _name_to_id(idx, "gun", first("gun"))
    ammo = _name_to_id(idx, "ammo", first("ammo"))
    monster = _name_to_id(idx, "monster", first("monster"))
    if mode == "melee":
        if weapon and weapon != first("prev_weapon") and weapon in idx.by_id:
            p.update(_weapon_stats(idx, weapon))
        if monster and monster != first("prev_monster") and monster in idx.by_id:
            ms = _monster_stats(idx, monster)
            for k in ("t_dodge", "a_bash", "a_cut", "a_stab", "t_hp"):
                p[k] = ms[k]
            p["size"] = ms["size"]
    else:
        if gun and gun != first("prev_gun") and gun in idx.by_id:
            p.update(_gun_stats(idx, gun))
        if ammo and ammo != first("prev_ammo") and ammo in idx.by_id:
            p.update(_ammo_stats(idx, ammo))
        if monster and monster != first("prev_monster") and monster in idx.by_id:
            ms = _monster_stats(idx, monster)
            p["t_dodge"], p["a_bullet"], p["t_hp"], p["size"] = (
                ms["t_dodge"], ms["a_bullet"], ms["t_hp"], ms["size"])

    for key, dflt, lo, hi in fields:
        p[key] = _cl(p[key], lo, hi)
        if key in _INT_KEYS:
            p[key] = int(round(p[key]))

    r = _melee_sim(p) if mode == "melee" else _ranged_sim(p)

    # ---- form ----
    hid = ('<input type=hidden name="ver" value="%d">'
           '<input type=hidden name="lang" value="%s">%s'
           '<input type=hidden name="prev_weapon" value="%s">'
           '<input type=hidden name="prev_gun" value="%s">'
           '<input type=hidden name="prev_ammo" value="%s">'
           '<input type=hidden name="prev_monster" value="%s">'
           % (ctx["ver"], h(ctx["lang"]),
              '<input type=hidden name="mods" value="1">' if ctx["mods"] else "",
              h(weapon), h(gun), h(ammo), h(monster)))

    def num(key):
        return ('<label class="simf"><span>%s</span>'
                '<input type=number name="%s" value="%s" step="1"></label>'
                % (h(T(ctx, "sim_" + key)), key, h(p[key])))

    def sel(name, kind, cur, ph_key):
        # searchable combobox: type to filter via native <datalist>; the input
        # holds the name and the server maps it back to the id on submit.
        dl = "".join('<option value="%s">' % h(nm) for nm, _i in _opts(idx, kind))
        val = idx.name(cur) if cur else ""
        return ('<label class="simf wide"><span>%s</span>'
                '<input name="%s" list="dl_%s" value="%s" placeholder="%s" '
                'autocomplete="off" onchange="this.form.submit()">'
                '<datalist id="dl_%s">%s</datalist></label>'
                % (h(T(ctx, "sim_pick_" + kind)), name, kind, h(val),
                   h(T(ctx, ph_key)), kind, dl))

    sizeopts = "".join('<option value="%s"%s>%s</option>'
                       % (s, " selected" if s == p["size"] else "", h(T(ctx, "sim_size_" + s)))
                       for s in _SIZES)
    size_field = ('<label class="simf"><span>%s</span><select name="size">%s</select></label>'
                  % (h(T(ctx, "sim_size")), sizeopts))

    modesel = ('<label class="simf"><span>%s</span><select name="mode" onchange="this.form.submit()">'
               '<option value="melee"%s>%s</option><option value="ranged"%s>%s</option>'
               '</select></label>'
               % (h(T(ctx, "sim_mode")), " selected" if mode == "melee" else "",
                  h(T(ctx, "sim_mode_melee")), " selected" if mode == "ranged" else "",
                  h(T(ctx, "sim_mode_ranged"))))

    def group(title, *fields_):
        return ('<div class="simgroup"><div class="section">%s</div>'
                '<div class="simgrid">%s</div></div>'
                % (h(title), "".join(fields_)))

    if mode == "melee":
        body_form = (
            group(T(ctx, "sim_attacker"), num("str"), num("dex"), num("per"),
                  num("sk_melee"), num("sk_weapon")) +
            group(T(ctx, "sim_weapon"), sel("weapon", "weapon", weapon, "sim_pick_custom"),
                  num("w_bash"), num("w_cut"), num("w_stab"), num("w_hit"),
                  num("w_vol"), num("w_wt")) +
            group(T(ctx, "sim_target"), sel("monster", "monster", monster, "sim_pick_custom"),
                  num("t_dodge"), num("a_bash"), num("a_cut"), num("a_stab"),
                  num("t_hp"), size_field))
    else:
        body_form = (
            group(T(ctx, "sim_attacker"), num("dex"), num("per"), num("sk_gun"),
                  num("sk_weapon")) +
            group(T(ctx, "sim_gun"), sel("gun", "gun", gun, "sim_pick_custom"),
                  num("gun_disp"), num("recoil"), num("range")) +
            group(T(ctx, "sim_ammo"), sel("ammo", "ammo", ammo, "sim_pick_custom"),
                  num("rng_dmg"), num("rng_pen"), num("proj_speed")) +
            group(T(ctx, "sim_target"), sel("monster", "monster", monster, "sim_pick_custom"),
                  num("t_dodge"), num("a_bullet"), num("t_hp"), size_field))

    form = ('<form class="simform" method="get" action="/sim">%s'
            '<div class="simgrid">%s</div>%s'
            '<button type="submit" class="simrun">%s</button></form>'
            % (hid, modesel, body_form, h(T(ctx, "sim_run"))))

    # ---- results ----
    def stat(label, value, sub=""):
        return ('<div class="simstat"><div class="sv">%s</div><div class="sl">%s</div>%s</div>'
                % (h(value), h(label),
                   ('<div class="ss">%s</div>' % h(sub)) if sub else ""))

    if mode == "melee":
        ttk = "∞" if r["ttk"] == float("inf") else ("%.1f" % r["ttk"])
        cards = "".join([
            stat(T(ctx, "sim_hitchance"), "%.1f%%" % (r["hit_chance"] * 100),
                 T(ctx, "sim_hit_sub", v="%.1f" % r["extra"])),
            stat(T(ctx, "sim_critchance"), "%.1f%%" % (r["crit"] * 100)),
            stat(T(ctx, "sim_dmg_hit"), "%.1f" % r["avg_hit"]),
            stat(T(ctx, "sim_dmg_swing"), "%.1f" % r["avg_swing"]),
            stat(T(ctx, "sim_movecost"), "%d" % round(r["move"]),
                 T(ctx, "sim_atk_sub", v="%.2f" % r["aps"])),
            stat(T(ctx, "sim_dps"), "%.1f" % r["dps"]),
            stat(T(ctx, "sim_ttk"), ttk + " s"),
        ])
        dist_label = T(ctx, "sim_dist", n=_TRIALS)
    else:
        stk = "∞" if r["stk"] == float("inf") else ("%.1f" % r["stk"])
        cards = "".join([
            stat(T(ctx, "sim_hitchance"), "%.1f%%" % (r["hit_chance"] * 100)),
            stat(T(ctx, "sim_aimed"), "%.1f%%" % (r["crit"] * 100)),
            stat(T(ctx, "sim_dmg_hit"), "%.1f" % r["avg_hit"]),
            stat(T(ctx, "sim_dmg_shot"), "%.1f" % r["avg_swing"]),
            stat(T(ctx, "sim_avgdisp"), "%d" % round(r["avg_disp"]), "MoA"),
            stat(T(ctx, "sim_shots_kill"), stk),
        ])
        dist_label = T(ctx, "sim_dist_shot", n=_TRIALS)

    rows = "".join(
        '<div class="hbar"><span class="hl">%s</span>'
        '<span class="htrack"><span class="hfill" style="width:%.1f%%"></span></span>'
        '<span class="hp">%.1f%%</span></div>'
        % (h(label), rel * 100, frac * 100)
        for label, c, frac, rel in _histogram(r["dist"]))
    hist = '<div class="section">%s</div><div class="hist">%s</div>' % (h(dist_label), rows)

    assume = "sim_assume" if mode == "melee" else "sim_assume_r"
    body = ('<h1 class="item">%s</h1><p class="hint">%s</p>%s'
            '<div class="simresults">%s</div>%s'
            '<p class="mechnote">%s</p>'
            % (h(T(ctx, "sim_title")), h(T(ctx, "sim_hint")), form,
               cards, hist, h(T(ctx, assume))))
    return page("%s — CDDA Recipes" % T(ctx, "sim_title"), body, ctx, nav="sim")
