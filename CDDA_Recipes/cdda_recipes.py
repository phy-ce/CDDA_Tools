#!/usr/bin/env python
"""CDDA Recipe Helper — offline crafting assistant for Cataclysm: DDA / BN.

A small local web app (standard library only). It reads the installed game's
data/json (optionally including added mods), indexes items + recipes +
requirements, and serves a browser UI that answers:

  - "How do I craft X?"  (ingredients, tools, qualities, skills, how to learn)
  - "What can I make with X?"  (reverse: recipes that use X)

Every item reference is a real hyperlink, so you can click an ingredient to see
its own recipe (forward link) or follow the "used as an ingredient in" list
(back link). Names are localized via the game's own gettext files (EN / 한국어 /
日本語 / …). Run it and your browser opens automatically.
"""
import os
import re
import glob
import json
import html
import gettext
import socket
import threading
import webbrowser
from urllib.parse import urlencode, parse_qs, urlparse, quote
from http.server import BaseHTTPRequestHandler, HTTPServer

HOME = os.path.expanduser("~")
GAMES_ROOT = os.path.join(HOME, "Games")
GAME_SUBDIRS = ["Cataclysm-DDA", "Cataclysm-BN"]

LOCALE_NAMES = {
    "en": "English", "ko": "한국어", "ja": "日本語",
    "zh_CN": "简体中文", "zh_TW": "繁體中文", "ru_RU": "Русский",
    "de": "Deutsch", "fr": "Français", "es_ES": "Español", "es_AR": "Español (AR)",
    "pt_BR": "Português (BR)", "it_IT": "Italiano", "pl_PL": "Polski",
}

# UI labels (the app's own chrome). Item/recipe *content* is localized from the
# game files; these are the surrounding labels. Falls back to English.
UI_STRINGS = {
    "en": {
        "brand": "CDDA Recipes", "search_ph": "search item name…", "mods": "mods",
        "hint": "{n} craftable items · {r} recipes. Type an item name above, or open "
                "one from a recipe to start clicking around.",
        "no_match": "No match.", "more": "… {n} more, refine your search.",
        "recipe": "Recipe", "skill": "Skill", "difficulty": "difficulty",
        "also_needs": "Also needs", "time": "Time", "learn": "Learn",
        "autolearn": "auto-learned", "books": "Books", "toolq": "Tool quality",
        "tools": "Tools", "ingredients": "Ingredients",
        "no_ing": "(no listed ingredients — may be gathered/disassembled)",
        "not_craftable": "Not craftable here — no recipe.",
        "used_in": "Used as an ingredient in ({n})",
        "disassembles": "Disassembles into", "tree": "Crafting tree",
        "weight": "Weight", "volume": "Volume", "material": "Material", "melee": "Melee",
        "categories": "Categories", "all_skills": "All skills", "max_lv": "Max level",
        "lv": "Lv", "found": "Found in (loot groups)", "all_cats": "← All categories",
        "items_n": "{n} items", "item_col": "Item", "browse_hint":
        "Pick a category to browse, or search by name above.",
        "settings": "Settings", "saved": "Saved.",
        "npc_loot": "Show NPC-inventory sources",
        "npc_loot_help": "Include groups carried by NPCs (NC_*) in 'Found in'. Off by default — they're noisy.",
        "group": "Loot group", "g_contains": "Can contain ({n})",
        "g_includes": "Includes groups ({n})", "g_partof": "Part of ({n})",
        "nav_items": "Items", "nav_loot": "Loot sources", "nav_mechanics": "Mechanics",
        "loot_title": "Loot sources",
        "loot_hint": "Top-level loot groups — the entry points where loot actually "
            "spawns on the map. Click one to drill into its sub-groups and items "
            "(each with its spawn chance). {n} groups.",
        "mech_title": "How it works (mechanics)",
        "g_contents": "Contents ({n})",
        "g_note_coll": "Collection — each entry rolls independently, so each % is its "
            "own chance and the total can exceed 100%.",
        "g_note_dist": "Distribution — exactly one entry is chosen by weight, so the "
            "chances add up to 100%.",
        "learn_more": "How probabilities work →", "inline_group": "(nested group)",
        "pick_one": "pick 1 of:", "all_of": "all of:",
        "dropped_by": "Dropped by ({n})", "placed_in": "Placed at ({n})",
        "book": "Book", "book_skill": "Trains skill", "book_recipes": "Recipes it teaches ({n})",
        "very_common": "Very common — found in most buildings. Top spots:",
        "abilities": "What you can do", "actions": "Use / actions",
        "techniques": "Melee techniques", "flags": "Flags",
        "expected_yield": "Expected yield ({n})", "avg_label": "avg",
    },
    "ko": {
        "brand": "CDDA 레시피", "search_ph": "아이템 이름 검색…", "mods": "모드",
        "hint": "제작 가능 {n}개 · 레시피 {r}개. 위에 아이템 이름을 입력하거나, "
                "레시피에서 아이템을 열어 클릭하며 탐색하세요.",
        "no_match": "검색 결과 없음.", "more": "… 외 {n}개, 검색어를 좁히세요.",
        "recipe": "레시피", "skill": "스킬", "difficulty": "난이도",
        "also_needs": "추가 요구", "time": "시간", "learn": "습득",
        "autolearn": "자동 습득", "books": "책", "toolq": "도구 품질",
        "tools": "도구", "ingredients": "재료",
        "no_ing": "(표시된 재료 없음 — 채집/분해로 얻을 수 있음)",
        "not_craftable": "여기서는 제작 불가 — 레시피 없음.",
        "used_in": "이 아이템이 쓰이는 곳 ({n})",
        "disassembles": "분해 시 나오는 것", "tree": "제작 트리",
        "weight": "무게", "volume": "부피", "material": "재질", "melee": "근접",
        "categories": "카테고리", "all_skills": "모든 스킬", "max_lv": "최대 레벨",
        "lv": "Lv", "found": "입수 (루트 그룹)", "all_cats": "← 전체 카테고리",
        "items_n": "{n}개", "item_col": "아이템", "browse_hint":
        "카테고리를 골라 둘러보거나, 위에서 이름으로 검색하세요.",
        "settings": "설정", "saved": "저장됨.",
        "npc_loot": "NPC 소지 입수원 표시",
        "npc_loot_help": "'입수'에 NPC가 소지한 그룹(NC_*)도 포함. 기본 꺼짐 — 노이즈가 많습니다.",
        "group": "루트 그룹", "g_contains": "나올 수 있는 아이템 ({n})",
        "g_includes": "하위 그룹 ({n})", "g_partof": "상위 그룹 ({n})",
        "nav_items": "아이템", "nav_loot": "입수처", "nav_mechanics": "메커니즘",
        "loot_title": "입수처",
        "loot_hint": "최상위 루트 그룹 — 맵에서 전리품이 실제로 생성되는 입수처입니다. "
            "클릭하면 하위 그룹과 아이템(각각의 생성 확률 포함)으로 타고 내려갑니다. "
            "그룹 {n}개.",
        "mech_title": "동작 방식 (메커니즘)",
        "g_contents": "구성 ({n})",
        "g_note_coll": "collection — 각 항목이 독립적으로 굴려져, 각 %는 그 항목 자체의 "
            "확률이고 합계가 100%를 넘을 수 있습니다.",
        "g_note_dist": "distribution — 가중치로 딱 하나만 선택되므로, 확률의 합이 100%입니다.",
        "learn_more": "확률이 계산되는 방식 →", "inline_group": "(중첩 그룹)",
        "pick_one": "1개 선택:", "all_of": "모두 포함:",
        "dropped_by": "드롭원 ({n})", "placed_in": "배치 위치 ({n})",
        "book": "책", "book_skill": "훈련 스킬", "book_recipes": "배우는 제작법 ({n})",
        "very_common": "매우 흔함 — 대부분의 건물에 있음. 확률 높은 곳:",
        "abilities": "할 수 있는 것", "actions": "사용 동작",
        "techniques": "근접 기술", "flags": "특성(플래그)",
        "expected_yield": "예상 산출 ({n})", "avg_label": "평균",
    },
    "ja": {
        "brand": "CDDAレシピ", "search_ph": "アイテム名で検索…", "mods": "MOD",
        "hint": "製作可能 {n}件 · レシピ {r}件。上にアイテム名を入力するか、"
                "レシピからアイテムを開いてクリックで辿ってください。",
        "no_match": "該当なし。", "more": "… 他 {n}件、検索語を絞ってください。",
        "recipe": "レシピ", "skill": "スキル", "difficulty": "難易度",
        "also_needs": "追加要件", "time": "時間", "learn": "習得",
        "autolearn": "自動習得", "books": "書籍", "toolq": "道具品質",
        "tools": "道具", "ingredients": "材料",
        "no_ing": "（記載の材料なし — 採取/分解で入手）",
        "not_craftable": "ここでは製作不可 — レシピなし。",
        "used_in": "材料として使われるレシピ ({n})",
        "disassembles": "分解で得られる", "tree": "製作ツリー",
        "weight": "重量", "volume": "体積", "material": "材質", "melee": "近接",
        "categories": "カテゴリ", "all_skills": "全スキル", "max_lv": "最大レベル",
        "lv": "Lv", "found": "入手（ルートグループ）", "all_cats": "← 全カテゴリ",
        "items_n": "{n}件", "item_col": "アイテム", "browse_hint":
        "カテゴリを選んで閲覧するか、上で名前検索してください。",
        "settings": "設定", "saved": "保存しました。",
        "npc_loot": "NPC所持の入手元を表示",
        "npc_loot_help": "「入手」にNPC所持グループ（NC_*）も含める。既定はオフ — ノイズが多いです。",
        "group": "ルートグループ", "g_contains": "入りうるアイテム ({n})",
        "g_includes": "内包グループ ({n})", "g_partof": "上位グループ ({n})",
        "nav_items": "アイテム", "nav_loot": "入手元", "nav_mechanics": "仕組み",
        "loot_title": "入手元",
        "loot_hint": "最上位のルートグループ — マップで戦利品が実際に生成される入手元です。"
            "クリックすると下位グループやアイテム（各生成確率つき）へ辿れます。"
            "グループ {n}件。",
        "mech_title": "仕組み（メカニズム）",
        "g_contents": "構成 ({n})",
        "g_note_coll": "collection — 各項目が独立して抽選され、各％はその項目自身の確率で、"
            "合計が100％を超えることがあります。",
        "g_note_dist": "distribution — 重みで1つだけ選ばれるため、確率の合計は100％です。",
        "learn_more": "確率の計算方法 →", "inline_group": "（入れ子グループ）",
        "pick_one": "1つ選択:", "all_of": "すべて含む:",
        "dropped_by": "ドロップ元 ({n})", "placed_in": "配置場所 ({n})",
        "book": "書籍", "book_skill": "訓練スキル", "book_recipes": "習得できるレシピ ({n})",
        "very_common": "とても一般的 — ほとんどの建物にあり。確率の高い場所:",
        "abilities": "できること", "actions": "使用・動作",
        "techniques": "近接技", "flags": "フラグ",
        "expected_yield": "期待産出 ({n})", "avg_label": "平均",
    },
}


