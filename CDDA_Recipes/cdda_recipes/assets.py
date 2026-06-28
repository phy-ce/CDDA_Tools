from . import state
from .i18n import LOCALE_NAMES, T
from .htmlutil import h
from .config import BROWSE_TYPES

PAGE_CSS = """
/* one palette, two themes — every colour is a variable so light AND dark
   stay consistent (the OS 'prefers-color-scheme' picks which) */
:root {
  color-scheme: light dark;
  --bg:#f4f5f7; --fg:#1c1f23; --panel:#ffffff; --panel2:#fff;
  --border:#e2e6ea; --border2:#cdd2d8; --muted:#6b7280; --faint:#8a929c;
  --link:#1558d6; --red:#d23a2e; --green:#2b8a3e;
  --pill-bg:#9aa3ad; --pill-fg:#ffffff; --hover:#e9edf2;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg:#16181d; --fg:#e6e8eb; --panel:#232730; --panel2:#2a2f3a;
    --border:#363b45; --border2:#3a4150; --muted:#9aa3ad; --faint:#7e8893;
    --link:#6ea8ff; --red:#ff8478; --green:#5cc777;
    --pill-bg:#4a515c; --pill-fg:#eef1f5; --hover:#2a2f3a;
  }
}
* { box-sizing: border-box; }
body { font-family: "Segoe UI", system-ui, sans-serif; margin: 0;
       background: var(--bg); color: var(--fg); }
header { position: sticky; top: 0; background: var(--panel);
         border-bottom: 1px solid var(--border);
         padding: 10px 16px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; z-index: 5; }
header .brand { font-weight: 700; margin-right: 6px; white-space: nowrap; }
header select, header input[type=search] { padding: 6px 8px; border: 1px solid var(--border2);
         border-radius: 7px; font-size: 14px; background: var(--panel2); color: var(--fg); }
header input[type=search] { min-width: 220px; flex: 1; }
header label { font-size: 13px; color: var(--muted); display: flex; align-items: center; gap: 4px; }
.wrap { max-width: 920px; margin: 18px auto; padding: 0 16px; }
h1.item { font-size: 22px; margin: 0 0 2px; }
.idtag { font: 12px ui-monospace, Consolas, monospace; color: var(--faint); }
.recipe { background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
          padding: 12px 14px; margin: 14px 0; }
.rtitle { font-weight: 700; color: var(--red); margin-bottom: 10px; font-size: 15px; }
.f { display: flex; gap: 12px; padding: 3px 0; align-items: baseline; }
.f .k { color: var(--muted); min-width: 132px; flex: none; font-size: 13px;
        text-align: right; }
.f .v { flex: 1; min-width: 0; }
.diff { color: var(--faint); font-size:12px; } .semi{ color: var(--faint); } .amp{ color: var(--faint); }
.or { font-size: 11px; color: var(--pill-fg); background: var(--pill-bg); border-radius: 4px;
      padding: 0 5px; margin: 0 2px; vertical-align: 1px; }
.qty { color: var(--muted); } .listreq { color: inherit; }
a.item { color: var(--link); text-decoration: none; }
a.item:hover { text-decoration: underline; }
ul.ing { margin: 6px 0 0; padding-left: 20px; } ul.ing li { padding: 2px 0; }
.muted { color: var(--faint); }
.section { margin: 20px 0 8px; font-weight: 700; font-size: 13.5px; color: var(--fg);
        border-bottom: 1px solid var(--border); padding-bottom: 5px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.chip { background: var(--panel); border: 1px solid var(--border2); border-radius: 999px;
        padding: 3px 11px; font-size: 13px; text-decoration: none; color: var(--link); }
.chip:hover { border-color: var(--link); }
.chip.loc { color: var(--muted); cursor: default; }
.chip.loc:hover { border-color: var(--border2); }
details.foundbox { margin-top: 0; }
details.foundbox > summary { cursor: pointer; list-style-position: inside; }
.cat { color: var(--muted); font-size: 13px; }
.tile { display: inline-block; image-rendering: pixelated; vertical-align: middle;
        background-repeat: no-repeat; zoom: 2; margin: 4px 0 8px;
        border: 1px solid var(--border); border-radius: 4px; }
pre.ascii { font: 12px/1.05 ui-monospace, Consolas, monospace; white-space: pre;
        overflow-x: auto; background: var(--panel); border: 1px solid var(--border);
        border-radius: 8px; padding: 8px 10px; margin: 8px 0; width: max-content;
        max-width: 100%; }
details.rawbox { margin: 14px 0; }
details.rawbox > summary { cursor: pointer; list-style-position: inside; }
.rawfields { margin-top: 6px; }
.rawfields .f { border-bottom: 1px solid var(--border); padding: 3px 0; }
.rawfields .k { min-width: 170px; font: 12px ui-monospace, Consolas, monospace; }
.rawfields code { font: 12px ui-monospace, Consolas, monospace; color: var(--fg);
        word-break: break-word; }
.results a { display: block; padding: 7px 10px; border-radius: 8px; color: inherit;
             text-decoration: none; }
.results a:hover { background: var(--hover); }
.results .rid { color: var(--faint); font: 11px ui-monospace, monospace; margin-left: 6px; }
.hint { color: var(--muted); margin-top: 24px; }
a.brand { text-decoration: none; color: inherit; }
a.gear { text-decoration: none; color: var(--muted); font-size: 18px; padding: 2px 6px; }
a.gear:hover { color: var(--fg); }
.desc { color: var(--muted); font-style: italic; margin: 6px 0 2px; }
.stats { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin: 8px 0 12px; }
.pill { background: var(--hover); border: 1px solid var(--border); border-radius: 999px;
        padding: 3px 11px; font-size: 13px; white-space: nowrap; color: var(--fg); }
.stats .atk { color: var(--green); font-weight: 600; cursor: help;
        text-decoration: underline dotted; text-underline-offset: 3px; }
details.treebox { margin-top: 10px; }
details.treebox > summary { cursor: pointer; color: var(--green); font-weight: 600; }
/* org-chart style tree: boxes connected by right-angle lines that branch/merge */
.treescroll { overflow-x: auto; padding: 8px 0 4px; }
ul.otree, ul.otree ul { position: relative; display: flex; justify-content: center;
        list-style: none; margin: 0; padding: 20px 0 0; }
ul.otree { padding-top: 2px; width: max-content; min-width: 100%; }
ul.otree li { position: relative; padding: 20px 9px 0; text-align: center; }
/* the elbow: each child draws a half-bus to the centre, plus a drop to itself */
ul.otree li::before, ul.otree li::after { content: ""; position: absolute; top: 0;
        right: 50%; width: 50%; height: 20px; border-top: 1px solid var(--border2); }
ul.otree li::after { right: auto; left: 50%; border-left: 1px solid var(--border2); }
ul.otree li:only-child::before, ul.otree li:only-child::after { display: none; }
ul.otree li:only-child { padding-top: 20px; }
ul.otree li:first-child::before, ul.otree li:last-child::after { border: 0 none; }
ul.otree li:last-child::before { border-right: 1px solid var(--border2);
        border-radius: 0 6px 0 0; }
ul.otree li:first-child::after { border-radius: 6px 0 0 0; }
ul.otree ul::before { content: ""; position: absolute; top: 0; left: 50%;
        height: 20px; border-left: 1px solid var(--border2); }
ul.otree .node { display: inline-block; border: 1px solid var(--border);
        background: var(--panel2); border-radius: 8px; padding: 5px 10px; white-space: nowrap; }
ul.otree .node.root { border-color: var(--link); font-weight: 600; }
ul.otree .node .alt { font-size: 11px; color: var(--muted); background: var(--hover);
        border-radius: 4px; padding: 0 4px; margin-left: 2px; cursor: pointer; }
ul.otree .node .alt:hover { color: var(--link); }
#altpop { position: absolute; z-index: 50; background: var(--panel);
        border: 1px solid var(--border2); border-radius: 8px; padding: 4px;
        box-shadow: 0 8px 28px rgba(0,0,0,.22); max-width: 300px; }
#altpop a, #altpop span { display: block; padding: 5px 10px; border-radius: 6px;
        text-decoration: none; font-size: 13px; }
#altpop a { color: var(--link); } #altpop a:hover { background: var(--hover); }
#altpop span { color: var(--muted); }
/* category grid + listing table + settings */
.catgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 10px; margin-top: 14px; }
.catcard { display: block; text-decoration: none; color: inherit; background: var(--panel);
        border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
.catcard:hover { border-color: var(--link); }
.catcard b { font-size: 16px; } .catcard span { color: var(--muted); font-size: 13px; }
table.cat { border-collapse: collapse; width: 100%; margin-top: 12px; }
table.cat th, table.cat td { text-align: left; padding: 6px 10px; border-bottom: 1px solid var(--border); }
table.cat th { color: var(--muted); font-weight: 600; font-size: 13px; }
table.cat td.lv, table.cat th.lv { text-align: right; color: var(--muted); width: 4em; }
table.cat tr:hover td { background: var(--hover); }
.filters { display: flex; gap: 10px; align-items: center; margin-top: 10px; flex-wrap: wrap; }
.filters select, .filters input { padding: 5px 8px; border: 1px solid var(--border2);
        border-radius: 7px; background: var(--panel2); color: var(--fg); }
.setrow { display: flex; gap: 10px; align-items: flex-start; margin: 14px 0; }
.setrow .help { color: var(--muted); font-size: 13px; }
.saved { color: var(--green); margin-left: 8px; }
/* left index sidebar + main column */
.layout { display: flex; align-items: flex-start; max-width: 1180px; margin: 0 auto; }
.layout > .wrap { flex: 1; min-width: 0; max-width: 920px; margin: 18px auto; }
.side { position: sticky; top: 53px; align-self: flex-start; width: 184px; flex: none;
        display: flex; flex-direction: column; gap: 2px; padding: 16px 8px;
        min-height: calc(100vh - 53px); }
.side .navlink { display: block; padding: 8px 12px; border-radius: 8px; font-size: 14px;
        color: var(--fg); text-decoration: none; }
.side .navlink:hover { background: var(--hover); }
.side .navlink.active { background: var(--hover); color: var(--link); font-weight: 600; }
.side .navspacer { flex: 1; min-height: 24px; }
@media (max-width: 720px) {
  .layout { flex-direction: column; }
  .side { position: static; flex-direction: row; flex-wrap: wrap; width: auto;
          min-height: 0; padding: 8px 12px; border-bottom: 1px solid var(--border); }
  .side .navspacer { display: none; }
}
/* loot-group probability list + mechanism note */
.mechnote { color: var(--muted); font-size: 13px; background: var(--hover);
        border-radius: 8px; padding: 8px 11px; margin: 12px 0; }
.mechnote a { color: var(--link); text-decoration: none; white-space: nowrap; }
ul.problist { list-style: none; margin: 8px 0; padding: 0; }
ul.problist li { display: flex; align-items: flex-start; gap: 10px; padding: 4px 2px;
        border-bottom: 1px solid var(--border); }
ul.problist .ent { flex: 1; min-width: 0; }
ul.problist.sub { margin: 6px 0 2px; padding-left: 12px; border-left: 2px solid var(--border); }
ul.problist.sub li { border-bottom: none; padding: 2px 0; }
.slot { color: var(--faint); font-size: 12px; font-style: italic; }
.chip.loc .locq { color: var(--faint); font-size: 11px; margin-left: 4px; }
.chip.flag { color: var(--link); font: 12px ui-monospace, Consolas, monospace;
        text-decoration: none; }
.chip.flag:hover { border-color: var(--link); }
/* click-to-expand "+N" for capped chip rows / lists */
details.morechips { margin-top: 6px; }
details.morechips > summary { display: inline-block; cursor: pointer; list-style: none;
        color: var(--link); }
details.morechips > summary::-webkit-details-marker { display: none; }
details.morechips > summary::marker { content: ""; }
details.morechips > summary:hover { border-color: var(--link); }
details.morechips[open] > summary { margin-bottom: 6px; }
/* search-box autocomplete dropdown */
#ac { display: none; position: absolute; top: 100%; left: 0; right: 0; z-index: 30;
      margin-top: 5px; background: var(--panel); border: 1px solid var(--border2);
      border-radius: 9px; max-height: 64vh; overflow: auto;
      box-shadow: 0 8px 28px rgba(0,0,0,.22); }
#ac a { display: flex; justify-content: space-between; align-items: baseline; gap: 12px;
        padding: 8px 12px; text-decoration: none; color: var(--fg); font-size: 14px; }
#ac a:hover { background: var(--hover); }
#ac .ack { color: var(--faint); font-size: 12px; white-space: nowrap; flex: none; }
.prob { font: 12px ui-monospace, Consolas, monospace; color: var(--muted);
        min-width: 3.6em; text-align: right; flex: none; padding-top: 1px; }
/* mechanics doc page */
.mech { max-width: 680px; } .mech h2 { font-size: 16px; margin: 20px 0 6px; }
.mech p { margin: 6px 0; line-height: 1.55; } .mech li { margin: 4px 0; line-height: 1.5; }
.mech ul { margin: 6px 0; padding-left: 20px; }
.mech code { background: var(--hover); border-radius: 4px; padding: 0 4px;
        font: 12px ui-monospace, Consolas, monospace; }
"""



