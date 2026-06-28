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
        "nav_monsters": "Monsters", "nav_skills": "Skills", "nav_qualities": "Tool qualities",
        "nav_flags": "Flags",
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
        "obtain": "Obtaining", "disassemble_from": "Disassemble from ({n})",
        "loot_at": "Found as loot ({n})",
        "flag_single": "Flag", "items_with_flag": "Items with this flag ({n})",
        "skill_single": "Skill", "skill_recipes_label": "Recipes using this skill ({n})",
        "skill_books_label": "Books that train it ({n})",
        "quality_single": "Tool quality", "quality_items_label": "Items with this quality ({n})",
        "monster_single": "Monster", "monster_drop_group": "Death-drop group",
        "monster_drops": "Can drop ({n})",
        "m_combat": "Combat", "m_defense": "Defense", "m_senses": "Senses & behavior",
        "m_life": "Lifecycle & butchering", "speed": "Speed", "dodge": "Dodge",
        "armor": "Armor", "vision": "Vision day/night", "species": "Species",
        "faction": "Faction", "aggression": "Aggression", "morale": "Morale",
        "m_atkcost": "Attack cost", "m_special": "Special attacks",
        "m_harvest": "Butchering", "m_death": "On death", "m_upgrades": "Upgrades to",
        "m_reproduces": "Reproduces", "m_becomes": "Becomes",
        "dmg_bash": "bash", "dmg_cut": "cut", "dmg_stab": "stab", "dmg_bullet": "ballistic",
        "dmg_acid": "acid", "dmg_fire": "fire", "dmg_cold": "cold", "dmg_elec": "electric",
        "m_extra_dmg": "Extra damage", "m_weapon": "Wields", "m_ammo": "Ammo",
        "m_when_hit": "When hit", "m_regen": "Regenerates", "bodytype": "Body type",
        "category": "Category", "m_anger": "Angered by", "m_fear": "Frightened by",
        "m_placate": "Placated by", "m_glow": "Luminance", "m_emit": "Emits",
        "m_zombify": "Zombifies into", "m_revert": "Reverts to", "m_aggro": "Hostile on sight",
        "m_food": "Pet food", "m_pettrain": "Tame bonuses", "m_seasons": "Breeding seasons",
        "raw_fields": "All JSON fields ({n})", "cat": "Category",
        "atk_time_fmt": "attack ~{a}–{b}s (skilled→new, {m0}–{m1} moves)",
        "atk_tip": ("Move cost per swing (100 moves = 1s at speed 100).\n"
                    "Base = 65 + volume/62.5mL + weight/60g.\n"
                    "Range shown is melee skill 15 (fast) → 0 (slow).\n"
                    "Dexterity lowers it further; encumbrance and low stamina raise "
                    "it. Floored at 25 moves.\n"
                    "Monsters use a fixed attack_cost instead — see Mechanics."),
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
        "nav_monsters": "몬스터", "nav_skills": "스킬", "nav_qualities": "도구 품질",
        "nav_flags": "특성(플래그)",
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
        "obtain": "입수", "disassemble_from": "분해로 얻기 ({n})",
        "loot_at": "전리품 ({n})",
        "flag_single": "특성(플래그)", "items_with_flag": "이 특성을 가진 아이템 ({n})",
        "skill_single": "스킬", "skill_recipes_label": "이 스킬로 만드는 레시피 ({n})",
        "skill_books_label": "훈련시키는 책 ({n})",
        "quality_single": "도구 품질", "quality_items_label": "이 품질을 가진 아이템 ({n})",
        "monster_single": "몬스터", "monster_drop_group": "사망 드롭 그룹",
        "monster_drops": "드롭 가능 ({n})",
        "m_combat": "전투", "m_defense": "방어", "m_senses": "감각·행동",
        "m_life": "생애·해체", "speed": "속도", "dodge": "회피",
        "armor": "방어구", "vision": "시야 주/야", "species": "종",
        "faction": "진영", "aggression": "공격성", "morale": "사기",
        "m_atkcost": "공격 비용", "m_special": "특수 공격",
        "m_harvest": "해체 산출", "m_death": "사망 시", "m_upgrades": "진화",
        "m_reproduces": "번식", "m_becomes": "변이",
        "dmg_bash": "타격", "dmg_cut": "절단", "dmg_stab": "관통", "dmg_bullet": "탄환",
        "dmg_acid": "산", "dmg_fire": "화염", "dmg_cold": "냉기", "dmg_elec": "전기",
        "m_extra_dmg": "추가 피해", "m_weapon": "장비 무기", "m_ammo": "탄약",
        "m_when_hit": "피격 시", "m_regen": "재생", "bodytype": "체형",
        "category": "분류", "m_anger": "분노 유발", "m_fear": "공포 유발",
        "m_placate": "진정 조건", "m_glow": "발광", "m_emit": "방출",
        "m_zombify": "좀비화", "m_revert": "되돌아감", "m_aggro": "발견 시 적대",
        "m_food": "먹이", "m_pettrain": "길들이기 보너스", "m_seasons": "번식 계절",
        "raw_fields": "원본 JSON 필드 ({n})", "cat": "분류",
        "atk_time_fmt": "공격 ~{a}–{b}초 (숙련→초보, {m0}–{m1}무브)",
        "atk_tip": ("한 번 휘두르는 데 드는 무브 (speed 100에서 100무브 = 1초).\n"
                    "기본 = 65 + 부피/62.5mL + 무게/60g.\n"
                    "표시 범위는 근접 스킬 15(빠름) → 0(느림).\n"
                    "민첩으로 더 줄고, 거추장·낮은 스태미나로 늘어남. 최소 25무브.\n"
                    "몬스터는 고정 attack_cost를 씀 — 자세히는 메커니즘 페이지."),
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
        "nav_monsters": "モンスター", "nav_skills": "スキル", "nav_qualities": "道具品質",
        "nav_flags": "フラグ",
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
        "obtain": "入手", "disassemble_from": "分解で入手 ({n})",
        "loot_at": "戦利品 ({n})",
        "flag_single": "フラグ", "items_with_flag": "このフラグを持つアイテム ({n})",
        "skill_single": "スキル", "skill_recipes_label": "このスキルで作るレシピ ({n})",
        "skill_books_label": "鍛える書籍 ({n})",
        "quality_single": "道具品質", "quality_items_label": "この品質を持つアイテム ({n})",
        "monster_single": "モンスター", "monster_drop_group": "死亡ドロップグループ",
        "monster_drops": "ドロップ可能 ({n})",
        "m_combat": "戦闘", "m_defense": "防御", "m_senses": "感覚・行動",
        "m_life": "生態・解体", "speed": "速度", "dodge": "回避",
        "armor": "装甲", "vision": "視界 昼/夜", "species": "種",
        "faction": "陣営", "aggression": "攻撃性", "morale": "士気",
        "m_atkcost": "攻撃コスト", "m_special": "特殊攻撃",
        "m_harvest": "解体", "m_death": "死亡時", "m_upgrades": "進化先",
        "m_reproduces": "繁殖", "m_becomes": "変化",
        "dmg_bash": "打撃", "dmg_cut": "切断", "dmg_stab": "刺突", "dmg_bullet": "弾",
        "dmg_acid": "酸", "dmg_fire": "火", "dmg_cold": "冷", "dmg_elec": "電",
        "m_extra_dmg": "追加ダメージ", "m_weapon": "武器", "m_ammo": "弾薬",
        "m_when_hit": "被弾時", "m_regen": "再生", "bodytype": "体型",
        "category": "分類", "m_anger": "怒りの誘発", "m_fear": "恐怖の誘発",
        "m_placate": "鎮静条件", "m_glow": "発光", "m_emit": "放出",
        "m_zombify": "ゾンビ化", "m_revert": "戻る", "m_aggro": "発見で敵対",
        "m_food": "餌", "m_pettrain": "テイム強化", "m_seasons": "繁殖季節",
        "raw_fields": "全JSONフィールド ({n})", "cat": "分類",
        "atk_time_fmt": "攻撃 ~{a}–{b}秒 (熟練→初心者, {m0}–{m1}ムーブ)",
        "atk_tip": ("1回振るのに必要なムーブ (speed 100で100ムーブ=1秒).\n"
                    "基礎 = 65 + 体積/62.5mL + 重量/60g.\n"
                    "表示範囲は近接スキル15(速)→0(遅).\n"
                    "器用さでさらに減少、かさばり・低スタミナで増加. 最低25ムーブ.\n"
                    "モンスターは固定のattack_costを使用 — 詳細は仕組みページ."),
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
        ("Auto-refuelling fires (Source: Firewood zone)",
         "<p>The game can keep a fire fed for you during long tasks. Designate a "
         "<b>Source: Firewood</b> zone (zone manager, <code>Y</code>) over a pile "
         "of firewood or other flammable items. While you do a long activity that "
         "carries the <code>refuel_fires</code> flag — crafting, reading, waiting "
         "— your character automatically pulls fuel from that zone and feeds "
         "nearby fires, keeping light and heat up so you never stop to tend "
         "them.</p>"
         "<p>In the data it's the <code>SOURCE_FIREWOOD</code> loot zone; the "
         "activities that use it carry <code>refuel_fires: true</code> in "
         "<code>player_activities</code>. (The separate <code>LOOT_WOOD</code> "
         "zone is just a tidy-up destination, not an auto-feed source.)</p>"),
        ("Time, turns and action cost",
         "<p>The world advances in <b>turns of 1 second</b>. Each creature gets "
         "<code>speed</code> <b>move points</b> per turn (a normal human is 100), "
         "spends them on actions, and when they run out that second passes. Higher "
         "speed = more moves = more actions per second. Walking one tile costs that "
         "tile's move cost (~100 on flat ground), so at speed 100 a step is about a "
         "second.</p>"
         "<p>A player's melee-swing move cost builds up like this (from the BN "
         "source):</p><ul>"
         "<li>weapon base = <code>65 + volume/62.5 mL + weight/60 g</code> "
         "(bulkier and heavier swings slower)</li>"
         "<li>start at <code>base / 2</code>, add torso + average-hand "
         "<b>encumbrance</b>, multiply by a <b>stamina</b> penalty (1× normally, "
         "rising toward 2× below 25% stamina)</li>"
         "<li>add a <b>skill</b> term <code>(base/2) × (15 − melee skill) / 15</code> "
         "(skill 15 removes it), then subtract your <b>Dexterity</b></li>"
         "<li>finally martial-arts and mutation modifiers; the result can't drop "
         "below 25 moves</li></ul>"
         "<p>Since 100 moves = one second at speed 100, a 100-move swing is one hit "
         "per second; lighter, more skilled and more dexterous = fewer moves = "
         "faster. Monsters skip all this — they carry an explicit "
         "<code>attack_cost</code> (in moves) in their JSON.</p>"),
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
        ("불 자동 연료 보충 (Source: Firewood 존)",
         "<p>장시간 작업 동안 게임이 알아서 불을 살려둘 수 있다. 존 관리자(<code>Y</code>)"
         "에서 <b>Source: Firewood</b> 존을 장작이나 가연물이 쌓인 자리에 지정하면, "
         "<code>refuel_fires</code> 플래그가 붙은 긴 작업 — 제작·독서·대기 — 을 하는 "
         "동안 캐릭터가 그 존에서 연료를 꺼내 근처 불에 자동으로 넣어 빛과 열을 유지한다. "
         "중간에 직접 불을 돌볼 필요가 없다.</p>"
         "<p>데이터에서는 <code>SOURCE_FIREWOOD</code> 전리품 존으로 정의되고, 이를 쓰는 "
         "활동들은 <code>player_activities</code>에 <code>refuel_fires: true</code>를 "
         "가진다. (별개의 <code>LOOT_WOOD</code> 존은 정리용 목적지일 뿐, 자동 투입 "
         "공급원이 아니다.)</p>"),
        ("시간·턴·행동 비용",
         "<p>세상은 <b>1초짜리 턴</b>으로 진행된다. 각 생물은 매 턴 <code>speed</code>만큼 "
         "<b>무브(이동점수)</b>를 받고(보통 사람 100), 행동에 소비하다가 무브가 떨어지면 "
         "그 1초가 흐른다. speed가 높을수록 무브가 많아 초당 더 많이 행동한다. 한 칸 이동은 "
         "그 지형의 이동비용(평지 ≈100)이라, speed 100이면 한 걸음이 약 1초.</p>"
         "<p>플레이어 근접 공격의 무브 비용은 이렇게 쌓인다(BN 소스 기준):</p><ul>"
         "<li>무기 기본 = <code>65 + 부피/62.5 mL + 무게/60 g</code> (크고 무거울수록 "
         "느림)</li>"
         "<li><code>기본 / 2</code>에서 시작 → 몸통+양손 평균 <b>거추장(encumbrance)</b>을 "
         "더함 → <b>스태미나</b> 페널티 곱함(평소 1배, 스태미나 25% 미만에서 최대 2배)</li>"
         "<li><b>스킬</b> 항 <code>(기본/2) × (15 − 근접스킬) / 15</code> 더함(스킬 15면 "
         "사라짐), 그다음 <b>민첩</b>을 뺌</li>"
         "<li>마지막으로 무술·변이 보정, 결과는 최소 25무브 아래로는 안 내려감</li></ul>"
         "<p>speed 100에서 100무브 = 1초이므로, 100무브 공격은 초당 1회다. 가볍고·숙련되고·"
         "민첩할수록 무브가 줄어 빨라진다. 몬스터는 이 계산을 거치지 않고 JSON에 "
         "<code>attack_cost</code>(무브)를 직접 가진다.</p>"),
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
        ("焚き火の自動燃料補給 (Source: Firewood ゾーン)",
         "<p>長時間の作業中、ゲームが自動で火を維持できる。ゾーン管理（<code>Y</code>）で "
         "<b>Source: Firewood</b> ゾーンを薪や可燃物の山に指定すると、"
         "<code>refuel_fires</code> フラグの付いた長時間作業（製作・読書・待機）の間、"
         "キャラクターがそのゾーンから燃料を取り出して近くの火にくべ、明かりと熱を維持する。"
         "途中で火の世話をする必要がない。</p>"
         "<p>データでは <code>SOURCE_FIREWOOD</code> 戦利品ゾーンとして定義され、使用する"
         "活動は <code>player_activities</code> に <code>refuel_fires: true</code> を持つ。"
         "（別の <code>LOOT_WOOD</code> ゾーンは整理用の目的地で、自動補給源ではない。）</p>"),
        ("時間・ターン・行動コスト",
         "<p>世界は<b>1秒のターン</b>で進む。各クリーチャーは毎ターン<code>speed</code>分の"
         "<b>ムーブ（行動点）</b>を得て（通常の人間は100）、行動で消費し、尽きるとその1秒が"
         "経過する。speedが高いほどムーブが多く、1秒あたりの行動が増える。1マス移動はその"
         "地形の移動コスト（平地≈100）なので、speed 100なら一歩が約1秒。</p>"
         "<p>プレイヤーの近接攻撃のムーブコストはこう積み上がる（BNソース準拠）:</p><ul>"
         "<li>武器の基礎 = <code>65 + 体積/62.5 mL + 重量/60 g</code>（大きく重いほど"
         "遅い）</li>"
         "<li><code>基礎 / 2</code>から開始 → 胴+両手平均の<b>かさばり（encumbrance）</b>を"
         "加算 → <b>スタミナ</b>ペナルティを乗算（通常1倍、スタミナ25%未満で最大2倍）</li>"
         "<li><b>スキル</b>項 <code>(基礎/2) × (15 − 近接スキル) / 15</code> を加算（スキル"
         "15で消滅）、その後<b>器用さ</b>を減算</li>"
         "<li>最後に武術・変異補正、結果は最低25ムーブを下回らない</li></ul>"
         "<p>speed 100では100ムーブ=1秒なので、100ムーブの攻撃は毎秒1回。軽く・熟練し・"
         "器用なほどムーブが減って速くなる。モンスターはこの計算を経ず、JSONに"
         "<code>attack_cost</code>（ムーブ）を直接持つ。</p>"),
    ],
}

