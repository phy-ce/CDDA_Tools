#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cataclysm 설치 & 버전 매니저 (Windows GUI) — CDDA / CDBN, 한국어/English
========================================================================
[설치] 탭 : 공식 stable / experimental 빌드 중 버전을 골라 다운로드·설치
[실행] 탭 : 설치된 여러 버전을 목록에서 골라 실행 / 삭제 / 모드 관리

- 게임(CDDA·CDBN)·버전마다 독립 폴더 + 독립 세이브
- 상단 언어 토글로 한국어/English 전환
- 표준 라이브러리(tkinter)만 사용 — 별도 설치 불필요
실행: cdda_installer.pyw 더블클릭  또는  python cdda_installer.pyw
"""

import os
import io
import re
import json
import time
import shutil
import zipfile
import tempfile
import subprocess
import threading
import traceback
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
# 모던 테마(ttkbootstrap)가 있으면 쓰고, 없으면 표준 ttk 로 폴백
# → exe 빌드 시엔 모던하게, 의존성 없이 .pyw 직접 실행도 그대로 동작.
try:
    import ttkbootstrap as ttk
    _TB_WINDOW = ttk.Window
    UI_THEME = "cosmo"   # 과하지 않은 밝은 플랫 테마
except Exception:
    from tkinter import ttk
    _TB_WINDOW = None
    UI_THEME = None

USER_AGENT = "CDDA-Installer/4.0 (+https://github.com/CleverRaven/Cataclysm-DDA)"
GITHUB_API = "https://api.github.com/repos"

# 지원 게임. CDBN(Bright Nights)은 CDDA의 포크라 릴리스 구조가 거의 같다.
# stable_tags: 정식 릴리스는 experimental에 밀려 목록 깊숙이 묻히므로 태그로 직접 조회.
#              /latest 가 최신 정식을 자동으로 잡아주고, 아래는 과거 정식 후보 목록.
GAMES = [
    {
        "key": "cdda",
        "name": "Cataclysm: Dark Days Ahead",
        "short": "CDDA",
        "repo": "CleverRaven/Cataclysm-DDA",
        "subdir": "Cataclysm-DDA",
        "stable_tags": ["0.I", "0.H", "0.G", "0.F", "0.E", "0.D", "0.C"],
    },
    {
        "key": "cdbn",
        "name": "Cataclysm: Bright Nights",
        "short": "CDBN",
        "repo": "cataclysmbn/Cataclysm-BN",
        "subdir": "Cataclysm-BN",
        "stable_tags": ["v0.12.0", "v0.11.0", "v0.10.0", "v0.9.0", "v0.8.0", "v0.7.0"],
    },
]
GAMES_BY_KEY = {g["key"]: g for g in GAMES}
# 각 게임은 이 폴더 아래 게임별 하위 폴더에, 다시 버전별 하위 폴더로 설치된다.
GAMES_ROOT = os.path.join(os.path.expanduser("~"), "Games")
META_NAME = ".cdda_meta.json"
# 이 도구로 추가한 모드 폴더에만 남기는 표시 파일(.json 이 아니라 게임이 무시함).
# 이게 있는 모드만 모드 관리 창에 보이게 해서 게임 번들 모드는 가린다.
MOD_MARKER = ".cdda_added"


# ---------------------------------------------------------------------------
# 다국어 (i18n)
# ---------------------------------------------------------------------------
STRINGS = {
    "ko": {
        "app_title": "Cataclysm 설치 & 버전 매니저 (CDDA / CDBN)",
        "lang_label": "언어 / Language:",
        "tab_install": "설치",
        "tab_run": "실행",
        # 설치 탭
        "install_subtitle": "버전을 골라 다운로드·설치합니다. (게임·버전별 독립 폴더)",
        "sec_game": "1. 게임",
        "sec_channel": "2. 채널",
        "ch_experimental": "experimental (최신 개발 빌드)",
        "ch_stable_radio": "정식 릴리스 (stable)",
        "sec_version": "3. 버전",
        "sec_edition": "4. 에디션",
        "sec_folder": "5. 설치 기본 폴더 (이 안에 버전별 폴더 생성)",
        "browse": "찾아보기",
        "run_after": "설치 후 바로 실행",
        "ready": "준비됨",
        "install_btn": "설치하기",
        "installed_already": "설치됨 ✓",
        "loading_versions": "버전 목록 불러오는 중...",
        "list_failed": "목록 실패: {e}",
        "none_to_show": "표시할 버전이 없습니다.",
        "loaded_n": "{n}개 버전 로드됨",
        "downloading": "다운로드 중: {name}",
        "dl_progress": "다운로드 {r:.1f}/{t:.1f} MB",
        "extracting": "압축 해제 중...",
        "install_done_status": "설치 완료 → {dest}",
        "failed": "실패",
        "prefix_stable": "정식",
        "prefix_experimental": "experimental",
        # 에디션
        "ed_graphics_sound": "그래픽 + 사운드 (권장)",
        "ed_graphics": "그래픽만 (사운드 없음)",
        "ed_terminal": "터미널 (ASCII)",
        "ed_other": "기타 (Windows)",
        # 설치 메시지박스
        "need_select_title": "선택 필요",
        "need_version_asset": "버전과 에디션을 선택하세요.",
        "need_path_title": "경로 필요",
        "need_path": "설치 기본 폴더를 지정하세요.",
        "already_title": "이미 설치됨",
        "already_msg": "이 버전 폴더가 이미 있습니다:\n{dest}\n\n덮어쓸까요?",
        "done_title": "완료",
        "install_done_msg": "설치 완료!\n\n버전: {name}\n위치: {dest}",
        "dl_failed_http": "다운로드 실패 (HTTP {code})",
        "error_tb": "오류: {e}\n\n{tb}",
        "install_failed_title": "설치 실패",
        # 실행 탭
        "installed_title": "설치된 버전 — {short}",
        "installed_title_plain": "설치된 버전 (CDDA · CDBN)",
        "run_subtitle": "설치된 모든 버전이 보입니다. 더블클릭하거나 아래 버튼으로 실행하세요.",
        "col_game": "게임",
        "installed_count_all": "{n}개 설치됨  (CDDA · CDBN 통합)",
        "col_version": "버전",
        "col_channel": "채널",
        "col_date": "설치일",
        "btn_run": "▶ 실행",
        "btn_mods": "🧩 모드",
        "btn_open_folder": "폴더 열기",
        "btn_delete": "🗑 삭제",
        "btn_refresh": "새로고침",
        "installed_count": "{n}개 설치됨  |  위치: {base}",
        "no_installs": "설치된 버전이 없습니다.  ('설치' 탭에서 먼저 설치하세요)",
        "need_run_select": "실행할 버전을 선택하세요.",
        "cant_run_title": "실행 불가",
        "no_exe": "이 폴더에서 실행 파일(.exe)을 찾지 못했습니다.",
        "running": "실행: {name}",
        "run_failed": "실행 실패",
        "need_open_select": "폴더를 열 버전을 선택하세요.",
        "open_failed": "열기 실패",
        "need_delete_select": "삭제할 버전을 선택하세요.",
        "delete_confirm_title": "삭제 확인",
        "delete_confirm": "이 버전을 완전히 삭제할까요?\n\n{name}\n{path}\n\n※ 세이브 데이터도 함께 삭제됩니다.",
        "deleted": "삭제됨: {name}",
        "delete_failed": "삭제 실패",
        "need_mod_select": "모드를 관리할 버전을 선택하세요.",
        # 모드 창
        "mod_title": "모드 관리 — {name}",
        "mod_header": "추가한 모드",
        "mod_subtitle": "이 도구로 추가한 모드만 표시됩니다. (게임 기본 번들 모드는 제외)",
        "mod_col_name": "모드 이름",
        "mod_col_folder": "폴더",
        "mod_btn_url": "🌐 URL에서 추가",
        "mod_btn_zip": "➕ zip 추가",
        "mod_btn_remove": "🗑 제거",
        "mod_btn_open": "폴더 열기",
        "mod_btn_close": "닫기",
        "mod_count": "{n}개 모드  |  {dir}",
        "mod_no_dir": "data/mods 폴더를 찾지 못했습니다.",
        "mod_err_title": "오류",
        "mod_no_dir_err": "이 버전에서 data/mods 폴더를 찾지 못했습니다.",
        "mod_url_title": "URL에서 모드 추가",
        "mod_url_prompt": "모드 zip 직접 링크 또는 GitHub 저장소 주소를 입력하세요:\n예) https://github.com/사용자/저장소",
        "mod_zip_title": "모드 zip 선택",
        "mod_zip_filter": "Zip 파일",
        "all_files": "모든 파일",
        "mod_added_n": "{n}개 모드를 추가했습니다.",
        "mod_none_title": "모드 없음",
        "mod_none_msg": "modinfo.json 이 없어 모드로 보이지 않습니다.",
        "mod_exists_title": "이미 있음",
        "mod_exists_msg": "'{name}' 모드가 이미 있습니다. 덮어쓸까요?",
        "mod_add_failed": "추가 실패",
        "mod_dl_status": "다운로드 중: {url}",
        "mod_dl_failed": "다운로드 실패",
        "mod_not_zip": "받은 파일이 zip 이 아닙니다. URL을 확인하세요.",
        "mod_remove_select": "제거할 모드를 선택하세요.",
        "mod_remove_title": "제거 확인",
        "mod_remove_msg": "이 모드를 삭제할까요?\n\n{name}\n{path}",
        "mod_remove_failed": "삭제 실패",
        "mod_no_folder_title": "폴더 없음",
        "mod_no_folder_msg": "data/mods 폴더가 아직 없습니다.",
        "mod_open_failed": "열기 실패",
        # 콘텐츠 관리 (모드/사운드/타일셋/폰트 통합)
        "btn_content": "🧩 콘텐츠",
        "content_title": "콘텐츠 관리 — {name}",
        "res_mods": "모드",
        "res_sound": "사운드팩",
        "res_tiles": "타일셋",
        "res_fonts": "폰트",
        "res_subtitle": "기본(번들) 항목은 보호되어 삭제할 수 없고, 이 도구로 추가한 항목만 제거됩니다.",
        "res_add_file": "➕ 파일 추가",
        "res_add_title": "추가할 파일 선택",
        "res_font_filter": "폰트 파일",
        "res_no_dir_err": "이 버전에서 대상 폴더를 찾지 못했습니다.",
        "res_no_dir": "대상 폴더를 찾지 못했습니다.",
        "res_none_msg": "추가할 항목을 찾지 못했습니다.",
        "res_zip_only": "이 항목은 zip 으로만 추가할 수 있습니다.",
        "res_count": "{n}개  |  {dir}",
        "col_source": "구분",
        "src_bundled": "기본",
        "src_added": "추가됨",
        "cant_remove_title": "삭제 불가",
        "cant_remove_bundled": "기본 제공 항목은 삭제할 수 없습니다.",
        "fonts_note": "⚠ 폰트는 복사만으로 적용되지 않습니다 — '적용'을 눌러 config/fonts.json 에 반영하세요.",
        "font_apply_btn": "🅰 편집/적용",
        "font_apply_title": "글꼴 편집 / 적용",
        "sysfont_btn": "🪟 시스템",
        "sysfont_title": "설치된 폰트에서 추가",
        "sysfont_prompt": "Windows에 설치된 폰트를 골라 추가합니다. (검색·복수 선택 가능)",
        "sysfont_none": "설치된 폰트를 찾지 못했습니다.",
        "sysfont_add": "추가",
        "font_apply_prompt": "'{name}' 을(를) 어느 글꼴 영역에 적용할까요?",
        "font_cat_typeface": "기본 (게임 텍스트)",
        "font_cat_gui": "메뉴 (GUI)",
        "font_cat_map": "지도",
        "font_cat_overmap": "전체 지도(overmap)",
        "font_apply_ok": "적용",
        "cancel": "취소",
        "font_applied": "적용했습니다:\n{dest}\n\n게임을 재시작하면 반영됩니다. (이전 설정은 .bak 로 백업됨)",
        "font_apply_none": "적용할 영역이나 크기를 하나 이상 지정하세요.",
        "font_apply_failed": "폰트 적용 실패",
        "font_size_section": "폰트 크기 (options.json — 비우면 그대로)",
        "fs_width": "폭",
        "fs_height": "높이",
        "fs_size": "크기",
        "font_size_disabled": "※ 크기는 게임을 한 번 실행한 뒤 바꿀 수 있습니다 (options.json 없음).",
        "font_size_bad": "크기 값은 숫자여야 합니다.",
        "applied_summary": "적용 완료. 게임을 재시작하면 반영됩니다.\n{detail}",
        "applied_typeface": "• 글꼴: {dest}",
        "applied_sizes": "• 크기 {n}개 항목 변경 (options.json)",
    },
    "en": {
        "app_title": "Cataclysm Installer & Version Manager (CDDA / CDBN)",
        "lang_label": "언어 / Language:",
        "tab_install": "Install",
        "tab_run": "Library",
        # Install tab
        "install_subtitle": "Pick a version to download & install. (separate folder per game/version)",
        "sec_game": "1. Game",
        "sec_channel": "2. Channel",
        "ch_experimental": "experimental (latest dev builds)",
        "ch_stable_radio": "stable release",
        "sec_version": "3. Version",
        "sec_edition": "4. Edition",
        "sec_folder": "5. Install base folder (a per-version folder is created inside)",
        "browse": "Browse",
        "run_after": "Run right after install",
        "ready": "Ready",
        "install_btn": "Install",
        "installed_already": "Installed ✓",
        "loading_versions": "Loading versions...",
        "list_failed": "List failed: {e}",
        "none_to_show": "No versions to show.",
        "loaded_n": "{n} versions loaded",
        "downloading": "Downloading: {name}",
        "dl_progress": "Downloaded {r:.1f}/{t:.1f} MB",
        "extracting": "Extracting...",
        "install_done_status": "Installed → {dest}",
        "failed": "Failed",
        "prefix_stable": "stable",
        "prefix_experimental": "experimental",
        # Editions
        "ed_graphics_sound": "Graphics + sound (recommended)",
        "ed_graphics": "Graphics only (no sound)",
        "ed_terminal": "Terminal (ASCII)",
        "ed_other": "Other (Windows)",
        # Install message boxes
        "need_select_title": "Selection required",
        "need_version_asset": "Select a version and an edition.",
        "need_path_title": "Path required",
        "need_path": "Please set the install base folder.",
        "already_title": "Already installed",
        "already_msg": "This version folder already exists:\n{dest}\n\nOverwrite?",
        "done_title": "Done",
        "install_done_msg": "Install complete!\n\nVersion: {name}\nLocation: {dest}",
        "dl_failed_http": "Download failed (HTTP {code})",
        "error_tb": "Error: {e}\n\n{tb}",
        "install_failed_title": "Install failed",
        # Run tab
        "installed_title": "Installed — {short}",
        "installed_title_plain": "Installed versions (CDDA · CDBN)",
        "run_subtitle": "Shows every installed version. Double-click or use the buttons below to run.",
        "col_game": "Game",
        "installed_count_all": "{n} installed  (CDDA · CDBN combined)",
        "col_version": "Version",
        "col_channel": "Channel",
        "col_date": "Installed",
        "btn_run": "▶ Run",
        "btn_mods": "🧩 Mods",
        "btn_open_folder": "Open folder",
        "btn_delete": "🗑 Delete",
        "btn_refresh": "Refresh",
        "installed_count": "{n} installed  |  at: {base}",
        "no_installs": "No versions installed.  (install one from the Install tab first)",
        "need_run_select": "Select a version to run.",
        "cant_run_title": "Cannot run",
        "no_exe": "Couldn't find an executable (.exe) in this folder.",
        "running": "Running: {name}",
        "run_failed": "Run failed",
        "need_open_select": "Select a version to open its folder.",
        "open_failed": "Open failed",
        "need_delete_select": "Select a version to delete.",
        "delete_confirm_title": "Confirm delete",
        "delete_confirm": "Delete this version completely?\n\n{name}\n{path}\n\nNote: save data will be deleted too.",
        "deleted": "Deleted: {name}",
        "delete_failed": "Delete failed",
        "need_mod_select": "Select a version to manage mods.",
        # Mod window
        "mod_title": "Mod manager — {name}",
        "mod_header": "Added mods",
        "mod_subtitle": "Only mods added with this tool are shown. (bundled mods excluded)",
        "mod_col_name": "Mod name",
        "mod_col_folder": "Folder",
        "mod_btn_url": "🌐 Add from URL",
        "mod_btn_zip": "➕ Add zip",
        "mod_btn_remove": "🗑 Remove",
        "mod_btn_open": "Open folder",
        "mod_btn_close": "Close",
        "mod_count": "{n} mods  |  {dir}",
        "mod_no_dir": "Couldn't find the data/mods folder.",
        "mod_err_title": "Error",
        "mod_no_dir_err": "Couldn't find a data/mods folder for this version.",
        "mod_url_title": "Add mod from URL",
        "mod_url_prompt": "Enter a direct mod zip link or a GitHub repo URL:\ne.g. https://github.com/user/repo",
        "mod_zip_title": "Select mod zip",
        "mod_zip_filter": "Zip files",
        "all_files": "All files",
        "mod_added_n": "Added {n} mod(s).",
        "mod_none_title": "No mod",
        "mod_none_msg": "No modinfo.json found — doesn't look like a mod.",
        "mod_exists_title": "Already exists",
        "mod_exists_msg": "Mod '{name}' already exists. Overwrite?",
        "mod_add_failed": "Add failed",
        "mod_dl_status": "Downloading: {url}",
        "mod_dl_failed": "Download failed",
        "mod_not_zip": "The downloaded file isn't a zip. Check the URL.",
        "mod_remove_select": "Select a mod to remove.",
        "mod_remove_title": "Confirm removal",
        "mod_remove_msg": "Delete this mod?\n\n{name}\n{path}",
        "mod_remove_failed": "Remove failed",
        "mod_no_folder_title": "No folder",
        "mod_no_folder_msg": "The data/mods folder doesn't exist yet.",
        "mod_open_failed": "Open failed",
        # Content manager (mods/soundpacks/tilesets/fonts)
        "btn_content": "🧩 Content",
        "content_title": "Content — {name}",
        "res_mods": "Mods",
        "res_sound": "Soundpacks",
        "res_tiles": "Tilesets",
        "res_fonts": "Fonts",
        "res_subtitle": "Bundled items are protected from deletion; only items added with this tool can be removed.",
        "res_add_file": "➕ Add file",
        "res_add_title": "Select file(s) to add",
        "res_font_filter": "Font files",
        "res_no_dir_err": "Couldn't find the target folder for this version.",
        "res_no_dir": "Target folder not found.",
        "res_none_msg": "No installable item found.",
        "res_zip_only": "This type can only be added from a zip.",
        "res_count": "{n} items  |  {dir}",
        "col_source": "Type",
        "src_bundled": "Bundled",
        "src_added": "Added",
        "cant_remove_title": "Can't delete",
        "cant_remove_bundled": "Bundled (built-in) items can't be deleted.",
        "fonts_note": "⚠ Copying a font isn't enough — press 'Apply' to write it into config/fonts.json.",
        "font_apply_btn": "🅰 Edit / Apply",
        "font_apply_title": "Edit / Apply font",
        "sysfont_btn": "🪟 System",
        "sysfont_title": "Add from installed fonts",
        "sysfont_prompt": "Pick fonts installed on Windows to add. (search, multi-select)",
        "sysfont_none": "No installed fonts found.",
        "sysfont_add": "Add",
        "font_apply_prompt": "Where should '{name}' be applied?",
        "font_cat_typeface": "Main (game text)",
        "font_cat_gui": "Menus (GUI)",
        "font_cat_map": "Map",
        "font_cat_overmap": "Overmap",
        "font_apply_ok": "Apply",
        "cancel": "Cancel",
        "font_applied": "Applied:\n{dest}\n\nRestart the game to see the change. (previous config backed up as .bak)",
        "font_apply_none": "Specify at least one area or a size.",
        "font_apply_failed": "Failed to apply font",
        "font_size_section": "Font size (options.json — blank = keep)",
        "fs_width": "Width",
        "fs_height": "Height",
        "fs_size": "Size",
        "font_size_disabled": "※ Sizes can be changed after running the game once (no options.json).",
        "font_size_bad": "Size values must be numbers.",
        "applied_summary": "Done. Restart the game to see the change.\n{detail}",
        "applied_typeface": "• Typeface: {dest}",
        "applied_sizes": "• Updated {n} size value(s) (options.json)",
    },
}

_LANG = "ko"


def set_lang(lang: str):
    global _LANG
    if lang in STRINGS:
        _LANG = lang


def t(key: str, **kw):
    """현재 언어의 문자열을 반환. 없으면 한국어 → 키 순으로 폴백."""
    s = STRINGS.get(_LANG, STRINGS["ko"]).get(key)
    if s is None:
        s = STRINGS["ko"].get(key, key)
    return s.format(**kw) if kw else s


# ---------------------------------------------------------------------------
# 에셋 분류 / API
# ---------------------------------------------------------------------------
def classify_asset(name: str):
    """Windows용 재생 가능 zip을 언어 중립 키로 분류. CDDA/CDBN 이름 규칙 모두 처리.
    반환: 'graphics_sound' | 'graphics' | 'terminal' | 'other' | None(제외)"""
    n = name.lower()
    if not n.endswith(".zip"):
        return None
    if "windows" not in n and "win" not in n:
        return None
    if "pdb" in n:
        return None  # 디버그 심볼 — 게임 아님 (CDBN)
    # 순서 주의: 'no-soundpack' 은 'sound' 를 포함하므로 먼저 검사
    if "no-soundpack" in n or "no_soundpack" in n or "nosound" in n:
        return "graphics"        # CDBN 무사운드
    if "sound" in n:
        return "graphics_sound"  # CDDA graphics-and-sounds
    if "curses" in n or "terminal" in n:
        return "terminal"
    if "graphics" in n:
        return "graphics"        # CDDA graphics-only
    if "tiles" in n:
        return "graphics_sound"  # CDBN tiles (사운드 포함)
    return "other"


def http_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT,
                                               "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_releases(game: dict, channel: str, limit: int = 40):
    """game: GAMES 항목. channel: 'stable'|'experimental'
    -> [{'tag','name','stable','assets':[(kind,name,url,size)]}]"""
    api = f"{GITHUB_API}/{game['repo']}/releases"
    results = []
    if channel == "stable":
        seen = set()
        # 1) 최신 정식 (미래 새 버전도 자동 포함)
        try:
            packed = _pack(http_json(api + "/latest"), stable=True)
            if packed["assets"]:
                results.append(packed)
                seen.add(packed["tag"])
        except Exception:
            pass
        # 2) 과거 정식은 목록 깊숙이 묻혀 있어 태그로 직접 조회
        for tag in game.get("stable_tags", []):
            if len(results) >= limit:
                break
            if tag in seen:
                continue
            try:
                packed = _pack(http_json(f"{api}/tags/{tag}"), stable=True)
            except Exception:
                continue  # 없는 태그(404 등)는 건너뜀
            if packed["assets"]:
                results.append(packed)
                seen.add(packed["tag"])
    else:
        page = 1
        while len(results) < limit and page <= 3:
            try:
                rels = http_json(f"{api}?per_page=100&page={page}")
            except Exception:
                break
            if not rels:
                break
            for r in rels:
                if r.get("prerelease"):
                    packed = _pack(r, stable=False)
                    if packed["assets"]:
                        results.append(packed)
                        if len(results) >= limit:
                            break
            page += 1
    return results


def _pack(rel: dict, stable: bool):
    assets = []
    for a in rel.get("assets", []):
        kind = classify_asset(a["name"])
        if kind:
            assets.append((kind, a["name"], a["browser_download_url"], a.get("size", 0)))
    order = {"graphics_sound": 0, "graphics": 1, "terminal": 2, "other": 3}
    assets.sort(key=lambda x: order.get(x[0], 9))
    name = rel.get("name") or rel["tag_name"]
    return {"tag": rel["tag_name"], "name": name, "stable": stable, "assets": assets}


def safe_folder_name(tag: str) -> str:
    """릴리스 태그를 폴더명으로 안전하게 변환"""
    s = re.sub(r"[^A-Za-z0-9._-]", "_", tag)
    return s.strip("_") or "cdda"


# ---------------------------------------------------------------------------
# 설치된 버전 스캔
# ---------------------------------------------------------------------------
def scan_installed(base_dir: str):
    """base_dir 아래 각 하위 폴더의 메타/실행파일을 읽어 목록 반환"""
    out = []
    if not os.path.isdir(base_dir):
        return out
    for entry in sorted(os.listdir(base_dir)):
        path = os.path.join(base_dir, entry)
        if not os.path.isdir(path):
            continue
        meta = {}
        mpath = os.path.join(path, META_NAME)
        if os.path.isfile(mpath):
            try:
                meta = json.load(open(mpath, encoding="utf-8"))
            except Exception:
                meta = {}
        exe = find_exe(path)
        if not exe and not meta:
            continue  # 게임 폴더가 아님
        out.append({
            "folder": entry,
            "path": path,
            "name": meta.get("name", entry),
            "game": meta.get("game_name") or meta.get("game", ""),
            "channel": meta.get("channel", "?"),
            "installed_at": meta.get("installed_at", ""),
            "exe": exe,
        })
    return out


def find_exe(root_dir: str):
    candidates = []
    for dirpath, _, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith(".exe"):
                full = os.path.join(dirpath, f)
                if "tiles" in f.lower():
                    return full
                candidates.append(full)
    return candidates[0] if candidates else None


def launch_game(exe: str):
    """게임을 그 폴더를 작업 디렉터리로 잡아 실행한다.
    (cwd 가 게임 폴더여야 'data/' 를 찾는다 — os.startfile 은 cwd 가 system32 라 실패)"""
    subprocess.Popen([exe], cwd=os.path.dirname(exe))


# ---------------------------------------------------------------------------
# 콘텐츠 관리 (모드 / 사운드팩 / 타일셋 / 폰트)
# ---------------------------------------------------------------------------
# 각 자원의 게임 폴더 내 위치와 식별 방식.
#   kind="folder": 하위 폴더 단위, id_file 로 식별 (modinfo.json / soundpack.txt / tileset.txt)
#   kind="files" : 개별 파일 단위 (폰트 .ttf/.otf/.ttc)
RESOURCE_SPECS = {
    "mods":  {"label_key": "res_mods",  "dirs": [("data", "mods")],
              "id_file": "modinfo.json", "kind": "folder"},
    "sound": {"label_key": "res_sound", "dirs": [("data", "sound"), ("sound",)],
              "id_file": "soundpack.txt", "kind": "folder"},
    "tiles": {"label_key": "res_tiles", "dirs": [("gfx",)],
              "id_file": "tileset.txt", "kind": "folder"},
    "fonts": {"label_key": "res_fonts", "dirs": [("data", "font"), ("font",)],
              "id_file": None, "kind": "files", "exts": (".ttf", ".ttc", ".otf"),
              "note_key": "fonts_note"},
}
FILE_MARKER_SUFFIX = ".cdda_added"  # 폰트 등 파일 자원은 옆에 마커 파일을 둔다


def read_mod_name(mod_dir: str):
    """modinfo.json 에서 표시용 모드 이름을 읽는다. modinfo 없으면 None."""
    mi = os.path.join(mod_dir, "modinfo.json")
    if not os.path.isfile(mi):
        return None
    try:
        data = json.load(open(mi, encoding="utf-8"))
    except Exception:
        return os.path.basename(mod_dir)
    entries = data if isinstance(data, list) else [data]
    for e in entries:
        if isinstance(e, dict) and e.get("type") == "MOD_INFO":
            name = e.get("name") or e.get("id") or os.path.basename(mod_dir)
            if isinstance(name, dict):  # 번역 형식 {"str": "..."}
                name = name.get("str") or name.get("str_sp") or os.path.basename(mod_dir)
            return name
    return os.path.basename(mod_dir)


def read_txt_field(path: str, key: str = "NAME"):
    """tileset.txt / soundpack.txt 의 'KEY: value' 줄에서 값을 읽는다."""
    try:
        for line in open(path, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            k, v = line.split(":", 1)
            if k.strip().upper() == key.upper():
                return v.strip()
    except Exception:
        pass
    return None


def read_resource_name(folder: str, spec: dict):
    """폴더형 자원의 표시 이름. id_file 없거나 못 읽으면 None(=자원 아님)."""
    idf = spec["id_file"]
    full = os.path.join(folder, idf)
    if not os.path.isfile(full):
        return None
    if idf.endswith(".json"):
        return read_mod_name(folder)
    name = read_txt_field(full, "NAME") or read_txt_field(full, "VIEW")
    return name or os.path.basename(folder)


def find_resource_dir(version: dict, spec: dict, create: bool = False):
    """선택한 버전에서 자원 폴더(data/mods, gfx, data/font 등) 경로를 찾는다."""
    roots = []
    if version.get("exe"):
        roots.append(os.path.dirname(version["exe"]))
    roots.append(version["path"])
    cands = [os.path.join(r, *parts) for r in roots for parts in spec["dirs"]]
    for c in cands:
        if os.path.isdir(c):
            return c
    # 폴더 트리에서 접미 경로가 일치하는 디렉터리 탐색 (예: ...\data\mods)
    suffix = os.path.join(*spec["dirs"][0])
    for dirpath, _, _ in os.walk(version["path"]):
        if os.path.normpath(dirpath).endswith(os.sep + suffix) or \
           os.path.normpath(dirpath).endswith(suffix):
            return dirpath
    if create and cands:
        os.makedirs(cands[0], exist_ok=True)
        return cands[0]
    return None


def scan_resources(rdir: str, spec: dict):
    """자원 목록 반환. 번들/추가를 모두 보여주되 각 항목에 bundled 플래그를 단다.
    bundled=True(마커 없음)는 게임 기본 제공 → 삭제 보호 대상."""
    out = []
    if not rdir or not os.path.isdir(rdir):
        return out
    if spec["kind"] == "folder":
        for entry in sorted(os.listdir(rdir), key=str.lower):
            p = os.path.join(rdir, entry)
            if not os.path.isdir(p):
                continue
            name = read_resource_name(p, spec)
            if name is None:
                continue  # 식별 파일 없으면 자원 아님
            bundled = not os.path.isfile(os.path.join(p, MOD_MARKER))
            out.append({"name": name, "folder": entry, "path": p, "bundled": bundled})
    else:  # files (폰트)
        for entry in sorted(os.listdir(rdir), key=str.lower):
            p = os.path.join(rdir, entry)
            if not os.path.isfile(p):
                continue
            if os.path.splitext(entry)[1].lower() not in spec["exts"]:
                continue
            bundled = not os.path.isfile(p + FILE_MARKER_SUFFIX)
            out.append({"name": entry, "folder": entry, "path": p, "bundled": bundled})
    return out


def resolve_mod_url(url: str):
    """입력 URL을 (다운로드용 zip URL, 기본 폴더명)으로 변환.
    GitHub 저장소 주소면 기본 브랜치 zip 링크로 바꾼다."""
    url = url.strip()
    if url.lower().split("?")[0].endswith(".zip"):
        name = os.path.splitext(os.path.basename(url.split("?")[0]))[0]
        return url, name or "mod"
    mo = re.match(r"https?://github\.com/([^/]+)/([^/]+)", url)
    if mo:
        user, repo = mo.group(1), mo.group(2).replace(".git", "")
        branch = "main"
        try:
            branch = http_json(f"https://api.github.com/repos/{user}/{repo}").get(
                "default_branch", "main")
        except Exception:
            pass
        return (f"https://github.com/{user}/{repo}/archive/refs/heads/{branch}.zip", repo)
    return url, "mod"


def download_bytes(url: str):
    """URL에서 바이트를 받아온다."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def strip_branch_suffix(name: str):
    """GitHub 아카이브 폴더명(repo-main 등)에서 브랜치 꼬리표 제거."""
    for suf in ("-main", "-master"):
        if name.endswith(suf):
            return name[:-len(suf)]
    return name