def T(ctx, key, **kw):
    s = UI_STRINGS.get(ctx["lang"], UI_STRINGS["en"]).get(key) or UI_STRINGS["en"][key]
    return s.format(**kw) if kw else s


# recipe category codes -> readable names. Order = how they're listed.
CAT_NAMES = {
    "CC_WEAPON": {"en": "Weapons", "ko": "무기", "ja": "武器"},
    "CC_AMMO": {"en": "Ammo", "ko": "탄약", "ja": "弾薬"},
    "CC_ARMOR": {"en": "Armor / Clothing", "ko": "방어구 / 의류", "ja": "防具 / 衣類"},
    "CC_FOOD": {"en": "Food & Drink", "ko": "음식 / 음료", "ja": "食料 / 飲料"},
    "CC_CHEM": {"en": "Chemistry", "ko": "화학", "ja": "化学"},
    "CC_ELECTRONIC": {"en": "Electronics", "ko": "전자기기", "ja": "電子機器"},
    "CC_ANIMALS": {"en": "Animals", "ko": "동물", "ja": "動物"},
    "CC_OTHER": {"en": "Other", "ko": "기타", "ja": "その他"},
}


def cat_name(code, lang):
    d = CAT_NAMES.get(code)
    if not d:
        return code.replace("CC_", "").replace("_", " ").title()
    return d.get(lang) or d["en"]


# Mechanics page: localized documentation of how the game data (and this tool's
# numbers) actually work. Each value is a list of (heading, body-html) sections;
# bodies are trusted internal HTML. Missing languages fall back to English.
MECH_DOC = {
    "en": [
        ("Data vs. engine",
         "<p>Cataclysm keeps almost all of its <b>content</b> as JSON under "
         "<code>data/json/</code>. The C++ engine only knows the <i>mechanisms</i> "
         "(how a recipe is crafted, how loot is rolled); the JSON says <i>what</i> "
         "exists. This helper reads that JSON, so everything matches your exact "
         "version and mods.</p>"),
        ("copy-from inheritance",
         "<p>An item often defines only a few fields and inherits the rest from a "
         "parent through <code>copy-from</code>. The names, descriptions and stats "
         "shown here are resolved by following that chain.</p>"),
        ("Shared requirements (using / LIST)",
         "<p>Recipes rarely spell out raw ingredients. They pull shared blocks from "
         "<code>requirements/</code> via <code>using</code>, and a component tagged "
         "<code>LIST</code> expands into the items of a named requirement. The "
         "ingredient lists you see already have these expanded.</p>"),
        ("Loot groups: collection vs distribution",
         "<p>An <code>item_group</code> is a loot table, and its <code>subtype</code> "
         "decides the probability math:</p><ul>"
         "<li><b>collection</b> — every entry rolls <i>independently</i>. Its "
         "<code>prob</code> is a plain percent (default 100), so the chances need "
         "not add up to 100% and several entries can appear at once.</li>"
         "<li><b>distribution</b> — exactly <i>one</i> entry is chosen, weighted by "
         "<code>prob</code>. Each chance is <code>prob ÷ (sum of all prob)</code>, "
         "so they add up to 100%.</li></ul>"),
        ("Cascading down nested groups",
         "<p>An entry can point at another group, which has its own subtype. To get "
         "an item's overall chance you <b>multiply down the tree</b>: e.g. "
         "P(a book in a school) = P(its sub-group is rolled) × P(that book within "
         "the sub-group). If the same item is reachable by several paths, add those "
         "chances together.</p>"),
        ("Why the % is approximate",
         "<p>The percentages shown are per-group spawn chances. The real in-game "
         "odds also depend on how mapgen places the group — it may be rolled several "
         "times, or only placed sometimes — plus item counts and containers, which "
         "live in the map files, not the group. Treat the numbers as a solid guide, "
         "not an exact rate.</p>"),
    ],
    "ko": [
        ("데이터 vs. 엔진",
         "<p>Cataclysm은 거의 모든 <b>콘텐츠</b>를 <code>data/json/</code> 아래 JSON으로 "
         "보관합니다. C++ 엔진은 <i>메커니즘</i>(레시피가 어떻게 제작되는지, 전리품이 "
         "어떻게 굴려지는지)만 알고, <i>무엇이</i> 존재하는지는 JSON이 정합니다. 이 도구는 "
         "그 JSON을 직접 읽으므로 당신의 정확한 버전·모드와 일치합니다.</p>"),
        ("copy-from 상속",
         "<p>아이템은 보통 일부 필드만 정의하고 나머지는 <code>copy-from</code>으로 부모에서 "
         "상속받습니다. 여기 표시되는 이름·설명·스탯은 그 사슬을 따라가 해석한 값입니다.</p>"),
        ("공유 요구사항 (using / LIST)",
         "<p>레시피는 원재료를 직접 적는 경우가 드뭅니다. <code>using</code>으로 "
         "<code>requirements/</code>의 공유 블록을 끌어오고, <code>LIST</code>로 표시된 "
         "구성요소는 명명된 요구사항의 아이템들로 펼쳐집니다. 화면의 재료 목록은 이미 이걸 "
         "펼친 상태입니다.</p>"),
        ("루트 그룹: collection vs distribution",
         "<p><code>item_group</code>은 전리품 표이고, <code>subtype</code>에 따라 확률 계산이 "
         "달라집니다:</p><ul>"
         "<li><b>collection</b> — 각 항목이 <i>독립적으로</i> 굴려집니다. <code>prob</code>은 "
         "그대로 퍼센트(기본 100)라, 확률 합이 100%가 아니어도 되고 여러 항목이 동시에 "
         "나올 수 있습니다.</li>"
         "<li><b>distribution</b> — 딱 <i>하나</i>만 <code>prob</code> 가중치로 선택됩니다. "
         "각 확률은 <code>prob ÷ (모든 prob의 합)</code>이라 합이 100%입니다.</li></ul>"),
        ("중첩 그룹 타고 내려가기",
         "<p>항목이 또 다른 그룹을 가리킬 수 있고, 그 그룹도 자기 subtype을 가집니다. 어떤 "
         "아이템의 전체 확률을 구하려면 <b>트리를 따라 곱하면</b> 됩니다: 예) P(학교에서 그 책) "
         "= P(해당 하위 그룹이 굴려짐) × P(그 하위 그룹 안에서 그 책). 같은 아이템이 여러 "
         "경로로 도달 가능하면 그 확률들을 더합니다.</p>"),
        ("왜 %가 근사치인가",
         "<p>표시된 퍼센트는 그룹 단위의 생성 확률입니다. 실제 게임 확률은 mapgen이 그 그룹을 "
         "어떻게 배치하는지(여러 번 굴리거나, 가끔만 배치)와 아이템 개수·컨테이너에도 "
         "좌우되는데, 이건 그룹이 아니라 맵 파일에 있습니다. 숫자는 정확한 비율이 아니라 "
         "믿을 만한 길잡이로 보세요.</p>"),
    ],
    "ja": [
        ("データ vs. エンジン",
         "<p>Cataclysmはほぼ全ての<b>コンテンツ</b>を<code>data/json/</code>下のJSONとして"
         "保持します。C++エンジンは<i>仕組み</i>（レシピの作り方、戦利品の抽選方法）だけを"
         "知り、<i>何が</i>存在するかはJSONが決めます。本ツールはそのJSONを直接読むため、"
         "お使いの正確なバージョン・MODと一致します。</p>"),
        ("copy-from 継承",
         "<p>アイテムは多くの場合一部のフィールドのみ定義し、残りは<code>copy-from</code>で"
         "親から継承します。ここに表示される名前・説明・ステータスはその連鎖を辿って"
         "解決した値です。</p>"),
        ("共有要件 (using / LIST)",
         "<p>レシピが原材料を直接書くことは稀です。<code>using</code>で"
         "<code>requirements/</code>の共有ブロックを取り込み、<code>LIST</code>付きの"
         "構成要素は名前付き要件のアイテム群に展開されます。表示中の材料リストは既に展開"
         "済みです。</p>"),
        ("ルートグループ: collection vs distribution",
         "<p><code>item_group</code>は戦利品テーブルで、<code>subtype</code>で確率計算が"
         "変わります:</p><ul>"
         "<li><b>collection</b> — 各項目が<i>独立して</i>抽選されます。<code>prob</code>は"
         "そのままパーセント（既定100）なので、合計が100％でなくてよく、複数同時に"
         "出ることもあります。</li>"
         "<li><b>distribution</b> — <code>prob</code>の重みで1つだけ選ばれます。各確率は"
         "<code>prob ÷ (全probの合計)</code>で、合計は100％です。</li></ul>"),
        ("入れ子グループを辿る",
         "<p>項目が別のグループを指すことがあり、そのグループも独自のsubtypeを持ちます。"
         "あるアイテムの全体確率を求めるには<b>木を辿って掛け算</b>します: 例) "
         "P(学校でその本) = P(その下位グループが抽選) × P(下位グループ内でその本)。同じ"
         "アイテムに複数の経路で到達できる場合はそれらの確率を足します。</p>"),
        ("なぜ％は近似値か",
         "<p>表示される％はグループ単位の生成確率です。実際のゲーム内確率は、mapgenがその"
         "グループをどう配置するか（複数回抽選、または時々のみ配置）や、アイテム数・容器にも"
         "左右され、これらはグループではなくマップファイルにあります。数値は正確な割合では"
         "なく確かな目安として見てください。</p>"),
    ],
}


