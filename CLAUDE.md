# CLAUDE.md

Guidance for working in the **CDDA_Tools** repository.

## What this repo is

Tools for **Cataclysm: Dark Days Ahead (CDDA)** and its fork
**Cataclysm: Bright Nights (CDBN)**.

- `CDDA_Installer/` — Windows tkinter GUI: install/manage game versions, and manage
  mods / soundpacks / tilesets / fonts per install.
- `CDDA_Recipes/` — offline crafting helper.

## Source of truth: the official CDDA `doc/` folder

When writing or changing any code that touches **game mechanics, file formats,
directory layout, or config files**, base it on the official Cataclysm
documentation — **not** on assumptions or memory.

- **Primary reference:** the `doc/` folder of the upstream repo
  `CleverRaven/Cataclysm-DDA` (for example `doc/user-guides/FONT_OPTIONS.md`
  for the font/config format).
- For CDBN-specific behavior, also check `cataclysmbn/Cataclysm-BN` `doc/`.
- **Verify concrete formats against the game's `data/` folder**, e.g.
  `data/fontdata.json`, `gfx/<tileset>/tileset.txt`,
  `data/sound/<pack>/soundpack.txt`, `data/mods/<mod>/modinfo.json`.
- If the docs and the actual data disagree, prefer the data (what the game
  really reads) and note the discrepancy.
- Do not hardcode asset/file-naming rules the docs say may change; parse
  dynamically where possible.

When unsure how a CDDA feature works, read the relevant file under `doc/` first,
then confirm against `data/`, before writing code.

## Format references already relied on

- **Fonts:** `config/fonts.json` (created from `data/fontdata.json` on first run).
  Categories: `typeface`, `gui_typeface`, `map_typeface`, `overmap_typeface`.
  Each entry is a path string or `{ "path": ..., "hinting": ... }`.
  See `doc/user-guides/FONT_OPTIONS.md`.
- **Mods:** `data/mods/<id>/modinfo.json` (object with `type: MOD_INFO`).
- **Soundpacks:** `data/sound/<name>/soundpack.txt` (`NAME:` line).
- **Tilesets:** `gfx/<name>/tileset.txt` (`NAME:` line).

## Conventions for CDDA_Installer

- Windows-only; **standard library only** (tkinter) — no third-party dependencies.
- All user-facing strings go through the i18n table (`STRINGS` + `t()`), with both
  Korean (`ko`) and English (`en`) entries. Keep both languages in sync.
- Bundled (built-in) game content is **delete-protected**; only items this tool
  added (marked with a `.cdda_added` file) may be removed.
- Each game/version installs into its own isolated folder; never mix saves.
- Launch the game with its own folder as the working directory (CDDA needs
  `cwd` to be the game root to find `data/`).
