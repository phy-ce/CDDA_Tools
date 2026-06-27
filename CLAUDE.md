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

## Third-party references

This repo is MIT; some other Cataclysm tools (e.g. the `cdda-guide` / `cbn-guide`
browsers) are GPL. Use them only to understand an algorithm or data format and
write our own implementation, grounded in CDDA's `doc/` and `data/`. No need to
note this in commits or comments — just keep the code original.

## Format references already relied on

- **Fonts:** `config/fonts.json` (created from `data/fontdata.json` on first run).
  Categories: `typeface`, `gui_typeface`, `map_typeface`, `overmap_typeface`.
  Each entry is a path string or `{ "path": ..., "hinting": ... }`.
  See `doc/user-guides/FONT_OPTIONS.md`.
- **Mods:** `data/mods/<id>/modinfo.json` (object with `type: MOD_INFO`).
- **Soundpacks:** `data/sound/<name>/soundpack.txt` (`NAME:` line).
- **Tilesets:** `gfx/<name>/tileset.txt` (`NAME:` line).
- **Loot groups (`item_group`):** the `subtype` decides the probability math —
  `collection` = each entry rolls independently (`prob` is a percent, default
  100), `distribution` = exactly one entry, weighted (`prob` / Σ`prob`). An entry
  may be an item, a `group` reference, or an inline `distribution`/`collection`.
  Things that fire a group: a MONSTER's `death_drops`, and mapgen placement keyed
  by `om_terrain`. Resolve nested groups by cascading (multiply down the tree).

## Conventions for CDDA_Installer

- Windows-only; **standard library only** (tkinter) — no third-party dependencies.
- All user-facing strings go through the i18n table (`STRINGS` + `t()`), with both
  Korean (`ko`) and English (`en`) entries. Keep both languages in sync.
- Bundled (built-in) game content is **delete-protected**; only items this tool
  added (marked with a `.cdda_added` file) may be removed.
- Each game/version installs into its own isolated folder; never mix saves.
- Launch the game with its own folder as the working directory (CDDA needs
  `cwd` to be the game root to find `data/`).

## Conventions for CDDA_Recipes

- Windows-friendly; **standard library only** — server-rendered HTML over
  `http.server`, opens in the browser. No third-party dependencies.
- User-facing UI strings go through `UI_STRINGS` + `T()` in **English (`en`),
  Korean (`ko`), and Japanese (`ja`)** — three languages; keep all in sync.
  (Note: CDDA_Installer is `ko`/`en` only.) Game content (item/recipe names and
  descriptions) is localized from the install's gettext `lang/mo/*.mo` files.
- Reads game data from the installs CDDA_Installer creates under
  `~/Games/Cataclysm-DDA|BN`; parse `data/json` (optionally `data/mods`),
  following `copy-from` inheritance and expanding `requirement`/`LIST` blocks.

## Build & release

- Pushing a `v*` tag triggers `.github/workflows/build.yml`, which builds both
  `CDDA-Manager.exe` and `CDDA-Recipes.exe` (PyInstaller, Windows) and attaches
  them to a single GitHub Release for that tag.
