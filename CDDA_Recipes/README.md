# CDDA Recipe Helper

An offline crafting assistant for **Cataclysm: Dark Days Ahead / Bright Nights**.
It runs as a tiny **local web app** (standard library only) and opens in your
browser.

It reads your installed game's `data/json` (optionally including added mods),
indexes every item, recipe, requirement and disassembly, and answers the
questions you keep hitting while playing:

- **"How do I craft X?"** — ingredients (with their *OR* alternatives), required
  tools and tool-qualities, the skill + difficulty, crafting time, and how the
  recipe is learned (autolearn / from which book).
- **"What can I make with X?"** — the reverse index: every recipe that uses the
  selected item as a component.
- **"What do I get if I take X apart?"** — disassembly (`uncraft`) yields.
- **"Where do I find X?"** — the loot/item groups it spawns in.
- **"What's craftable in a category?"** — browse by category (weapons, food, …),
  filtered by skill and crafting level — handy when you don't know the item's name.

Because everything is parsed straight from your local install, the answers always
match your **exact version and mods** — no network, no API key, no out-of-date wiki.

## Run

Requires Python 3.8+ (no third-party packages).

- **Easiest:** double-click **`run.bat`**.
- Or from a terminal: `python cdda_recipes.py`

It indexes the game data, then opens `http://127.0.0.1:<port>/` in your default
browser.

**To stop it**, close the console window (the one `run.bat` / `python` opened) or
press **Ctrl+C** in it.

## Usage

- **Version** — installs under `~/Games/Cataclysm-DDA` / `~/Games/Cataclysm-BN`
  (the folders [CDDA_Installer](../CDDA_Installer/README.md) creates) are detected
  automatically; pick one from the dropdown.
- **Language** — switch the display language (English / 한국어 / 日本語 / … whatever
  the install ships). Both the **item names and the UI labels** are localized, and
  search matches the localized name, the English name, *or* the raw id — so you can
  type `acorn` even in Korean mode.
- **mods** — also parse `data/mods` so modded recipes show up.
- **Browse by category** — the home page lists categories (weapons, armor, food,
  …); open one for a sortable table you can filter by **skill** and **max level**.
  Good when you don't know an item's exact name.
- **Search** an item by name, click a result, and read the breakdown.
- **Click any item** to jump to it — a *forward* link on an ingredient/tool shows
  how to make that thing; the *"used as an ingredient in"* chips at the bottom are
  the *backlinks* the other way. Use your browser's Back/Forward to retrace.
- **🌳 Crafting tree** — each recipe shows a node-graph diagram (boxes joined by
  branching connector lines) of the product and its sub-ingredients. Each box is a
  single item (`+N` marks how many OR alternatives it has); click an item to focus
  its own tree, or scroll the diagram for wide chains.
- **Found in** — loot/item groups the item spawns in (count shown; long lists
  collapse). NPC-carried groups are hidden by default — enable them in **⚙ Settings**.
  Each group is **clickable like an item**: a group page lists what it can spawn,
  the groups it includes, and the groups it's part of — so you can navigate loot
  groups the same way you navigate items.
- **⚙ Settings** — a separate page for options (currently: show NPC-inventory sources).

## How it works

CDDA stores all game logic as JSON. The helper walks `data/json`, then:

- resolves item display names **and descriptions**, following `copy-from` inheritance;
- expands `"LIST"` components and `using` blocks via the `requirement` entries
  they reference, so you see the real ingredients, not opaque list ids;
- merges tool / quality requirements pulled in through those requirements;
- indexes `uncraft` entries for disassembly yields; skips `obsolete` recipe tombstones;
- groups craftable items by recipe `category`, with each item's lowest crafting level;
- reverse-indexes `item_group` definitions (a couple of levels deep) to list where
  an item spawns;
- builds a reverse "used as an ingredient in" index.

For localized names/descriptions it loads the game's gettext catalogs from
`lang/mo/<locale>/LC_MESSAGES/*.mo` and translates each English string (falling
back to English for anything untranslated, e.g. a few abstract tool entries).

The UI is server-rendered HTML over Python's `http.server` — no third-party
dependencies, matching the repo's standard-library-only convention.

## Limitations

- Translations are only as complete as the game's own `.mo` files; some strings
  (and a few skill/quality edge cases) may stay English.
- The crafting tree is depth- and size-capped to keep pages snappy; for anything
  beyond that, click an ingredient to open its own page.
- **"Found in"** is loot-*group* membership, not exact map coordinates — it tells
  you which spawn groups list the item, not the precise building tile.