# ---- 폰트 적용 (config/fonts.json 편집) ---------------------------------
# 형식 근거: CleverRaven/Cataclysm-DDA  doc/user-guides/FONT_OPTIONS.md
# config/fonts.json 은 첫 실행 시 data/fontdata.json 기본값으로 생성된다.
FONT_CATEGORIES = ["typeface", "gui_typeface", "map_typeface", "overmap_typeface"]


def list_system_fonts():
    """Windows에 설치된 폰트 파일 목록 [(표시명, 경로)] 반환 (중복 제거)."""
    dirs = [os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")]
    la = os.environ.get("LOCALAPPDATA")
    if la:
        dirs.append(os.path.join(la, "Microsoft", "Windows", "Fonts"))
    exts = (".ttf", ".ttc", ".otf")
    seen, out = set(), []
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d), key=str.lower):
            if os.path.splitext(f)[1].lower() in exts and f.lower() not in seen:
                seen.add(f.lower())
                out.append((f, os.path.join(d, f)))
    return out


def game_root_of(version: dict):
    return os.path.dirname(version["exe"]) if version.get("exe") else version["path"]


def font_config_path(version: dict):
    return os.path.join(game_root_of(version), "config", "fonts.json")


def _font_template_paths(version: dict):
    """게임 기본 글꼴 템플릿 후보 (CDDA=data/fontdata.json, CDBN=data/raw/fonts.json)."""
    root = game_root_of(version)
    return [os.path.join(root, "data", "fontdata.json"),
            os.path.join(root, "data", "raw", "fonts.json")]


