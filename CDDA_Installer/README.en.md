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

## Layout (2 tabs)

### [Library] tab — first screen
**All CDDA and CDBN installs** appear in one unified table (game / version / channel / install date).
- **Double-click** or **▶ Run** : launch that version
- **🧩 Mods** : open the mod manager for the selected version (see below)
- **Open folder** : open the install folder in Explorer
- **🗑 Delete** : permanently delete the version + its saves

### [Install] tab
1. **Game**: choose CDDA / CDBN
2. **Channel**: experimental (daily builds) / official release (stable)
3. **Version**: pick a specific build from the dropdown
4. **Edition**: graphics+sound (recommended) / graphics only / terminal (the `pdb` debug symbols are excluded automatically)
5. **Base install folder**: per-version subfolders are created automatically inside this folder

Installing extracts to `base-folder/<version-tag>/`. Already-installed versions show the button as **Installed ✓**.

## Mod Management

In the Library tab, select a version and press **🧩 Mods** to open the mod manager.
**Only mods added with this tool** appear in the list (the game's bundled mods are excluded).

- **🌐 Add from URL** : enter a GitHub repo URL or a direct zip link → download & install.
  A GitHub URL (`https://github.com/user/repo`) is automatically converted to the default-branch zip.
- **➕ Add zip** : pick a local mod zip to add (handles multiple files / multiple mods at once).
- **🗑 Remove** / **Open folder**

When adding, the tool finds folders containing a `modinfo.json` inside the zip/repo, copies them to `data/mods/`,
and leaves a `.cdda_added` marker file in each so they can be distinguished in the list.

> CDDA has no central mod repository/API, so a "browse a list and pick" approach isn't possible.
> Instead you fetch via a GitHub URL or zip link (most mods live on GitHub).

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
pip install pyinstaller
pyinstaller --onefile --noconsole --name CDDA-Manager cdda_installer.pyw
```
The output is `dist/CDDA-Manager.exe`.
Pushing a `v*` tag triggers GitHub Actions (`.github/workflows/build.yml`) to automatically
build the exe and attach it to that Release.

> `--onefile` exe builds can occasionally trigger antivirus false positives (a known PyInstaller trait).

## Limitations

- Windows only. Linux/macOS would need changes to the launch / open-folder parts.
- The very latest experimental build may still be uploading assets, so it is automatically excluded from the list.
