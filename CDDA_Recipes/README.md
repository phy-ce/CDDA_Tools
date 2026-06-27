# CDDA Recipe Helper

An offline crafting assistant for **Cataclysm: Dark Days Ahead / Bright Nights**.

It reads your installed game's `data/json` (optionally including added mods),
indexes every item, recipe, and requirement, and answers the two questions you
keep hitting while playing:

- **"How do I craft X?"** — ingredients (with their *OR* alternatives), required
  tools and tool-qualities, the skill + difficulty, crafting time, and how the
  recipe is learned (autolearn / from which book).
- **"What can I make with X?"** — the reverse index: every recipe that uses the
  selected item as a component.

Because everything is parsed straight from your local install, the answers always
match your **exact version and mods** — no network, no API key, no out-of-date wiki.

## Run

Requires Python 3.8+ (Windows usually bundles tkinter).

```
double-click cdda_recipes.pyw
```
or: `python cdda_recipes.pyw`

## Usage

1. **Version** — installs under `~/Games/Cataclysm-DDA` / `~/Games/Cataclysm-BN`
   (the folders [CDDA_Installer](../CDDA_Installer/README.md) creates) are detected
   automatically. Use **Browse…** to point at any other `data/json` folder.
2. **Include mods** — also parse `data/mods` so modded recipes show up.
3. **Lang** — switch the display language (English / 한국어 / 日本語 / … whatever the
   install ships). Names are translated using the game's own files, and you can
   search in the selected language too.
4. **Search** an item by name on the left, click it, and read the breakdown on the right.

## How it works

CDDA stores all game logic as JSON. The helper walks `data/json`, then:

- resolves item display names, following `copy-from` inheritance;
- expands `"LIST"` components and `using` blocks via the `requirement` entries
  they reference, so you see the real ingredients, not opaque list ids;
- merges tool / quality requirements pulled in through those requirements;
- skips `obsolete` recipe tombstones;
- builds a reverse "used as an ingredient in" index.

For localized names it loads the game's gettext catalogs from
`lang/mo/<locale>/LC_MESSAGES/*.mo` and translates each English name (falling
back to English for anything untranslated, e.g. a few abstract tool entries).

## Limitations

- Translations are only as complete as the game's own `.mo` files; a handful of
  strings (and most skill/quality edge cases) may stay English.
- Crafting trees are shown one level deep per requirement; it does not yet
  recursively expand a craftable ingredient into its own sub-recipe.