def load_font_config(version: dict):
    """config/fonts.json → 없으면 게임 기본 템플릿 → 없으면 빈 dict."""
    for p in [font_config_path(version)] + _font_template_paths(version):
        if os.path.isfile(p):
            try:
                return json.load(open(p, encoding="utf-8"))
            except Exception:
                pass
    return {}


def supported_font_categories(version: dict):
    """이 게임이 지원하는 typeface 카테고리. 기본 템플릿(data/...)을 우선 근거로 한다.
    (예: CDBN 은 gui_typeface 가 없어 그걸 쓰면 JSON 오류가 난다.)"""
    for p in _font_template_paths(version):  # config 가 아니라 게임 기본 템플릿 기준
        if os.path.isfile(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
                cats = [c for c in FONT_CATEGORIES if c in d]
                if cats:
                    return cats
            except Exception:
                pass
    return list(FONT_CATEGORIES)


def _font_entry_path(entry):
    return entry.get("path", "") if isinstance(entry, dict) else entry


def apply_font_to_config(version: dict, font_abs_path: str, categories: list):
    """선택 폰트를 config/fonts.json 의 지정 카테고리 맨 앞(주 글꼴)에 넣는다.
    기존 파일은 .bak 로 백업한 뒤 기록. 기록한 경로를 반환."""
    root = game_root_of(version)
    rel = os.path.relpath(font_abs_path, root).replace("\\", "/")
    supported = supported_font_categories(version)
    categories = [c for c in categories if c in supported]  # 미지원 필드 방지(CDBN gui_typeface 등)
    cfg = load_font_config(version)
    for cat in categories:
        cur = cfg.get(cat)
        lst = list(cur) if isinstance(cur, list) else ([] if cur is None else [cur])
        lst = [e for e in lst if _font_entry_path(e) != rel]  # 중복 제거
        lst.insert(0, rel)                                    # 주 글꼴로 맨 앞에
        cfg[cat] = lst
    dest = font_config_path(version)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.isfile(dest):
        try:
            shutil.copy2(dest, dest + ".bak")
        except Exception:
            pass
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, ensure_ascii=False, indent=2)
    return dest