def page(title, body, ctx, q="", nav=None):
    locs = state.locales_for(ctx["ver"])
    order = ["en", "ko", "ja"]
    codes = sorted(locs.keys(), key=lambda c: (order.index(c) if c in order else 99, c))
    vers = "".join('<option value="%d"%s>%s</option>'
                   % (i, " selected" if i == ctx["ver"] else "", h(inst["label"]))
                   for i, inst in enumerate(state.INSTALLS))
    langs = "".join('<option value="%s"%s>%s</option>'
                    % (c, " selected" if c == ctx["lang"] else "", h(LOCALE_NAMES.get(c, c)))
                    for c in codes)
    mods_chk = " checked" if ctx["mods"] else ""
    # settings form reloads the current page; search form goes to "/"
    if ctx.get("item_id"):
        action = "/item"
        hidden = '<input type=hidden name=id value="%s">' % h(ctx["item_id"])
    elif ctx.get("group_id"):
        action = "/group"
        hidden = '<input type=hidden name=group value="%s">' % h(ctx["group_id"])
    else:
        action, hidden = "/", ""
    header = """
<header>
  <a class="brand" href="/?ver=%(ver)d&lang=%(lang)s%(mods_q)s">🔧 %(brand)s</a>
  <form method="get" action="%(action)s" style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0;">
    %(hidden)s
    <select name="ver" onchange="this.form.submit()">%(vers)s</select>
    <select name="lang" onchange="this.form.submit()">%(langs)s</select>
    <label><input type=checkbox name="mods" value="1"%(mods_chk)s onchange="this.form.submit()"> %(mods_label)s</label>
  </form>
  <form method="get" action="/" style="display:flex;flex:1;gap:8px;margin:0;position:relative;">
    <input type=hidden name="ver" value="%(ver)d">
    <input type=hidden name="lang" value="%(lang)s">
    %(mods_hidden)s
    <input id="searchbox" autocomplete="off"
           data-sg="/suggest?ver=%(ver)d&lang=%(lang)s%(mods_q)s"
           type=search name="q" value="%(q)s" placeholder="%(search_ph)s" autofocus>
    <div id="ac"></div>
  </form>
</header>""" % {
        "action": action, "hidden": hidden, "vers": vers, "langs": langs,
        "mods_chk": mods_chk, "ver": ctx["ver"], "lang": h(ctx["lang"]),
        "mods_q": "&mods=1" if ctx["mods"] else "",
        "mods_hidden": '<input type=hidden name="mods" value="1">' if ctx["mods"] else "",
        "brand": h(T(ctx, "brand")), "mods_label": h(T(ctx, "mods")),
        "search_ph": h(T(ctx, "search_ph")), "q": h(q), "settings": h(T(ctx, "settings"))}
    # scroll each crafting tree so its (centered) root box is in view on load
    script = ("<script>addEventListener('load',function(){"
              "document.querySelectorAll('.treescroll').forEach(function(s){"
              "var r=s.querySelector('.node.root');if(!r)return;"
              "var a=r.getBoundingClientRect(),b=s.getBoundingClientRect();"
              "s.scrollLeft+=(a.left+a.width/2)-(b.left+b.width/2);});});</script>"
              # search-box autocomplete: debounced fetch to /suggest, dropdown of links
              "<script>(function(){var b=document.getElementById('searchbox'),"
              "ac=document.getElementById('ac');if(!b||!ac)return;var t,base=b.dataset.sg;"
              "function hide(){ac.style.display='none';ac.innerHTML='';}"
              "function esc(s){return s.replace(/[&<>\"]/g,function(c){"
              "return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c];});}"
              "b.addEventListener('input',function(){clearTimeout(t);"
              "var q=b.value.trim();if(!q){hide();return;}"
              "t=setTimeout(function(){fetch(base+'&q='+encodeURIComponent(q))"
              ".then(function(r){return r.json();}).then(function(d){"
              "if(!d.length){hide();return;}ac.innerHTML=d.map(function(it){"
              "return '<a href=\"'+esc(it.url)+'\"><span>'+esc(it.label)+"
              "'</span><span class=ack>'+esc(it.kind)+'</span></a>';}).join('');"
              "ac.style.display='block';}).catch(hide);},130);});"
              "b.addEventListener('blur',function(){setTimeout(hide,180);});"
              "addEventListener('keydown',function(e){if(e.key=='Escape')hide();});"
              "})();</script>"
              # crafting-tree "+N": click to pop up the alternative ingredients as links
              "<script>(function(){function esc(s){return String(s).replace("
              "/[&<>\"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;',"
              "'\"':'&quot;'}[c];});}document.addEventListener('click',function(ev){"
              "var ex=document.getElementById('altpop');if(ex)ex.remove();"
              "var t=ev.target.closest?ev.target.closest('.alt'):null;"
              "if(!t||!t.dataset.alts)return;ev.preventDefault();var d;"
              "try{d=JSON.parse(t.dataset.alts);}catch(e){return;}"
              "var p=document.createElement('div');p.id='altpop';p.innerHTML=d.map("
              "function(it){return it.url?'<a href=\"'+esc(it.url)+'\">'+esc(it.label)"
              "+'</a>':'<span>'+esc(it.label)+'</span>';}).join('');"
              "document.body.appendChild(p);var r=t.getBoundingClientRect();"
              "p.style.left=(window.scrollX+r.left)+'px';"
              "p.style.top=(window.scrollY+r.bottom+4)+'px';});})();</script>")
    # left index/nav; settings live at the bottom of it (not a top-corner gear)
    qsuf = "ver=%d&lang=%s%s" % (ctx["ver"], h(ctx["lang"]), "&mods=1" if ctx["mods"] else "")

    def nl(key, path, icon, label):
        cls = "navlink active" if nav == key else "navlink"
        return '<a class="%s" href="%s?%s">%s %s</a>' % (cls, path, qsuf, icon, h(label))

    base = [
        nl("items", "/", "📦", T(ctx, "nav_items")),
        nl("loot", "/loot", "🎒", T(ctx, "nav_loot")),
        nl("monsters", "/monsters", "🧟", T(ctx, "nav_monsters")),
        nl("skills", "/skills", "🎓", T(ctx, "nav_skills")),
        nl("qualities", "/qualities", "🛠", T(ctx, "nav_qualities")),
        nl("flags", "/flags", "🏷", T(ctx, "nav_flags")),
    ]
    base += [nl(route.lstrip("/"), route, icon, T(ctx, nav_key))
             for (typ, nav_key, icon, route) in BROWSE_TYPES]
    base.append(nl("mechanics", "/mechanics", "📖", T(ctx, "nav_mechanics")))
    links = "".join(base)
    side = ('<nav class="side">%s<div class="navspacer"></div>%s</nav>'
            % (links, nl("settings", "/settings", "⚙", T(ctx, "settings"))))
    return ("<!doctype html><html><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>%s</title><style>%s</style></head><body>%s"
            "<div class='layout'>%s<div class='wrap'>%s</div></div>%s</body></html>"
            % (h(title), PAGE_CSS, header, side, body, script))

