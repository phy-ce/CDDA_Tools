[한국어](README.md) | **English**

# Cataclysm Installer & Version Manager (CDDA / CDBN)

A Windows GUI. Download and install any version from the official GitHub
releases, then pick from your installed versions to launch, delete, or manage mods.

**Two games supported**:
- **CDDA** — Cataclysm: Dark Days Ahead (mainline)
- **CDBN** — Cataclysm: Bright Nights (fork/variant)

Each game installs into a separate folder (`~/Games/Cataclysm-DDA`, `~/Games/Cataclysm-BN`).
**Language**: a toggle at the top of the window switches between **Korean / English** in real time.

## Install / Run

**Option 1 — exe (no Python required)**
Download the latest `CDDA-Manager.exe` from the [Releases](../../../releases) page and double-click it.

**Option 2 — run from source** (only Python needed; Windows usually bundles tkinter)
```
double-click cdda_installer.pyw
```
or: `python cdda_installer.pyw`

> The modern theme comes from the optional dependency **ttkbootstrap** (`pip install ttkbootstrap`).
> Without it the app falls back to standard tkinter, so it runs either way. The exe bundles it.
> A toggle at the top-right switches **Light / Dark / Purple** themes live (default: Dark, when ttkbootstrap is present).

## Layout (2 tabs)

### [Library] tab — first screen
**All CDDA and CDBN installs** appear in one unified table (game / version / channel / install date).
- **Double-click** or **▶ Run** : launch that version
- **🧩 Content** : open the content manager for the selected version (mods/soundpacks/tilesets/fonts, see below)
- **Open folder** : open the install folder in Explorer
- **🗑 Delete** : permanently delete the version + its saves

### [Install] tab
1. **Game**: choose CDDA / CDBN
2. **Channel**: experimental (daily builds) / official release (stable)
3. **Version**: pick a specific build from the dropdown
4. **Edition**: graphics+sound (recommended) / graphics only / terminal (the `pdb` debug symbols are excluded automatically)
5. **Base install folder**: per-version subfolders are created automatically inside this folder

Installing extracts to `base-folder/<version-tag>/`. Already-installed versions show the button as **Installed ✓**.

## Content Management (mods / soundpacks / tilesets / fonts)

In the Library tab, select a version and press **🧩 Content** to open a window with 4 tabs.
**Both bundled and added** items are shown (marked in the "Type" column); **bundled items are
protected from deletion** and only items added with this tool can be removed.

| Resource | Install location | Identified by |
|---|---|---|
| Mods | `data/mods/<folder>/` | `modinfo.json` |
| Soundpacks | `data/sound/<folder>/` | `soundpack.txt` |
| Tilesets | `gfx/<folder>/` | `tileset.txt` |
| Fonts | `data/font/*.ttf .otf .ttc` | individual files |

- **🌐 Add from URL** : a GitHub repo URL or a direct zip (fonts also accept a `.ttf` link) → download & install.
- **➕ Add zip / Add file** : pick a local zip (the Fonts tab also accepts font files).
- **🗑 Remove** / **Open folder**

When adding, the tool finds folders containing the identifier file (`modinfo.json`/`soundpack.txt`/`tileset.txt`),
or font files for the Fonts tab, copies them to the target folder, and leaves a `.cdda_added` marker. Only
marked items count as "Added" and can be deleted; unmarked bundled content is protected.

### Applying a font

CDDA only uses fonts referenced by `config/fonts.json`, even if the file sits in `data/font/`
(there is no in-game font picker). Fonts tab buttons:

- **🪟 System**: pick **fonts installed on Windows** (search, multi-select) and copy them into `data/font/`
- **➕ Add file**: add a local font file / zip
- **🅰 Edit / Apply**: write the font and size into the game config

**🅰 Edit / Apply** flow:
0. (with Pillow installed) a **preview** of the selected font is shown — Latin/Korean/Kanji sample.
1. Choose where to apply it — Main (game text) / Menus (GUI) / Map / Overmap.
2. (optional) Enter a **font size** — Width (FONT_WIDTH) / Height (FONT_HEIGHT) / Size (FONT_SIZE).
3. On apply:
   - **Typeface**: `config/fonts.json` gets that font as the primary (first) entry, keeping existing as fallback.
   - **Size**: `config/options.json` `FONT_WIDTH/HEIGHT/SIZE` values are updated.
   - The previous configs are backed up as `.bak`; restart the game to see the change.

> Defaults: all four areas use **Terminus.ttf** (+ unifont fallback); size is **width 8 / height 16 / size 16**.
> Width/height are the pixel size of one character cell; size is the glyph render size inside the cell
> (usually raised together). Typeface can differ per area (main/menu/map/overmap); sizes are three
> separate sets (main/map/overmap — the menu has no separate size). This dialog exposes the four
> typefaces plus the main size.

`config/fonts.json` is seeded from `data/fontdata.json`, and `config/options.json` is created,
on first run. Formats follow the upstream docs/source (`doc/user-guides/FONT_OPTIONS.md`,
`src/options.cpp`). The size fields are enabled only when `options.json` exists (game run once).
Bundled fonts (Terminus/unifont, etc.) are delete-protected.

> Note: finer settings (map/overmap font sizes, etc.) can also be changed in-game via
> **Options → Graphics** — both write to the same `options.json`.

> CDDA has no central content repository/API, so a "browse a list and pick" approach isn't possible.
> Instead you fetch via a GitHub URL or zip/file link (most content lives on GitHub).

## Per-version independent saves

Each version installs independently inside its own folder, so saves are kept separate too.
Experimental builds frequently break save compatibility, but with this structure they don't affect one another.
(Each folder records version/game info in `.cdda_meta.json`, which the Library tab reads.)

## How it works

It fetches the release list from each game's GitHub Releases API and **dynamically parses**
the Windows zip assets by name (handling both the CDDA and CDBN naming conventions, excluding `pdb` debug symbols).
Stable releases get buried deep in the list under the daily experimental builds, so they are
fetched via `/releases/latest` plus a direct lookup of known stable tags.
When a new stable major is released, just add one line for its tag to `GAMES[...]["stable_tags"]` in the code.

## Build your own .exe

```
pip install pyinstaller ttkbootstrap pillow
pyinstaller --onefile --noconsole --name CDDA-Manager --collect-all ttkbootstrap cdda_installer.pyw
```
The output is `dist/CDDA-Manager.exe`.
Pushing a `v*` tag triggers GitHub Actions (`.github/workflows/build.yml`) to automatically
build the exe and attach it to that Release.

> `--onefile` exe builds can occasionally trigger antivirus false positives (a known PyInstaller trait).

## Limitations

- Windows only. Linux/macOS would need changes to the launch / open-folder parts.
- The very latest experimental build may still be uploading assets, so it is automatically excluded from the list.