# ---- 폰트 크기 등 게임 옵션 (config/options.json 편집) -------------------
# 형식 근거: CleverRaven/Cataclysm-DDA  src/options.cpp (serialize)
# options.json 은 {"info","default","name","value"} 객체의 배열이고,
# 게임은 로드 시 name+value 만 읽는다(value 는 문자열). 첫 실행 시 생성됨.
FONT_SIZE_KEYS = ["FONT_WIDTH", "FONT_HEIGHT", "FONT_SIZE"]


def options_path(version: dict):
    return os.path.join(game_root_of(version), "config", "options.json")


def load_options(version: dict):
    """config/options.json 을 리스트로 반환. 없거나 형식 이상이면 None."""
    p = options_path(version)
    if not os.path.isfile(p):
        return None
    try:
        data = json.load(open(p, encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, list) else None


def get_option_value(options_list, name):
    for o in options_list or []:
        if isinstance(o, dict) and o.get("name") == name:
            return o.get("value")
    return None


def set_option_values(version: dict, changes: dict):
    """{name: value} 의 value 만 갱신해 기록. 백업 후 저장. 적용 개수 반환.
    options.json 이 없으면 None(게임 미실행)."""
    p = options_path(version)
    data = load_options(version)
    if data is None:
        return None
    applied = 0
    for o in data:
        if isinstance(o, dict) and o.get("name") in changes:
            o["value"] = str(changes[o["name"]])
            applied += 1
    try:
        shutil.copy2(p, p + ".bak")
    except Exception:
        pass
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return applied


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.lang = tk.StringVar(value="en")
        set_lang("en")

        self.game = tk.StringVar(value="cdda")
        # 게임마다 설치 폴더를 분리해 목록이 섞이지 않게 한다
        self.base_dirs = {g["key"]: tk.StringVar(value=os.path.join(GAMES_ROOT, g["subdir"]))
                          for g in GAMES}
        self.channel = tk.StringVar(value="experimental")
        self.run_after = tk.BooleanVar(value=False)
        self.releases = []
        self._busy = False

        # 언어 변경 시 다시 번역할 위젯 등록부
        self._i18n_text = []      # [(widget, key)]  -> config(text=...)
        self._i18n_headings = []  # [(tree, col, key)]

        root.title(t("app_title"))
        root.geometry("680x640")
        root.minsize(620, 580)

        # 큰 세그먼트 버튼(탭) 스타일 — 텍스트를 가운데 정렬하고 크게
        style = ttk.Style()
        style.configure("Big.Toolbutton", font=("Segoe UI", 14, "bold"),
                        padding=[10, 16], anchor="center", justify="center")

        top = ttk.Frame(root)
        top.pack(fill="x", padx=10, pady=(8, 0))
        self.reg(ttk.Label(top, text=t("lang_label")), "lang_label").pack(side="left")
        ttk.Radiobutton(top, text="한국어", variable=self.lang, value="ko",
                        command=self.apply_language).pack(side="left", padx=(6, 0))
        ttk.Radiobutton(top, text="English", variable=self.lang, value="en",
                        command=self.apply_language).pack(side="left")

        # 폭을 절반씩 나눈 큰 탭(세그먼트 버튼) — Library 가 왼쪽(첫 번째)
        self.view = tk.StringVar(value="library")
        sel = ttk.Frame(root)
        sel.pack(fill="x", padx=8, pady=(8, 0))
        sel.columnconfigure(0, weight=1)
        sel.columnconfigure(1, weight=1)
        b_lib = ttk.Radiobutton(sel, text=t("tab_run"), variable=self.view, value="library",
                                style="Big.Toolbutton", command=self._show_view)
        b_ins = ttk.Radiobutton(sel, text=t("tab_install"), variable=self.view, value="install",
                                style="Big.Toolbutton", command=self._show_view)
        b_lib.grid(row=0, column=0, sticky="nsew")
        b_ins.grid(row=0, column=1, sticky="nsew")
        self.reg(b_lib, "tab_run")
        self.reg(b_ins, "tab_install")

        # 두 탭 프레임을 같은 칸에 겹쳐 두고 선택된 것을 위로 올린다
        content = ttk.Frame(root)
        content.pack(fill="both", expand=True, padx=8, pady=8)
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)
        self.tab_install = ttk.Frame(content, padding=10)
        self.tab_run = ttk.Frame(content, padding=10)
        self.tab_install.grid(row=0, column=0, sticky="nsew")
        self.tab_run.grid(row=0, column=0, sticky="nsew")

        self._build_install_tab()
        self._build_run_tab()
        self.refresh_releases()
        self._show_view()  # 기본 Library

    def _show_view(self):
        if self.view.get() == "install":
            self.tab_install.tkraise()
            self.update_install_state()
        else:
            self.tab_run.tkraise()
            self.refresh_installed()

    # ---- i18n 헬퍼 ----
    def reg(self, widget, key):
        """text= 를 가진 위젯을 등록하고 즉시 번역해 준다. 위젯을 반환."""
        self._i18n_text.append((widget, key))
        return widget

    def apply_language(self):
        set_lang(self.lang.get())
        self.root.title(t("app_title"))
        for w, k in self._i18n_text:
            try:
                w.config(text=t(k))
            except tk.TclError:
                pass
        for tree, col, k in self._i18n_headings:
            tree.heading(col, text=t(k))
        self.title_lbl.config(text=self._game()["name"])  # 게임명은 고유명사
        if self.releases:
            self.render_versions(keep=True)
        self.refresh_installed()
        self.update_install_state()
        if not self._busy:
            self.set_status(t("ready"))

    # ===================== 설치 탭 =====================
    def _build_install_tab(self):
        f = self.tab_install
        self.title_lbl = ttk.Label(f, text=self._game()["name"], font=("Segoe UI", 15, "bold"))
        self.title_lbl.pack(anchor="w")
        self.reg(ttk.Label(f, text=t("install_subtitle"), foreground="#666"),
                 "install_subtitle").pack(anchor="w", pady=(0, 8))

        gf = self.reg(ttk.Labelframe(f, text=t("sec_game"), padding=8), "sec_game")
        gf.pack(fill="x", pady=3)
        for g in GAMES:
            ttk.Radiobutton(gf, text=f"{g['short']} — {g['name']}", variable=self.game,
                            value=g["key"], command=self.on_game_change).pack(side="left", padx=(0, 14))

        ch = self.reg(ttk.Labelframe(f, text=t("sec_channel"), padding=8), "sec_channel")
        ch.pack(fill="x", pady=3)
        self.reg(ttk.Radiobutton(ch, text=t("ch_experimental"), variable=self.channel,
                 value="experimental", command=self.refresh_releases),
                 "ch_experimental").pack(anchor="w")
        self.reg(ttk.Radiobutton(ch, text=t("ch_stable_radio"), variable=self.channel,
                 value="stable", command=self.refresh_releases),
                 "ch_stable_radio").pack(anchor="w")

        vf = self.reg(ttk.Labelframe(f, text=t("sec_version"), padding=8), "sec_version")
        vf.pack(fill="x", pady=3)
        self.version_cb = ttk.Combobox(vf, state="readonly")
        self.version_cb.pack(fill="x")
        self.version_cb.bind("<<ComboboxSelected>>", lambda e: self.update_assets())

        af = self.reg(ttk.Labelframe(f, text=t("sec_edition"), padding=8), "sec_edition")
        af.pack(fill="x", pady=3)
        self.asset_cb = ttk.Combobox(af, state="readonly")
        self.asset_cb.pack(fill="x")

        pf = self.reg(ttk.Labelframe(f, text=t("sec_folder"), padding=8), "sec_folder")
        pf.pack(fill="x", pady=3)
        row = ttk.Frame(pf)
        row.pack(fill="x")
        self.dir_entry = ttk.Entry(row, textvariable=self.base_dirs[self.game.get()])
        self.dir_entry.pack(side="left", fill="x", expand=True)
        self.reg(ttk.Button(row, text=t("browse"), command=self.choose_dir),
                 "browse").pack(side="left", padx=(6, 0))
        self.reg(ttk.Checkbutton(pf, text=t("run_after"), variable=self.run_after),
                 "run_after").pack(anchor="w", pady=(6, 0))

        self.status = ttk.Label(f, text=t("ready"), foreground="#333")
        self.status.pack(anchor="w", pady=(10, 2))
        self.pbar = ttk.Progressbar(f, mode="determinate", maximum=100)
        self.pbar.pack(fill="x")
        self.install_btn = self.reg(ttk.Button(f, text=t("install_btn"), command=self.start_install),
                                    "install_btn")
        self.install_btn.pack(pady=10, ipadx=20, ipady=3)

    def set_status(self, text, c="#333"):
        self.status.config(text=text, foreground=c)

    def _game(self):
        return GAMES_BY_KEY[self.game.get()]

    def _base_var(self):
        return self.base_dirs[self.game.get()]

    def _base(self):
        return self._base_var().get().strip()

    def on_game_change(self):
        # 설치 폴더 입력칸을 현재 게임 것으로 교체하고 목록 새로고침
        self.title_lbl.config(text=self._game()["name"])
        self.dir_entry.config(textvariable=self._base_var())
        self.refresh_releases()
        self.refresh_installed()

    def choose_dir(self):
        d = filedialog.askdirectory(initialdir=self._base() or os.path.expanduser("~"))
        if d:
            self._base_var().set(d)

    def _vlabel(self, r):
        if r["stable"]:
            return f"[{t('prefix_stable')}] {r['name']}  ({r['tag']})"
        return f"[{t('prefix_experimental')}] {r['name']}"

    def render_versions(self, keep=False):
        """self.releases 로부터 버전 콤보박스를 (현재 언어로) 다시 그린다."""
        labels = [self._vlabel(r) for r in self.releases]
        cur = self.version_cb.current() if keep else 0
        self.version_cb["values"] = labels
        if labels:
            self.version_cb.current(cur if 0 <= cur < len(labels) else 0)
            self.update_assets()

    def refresh_releases(self):
        if self._busy:
            return
        self.set_status(t("loading_versions"), "#0066cc")
        self.version_cb.set(""); self.version_cb["values"] = []
        self.asset_cb.set(""); self.asset_cb["values"] = []
        game = self._game()

        def work():
            try:
                rels = fetch_releases(game, self.channel.get())
            except Exception as e:
                self.root.after(0, lambda: self.set_status(t("list_failed", e=e), "red")); return
            self.releases = rels

            def done():
                if not self.releases:
                    self.set_status(t("none_to_show"), "red"); return
                self.render_versions()
                self.set_status(t("loaded_n", n=len(self.releases)), "#008000")
            self.root.after(0, done)
        threading.Thread(target=work, daemon=True).start()

    def update_assets(self):
        i = self.version_cb.current()
        if i < 0 or i >= len(self.releases):
            self.update_install_state()
            return
        labels = []
        for kind, name, url, size in self.releases[i]["assets"]:
            mb = f" (~{size/1048576:.0f}MB)" if size else ""
            labels.append(f"{t('ed_' + kind)}{mb}")
        self.asset_cb["values"] = labels
        if labels:
            self.asset_cb.current(0)
        self.update_install_state()

    def _is_installed(self, rel):
        dest = os.path.join(self._base(), safe_folder_name(rel["tag"]))
        return os.path.isdir(dest) and bool(os.listdir(dest))

    def update_install_state(self):
        """선택한 버전이 이미 설치돼 있으면 버튼을 'Installed'로 비활성화."""
        if self._busy:
            self.install_btn.config(text=t("install_btn"), state="disabled")
            return
        i = self.version_cb.current()
        if 0 <= i < len(self.releases) and self._is_installed(self.releases[i]):
            self.install_btn.config(text=t("installed_already"), state="disabled")
        else:
            self.install_btn.config(text=t("install_btn"), state="normal")

    def start_install(self):
        if self._busy:
            return
        vi, ai = self.version_cb.current(), self.asset_cb.current()
        if vi < 0 or ai < 0:
            messagebox.showwarning(t("need_select_title"), t("need_version_asset")); return
        rel = self.releases[vi]
        kind, name, url, size = rel["assets"][ai]
        base = self._base()
        if not base:
            messagebox.showwarning(t("need_path_title"), t("need_path")); return
        dest = os.path.join(base, safe_folder_name(rel["tag"]))
        if os.path.isdir(dest) and os.listdir(dest):
            if not messagebox.askyesno(t("already_title"), t("already_msg", dest=dest)):
                return
        self._busy = True
        self.install_btn.config(state="disabled")
        threading.Thread(target=self._do_install,
                         args=(url, name, dest, rel, self._game()), daemon=True).start()

    def _do_install(self, url, name, dest, rel, game):
        try:
            os.makedirs(dest, exist_ok=True)
            self.root.after(0, lambda: self.set_status(t("downloading", name=name), "#0066cc"))
            buf = io.BytesIO()
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                total = int(resp.headers.get("Content-Length", 0)); read = 0
                while True:
                    data = resp.read(262144)
                    if not data:
                        break
                    buf.write(data); read += len(data)
                    if total:
                        self.root.after(0, lambda p=read*100/total, r=read, tt=total:
                            self._progress(p, t("dl_progress", r=r/1048576, t=tt/1048576)))
            self.root.after(0, lambda: self.set_status(t("extracting"), "#0066cc"))
            self.root.after(0, lambda: self.pbar.config(mode="indeterminate"))
            self.root.after(0, self.pbar.start)
            buf.seek(0)
            with zipfile.ZipFile(buf) as z:
                z.extractall(dest)
            self.root.after(0, self.pbar.stop)
            self.root.after(0, lambda: self.pbar.config(mode="determinate", value=100))

            # 메타 기록
            meta = {"name": rel["name"], "tag": rel["tag"],
                    "game": game["key"], "game_name": game["short"],
                    "channel": "stable" if rel["stable"] else "experimental",
                    "asset": name, "installed_at": time.strftime("%Y-%m-%d %H:%M")}
            try:
                json.dump(meta, open(os.path.join(dest, META_NAME), "w", encoding="utf-8"),
                          ensure_ascii=False, indent=2)
            except Exception:
                pass

            exe = find_exe(dest)
            self.root.after(0, lambda: self.set_status(t("install_done_status", dest=dest), "#008000"))
            self.root.after(0, self.refresh_installed)
            if self.run_after.get() and exe:
                try:
                    launch_game(exe)
                except Exception:
                    pass
            self.root.after(0, lambda: messagebox.showinfo(
                t("done_title"), t("install_done_msg", name=rel["name"], dest=dest)))
        except urllib.error.HTTPError as e:
            self.root.after(0, lambda: self._fail(t("dl_failed_http", code=e.code)))
        except Exception as e:
            tb = traceback.format_exc()
            self.root.after(0, lambda: self._fail(t("error_tb", e=e, tb=tb)))
        finally:
            self._busy = False
            self.root.after(0, self.update_install_state)

    def _progress(self, p, text):
        self.pbar.config(value=p); self.set_status(text, "#0066cc")

    def _fail(self, msg):
        self.pbar.stop(); self.pbar.config(mode="determinate", value=0)
        self.set_status(t("failed"), "red"); messagebox.showerror(t("install_failed_title"), msg)

    # ===================== 실행 탭 =====================
    def _build_run_tab(self):
        f = self.tab_run
        self.run_title_lbl = ttk.Label(f, text=t("installed_title_plain"), font=("Segoe UI", 15, "bold"))
        self.run_title_lbl.pack(anchor="w")
        self.reg(ttk.Label(f, text=t("run_subtitle"), foreground="#666"),
                 "run_subtitle").pack(anchor="w", pady=(0, 8))

        cols = ("game", "name", "channel", "date")
        self.tree = ttk.Treeview(f, columns=cols, show="headings", height=12)
        self.tree.heading("game", text=t("col_game"))
        self.tree.heading("name", text=t("col_version"))
        self.tree.heading("channel", text=t("col_channel"))
        self.tree.heading("date", text=t("col_date"))
        self._i18n_headings += [(self.tree, "game", "col_game"),
                                (self.tree, "name", "col_version"),
                                (self.tree, "channel", "col_channel"),
                                (self.tree, "date", "col_date")]
        self.tree.column("game", width=70, anchor="center")
        self.tree.column("name", width=270)
        self.tree.column("channel", width=110, anchor="center")
        self.tree.column("date", width=130, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=4)
        self.tree.bind("<Double-1>", lambda e: self.run_selected())

        self.run_status = ttk.Label(f, text="", foreground="#666")
        self.run_status.pack(anchor="w", pady=(2, 6))

        btns = ttk.Frame(f)
        btns.pack(fill="x")
        self.reg(ttk.Button(btns, text=t("btn_run"), command=self.run_selected),
                 "btn_run").pack(side="left", ipadx=10)
        self.reg(ttk.Button(btns, text=t("btn_content"), command=self.manage_content),
                 "btn_content").pack(side="left", padx=6)
        self.reg(ttk.Button(btns, text=t("btn_open_folder"), command=self.open_folder),
                 "btn_open_folder").pack(side="left")
        self.reg(ttk.Button(btns, text=t("btn_delete"), command=self.delete_selected),
                 "btn_delete").pack(side="left", padx=6)
        self.reg(ttk.Button(btns, text=t("btn_refresh"), command=self.refresh_installed),
                 "btn_refresh").pack(side="right")

        self._installed = []

    def refresh_installed(self):
        if not hasattr(self, "tree"):
            return  # 실행 탭이 아직 만들어지기 전 호출 방지
        self.run_title_lbl.config(text=t("installed_title_plain"))
        for i in self.tree.get_children():
            self.tree.delete(i)
        # CDDA·CDBN 모든 게임의 설치본을 통합해서 보여준다
        self._installed = []
        for g in GAMES:
            base = self.base_dirs[g["key"]].get().strip()
            for v in scan_installed(base):
                if not v.get("game"):
                    v["game"] = g["short"]  # 옛 설치(메타에 게임 없음) 폴백
                self._installed.append(v)
        for v in self._installed:
            self.tree.insert("", "end",
                             values=(v["game"], v["name"], v["channel"], v["installed_at"]))
        n = len(self._installed)
        self.run_status.config(
            text=t("installed_count_all", n=n) if n else t("no_installs"))

    def _selected_version(self):
        sel = self.tree.selection()
        if not sel:
            return None
        idx = self.tree.index(sel[0])
        if 0 <= idx < len(self._installed):
            return self._installed[idx]
        return None

    def run_selected(self):
        v = self._selected_version()
        if not v:
            messagebox.showinfo(t("need_select_title"), t("need_run_select")); return
        if not v["exe"]:
            messagebox.showerror(t("cant_run_title"), t("no_exe")); return
        try:
            launch_game(v["exe"])
            self.run_status.config(text=t("running", name=os.path.basename(v["exe"])))
        except Exception as e:
            messagebox.showerror(t("run_failed"), str(e))

    def open_folder(self):
        v = self._selected_version()
        if not v:
            messagebox.showinfo(t("need_select_title"), t("need_open_select")); return
        try:
            os.startfile(v["path"])
        except Exception as e:
            messagebox.showerror(t("open_failed"), str(e))

    def delete_selected(self):
        v = self._selected_version()
        if not v:
            messagebox.showinfo(t("need_select_title"), t("need_delete_select")); return
        if not messagebox.askyesno(t("delete_confirm_title"),
                                   t("delete_confirm", name=v["name"], path=v["path"])):
            return
        try:
            shutil.rmtree(v["path"])
            self.refresh_installed()
            self.run_status.config(text=t("deleted", name=v["name"]))
        except Exception as e:
            messagebox.showerror(t("delete_failed"), str(e))

    def manage_content(self):
        v = self._selected_version()
        if not v:
            messagebox.showinfo(t("need_select_title"), t("need_mod_select")); return
        ContentWindow(self.root, v)


