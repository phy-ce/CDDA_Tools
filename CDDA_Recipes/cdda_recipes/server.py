import socket
import threading
import webbrowser

from urllib.parse import parse_qs, urlparse
from http.server import BaseHTTPRequestHandler, HTTPServer

from . import state
from .config import SETTINGS
from .installs import find_installs
from .htmlutil import h
from .render import (render_item, render_group, render_loot, render_mechanics,
                     suggest_json, render_flag, render_skill, render_quality,
                     render_monster, render_category, render_search,
                     render_landing, render_settings)

# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------
def parse_ctx(qs):
    def first(k, d=""):
        v = qs.get(k)
        return v[0] if v else d
    try:
        ver = int(first("ver", "0"))
    except ValueError:
        ver = 0
    ver = max(0, min(ver, len(state.INSTALLS) - 1))
    return {"ver": ver, "lang": first("lang", "en") or "en",
            "mods": first("mods", "") in ("1", "true", "on"),
            "item_id": first("id", "")}



class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, status=200, content_type="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        ctx = parse_ctx(qs)

        def first(k, d=""):
            v = qs.get(k)
            return v[0] if v else d

        try:
            if u.path == "/item" and ctx["item_id"]:
                self._send(render_item(ctx))
            elif u.path == "/group" and first("group"):
                self._send(render_group(ctx, first("group")))
            elif u.path == "/loot":
                self._send(render_loot(ctx))
            elif u.path == "/mechanics":
                self._send(render_mechanics(ctx))
            elif u.path == "/suggest":
                self._send(suggest_json(ctx, first("q")),
                           content_type="application/json; charset=utf-8")
            elif u.path == "/flag" and first("flag"):
                self._send(render_flag(ctx, first("flag")))
            elif u.path == "/skill" and first("id"):
                self._send(render_skill(ctx, first("id")))
            elif u.path == "/quality" and first("id"):
                self._send(render_quality(ctx, first("id")))
            elif u.path == "/monster" and first("id"):
                self._send(render_monster(ctx, first("id")))
            elif u.path == "/settings":
                saved = first("save") == "1"
                if saved:                       # checkbox absent => unchecked
                    SETTINGS["npc_loot"] = first("npc_loot") in ("1", "true", "on")
                self._send(render_settings(ctx, saved))
            elif first("cat"):
                maxlv = first("maxlv")
                maxlv = int(maxlv) if maxlv.isdigit() else None
                self._send(render_category(ctx, first("cat"), first("skill"), maxlv))
            elif first("q"):
                self._send(render_search(ctx, first("q")))
            else:
                self._send(render_landing(ctx))
        except Exception as e:
            self._send("<pre>error: %s</pre>" % h(e), 500)



def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p



def main():
    state.INSTALLS = find_installs()
    if not state.INSTALLS:
        print("No CDDA installs found under ~/Games/Cataclysm-DDA|BN.")
        print("Install a version with CDDA_Installer first.")
        return
    print("Indexing %s …" % state.INSTALLS[0]["label"].strip())
    state.get_index(0, False)          # preload default so the first page is instant
    port = _free_port()
    url = "http://127.0.0.1:%d/" % port
    httpd = HTTPServer(("127.0.0.1", port), Handler)
    threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    print("CDDA Recipe Helper running at %s" % url)
    print("To stop: close this window, or press Ctrl+C.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    print("stopped.")