# object "type" values that are real items (searchable, can have item pages)
ITEM_TYPES = {"GENERIC", "COMESTIBLE", "ARMOR", "TOOL", "TOOL_ARMOR", "TOOLMOD",
              "GUN", "GUNMOD", "MAGAZINE", "AMMO", "BOOK", "BIONIC_ITEM",
              "ENGINE", "WHEEL", "PET_ARMOR", "CONTAINER", "BATTERY"}


# in-memory app settings (single local user). Set from the Settings page.
SETTINGS = {"npc_loot": False}


# ---------------------------------------------------------------------------
# Install discovery + localization (same conventions as CDDA_Installer)
# ---------------------------------------------------------------------------
def name_str(nm):
    if nm is None:
        return None
    if isinstance(nm, str):
        return nm
    if isinstance(nm, dict):
        return nm.get("str") or nm.get("str_sp") or nm.get("str_pl")
    if isinstance(nm, list) and nm:
        return name_str(nm[0])
    return None


def find_json_dir(base):
    cand = os.path.join(base, "data", "json")
    if os.path.isdir(cand):
        return cand
    for dirpath, dirs, _ in os.walk(base):
        if os.path.basename(dirpath) == "data" and "json" in dirs:
            return os.path.join(dirpath, "json")
    return None


def read_meta(path):
    try:
        return json.load(open(os.path.join(path, ".cdda_meta.json"), encoding="utf-8"))
    except Exception:
        return {}


def find_installs():
    installs = []
    for sub in GAME_SUBDIRS:
        root = os.path.join(GAMES_ROOT, sub)
        if not os.path.isdir(root):
            continue
        for entry in sorted(os.listdir(root)):
            vpath = os.path.join(root, entry)
            if not os.path.isdir(vpath):
                continue
            jdir = find_json_dir(vpath)
            if not jdir:
                continue
            meta = read_meta(vpath)
            label = "{}  |  {}".format(meta.get("game", sub), meta.get("version", entry))
            installs.append({"label": label, "json_dir": jdir,
                             "mods_dir": os.path.join(os.path.dirname(jdir), "mods")})
    return installs


def find_locales(json_dir):
    out = {"en": None}
    install_root = os.path.dirname(os.path.dirname(json_dir))
    modir = os.path.join(install_root, "lang", "mo")
    if os.path.isdir(modir):
        for loc in sorted(os.listdir(modir)):
            mos = glob.glob(os.path.join(modir, loc, "LC_MESSAGES", "*.mo"))
            if mos:
                out[loc] = mos[0]
    return out


class Translator:
    def __init__(self, mo_path=None):
        self.gt = None
        self._ctx_fallback = {}
        if mo_path:
            try:
                self.gt = gettext.GNUTranslations(open(mo_path, "rb"))
                for k, v in self.gt._catalog.items():
                    if isinstance(k, str) and "\x04" in k:
                        self._ctx_fallback.setdefault(k.split("\x04", 1)[1], v)
            except Exception:
                self.gt = None

    def __call__(self, s):
        if not self.gt or not s:
            return s
        r = self.gt.gettext(s)
        if r != s:
            return r
        return self._ctx_fallback.get(s, s)