# ---------------------------------------------------------------------------
# 콘텐츠 관리 창  (모드/사운드/타일셋/폰트 탭. grab 모달이라 언어는 열 때 기준 고정)
# ---------------------------------------------------------------------------
class ContentWindow:
    def __init__(self, master, version):
        self.version = version
        win = tk.Toplevel(master)
        self.win = win
        win.title(t("content_title", name=version["name"]))
        win.geometry("600x500")
        win.minsize(520, 420)
        win.transient(master)
        win.grab_set()

        nb = ttk.Notebook(win)
        nb.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        for key in ("mods", "sound", "tiles", "fonts"):
            spec = RESOURCE_SPECS[key]
            frame = ttk.Frame(nb, padding=10)
            nb.add(frame, text=t(spec["label_key"]))
            ResourceTab(self, frame, spec)

        ttk.Button(win, text=t("mod_btn_close"), command=win.destroy).pack(pady=(0, 8))


class ResourceTab:
    """모드/사운드/타일셋/폰트 한 종류를 다루는 탭. spec 으로 동작이 결정된다."""
    def __init__(self, owner, parent, spec):
        self.win = owner.win
        self.version = owner.version
        self.spec = spec
        self.rdir = find_resource_dir(self.version, spec)
        self._items = []

        ttk.Label(parent, text=t("res_subtitle"), foreground="#666").pack(anchor="w", pady=(0, 2))
        if spec.get("note_key"):
            ttk.Label(parent, text=t(spec["note_key"]), foreground="#b06000",
                      wraplength=540, justify="left").pack(anchor="w", pady=(0, 4))

        cols = ("name", "source", "folder")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", height=10)
        self.tree.heading("name", text=t("mod_col_name"))
        self.tree.heading("source", text=t("col_source"))
        self.tree.heading("folder", text=t("mod_col_folder"))
        self.tree.column("name", width=260)
        self.tree.column("source", width=70, anchor="center")
        self.tree.column("folder", width=180)
        self.tree.pack(fill="both", expand=True, pady=4)

        self.status = ttk.Label(parent, text="", foreground="#666")
        self.status.pack(anchor="w", pady=(2, 6))

        btns = ttk.Frame(parent)
        btns.pack(fill="x")
        ttk.Button(btns, text=t("mod_btn_url"), command=self.add_url).pack(side="left")
        add_label = t("res_add_file") if spec["kind"] == "files" else t("mod_btn_zip")
        ttk.Button(btns, text=add_label, command=self.add_local).pack(side="left", padx=6)
        if spec["kind"] == "files":  # 폰트: 시스템 폰트에서 추가
            ttk.Button(btns, text=t("sysfont_btn"), command=self.add_system_font).pack(side="left", padx=6)
        ttk.Button(btns, text=t("mod_btn_remove"), command=self.remove).pack(side="left")
        if spec["kind"] == "files":  # 폰트: config 에 편집/적용
            ttk.Button(btns, text=t("font_apply_btn"), command=self.apply_font).pack(side="left", padx=6)
        ttk.Button(btns, text=t("mod_btn_open"), command=self.open_dir).pack(side="right")

        self.refresh()

    # ---- 공통 ----
    def _set_status(self, text, color="#666"):
        self.win.after(0, lambda: self.status.config(text=text, foreground=color))

    def _ensure_dir(self):
        if not self.rdir:
            self.rdir = find_resource_dir(self.version, self.spec, create=True)
        if not self.rdir:
            messagebox.showerror(t("mod_err_title"), t("res_no_dir_err"), parent=self.win)
            return False
        return True

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.rdir = find_resource_dir(self.version, self.spec) or self.rdir
        self._items = scan_resources(self.rdir, self.spec)
        for it in self._items:
            src = t("src_bundled") if it.get("bundled") else t("src_added")
            self.tree.insert("", "end", values=(it["name"], src, it["folder"]))
        if self.rdir:
            self.status.config(text=t("res_count", n=len(self._items), dir=self.rdir), foreground="#666")
        else:
            self.status.config(text=t("res_no_dir"), foreground="red")

    def _selected(self):
        sel = self.tree.selection()
        if not sel:
            return None
        idx = self.tree.index(sel[0])
        return self._items[idx] if 0 <= idx < len(self._items) else None

    # ---- 추가 (로컬 파일/zip) ----
    def add_local(self):
        if not self._ensure_dir():
            return
        if self.spec["kind"] == "files":
            pat = " ".join("*" + e for e in self.spec["exts"])
            ft = [(t("res_font_filter"), pat), (t("mod_zip_filter"), "*.zip"), (t("all_files"), "*.*")]
        else:
            ft = [(t("mod_zip_filter"), "*.zip"), (t("all_files"), "*.*")]
        files = filedialog.askopenfilenames(parent=self.win, title=t("res_add_title"), filetypes=ft)
        if not files:
            return
        added = 0
        for fp in files:
            try:
                if fp.lower().endswith(".zip"):
                    with open(fp, "rb") as fh:
                        added += self._copy_zip(fh.read(),
                                                os.path.splitext(os.path.basename(fp))[0])
                elif self.spec["kind"] == "files":
                    added += self._copy_file(fp)
                else:
                    messagebox.showwarning(t("mod_add_failed"), t("res_zip_only"), parent=self.win)
            except Exception as e:
                messagebox.showerror(t("mod_add_failed"), f"{os.path.basename(fp)}:\n{e}", parent=self.win)
        if added:
            messagebox.showinfo(t("done_title"), t("mod_added_n", n=added), parent=self.win)
        self.refresh()

    # ---- 추가 (URL) ----
    def add_url(self):
        url = simpledialog.askstring(t("mod_url_title"), t("mod_url_prompt"), parent=self.win)
        if not url or not url.strip():
            return
        url = url.strip()
        if not self._ensure_dir():
            return
        self._set_status(t("mod_dl_status", url=url), "#0066cc")
        threading.Thread(target=self._dl_thread, args=(url,), daemon=True).start()

    def _dl_thread(self, url):
        try:
            zip_url, fallback = resolve_mod_url(url)
            data = download_bytes(zip_url)
            is_zip = zip_url.lower().split("?")[0].endswith(".zip") or "/archive/" in zip_url
        except Exception as e:
            self._set_status(t("failed"), "red")
            self.win.after(0, lambda: messagebox.showerror(t("mod_dl_failed"), str(e), parent=self.win))
            return
        self.win.after(0, lambda: self._finish_url(data, fallback, url, is_zip))

    def _finish_url(self, data, fallback, url, is_zip):
        try:
            ext = os.path.splitext(url.split("?")[0])[1].lower()
            if (not is_zip) and self.spec["kind"] == "files" and ext in self.spec["exts"]:
                count = self._write_file(os.path.basename(url.split("?")[0]), data)
            else:
                count = self._copy_zip(data, fallback)
        except zipfile.BadZipFile:
            self._set_status(t("failed"), "red")
            messagebox.showerror(t("mod_add_failed"), t("mod_not_zip"), parent=self.win); return
        except Exception as e:
            self._set_status(t("failed"), "red")
            messagebox.showerror(t("mod_add_failed"), str(e), parent=self.win); return
        if count:
            messagebox.showinfo(t("done_title"), t("mod_added_n", n=count), parent=self.win)
        else:
            messagebox.showwarning(t("mod_none_title"), t("res_none_msg"), parent=self.win)
        self.refresh()

    # ---- 설치 구현 ----
    def _copy_zip(self, data, fallback):
        """zip 바이트를 풀어 spec 에 맞는 콘텐츠를 대상 폴더로 복사. 개수 반환."""
        tmp = tempfile.mkdtemp(prefix="cdda_res_")
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(tmp)
            count = 0
            if self.spec["kind"] == "folder":
                idf = self.spec["id_file"]
                srcs = [dp for dp, _, files in os.walk(tmp) if idf in files]
                for md in srcs:
                    raw = fallback if os.path.normpath(md) == os.path.normpath(tmp) \
                        else os.path.basename(md)
                    name = safe_folder_name(strip_branch_suffix(raw))
                    dest = os.path.join(self.rdir, name)
                    if os.path.isdir(dest):
                        if not messagebox.askyesno(t("mod_exists_title"),
                                t("mod_exists_msg", name=name), parent=self.win):
                            continue
                        shutil.rmtree(dest)
                    shutil.copytree(md, dest)
                    open(os.path.join(dest, MOD_MARKER), "w").close()
                    count += 1
            else:  # files (폰트): zip 안 폰트 파일들을 추출
                for dp, _, files in os.walk(tmp):
                    for fn in files:
                        if os.path.splitext(fn)[1].lower() in self.spec["exts"]:
                            count += self._copy_file(os.path.join(dp, fn))
            return count
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _copy_file(self, src):
        """개별 파일(폰트)을 대상 폴더로 복사 + 마커. 1 또는 0 반환."""
        return self._write_file(os.path.basename(src), open(src, "rb").read())

    def _write_file(self, filename, data):
        dest = os.path.join(self.rdir, filename)
        if os.path.isfile(dest):
            if not messagebox.askyesno(t("mod_exists_title"),
                    t("mod_exists_msg", name=filename), parent=self.win):
                return 0
        with open(dest, "wb") as fh:
            fh.write(data)
        open(dest + FILE_MARKER_SUFFIX, "w").close()
        return 1

    # ---- 제거 / 열기 ----
    def remove(self):
        it = self._selected()
        if not it:
            messagebox.showinfo(t("need_select_title"), t("mod_remove_select"), parent=self.win); return
        if it.get("bundled"):  # 게임 기본 제공 항목은 보호 (지우면 게임이 깨질 수 있음)
            messagebox.showinfo(t("cant_remove_title"), t("cant_remove_bundled"), parent=self.win); return
        if not messagebox.askyesno(t("mod_remove_title"),
                                   t("mod_remove_msg", name=it["name"], path=it["path"]), parent=self.win):
            return
        try:
            if os.path.isdir(it["path"]):
                shutil.rmtree(it["path"])
            else:
                os.remove(it["path"])
                mk = it["path"] + FILE_MARKER_SUFFIX
                if os.path.isfile(mk):
                    os.remove(mk)
            self.refresh()
        except Exception as e:
            messagebox.showerror(t("mod_remove_failed"), str(e), parent=self.win)

    def open_dir(self):
        if not self.rdir or not os.path.isdir(self.rdir):
            messagebox.showinfo(t("mod_no_folder_title"), t("mod_no_folder_msg"), parent=self.win); return
        try:
            os.startfile(self.rdir)
        except Exception as e:
            messagebox.showerror(t("mod_open_failed"), str(e), parent=self.win)

    # ---- 시스템(Windows) 설치 폰트에서 추가 ----
    def add_system_font(self):
        if not self._ensure_dir():
            return
        fonts = list_system_fonts()
        if not fonts:
            messagebox.showinfo(t("sysfont_title"), t("sysfont_none"), parent=self.win); return
        paths = self._pick_system_fonts(fonts)
        if not paths:
            return
        added = 0
        for p in paths:
            try:
                added += self._copy_file(p)
            except Exception as e:
                messagebox.showerror(t("mod_add_failed"), f"{os.path.basename(p)}:\n{e}", parent=self.win)
        if added:
            messagebox.showinfo(t("done_title"), t("mod_added_n", n=added), parent=self.win)
        self.refresh()

    def _pick_system_fonts(self, fonts):
        """설치 폰트 선택 대화창(검색+복수). 선택 경로 리스트 반환(취소 시 빈 리스트)."""
        dlg = tk.Toplevel(self.win)
        dlg.title(t("sysfont_title"))
        dlg.transient(self.win)
        dlg.grab_set()
        dlg.geometry("380x440")
        ttk.Label(dlg, text=t("sysfont_prompt"), wraplength=350,
                  justify="left", padding=(10, 8)).pack(anchor="w")
        fv = tk.StringVar()
        ttk.Entry(dlg, textvariable=fv).pack(fill="x", padx=10)
        lf = ttk.Frame(dlg, padding=10)
        lf.pack(fill="both", expand=True)
        lb = tk.Listbox(lf, selectmode="extended")
        lb.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(lf, command=lb.yview)
        sb.pack(side="right", fill="y")
        lb.config(yscrollcommand=sb.set)
        state = {"items": [], "sel": []}

        def repop(*_):
            q = fv.get().lower().strip()
            lb.delete(0, "end")
            state["items"] = []
            for disp, path in fonts:
                if q in disp.lower():
                    lb.insert("end", disp)
                    state["items"].append(path)
        fv.trace_add("write", repop)
        repop()

        def ok():
            state["sel"] = [state["items"][i] for i in lb.curselection()]
            dlg.destroy()
        lb.bind("<Double-1>", lambda e: ok())
        btns = ttk.Frame(dlg, padding=10)
        btns.pack(fill="x")
        ttk.Button(btns, text=t("sysfont_add"), command=ok).pack(side="right")
        ttk.Button(btns, text=t("cancel"), command=dlg.destroy).pack(side="right", padx=6)
        dlg.wait_window()
        return state["sel"]

    # ---- 폰트 적용 (config/fonts.json 글꼴 + config/options.json 크기) ----
    def apply_font(self):
        it = self._selected()
        if not it:
            messagebox.showinfo(t("need_select_title"), t("mod_remove_select"), parent=self.win); return
        res = self._ask_font_apply(it["name"])
        if res is None:
            return  # 취소
        cats, sizes = res
        if not cats and not sizes:
            messagebox.showwarning(t("font_apply_title"), t("font_apply_none"), parent=self.win); return
        detail = []
        try:
            if cats:
                dest = apply_font_to_config(self.version, it["path"], cats)
                detail.append(t("applied_typeface", dest=dest))
            if sizes:
                n = set_option_values(self.version, sizes)
                if n:
                    detail.append(t("applied_sizes", n=n))
        except Exception as e:
            messagebox.showerror(t("font_apply_failed"), str(e), parent=self.win); return
        messagebox.showinfo(t("done_title"),
                            t("applied_summary", detail="\n".join(detail)), parent=self.win)

    def _ask_font_apply(self, font_name):
        """글꼴 영역 + 크기 입력 대화창. (cats, sizes) 또는 None(취소).
        cats: 적용할 typeface 카테고리 리스트. sizes: {옵션키: 값} (변경분만)."""
        opts = load_options(self.version)  # None 이면 options.json 없음(크기 비활성)
        dlg = tk.Toplevel(self.win)
        dlg.title(t("font_apply_title"))
        dlg.transient(self.win)
        dlg.grab_set()
        dlg.resizable(False, False)
        ttk.Label(dlg, text=t("font_apply_prompt", name=font_name),
                  padding=(12, 10)).pack(anchor="w")

        body = ttk.Frame(dlg, padding=(14, 0))
        body.pack(fill="x")
        defaults = {"typeface": True, "gui_typeface": True,
                    "map_typeface": False, "overmap_typeface": False}
        labels = {"typeface": "font_cat_typeface", "gui_typeface": "font_cat_gui",
                  "map_typeface": "font_cat_map", "overmap_typeface": "font_cat_overmap"}
        # 게임이 지원하는 카테고리만 노출 (CDBN 은 gui_typeface 없음)
        supported = supported_font_categories(self.version)
        cvars = {}
        for cat in FONT_CATEGORIES:
            if cat not in supported:
                continue
            v = tk.BooleanVar(value=defaults[cat])
            cvars[cat] = v
            ttk.Checkbutton(body, text=t(labels[cat]), variable=v).pack(anchor="w")

        # 크기 섹션 (options.json)
        sf = ttk.Labelframe(dlg, text=t("font_size_section"), padding=10)
        sf.pack(fill="x", padx=12, pady=(8, 0))
        size_vars = {}
        labels_fs = {"FONT_WIDTH": "fs_width", "FONT_HEIGHT": "fs_height", "FONT_SIZE": "fs_size"}
        if opts is None:
            ttk.Label(sf, text=t("font_size_disabled"), foreground="#b06000").pack(anchor="w")
        else:
            row = ttk.Frame(sf); row.pack(fill="x")
            for key in FONT_SIZE_KEYS:
                ttk.Label(row, text=t(labels_fs[key])).pack(side="left")
                var = tk.StringVar(value=str(get_option_value(opts, key) or ""))
                size_vars[key] = var
                ttk.Entry(row, textvariable=var, width=5).pack(side="left", padx=(2, 10))

        state = {"ok": False}
        btns = ttk.Frame(dlg, padding=10)
        btns.pack(fill="x")

        def ok():
            state["ok"] = True
            dlg.destroy()
        ttk.Button(btns, text=t("font_apply_ok"), command=ok).pack(side="right")
        ttk.Button(btns, text=t("cancel"), command=dlg.destroy).pack(side="right", padx=6)
        dlg.wait_window()
        if not state["ok"]:
            return None

        cats = [c for c in FONT_CATEGORIES if c in cvars and cvars[c].get()]
        sizes = {}
        for key, var in size_vars.items():
            txt = var.get().strip()
            if not txt:
                continue
            if not txt.isdigit():
                messagebox.showwarning(t("font_apply_title"), t("font_size_bad"), parent=self.win)
                return ([], {})  # 잘못된 입력 → 아무것도 안 함
            cur = get_option_value(opts, key)
            if str(cur) != txt:        # 바뀐 값만
                sizes[key] = txt
        return cats, sizes


def main():
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = _TB_WINDOW(themename=UI_THEME) if _TB_WINDOW is not None else tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
