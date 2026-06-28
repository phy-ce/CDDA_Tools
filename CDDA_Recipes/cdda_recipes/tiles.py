"""Tileset sprite lookup (standard library only).

Parses a tileset's ``tile_config.json`` and maps an entity id to a sprite cell
in one of the tilesheet PNGs. Sprites are never decoded here — the PNG is served
whole and cropped in the browser with CSS ``background-position`` — so no image
library is needed. PNG dimensions are read straight from the IHDR header.
"""
import os
import json
import struct


def _png_size(path):
    try:
        with open(path, "rb") as f:
            f.read(16)                       # 8 sig + 4 len + 4 "IHDR"
            return struct.unpack(">II", f.read(8))
    except Exception:
        return None


def _configured_tileset(install_root):
    """The tileset NAME chosen in config/options.json (the TILES option)."""
    try:
        opts = json.load(open(os.path.join(install_root, "config", "options.json"),
                              encoding="utf-8"))
    except Exception:
        return None
    for o in (opts if isinstance(opts, list) else []):
        if isinstance(o, dict) and o.get("name") == "TILES":
            return o.get("value")
    return None


def _tileset_dir(gfx_dir, want_name):
    """Folder whose tileset.txt NAME matches want_name; else the first that has
    a tile_config.json."""
    if not os.path.isdir(gfx_dir):
        return None
    fallback = None
    for d in sorted(os.listdir(gfx_dir)):
        full = os.path.join(gfx_dir, d)
        if not (os.path.isdir(full) and
                os.path.exists(os.path.join(full, "tile_config.json"))):
            continue
        if fallback is None:
            fallback = full
        name = None
        tp = os.path.join(full, "tileset.txt")
        if os.path.exists(tp):
            for ln in open(tp, encoding="utf-8", errors="ignore"):
                if ln.strip().upper().startswith("NAME:"):
                    name = ln.split(":", 1)[1].strip()
                    break
        if want_name and name == want_name:
            return full
    return fallback


def _first_sprite(fg):
    """A single representative sprite index from a tile's fg (int / list of ints
    or weighted dicts / dict)."""
    if isinstance(fg, int):
        return fg
    if isinstance(fg, list) and fg:
        x = fg[0]
        if isinstance(x, int):
            return x
        if isinstance(x, dict):
            return x.get("sprite")
    if isinstance(fg, dict):
        return fg.get("sprite")
    return None


def build_tileset(gfx_dir):
    """Parse the active tileset. Returns {dir, files, id2s} or None.
    files: [{file, base, cols, sw, sh, cells}] in declaration order.
    id2s:  {entity id -> global sprite index}."""
    if not gfx_dir:
        return None
    install_root = os.path.dirname(gfx_dir)
    tdir = _tileset_dir(gfx_dir, _configured_tileset(install_root))
    if not tdir:
        return None
    try:
        cfg = json.load(open(os.path.join(tdir, "tile_config.json"), encoding="utf-8"))
    except Exception:
        return None
    ti = (cfg.get("tile_info") or [{}])[0]
    dsw, dsh = ti.get("width", 32), ti.get("height", 32)
    files, id2s, base = [], {}, 0
    for fi in cfg.get("tiles-new", []):
        fn = fi.get("file")
        if not isinstance(fn, str):
            continue
        sw = fi.get("sprite_width", dsw) or dsw
        sh = fi.get("sprite_height", dsh) or dsh
        dim = _png_size(os.path.join(tdir, fn))
        cols = max(1, dim[0] // sw) if dim else 0
        cells = cols * (dim[1] // sh) if dim else 0
        files.append({"file": fn, "base": base, "cols": cols,
                      "sw": sw, "sh": sh, "cells": cells})
        for t in fi.get("tiles", []):
            s = _first_sprite(t.get("fg"))
            if s is None:
                continue
            ids = t.get("id")
            for i in (ids if isinstance(ids, list) else [ids]):
                if isinstance(i, str):
                    id2s.setdefault(i, s)
        base += cells
    return {"dir": tdir, "files": files, "id2s": id2s}


def sprite_pos(ts, sprite_idx):
    """(file_rel, x, y, w, h) for a global sprite index, or None."""
    for f in ts["files"]:
        if f["cells"] and f["base"] <= sprite_idx < f["base"] + f["cells"]:
            local = sprite_idx - f["base"]
            return (f["file"], (local % f["cols"]) * f["sw"],
                    (local // f["cols"]) * f["sh"], f["sw"], f["sh"])
    return None