# ---------------------------------------------------------------------------
# Data index
# ---------------------------------------------------------------------------
class DataIndex:
    def __init__(self):
        self.by_id = {}
        self.reqs = {}
        self.quals = {}
        self.recipes = []
        self.by_result = {}
        self.used_in = {}
        self.uncrafts = {}       # item id -> [uncraft entry, ...]
        self.book_recipes = {}   # book id -> [(recipe result, level), ...]
        self.flag_info = {}      # flag id -> info text (json_flag)
        self.action_names = {}   # item_action id -> readable name
        self.item_ids = []       # ids whose type is a real item (for search)
        self.cat_of = {}         # result id -> recipe category code (e.g. CC_WEAPON)
        self.by_cat = {}         # category code -> [result id, ...]
        self.item_groups_of = {}  # item id -> set(group id) it appears in (direct)
        self.group_parents = {}   # child group id -> set(parent group id)
        self.group_items = {}     # group id -> set(item id) it can spawn (direct)
        self.group_subgroups = {}  # group id -> set(child group id)
        self.group_def = {}      # group id -> raw def (kept for probabilities)
        self.group_dropped_by = {}  # group id -> set(monster id) (death_drops)
        self.group_places = {}   # group id -> {location: chance or None} (mapgen)
        self._groups = []        # raw item_group defs, processed after load
        self._monsters = []      # MONSTER defs with death_drops, processed after load
        self._mapgens = []       # mapgen defs, processed after load
        self._palettes = []      # palette defs, processed after load
        self._namecache = {}
        self._desccache = {}
        self.tr = lambda s: s

    def load(self, json_dirs):
        for d in json_dirs:
            for dirpath, _, files in os.walk(d):
                for f in files:
                    if f.endswith(".json"):
                        self._load_file(os.path.join(dirpath, f))
        self._index_recipes()

    def _load_file(self, path):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except Exception:
            return
        for e in (data if isinstance(data, list) else [data]):
            if not isinstance(e, dict):
                continue
            t = e.get("type")
            eid = e.get("id") or e.get("abstract")
            if t == "recipe":
                if not e.get("obsolete"):
                    self.recipes.append(e)
            elif t == "uncraft" and isinstance(e.get("result"), str):
                self.uncrafts.setdefault(e["result"], []).append(e)
            elif t == "item_group" and isinstance(eid, str):
                self._groups.append(e)
            elif t == "requirement" and isinstance(eid, str):
                self.reqs[eid] = e
            elif t == "tool_quality" and isinstance(eid, str):
                self.quals[eid] = name_str(e.get("name")) or eid
            elif t == "json_flag" and isinstance(eid, str):
                if isinstance(e.get("info"), str):
                    self.flag_info[eid] = e["info"]
            elif t == "item_action" and isinstance(eid, str):
                nm = name_str(e.get("name"))
                if nm:
                    self.action_names[eid] = nm
            elif t == "MONSTER" and e.get("death_drops") is not None:
                self._monsters.append(e)
            elif t == "mapgen":
                self._mapgens.append(e)
            elif t == "palette":
                self._palettes.append(e)
            if isinstance(eid, str):
                self.by_id.setdefault(eid, e)

    def _index_recipes(self):
        for r in self.recipes:
            res = r.get("result")
            if not isinstance(res, str):
                continue
            self.by_result.setdefault(res, []).append(r)
            if res not in self.cat_of and r.get("category"):
                self.cat_of[res] = r["category"]
            for iid in self._recipe_component_ids(r):
                self.used_in.setdefault(iid, set()).add(res)
            self._index_book_learn(r, res)
        for res, cat in self.cat_of.items():
            self.by_cat.setdefault(cat, []).append(res)
        self.item_ids = [eid for eid, e in self.by_id.items()
                         if isinstance(e, dict) and e.get("type") in ITEM_TYPES]
        self._index_groups()

    def _index_book_learn(self, recipe, res):
        """Reverse a recipe's book_learn so each book lists the recipes it teaches."""
        def add(bid, lvl):
            if isinstance(bid, str):
                self.book_recipes.setdefault(bid, []).append((res, lvl))
        bl = recipe.get("book_learn")
        if isinstance(bl, list):
            for b in bl:
                if isinstance(b, list) and b:
                    add(b[0], b[1] if len(b) > 1 else None)
                elif isinstance(b, str):
                    add(b, None)
        elif isinstance(bl, dict):
            for bid, v in bl.items():
                add(bid, v.get("skill_level") if isinstance(v, dict) else None)

    def _index_groups(self):
        for g in self._groups:
            gid = g.get("id") or g.get("abstract")
            if not isinstance(gid, str):
                continue
            self.group_def[gid] = g
            items, subgroups = self._group_members(g)
            self.group_items.setdefault(gid, set()).update(items)
            self.group_subgroups.setdefault(gid, set()).update(subgroups)
            for it in items:
                self.item_groups_of.setdefault(it, set()).add(gid)
            for sg in subgroups:
                self.group_parents.setdefault(sg, set()).add(gid)
        self._groups = []
        self._index_sources()

    _REF_KEYS = ("item", "group", "item_group", "groups")

    def _group_refs(self, node, out=None):
        """(gid, chance) for every known item-group id referenced under a
        reference key anywhere inside node. A ref-key string that isn't a known
        group (e.g. a plain item id) is ignored."""
        if out is None:
            out = []
        if isinstance(node, dict):
            ch = node.get("chance")
            for k, v in node.items():
                if k in self._REF_KEYS:
                    for x in (v if isinstance(v, list) else [v]):
                        if isinstance(x, str) and x in self.group_def:
                            out.append((x, ch))
                        elif isinstance(x, (dict, list)):
                            self._group_refs(x, out)
                elif isinstance(v, (dict, list)):
                    self._group_refs(v, out)
        elif isinstance(node, list):
            for x in node:
                self._group_refs(x, out)
        return out

    def _index_sources(self):
        """Reverse index: which monsters drop a group on death, and which map
        locations place it (with the mapgen 'chance' when given)."""
        def locs_of(mg):
            # only real overmap places; nested-mapgen chunks have no location and
            # would show as cryptic ids (e.g. 4x4_cr1), so they're left out
            labels = []

            def flat(x):
                if isinstance(x, str):
                    labels.append(x)
                elif isinstance(x, list):
                    for y in x:
                        flat(y)
            flat(mg.get("om_terrain"))
            return labels

        for mon in self._monsters:
            mid = mon.get("id")
            if not isinstance(mid, str):
                continue
            dd = mon.get("death_drops")
            if isinstance(dd, str):                      # direct group reference
                refs = [(dd, None)] if dd in self.group_def else []
            else:                                        # inline group object
                refs = self._group_refs(dd)
            for gid, _ in refs:
                self.group_dropped_by.setdefault(gid, set()).add(mid)

        # palette id -> set(locations) of the mapgens that pull it in
        pal_locs = {}
        for mg in self._mapgens:
            obj = mg.get("object") or {}
            for p in (obj.get("palettes") or []):
                if isinstance(p, str):
                    pal_locs.setdefault(p, set()).update(locs_of(mg))

        def add_place(gid, loc, ch):
            if not loc:
                return
            d = self.group_places.setdefault(gid, {})
            if loc not in d or (ch is not None and (d[loc] is None or ch > d[loc])):
                d[loc] = ch

        for mg in self._mapgens:
            labels = locs_of(mg)
            for gid, ch in self._group_refs(mg.get("object")):
                for loc in labels:
                    add_place(gid, loc, ch)

        for pal in self._palettes:
            pid = pal.get("id")
            refs = self._group_refs(pal)
            if not refs:
                continue
            targets = pal_locs.get(pid)
            if targets:                       # only attribute to real places
                for gid, ch in refs:
                    for loc in targets:
                        add_place(gid, loc, ch)

        self._monsters = []
        self._mapgens = []
        self._palettes = []

    @staticmethod
    def _group_members(g):
        """Item ids and child-group ids referenced by an item_group def."""
        items, groups = set(), set()

        def walk(node):
            if isinstance(node, list):
                for x in node:
                    if isinstance(x, list) and x and isinstance(x[0], str):
                        items.add(x[0])              # ["id", prob]
                    elif isinstance(x, dict):
                        walk(x)
                    elif isinstance(x, str):
                        items.add(x)
            elif isinstance(node, dict):
                if isinstance(node.get("item"), str):
                    items.add(node["item"])
                if isinstance(node.get("group"), str):
                    groups.add(node["group"])
                for key in ("entries", "items", "distribution", "collection"):
                    if key in node:
                        walk(node[key])

        for key in ("entries", "items", "distribution", "collection"):
            if key in g:
                walk(g[key])
        return items, groups

    def found_in(self, iid):
        """All loot/item groups this item appears in (direct + a couple levels up)."""
        groups = set(self.item_groups_of.get(iid, ()))
        frontier = set(groups)
        for _ in range(2):
            nxt = set()
            for g in frontier:
                nxt |= self.group_parents.get(g, set())
            nxt -= groups
            groups |= nxt
            frontier = nxt
            if not frontier:
                break
        # NPC-inventory groups (NC_*) are noisy; hidden unless enabled in Settings
        if not SETTINGS.get("npc_loot"):
            groups = [g for g in groups if not g.startswith("NC_")]
        return sorted(groups, key=str.lower)

    def loc_name(self, loc):
        """Readable, localized place name for an om_terrain/city_building id, or
        None if it has no name (caller falls back to a cleaned id)."""
        e = self.by_id.get(loc)
        if e:
            nm = name_str(e.get("name"))
            if nm:
                return self.tr(nm)
        return None

    def raw_name(self, eid, _seen=None):
        if not isinstance(eid, str):
            return str(eid)
        if eid in self._namecache:
            return self._namecache[eid]
        seen = _seen or set()
        if eid in seen:
            return eid
        seen.add(eid)
        e = self.by_id.get(eid)
        if not e:
            return eid
        nm = name_str(e.get("name"))
        if nm is None and isinstance(e.get("copy-from"), str):
            nm = self.raw_name(e["copy-from"], seen)
        if nm is None:
            nm = eid
        self._namecache[eid] = nm
        return nm

    def name(self, eid):
        return self.tr(self.raw_name(eid))

    def raw_desc(self, eid, _seen=None):
        """English description (cached), following copy-from inheritance."""
        if not isinstance(eid, str):
            return None
        if eid in self._desccache:
            return self._desccache[eid]
        seen = _seen or set()
        if eid in seen:
            return None
        seen.add(eid)
        e = self.by_id.get(eid)
        if not e:
            return None
        d = name_str(e.get("description"))
        if d is None and isinstance(e.get("copy-from"), str):
            d = self.raw_desc(e["copy-from"], seen)
        self._desccache[eid] = d
        return d

    def desc(self, eid):
        d = self.raw_desc(eid)
        return self.tr(d) if d else None

    def stats(self, eid):
        """A few headline item stats, inherited via copy-from. Raw strings."""
        out, seen = {}, set()
        cur = eid
        keys = ("weight", "volume", "material", "to_hit", "bashing", "cutting")
        while isinstance(cur, str) and cur not in seen:
            seen.add(cur)
            e = self.by_id.get(cur)
            if not e:
                break
            for k in keys:
                if k not in out and e.get(k) is not None:
                    out[k] = e[k]
            cur = e.get("copy-from")
        return out

    def _recipe_component_ids(self, recipe, _depth=0):
        ids = set()
        groups = list(recipe.get("components", []))
        for use in recipe.get("using", []):
            if isinstance(use, list) and use and use[0] in self.reqs:
                groups += self.reqs[use[0]].get("components", [])
        for group in groups:
            if not isinstance(group, list):
                continue
            for entry in group:
                if not isinstance(entry, list) or not entry:
                    continue
                iid = entry[0]
                is_list = len(entry) > 2 and entry[2] == "LIST"
                if is_list and iid in self.reqs and _depth < 3:
                    ids |= self._recipe_component_ids(
                        {"components": self.reqs[iid].get("components", [])}, _depth + 1)
                elif isinstance(iid, str):
                    ids.add(iid)
        return ids

    def craftable(self):
        rows = [(self.name(rid), rid) for rid in self.by_result]
        rows.sort(key=lambda x: x[0].lower())
        return rows

    def all_items(self):
        rows = [(self.name(i), i) for i in self.item_ids]
        rows.sort(key=lambda x: x[0].lower())
        return rows

    def book_info(self, rid):
        """If rid (following copy-from) is a BOOK, the skill it trains and the
        level range; else None. Novels etc. return {} (a book, but no skill)."""
        seen, info, is_book = set(), {}, False
        cur = rid
        while isinstance(cur, str) and cur not in seen:
            seen.add(cur)
            e = self.by_id.get(cur)
            if not e:
                break
            if e.get("type") == "BOOK":
                is_book = True
            for k in ("skill", "max_level", "required_level"):
                if k not in info and e.get(k) is not None:
                    info[k] = e[k]
            cur = e.get("copy-from")
        return info if is_book else None

    def _chain(self, rid):
        """The item def + its copy-from ancestors, most-derived first."""
        out, seen, cur = [], set(), rid
        while isinstance(cur, str) and cur not in seen:
            seen.add(cur)
            e = self.by_id.get(cur)
            if not e:
                break
            out.append(e)
            cur = e.get("copy-from")
        return out

    def flags_of(self, rid):
        """Flags on an item, merging copy-from + extend, minus delete."""
        flags = set()
        for e in reversed(self._chain(rid)):   # parents first so child can delete
            for f in (e.get("flags") or []):
                if isinstance(f, str):
                    flags.add(f)
            ext = e.get("extend")
            if isinstance(ext, dict):
                for f in (ext.get("flags") or []):
                    if isinstance(f, str):
                        flags.add(f)
            dl = e.get("delete")
            if isinstance(dl, dict):
                for f in (dl.get("flags") or []):
                    flags.discard(f)
        return flags

    def qualities_of(self, rid):
        for e in self._chain(rid):
            q = e.get("qualities")
            if q:
                return [(it[0], it[1] if len(it) > 1 else 1)
                        for it in q if isinstance(it, list) and it]
        return []

    def techniques_of(self, rid):
        for e in self._chain(rid):
            t = e.get("techniques")
            if t:
                return [x for x in t if isinstance(x, str)]
        return []

    def actions_of(self, rid):
        """Readable labels for an item's use_action(s)."""
        for e in self._chain(rid):
            ua = e.get("use_action")
            if ua is not None:
                out, seen = [], set()
                for x in (ua if isinstance(ua, list) else [ua]):
                    lbl = None
                    if isinstance(x, str):
                        lbl = self.action_names.get(x) or x.replace("_", " ").lower()
                    elif isinstance(x, dict):
                        lbl = (name_str(x.get("name")) or name_str(x.get("menu_text"))
                               or (x.get("type") or "").replace("_", " "))
                    if lbl:
                        lbl = self.tr(lbl)
                        if lbl not in seen:
                            seen.add(lbl)
                            out.append(lbl)
                return out
        return []

    def flag_desc(self, flag):
        info = self.flag_info.get(flag)
        if not info:
            return None
        return self.tr(re.sub(r"<[^>]+>", "", info)).strip()


# ---------------------------------------------------------------------------
# Caches: one index per (version, include-mods); one translator per (ver, loc)
# ---------------------------------------------------------------------------
INSTALLS = []
_index_cache = {}
_tr_cache = {}
_lock = threading.Lock()


def get_index(ver, mods):
    key = (ver, mods)
    with _lock:
        idx = _index_cache.get(key)
        if idx is None:
            inst = INSTALLS[ver]
            dirs = [inst["json_dir"]]
            if mods and os.path.isdir(inst["mods_dir"]):
                dirs.append(inst["mods_dir"])
            idx = DataIndex()
            idx.load(dirs)
            _index_cache[key] = idx
        return idx


def get_translator(ver, loc):
    key = (ver, loc)
    tr = _tr_cache.get(key)
    if tr is None:
        locs = find_locales(INSTALLS[ver]["json_dir"])
        tr = Translator(locs.get(loc))
        _tr_cache[key] = tr
    return tr


def locales_for(ver):
    return find_locales(INSTALLS[ver]["json_dir"])


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------
def h(s):
    return html.escape(str(s))


def item_url(iid, ctx):
    p = {"id": iid, "ver": ctx["ver"], "lang": ctx["lang"]}
    if ctx["mods"]:
        p["mods"] = 1
    return "/item?" + urlencode(p)


def a_item(idx, iid, ctx, label=None):
    return '<a class="item" href="%s">%s</a>' % (
        item_url(iid, ctx), h(label if label is not None else idx.name(iid)))


def group_url(gid, ctx):
    p = {"group": gid, "ver": ctx["ver"], "lang": ctx["lang"]}
    if ctx["mods"]:
        p["mods"] = 1
    return "/group?" + urlencode(p)


def a_group(gid, ctx):
    return '<a class="chip" href="%s">%s</a>' % (group_url(gid, ctx), h(gid.replace("_", " ")))


def _subtype_and_raw(node):
    """(subtype, raw-entry-list) for either a group def or an inline
    distribution/collection node."""
    if isinstance(node.get("distribution"), list):
        return "distribution", node["distribution"]
    if isinstance(node.get("collection"), list):
        return "collection", node["collection"]
    st = node.get("subtype")
    if st not in ("collection", "distribution"):
        st = "collection"          # default / legacy "old" behaves like a collection
    raw = node.get("entries")
    if raw is None:
        raw = node.get("items")
    return st, (raw if isinstance(raw, list) else [])


def _norm_entries(raw, subtype):
    """Normalize an entry list and attach each entry's spawn 'frac' per the
    parent subtype. An inline distribution/collection keeps its child list in
    'inline' = (subtype, raw) so the caller can recurse and expand it."""
    out = []
    if not isinstance(raw, list):
        return out
    for e in raw:
        if isinstance(e, list) and e and isinstance(e[0], str):
            prob = e[1] if len(e) > 1 and isinstance(e[1], (int, float)) else 100
            out.append({"kind": "item", "id": e[0], "prob": prob, "count": None, "inline": None})
        elif isinstance(e, dict):
            prob = e.get("prob", 100)
            if not isinstance(prob, (int, float)):
                prob = 100
            if isinstance(e.get("item"), str):
                out.append({"kind": "item", "id": e["item"], "prob": prob,
                            "count": e.get("count") or e.get("charges"), "inline": None})
            elif isinstance(e.get("group"), str):
                out.append({"kind": "group", "id": e["group"], "prob": prob,
                            "count": None, "inline": None})
            elif isinstance(e.get("distribution"), list):
                out.append({"kind": "inline", "id": None, "prob": prob, "count": None,
                            "inline": ("distribution", e["distribution"])})
            elif isinstance(e.get("collection"), list):
                out.append({"kind": "inline", "id": None, "prob": prob, "count": None,
                            "inline": ("collection", e["collection"])})
    if subtype == "distribution":
        total = sum(max(0, x["prob"]) for x in out) or 1
        for x in out:
            x["frac"] = max(0, x["prob"]) / total
    else:
        for x in out:
            x["frac"] = min(max(x["prob"], 0), 100) / 100.0
    return out


def pct_html(frac):
    p = frac * 100
    if p >= 99.5:
        return "100%"
    if p >= 1:
        return "~%d%%" % round(p)
    if p > 0:
        return "<1%"
    return "0%"


def _count_html(c):
    if not c:
        return ""
    shown = "%s–%s" % (c[0], c[1]) if isinstance(c, list) and len(c) == 2 else c
    return ' <span class="qty">×%s</span>' % h(shown)


_LOC_DROP = {"basement", "roof", "first", "second", "third", "ground", "upper",
             "lower", "north", "south", "east", "west", "ne", "nw", "se", "sw",
             "open", "closed", "interior", "entrance"}


def _loc_base(loc):
    """Collapse a mapgen om_terrain id to its base place: drop variant tokens
    (numbers, single letters, floor/direction qualifiers) so house_20 /
    house_24_roof -> 'house'."""
    loc = loc.replace("palette:", "")
    toks = [t for t in loc.split("_")
            if t and not t.isdigit() and len(t) > 1 and t.lower() not in _LOC_DROP]
    return " ".join(toks) if toks else loc.replace("_", " ")


def entries_html(idx, ctx, raw, subtype, depth=0):
    """Recursive <li> rows for a group's entries. Inline anonymous groups are
    expanded in place (labelled 'pick 1 of' / 'all of'), so nothing is opaque."""
    rows = []
    for e in _norm_entries(raw, subtype):
        if e["kind"] == "item":
            label, sub = a_item(idx, e["id"], ctx), ""
        elif e["kind"] == "group":
            label, sub = a_group(e["id"], ctx), ""
        else:
            sub_st, sub_raw = e["inline"]
            label = '<span class="slot">%s</span>' % h(
                T(ctx, "pick_one" if sub_st == "distribution" else "all_of"))
            sub = ("" if depth >= 6 else
                   '<ul class="problist sub">%s</ul>'
                   % entries_html(idx, ctx, sub_raw, sub_st, depth + 1))
        rows.append('<li><span class="prob">%s</span><div class="ent">%s%s%s</div></li>'
                    % (pct_html(e["frac"]), label, _count_html(e["count"]), sub))
    return "".join(rows)


# ---------------------------------------------------------------------------
# Loot probability engine.  Each item carries (prob, expected):
#   prob     = probability of getting >= 1   (a "chance"; capped at 1.0)
#   expected = expected count (the average; uncapped, so a >100% chance reads as
#              "more than one expected", not "more than certain")
# Derived from CDDA's own item_group rules (collection = independent rolls,
# distribution = weighted pick-one).
# ---------------------------------------------------------------------------
def _avg_count(c):
    if isinstance(c, list) and len(c) == 2:
        try:
            return (float(c[0]) + float(c[1])) / 2.0
        except (TypeError, ValueError):
            return 1.0
    if isinstance(c, (int, float)):
        return float(c)
    return 1.0


def _chance_ic(chance):
    p = chance / 100.0
    return (min(1.0, p), p)


def _or_ic(a, b):       # two independent rolls (collection)
    return (1.0 - (1.0 - a[0]) * (1.0 - b[0]), a[1] + b[1])


def _add_ic(a, b):      # mutually exclusive options (distribution)
    return (min(1.0, a[0] + b[0]), a[1] + b[1])


def _entry_loot(idx, e, parent_st, seen, depth):
    cnt = _avg_count(e.get("count"))
    if e["kind"] == "item":
        base = _chance_ic(e["prob"]) if parent_st == "collection" else (1.0, 1.0)
        return {e["id"]: (base[0], base[1] * cnt)}
    if e["kind"] == "group":
        gid = e["id"]
        if gid in seen:
            return {}
        d = idx.group_def.get(gid)
        if not d:
            return {}
        sub = group_loot(idx, d, seen | {gid}, depth + 1)
    else:                                   # inline distribution/collection
        st2, raw2 = e["inline"]
        sub = group_loot(idx, {"subtype": st2, "entries": raw2}, seen, depth + 1)
    if parent_st == "collection":           # the sub-group fires with prob%
        m = e["prob"] / 100.0
        sub = {k: (min(1.0, p * m), ex * m) for k, (p, ex) in sub.items()}
    return sub


def group_loot(idx, g, seen=None, depth=0):
    """Flatten an item_group to {item_id: (prob, expected)} over its whole tree."""
    seen = set() if seen is None else seen
    if depth > 12:
        return {}
    st, raw = _subtype_and_raw(g)
    entries = _norm_entries(raw, st)
    loot = {}
    if st == "distribution":
        total = sum(max(0, e["prob"]) for e in entries) or 1
        for e in entries:
            t = max(0, e["prob"]) / total
            for iid, ic in _entry_loot(idx, e, st, seen, depth).items():
                sc = (min(1.0, ic[0] * t), ic[1] * t)
                loot[iid] = sc if iid not in loot else _add_ic(loot[iid], sc)
    else:                                   # collection
        for e in entries:
            for iid, ic in _entry_loot(idx, e, st, seen, depth).items():
                loot[iid] = ic if iid not in loot else _or_ic(loot[iid], ic)
    return loot


def avg_html(expected):
    if expected >= 9.95:
        return "×%d" % round(expected)
    return "×%.1f" % expected


def group_html(idx, group, ctx, depth=0):
    alts = []
    for entry in group:
        if not isinstance(entry, list) or not entry:
            continue
        iid = entry[0]
        cnt = entry[1] if len(entry) > 1 else 1
        is_list = len(entry) > 2 and entry[2] == "LIST"
        if is_list and iid in idx.reqs and depth < 2:
            subs = idx.reqs[iid].get("components", [])
            inner = " <span class=amp>&amp;</span> ".join(
                group_html(idx, g, ctx, depth + 1) for g in subs)
            alts.append('<span class="listreq">%s: %s</span>' % (h(idx.name(iid)), inner))
        else:
            tail = "" if is_list else ' <span class=qty>×%s</span>' % h(cnt)
            alts.append(a_item(idx, iid, ctx) + tail)
    if not alts:
        return "?"
    return ' <span class="or">OR</span> '.join(alts)


def _recipe_comps(idx, recipe):
    """A recipe's components with `using` requirements merged in."""
    comps = list(recipe.get("components") or [])
    for use in recipe.get("using") or []:
        if isinstance(use, list) and use and use[0] in idx.reqs:
            comps += idx.reqs[use[0]].get("components") or []
    return comps


def _otree_node(idx, group, ctx, depth, seen, budget):
    """One ingredient group -> one compact box node in the org-chart tree. The
    box shows a single representative item (the craftable one we expand, else
    the first) + qty, with a '+N' badge when the group has OR alternatives. The
    representative's sub-recipe branches into child boxes below it."""
    entries = [e for e in group if isinstance(e, list) and e]
    if not entries:
        return '<li><div class="node">?</div></li>'
    follow = next((e for e in entries
                   if not (len(e) > 2 and e[2] == "LIST")
                   and e[0] in idx.by_result and e[0] not in seen), None)
    primary = follow or entries[0]
    pid = primary[0]
    cnt = primary[1] if len(primary) > 1 else 1
    is_list = len(primary) > 2 and primary[2] == "LIST"
    label = h(idx.name(pid)) if is_list else a_item(idx, pid, ctx)
    qty = "" if is_list else ' <span class="qty">×%s</span>' % h(cnt)
    alts = len(entries) - 1
    badge = ""
    if alts > 0:
        others = ", ".join(idx.name(e[0]) for e in entries if e is not primary)
        badge = ' <span class="alt" title="%s">+%d</span>' % (h(others), alts)
    box = '<div class="node">%s%s%s</div>' % (label, qty, badge)
    kids = ""
    if follow and depth > 0 and budget[0] > 0:
        budget[0] -= 1
        comps = _recipe_comps(idx, idx.by_result[pid][0])
        kids = "<ul>%s</ul>" % "".join(
            _otree_node(idx, g, ctx, depth - 1, seen | {pid}, budget)
            for g in comps if isinstance(g, list))
    return "<li>%s%s</li>" % (box, kids)


def tree_block(idx, recipe, ctx):
    ids = idx._recipe_component_ids(recipe)
    if not any(i in idx.by_result for i in ids):
        return ""   # nothing craftable to expand
    budget = [80]
    children = "".join(_otree_node(idx, g, ctx, 2, set(), budget)
                       for g in _recipe_comps(idx, recipe) if isinstance(g, list))
    root = a_item(idx, recipe.get("result", ""), ctx)
    tree = ('<ul class="otree"><li><div class="node root">%s</div>'
            '<ul>%s</ul></li></ul>' % (root, children))
    return ('<details class="treebox" open><summary>🌳 %s</summary>'
            '<div class="treescroll">%s</div></details>' % (h(T(ctx, "tree")), tree))


def recipe_html(idx, recipe, ctx, n=None):
    rows = []

    def field(label, value_html):
        rows.append('<div class="f"><span class="k">%s</span>'
                    '<span class="v">%s</span></div>' % (label, value_html))

    skill = recipe.get("skill_used")
    diff = recipe.get("difficulty")
    if skill or diff is not None:
        s = h(idx.name(skill)) if skill else "?"
        if diff is not None:
            s += ' <span class="diff">%s %s</span>' % (h(T(ctx, "difficulty")), h(diff))
        field(h(T(ctx, "skill")), s)
    req = recipe.get("skills_required")
    if req:
        pairs = req if (req and isinstance(req[0], list)) else [req]
        field(h(T(ctx, "also_needs")), ", ".join("%s&nbsp;%s" % (h(idx.name(p[0])), h(p[1]))
                                                  for p in pairs if isinstance(p, list)))
    if recipe.get("time"):
        field(h(T(ctx, "time")), h(recipe["time"]))

    learn = []
    al = recipe.get("autolearn")
    if al is True:
        learn.append(h(T(ctx, "autolearn")))
    elif isinstance(al, list):
        learn.append(h(T(ctx, "autolearn")) + " (" +
                     ", ".join("%s %s" % (h(p[0]), h(p[1])) for p in al) + ")")
    if learn:
        field(h(T(ctx, "learn")), "; ".join(learn))
    books = [b for b in (recipe.get("book_learn") or []) if isinstance(b, list) and b]
    if books:
        field(h(T(ctx, "books")), ", ".join(a_item(idx, b[0], ctx) for b in books))

    quals = list(recipe.get("qualities") or [])
    tools = list(recipe.get("tools") or [])
    for use in recipe.get("using") or []:
        if isinstance(use, list) and use and use[0] in idx.reqs:
            r = idx.reqs[use[0]]
            quals += r.get("qualities") or []
            tools += r.get("tools") or []

    if quals:
        qs = []
        for q in quals:
            if isinstance(q, dict):
                qs.append("%s&nbsp;%s" % (h(idx.tr(idx.quals.get(q.get("id"), q.get("id")))),
                                          h(q.get("level", 1))))
        if qs:
            field(h(T(ctx, "toolq")), ", ".join(qs))
    if tools:
        groups = []
        for group in tools:
            if not isinstance(group, list):
                continue
            opts = [e for e in group if isinstance(e, list) and e]
            if not opts:
                continue
            parts = []
            for e in opts:
                charges = e[1] if len(e) > 1 else -1
                t = a_item(idx, e[0], ctx)
                if isinstance(charges, int) and charges > 0:
                    t += ' <span class=qty>(%d)</span>' % charges
                parts.append(t)
            groups.append(' <span class="or">OR</span> '.join(parts))
        if groups:
            field(h(T(ctx, "tools")), ' <span class="semi">;</span> '.join(groups))

    comps = _recipe_comps(idx, recipe)
    ing = ""
    if comps:
        items = "".join("<li>%s</li>" % group_html(idx, g, ctx)
                        for g in comps if isinstance(g, list))
        ing = ('<div class="f"><span class="k">%s</span><span class="v">'
               '<ul class="ing">%s</ul></span></div>' % (h(T(ctx, "ingredients")), items))
    elif not tools and not quals:
        ing = '<div class="muted">%s</div>' % h(T(ctx, "no_ing"))

    title = h(T(ctx, "recipe")) + ("" if n is None else " #%d" % n)
    return ('<div class="recipe"><div class="rtitle">%s</div>%s%s%s</div>'
            % (title, "".join(rows), ing, tree_block(idx, recipe, ctx)))


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
.rtitle { font-weight: 700; color: var(--red); margin-bottom: 8px; }
.f { display: flex; gap: 8px; padding: 2px 0; }
.f .k { color: var(--muted); min-width: 110px; flex: none; font-size: 13px; padding-top:1px; }
.f .v { flex: 1; }
.diff { color: var(--faint); font-size:12px; } .semi{ color: var(--faint); } .amp{ color: var(--faint); }
.or { font-size: 11px; color: var(--pill-fg); background: var(--pill-bg); border-radius: 4px;
      padding: 0 5px; margin: 0 2px; vertical-align: 1px; }
.qty { color: var(--muted); } .listreq { color: inherit; }
a.item { color: var(--link); text-decoration: none; }
a.item:hover { text-decoration: underline; }
ul.ing { margin: 6px 0 0; padding-left: 20px; } ul.ing li { padding: 2px 0; }
.muted { color: var(--faint); }
.section { margin-top: 18px; font-weight: 600; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.chip { background: var(--panel); border: 1px solid var(--border2); border-radius: 999px;
        padding: 3px 11px; font-size: 13px; text-decoration: none; color: var(--link); }
.chip:hover { border-color: var(--link); }
.chip.loc { color: var(--muted); cursor: default; }
.chip.loc:hover { border-color: var(--border2); }
details.foundbox { margin-top: 0; }
details.foundbox > summary { cursor: pointer; list-style-position: inside; }
.results a { display: block; padding: 7px 10px; border-radius: 8px; color: inherit;
             text-decoration: none; }
.results a:hover { background: var(--hover); }
.results .rid { color: var(--faint); font: 11px ui-monospace, monospace; margin-left: 6px; }
.hint { color: var(--muted); margin-top: 24px; }
a.brand { text-decoration: none; color: inherit; }
a.gear { text-decoration: none; color: var(--muted); font-size: 18px; padding: 2px 6px; }
a.gear:hover { color: var(--fg); }
.desc { color: var(--muted); font-style: italic; margin: 6px 0 2px; }
.stats { color: var(--muted); font-size: 13px; margin: 2px 0 4px; }
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
        border-radius: 4px; padding: 0 4px; margin-left: 2px; cursor: help; }
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
.chip.flag { color: var(--muted); cursor: help; font: 12px ui-monospace, Consolas, monospace; }
.chip.flag:hover { border-color: var(--link); }
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
    locs = locales_for(ctx["ver"])
    order = ["en", "ko", "ja"]
    codes = sorted(locs.keys(), key=lambda c: (order.index(c) if c in order else 99, c))
    vers = "".join('<option value="%d"%s>%s</option>'
                   % (i, " selected" if i == ctx["ver"] else "", h(inst["label"]))
                   for i, inst in enumerate(INSTALLS))
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
  <form method="get" action="/" style="display:flex;flex:1;gap:8px;margin:0;">
    <input type=hidden name="ver" value="%(ver)d">
    <input type=hidden name="lang" value="%(lang)s">
    %(mods_hidden)s
    <input type=search name="q" value="%(q)s" placeholder="%(search_ph)s" autofocus>
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
              "s.scrollLeft+=(a.left+a.width/2)-(b.left+b.width/2);});});</script>")
    # left index/nav; settings live at the bottom of it (not a top-corner gear)
    qsuf = "ver=%d&lang=%s%s" % (ctx["ver"], h(ctx["lang"]), "&mods=1" if ctx["mods"] else "")

    def nl(key, path, icon, label):
        cls = "navlink active" if nav == key else "navlink"
        return '<a class="%s" href="%s?%s">%s %s</a>' % (cls, path, qsuf, icon, h(label))

    side = ('<nav class="side">%s%s%s<div class="navspacer"></div>%s</nav>' % (
        nl("items", "/", "📦", T(ctx, "nav_items")),
        nl("loot", "/loot", "🎒", T(ctx, "nav_loot")),
        nl("mechanics", "/mechanics", "📖", T(ctx, "nav_mechanics")),
        nl("settings", "/settings", "⚙", T(ctx, "settings"))))
    return ("<!doctype html><html><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>%s</title><style>%s</style></head><body>%s"
            "<div class='layout'>%s<div class='wrap'>%s</div></div>%s</body></html>"
            % (h(title), PAGE_CSS, header, side, body, script))


def _result_section(label, total, links, ctx):
    shown = links[:400]
    more = ("<p class='muted'>%s</p>" % h(T(ctx, "more", n=total - len(shown)))
            if total > len(shown) else "")
    return ('<div class="section">%s · %d</div><div class="results">%s</div>%s'
            % (h(label), total, "".join(shown), more))


def render_search(ctx, q):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    if not q.strip():
        craft = idx.craftable()
        body = '<p class="hint">%s</p>' % h(T(ctx, "hint", n=len(craft), r=len(idx.recipes)))
        return page(T(ctx, "brand"), body, ctx, q, nav="items")
    ql = q.strip().lower()

    # items: match name (localized + English), id, description text, or a flag
    def hit(disp, rid):
        if ql in disp.lower() or ql in idx.raw_name(rid).lower() or ql in rid.lower():
            return True
        d = idx.desc(rid)
        if d and ql in d.lower():
            return True
        rd = idx.raw_desc(rid)
        if rd and ql in rd.lower():
            return True
        return any(ql in f.lower() for f in idx.flags_of(rid))
    items = [(disp, rid) for disp, rid in idx.all_items() if hit(disp, rid)]
    # loot groups: match the id, raw or spaced
    groups = sorted(g for g in idx.group_def
                    if ql in g.lower() or ql in g.replace("_", " ").lower())

    sections = []
    if items:
        links = ['<a href="%s">%s<span class="rid">%s</span></a>'
                 % (item_url(rid, ctx), h(disp), h(rid)) for disp, rid in items]
        sections.append(_result_section(T(ctx, "nav_items"), len(items), links, ctx))
    if groups:
        links = ['<a href="%s">%s<span class="rid">%s</span></a>'
                 % (group_url(g, ctx), h(g.replace("_", " ")), h(g)) for g in groups]
        sections.append(_result_section(T(ctx, "nav_loot"), len(groups), links, ctx))

    body = "".join(sections) or "<p class='muted'>%s</p>" % h(T(ctx, "no_match"))
    return page("%s — CDDA Recipes" % q, body, ctx, q, nav="items")


def _stats_html(idx, ctx, rid):
    st = idx.stats(rid)
    if not st:
        return ""
    bits = []
    if st.get("weight"):
        bits.append("%s %s" % (h(T(ctx, "weight")), h(st["weight"])))
    if st.get("volume"):
        bits.append("%s %s" % (h(T(ctx, "volume")), h(st["volume"])))
    mat = st.get("material")
    if mat:
        mats = mat if isinstance(mat, list) else [mat]
        names = [h(idx.name(m if isinstance(m, str) else m.get("type", "")))
                 for m in mats if m]
        if names:
            bits.append("%s %s" % (h(T(ctx, "material")), ", ".join(names)))
    dmg = st.get("bashing") or st.get("cutting")
    if dmg:
        bits.append("%s %s" % (h(T(ctx, "melee")), h(dmg)))
    if not bits:
        return ""
    return '<div class="stats">%s</div>' % "  ·  ".join(bits)


def _abilities_html(idx, ctx, rid):
    """What you can do with the item: tool qualities, use actions, melee
    techniques, and its flags (with descriptions on hover)."""
    def field(label, value_html):
        return ('<div class="f"><span class="k">%s</span><span class="v">%s</span></div>'
                % (h(label), value_html))

    rows = []
    quals = idx.qualities_of(rid)
    if quals:
        rows.append(field(T(ctx, "toolq"), ", ".join(
            "%s&nbsp;%s" % (h(idx.tr(idx.quals.get(q, q))), h(lv)) for q, lv in quals)))
    acts = idx.actions_of(rid)
    if acts:
        rows.append(field(T(ctx, "actions"), ", ".join(h(a) for a in acts)))
    techs = idx.techniques_of(rid)
    if techs:
        rows.append(field(T(ctx, "techniques"),
                          ", ".join(h(idx.name(t)) for t in techs)))
    flags = sorted(idx.flags_of(rid))
    flag_html = ""
    if flags:
        chips = []
        for f in flags:
            d = idx.flag_desc(f)
            tip = ' title="%s"' % h(d) if d else ""
            chips.append('<span class="chip flag"%s>%s</span>' % (tip, h(f)))
        flag_html = ('<div class="f"><span class="k">%s</span>'
                     '<span class="v"><div class="chips">%s</div></span></div>'
                     % (h(T(ctx, "flags")), "".join(chips)))
    if not rows and not flag_html:
        return ""
    return ('<div class="recipe"><div class="rtitle">🛠 %s</div>%s%s</div>'
            % (h(T(ctx, "abilities")), "".join(rows), flag_html))


def render_item(ctx):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    rid = ctx["item_id"]
    title = idx.name(rid)
    parts = ['<h1 class="item">%s</h1><div class="idtag">%s</div>' % (h(title), h(rid))]
    desc = idx.desc(rid)
    if desc:
        parts.append('<div class="desc">%s</div>' % h(desc))
    parts.append(_stats_html(idx, ctx, rid))
    parts.append(_abilities_html(idx, ctx, rid))

    recipes = idx.by_result.get(rid, [])
    if recipes:
        for i, r in enumerate(recipes, 1):
            parts.append(recipe_html(idx, r, ctx, i if len(recipes) > 1 else None))
    else:
        parts.append('<div class="recipe muted">%s</div>' % h(T(ctx, "not_craftable")))

    # disassembly (uncraft)
    for un in idx.uncrafts.get(rid, []):
        comps = un.get("components") or []
        if not comps:
            continue
        items = "".join("<li>%s</li>" % group_html(idx, g, ctx)
                        for g in comps if isinstance(g, list))
        parts.append('<div class="recipe"><div class="rtitle">%s</div>'
                     '<ul class="ing">%s</ul></div>'
                     % (h(T(ctx, "disassembles")), items))

    # if this item is a book: the skill it trains + the recipes it teaches
    bi = idx.book_info(rid)
    if bi is not None:
        rows = []
        sk = bi.get("skill")
        if sk:
            lo = bi.get("required_level") or 0
            hi = bi.get("max_level")
            lvl = (" <span class=\"diff\">%s %s–%s</span>" % (h(T(ctx, "lv")), h(lo), h(hi))
                   if hi is not None else "")
            rows.append('<div class="f"><span class="k">%s</span>'
                        '<span class="v">%s%s</span></div>'
                        % (h(T(ctx, "book_skill")), h(idx.name(sk)), lvl))
        learn, seen = [], set()
        for resv, _lv in sorted(idx.book_recipes.get(rid, ()),
                                key=lambda x: idx.name(x[0]).lower()):
            if resv not in seen:
                seen.add(resv)
                learn.append('<a class="chip" href="%s">%s</a>'
                             % (item_url(resv, ctx), h(idx.name(resv))))
        if rows or learn:
            box = "".join(rows)
            if learn:
                box += ('<div class="section">%s</div><div class="chips">%s</div>'
                        % (h(T(ctx, "book_recipes", n=len(learn))), "".join(learn)))
            parts.append('<div class="recipe"><div class="rtitle">📖 %s</div>%s</div>'
                         % (h(T(ctx, "book")), box))

    # where it's found (loot/item groups) — clickable, like items; collapse if long
    locs = idx.found_in(rid)
    if locs:
        chips = "".join(a_group(g, ctx) for g in locs)
        hdr = "%s · %d" % (h(T(ctx, "found")), len(locs))
        if len(locs) > 30:
            parts.append('<details class="foundbox"><summary class="section">%s</summary>'
                         '<div class="chips">%s</div></details>' % (hdr, chips))
        else:
            parts.append('<div class="section">%s</div><div class="chips">%s</div>' % (hdr, chips))

    users = sorted(idx.used_in.get(rid, ()), key=lambda x: idx.name(x).lower())
    if users:
        chips = "".join('<a class="chip" href="%s">%s</a>' % (item_url(u, ctx), h(idx.name(u)))
                        for u in users)
        parts.append('<div class="section">%s</div><div class="chips">%s</div>'
                     % (h(T(ctx, "used_in", n=len(users))), chips))
    return page("%s — CDDA Recipes" % title, "".join(parts), ctx, nav="items")


def render_group(ctx, gid):
    """A loot/item group shown like an item page: what it can spawn, the groups
    it includes, and the groups it's part of — all clickable."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    ctx["group_id"] = gid
    parts = ['<div class="idtag">%s</div><h1 class="item">%s</h1><div class="idtag">%s</div>'
             % (h(T(ctx, "group")), h(gid.replace("_", " ")), h(gid))]

    def section(key, chips_html, n):
        parts.append('<div class="section">%s</div><div class="chips">%s</div>'
                     % (h(T(ctx, key, n=n)), chips_html))

    g = idx.group_def.get(gid)
    if g is not None:
        st, raw = _subtype_and_raw(g)
        note = T(ctx, "g_note_coll" if st == "collection" else "g_note_dist")
        qsuf = "ver=%d&lang=%s%s" % (ctx["ver"], h(ctx["lang"]),
                                     "&mods=1" if ctx["mods"] else "")
        parts.append('<div class="mechnote">%s &nbsp;<a href="/mechanics?%s">%s</a></div>'
                     % (h(note), qsuf, h(T(ctx, "learn_more"))))
        rows = entries_html(idx, ctx, raw, st)
        if rows:
            n = len(_norm_entries(raw, st))
            parts.append('<details class="treebox"><summary class="section">%s</summary>'
                         '<ul class="problist">%s</ul></details>'
                         % (h(T(ctx, "g_contents", n=n)), rows))
        # flattened: what you actually get, per final item (chance + avg count)
        loot = group_loot(idx, g)
        if loot:
            top = sorted(loot.items(), key=lambda kv: (-kv[1][1], -kv[1][0]))
            lis = []
            for iid, (p, ex) in top[:60]:
                avg = ("%.2f" % ex) if ex < 10 else str(round(ex))
                lis.append('<li><span class="prob">%s</span><div class="ent">%s'
                           ' <span class="locq">%s %s</span></div></li>'
                           % (pct_html(p), a_item(idx, iid, ctx),
                              h(T(ctx, "avg_label")), h(avg)))
            extra = ("" if len(loot) <= 60 else
                     '<div class="chips"><span class="chip loc">+%d</span></div>'
                     % (len(loot) - 60))
            parts.append('<div class="section">%s</div><ul class="problist">%s</ul>%s'
                         % (h(T(ctx, "expected_yield", n=len(loot))), "".join(lis), extra))
    else:
        # fallback: older set-based view (no raw def captured)
        items = sorted(idx.group_items.get(gid, ()), key=lambda x: idx.name(x).lower())
        if items:
            section("g_contains", "".join(
                '<a class="chip" href="%s">%s</a>' % (item_url(it, ctx), h(idx.name(it)))
                for it in items), len(items))
        subs = sorted(idx.group_subgroups.get(gid, ()))
        if subs:
            section("g_includes", "".join(a_group(s, ctx) for s in subs), len(subs))

    # where/when it triggers: monster death drops + map placements
    drops = sorted(idx.group_dropped_by.get(gid, ()), key=lambda x: idx.name(x).lower())
    if drops:
        section("dropped_by", "".join(
            '<a class="chip" href="%s">%s</a>' % (item_url(d, ctx), h(idx.name(d)))
            for d in drops), len(drops))
    places = idx.group_places.get(gid) or {}
    if places:
        # resolve each location to its readable place name (variants like
        # house_20 / house_24 share a name and collapse), keeping the best chance
        agg = {}
        for loc, ch in places.items():
            label = idx.loc_name(loc) or _loc_base(loc)
            if label not in agg or (ch is not None and (agg[label] is None or ch > agg[label])):
                agg[label] = ch

        def loc_chip(name, ch):
            sfx = "" if ch is None else ' <span class="locq">%s%%</span>' % h(ch)
            return '<span class="chip loc">%s%s</span>' % (h(name), sfx)
        # most-likely places first, then alphabetical
        rows = sorted(agg.items(), key=lambda kv: (-(kv[1] or 0), kv[0].lower()))
        cap = 24
        shown = rows[:cap]
        chips = "".join(loc_chip(l, c) for l, c in shown)
        if len(rows) > cap:
            chips += '<span class="chip loc">+%d</span>' % (len(rows) - cap)
        # ubiquitous groups (trash, etc.): lead with a plain-language summary
        lead = ('<span class="muted" style="font-size:13px">%s</span> '
                % h(T(ctx, "very_common")) if len(rows) > 60 else "")
        parts.append('<div class="section">%s</div>%s<div class="chips">%s</div>'
                     % (h(T(ctx, "placed_in", n=len(rows))), lead, chips))

    parents = sorted(idx.group_parents.get(gid, ()))
    if parents:
        section("g_partof", "".join(a_group(p, ctx) for p in parents), len(parents))
    return page("%s — CDDA Recipes" % gid, "".join(parts), ctx, nav="loot")


def render_landing(ctx):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    order = list(CAT_NAMES.keys())
    cats = sorted(idx.by_cat.keys(), key=lambda c: (order.index(c) if c in order else 99, c))
    cards = []
    for c in cats:
        cards.append('<a class="catcard" href="/?cat=%s&ver=%d&lang=%s%s">'
                     '<b>%s</b><br><span>%s</span></a>'
                     % (quote(c), ctx["ver"], h(ctx["lang"]), "&mods=1" if ctx["mods"] else "",
                        h(cat_name(c, ctx["lang"])), h(T(ctx, "items_n", n=len(idx.by_cat[c])))))
    body = ('<p class="hint">%s</p><div class="catgrid">%s</div>'
            % (h(T(ctx, "browse_hint")), "".join(cards)))
    return page(T(ctx, "brand"), body, ctx, nav="items")


def _item_level(idx, rid):
    """Lowest crafting difficulty across this item's recipes, and the skill."""
    recs = idx.by_result.get(rid, [])
    diffs = [r.get("difficulty") for r in recs if isinstance(r.get("difficulty"), int)]
    lv = min(diffs) if diffs else 0
    skill = next((r.get("skill_used") for r in recs if r.get("skill_used")), None)
    return lv, skill


def render_category(ctx, cat, skill, maxlv):
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    ids = idx.by_cat.get(cat, [])
    rows = []
    skills = set()
    for rid in ids:
        lv, sk = _item_level(idx, rid)
        if sk:
            skills.add(sk)
        rows.append((idx.name(rid), rid, lv, sk))
    if skill:
        rows = [r for r in rows if r[3] == skill]
    if maxlv is not None:
        rows = [r for r in rows if r[2] <= maxlv]
    rows.sort(key=lambda r: (r[2], r[0].lower()))

    skopts = '<option value="">%s</option>' % h(T(ctx, "all_skills"))
    for sk in sorted(skills, key=lambda s: idx.name(s).lower()):
        skopts += '<option value="%s"%s>%s</option>' % (
            h(sk), " selected" if sk == skill else "", h(idx.name(sk)))
    base = 'ver=%d&lang=%s%s' % (ctx["ver"], h(ctx["lang"]), "&mods=1" if ctx["mods"] else "")
    filters = (
        '<form class="filters" method="get" action="/">'
        '<input type=hidden name="cat" value="%s">'
        '<input type=hidden name="ver" value="%d"><input type=hidden name="lang" value="%s">%s'
        '<select name="skill" onchange="this.form.submit()">%s</select>'
        '<input type=number name="maxlv" min="0" placeholder="%s" value="%s" '
        'style="width:6em" onchange="this.form.submit()">'
        '</form>'
        % (h(cat), ctx["ver"], h(ctx["lang"]),
           '<input type=hidden name="mods" value="1">' if ctx["mods"] else "",
           skopts, h(T(ctx, "max_lv")), "" if maxlv is None else h(maxlv)))

    trs = "".join(
        '<tr><td><a class="item" href="%s">%s</a></td><td>%s</td><td class="lv">%s</td></tr>'
        % (item_url(rid, ctx), h(name), h(idx.name(sk)) if sk else "", lv)
        for name, rid, lv, sk in rows)
    table = ('<table class="cat"><tr><th>%s</th><th>%s</th><th class="lv">%s</th></tr>%s</table>'
             % (h(T(ctx, "item_col")), h(T(ctx, "skill")), h(T(ctx, "lv")), trs))
    head = ('<a class="item" href="/?%s">%s</a><h1 class="item">%s <span class="idtag">(%s)</span></h1>'
            % (base, h(T(ctx, "all_cats")), h(cat_name(cat, ctx["lang"])),
               h(T(ctx, "items_n", n=len(rows)))))
    return page("%s — CDDA Recipes" % cat_name(cat, ctx["lang"]),
                head + filters + table, ctx, nav="items")


def render_settings(ctx, saved):
    npc = SETTINGS.get("npc_loot")
    saved_tag = ' <span class="saved">%s</span>' % h(T(ctx, "saved")) if saved else ""
    body = (
        '<h1 class="item">%s%s</h1>'
        '<form method="get" action="/settings">'
        '<input type=hidden name="save" value="1">'
        '<input type=hidden name="ver" value="%d"><input type=hidden name="lang" value="%s">%s'
        '<div class="setrow"><label><input type=checkbox name="npc_loot" value="1"%s '
        'onchange="this.form.submit()"> %s</label></div>'
        '<div class="help">%s</div>'
        '</form>'
        % (h(T(ctx, "settings")), saved_tag, ctx["ver"], h(ctx["lang"]),
           '<input type=hidden name="mods" value="1">' if ctx["mods"] else "",
           " checked" if npc else "", h(T(ctx, "npc_loot")), h(T(ctx, "npc_loot_help"))))
    return page("%s — CDDA Recipes" % T(ctx, "settings"), body, ctx, nav="settings")


def render_loot(ctx):
    """Browse loot from the top: root groups (not nested under any other group)
    are the entry points mapgen actually places. Click to drill down."""
    idx = get_index(ctx["ver"], ctx["mods"])
    idx.tr = get_translator(ctx["ver"], ctx["lang"])
    roots = [gid for gid in idx.group_def if not idx.group_parents.get(gid)]
    if not SETTINGS.get("npc_loot"):
        roots = [g for g in roots if not g.startswith("NC_")]
    roots.sort(key=str.lower)
    chips = "".join(a_group(g, ctx) for g in roots)
    body = ('<h1 class="item">%s</h1><p class="hint">%s</p><div class="chips">%s</div>'
            % (h(T(ctx, "loot_title")), h(T(ctx, "loot_hint", n=len(roots))), chips))
    return page(T(ctx, "loot_title"), body, ctx, nav="loot")


def render_mechanics(ctx):
    doc = MECH_DOC.get(ctx["lang"]) or MECH_DOC["en"]
    secs = "".join("<h2>%s</h2>%s" % (h(head), body) for head, body in doc)
    body = ('<h1 class="item">%s</h1><div class="mech">%s</div>'
            % (h(T(ctx, "mech_title")), secs))
    return page(T(ctx, "mech_title"), body, ctx, nav="mechanics")


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
    ver = max(0, min(ver, len(INSTALLS) - 1))
    return {"ver": ver, "lang": first("lang", "en") or "en",
            "mods": first("mods", "") in ("1", "true", "on"),
            "item_id": first("id", "")}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, status=200):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
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
    global INSTALLS
    INSTALLS = find_installs()
    if not INSTALLS:
        print("No CDDA installs found under ~/Games/Cataclysm-DDA|BN.")
        print("Install a version with CDDA_Installer first.")
        return
    print("Indexing %s …" % INSTALLS[0]["label"].strip())
    get_index(0, False)          # preload default so the first page is instant
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


if __name__ == "__main__":
    main()
