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
        "all_items": "All items", "cat_any": "All categories",
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
        "nav_mutations": "Mutations", "nav_bionics": "Bionics",
        "nav_professions": "Professions", "nav_martial": "Martial arts",
        "nav_techniques": "Techniques", "nav_effects": "Effects",
        "nav_spells": "Spells", "nav_vehicles": "Vehicles",
        "nav_vparts": "Vehicle parts", "nav_constructions": "Constructions",
        "nav_terrain": "Terrain", "nav_furniture": "Furniture",
        "nav_materials": "Materials",
        "filter_ph": "filter…", "m_other": "Other",
        "trait_pos": "Beneficial", "trait_neu": "Neutral", "trait_neg": "Detrimental",
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
        "nav_table": "Item table", "table_title": "Item table",
        "table_hint": "Sortable table. A category adds its type's stat columns; "
            "choose a tool quality, filter by name, and click any column header to sort.",
        "all_types": "All types", "type_col": "Type", "none_quality": "Tool quality…",
        "tfilter_ph": "filter by name…",
        "col_bash": "Bash", "col_cut": "Cut", "col_tohit": "To-hit",
        "col_enc": "Encumbrance", "col_cov": "Coverage", "col_warmth": "Warmth",
        "col_thick": "Thickness", "col_cal": "Calories", "col_quench": "Quench",
        "col_healthy": "Healthy", "col_fun": "Enjoy", "col_range": "Range",
        "col_disp": "Dispersion", "qual_lv": "{q} Lv",
        "mech_pick": "Pick a topic to read.", "mech_back": "← All topics",
        "sim_nav": "Combat sim", "sim_title": "Melee combat simulator",
        "sim_hint": "Estimate hit chance, damage and time-to-kill from the BN melee "
                    "formulas. Edit the values and run.",
        "sim_run": "Run", "sim_attacker": "Attacker", "sim_weapon": "Weapon",
        "sim_target": "Target", "sim_str": "Strength", "sim_dex": "Dexterity",
        "sim_per": "Perception", "sim_sk_melee": "Melee skill", "sim_sk_weapon": "Weapon skill",
        "sim_w_bash": "Bash dmg", "sim_w_cut": "Cut dmg", "sim_w_stab": "Stab dmg",
        "sim_w_hit": "To-hit", "sim_w_vol": "Volume (mL)", "sim_w_wt": "Weight (g)",
        "sim_t_dodge": "Dodge", "sim_a_bash": "Armor bash", "sim_a_cut": "Armor cut",
        "sim_a_stab": "Armor stab", "sim_t_hp": "HP", "sim_size": "Size",
        "sim_size_tiny": "Tiny", "sim_size_small": "Small", "sim_size_medium": "Medium",
        "sim_size_large": "Large", "sim_size_huge": "Huge",
        "sim_hitchance": "Hit chance", "sim_critchance": "Crit (per hit)",
        "sim_dmg_hit": "Damage / hit", "sim_dmg_swing": "Damage / swing",
        "sim_movecost": "Attack moves", "sim_dps": "Damage / second",
        "sim_ttk": "Time to kill", "sim_hit_sub": "to-hit {v}", "sim_atk_sub": "{v} /s",
        "sim_dist": "Per-swing damage distribution ({n} trials)",
        "sim_assume": "Assumes full stamina, no encumbrance, two arms, no "
                      "martial-arts/mutation buffs; two-handed swing bonus not applied. "
                      "Damage uses the exact bash/cut/stab rolls; hit chance is "
                      "Φ((hit−dodge)/5) with the real σ=25.",
        "sim_mode": "Mode", "sim_mode_melee": "Melee", "sim_mode_ranged": "Ranged",
        "sim_gun": "Gun", "sim_ammo": "Ammo",
        "sim_pick_weapon": "Pick weapon", "sim_pick_monster": "Pick monster",
        "sim_pick_gun": "Pick gun", "sim_pick_ammo": "Pick ammo",
        "sim_pick_custom": "type to search…",
        "sim_sk_gun": "Gun skill", "sim_gun_disp": "Dispersion (MoA)",
        "sim_recoil": "Recoil (MoA)", "sim_range": "Range (tiles)",
        "sim_rng_dmg": "Damage", "sim_rng_pen": "Armor pen",
        "sim_proj_speed": "Projectile speed", "sim_a_bullet": "Armor bullet",
        "sim_aimed": "Crit (aimed)", "sim_dmg_shot": "Damage / shot",
        "sim_avgdisp": "Avg dispersion", "sim_shots_kill": "Shots to kill",
        "sim_dist_shot": "Per-shot damage distribution ({n} trials)",
        "sim_assume_r": "Per-shot; ignores aim-time and fire-rate. Assumes torso hits "
                        "(severity ≤1.5, no headshot bonus). Dispersion = weapon + "
                        "Dexterity + skill + recoil; you hit when the scatter lands "
                        "within the target's size.",
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
        "all_items": "전체 아이템", "cat_any": "모든 카테고리",
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
        "nav_mutations": "변이", "nav_bionics": "바이오닉",
        "nav_professions": "직업", "nav_martial": "무술",
        "nav_techniques": "기술", "nav_effects": "효과",
        "nav_spells": "주문", "nav_vehicles": "차량",
        "nav_vparts": "차량 부품", "nav_constructions": "건설",
        "nav_terrain": "지형", "nav_furniture": "가구",
        "nav_materials": "재질",
        "filter_ph": "필터…", "m_other": "기타",
        "trait_pos": "긍정 특성", "trait_neu": "중립 특성", "trait_neg": "부정 특성",
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
        "dmg_bash": "타격", "dmg_cut": "베기", "dmg_stab": "관통", "dmg_bullet": "탄환",
        "dmg_acid": "산", "dmg_fire": "화염", "dmg_cold": "냉기", "dmg_elec": "전기",
        "m_extra_dmg": "추가 피해", "m_weapon": "장비 무기", "m_ammo": "탄약",
        "m_when_hit": "피격 시", "m_regen": "재생", "bodytype": "체형",
        "category": "분류", "m_anger": "분노 유발", "m_fear": "공포 유발",
        "m_placate": "진정 조건", "m_glow": "발광", "m_emit": "방출",
        "m_zombify": "좀비화", "m_revert": "되돌아감", "m_aggro": "발견 시 적대",
        "m_food": "먹이", "m_pettrain": "길들이기 보너스", "m_seasons": "번식 계절",
        "raw_fields": "원본 JSON 필드 ({n})", "cat": "분류",
        "atk_time_fmt": "공격 ~{a}–{b}초 (숙련→초보, {m0}–{m1}행동력)",
        "atk_tip": ("한 번 휘두르는 데 드는 행동력 (speed 100에서 100행동력 = 1초).\n"
                    "기본 = 65 + 부피/62.5mL + 무게/60g.\n"
                    "표시 범위는 근접 스킬 15(빠름) → 0(느림).\n"
                    "민첩성으로 더 줄고, 방해도·낮은 스태미나로 늘어남. 최소 25행동력.\n"
                    "몬스터는 고정 attack_cost를 씀 — 자세히는 메커니즘 페이지."),
        "nav_table": "아이템 표", "table_title": "아이템 표",
        "table_hint": "정렬 가능한 표. 카테고리를 고르면 그 타입의 스탯 열이 추가되고, "
            "도구 품질 선택·이름 필터가 가능하며, 열 머리글을 클릭하면 정렬됩니다.",
        "all_types": "모든 타입", "type_col": "타입", "none_quality": "도구 품질…",
        "tfilter_ph": "이름으로 필터…",
        "col_bash": "타격", "col_cut": "베기", "col_tohit": "명중률",
        "col_enc": "방해도", "col_cov": "범위", "col_warmth": "보온력",
        "col_thick": "두께", "col_cal": "칼로리", "col_quench": "갈증 해소",
        "col_healthy": "건강도", "col_fun": "의욕", "col_range": "사정거리",
        "col_disp": "분산도", "qual_lv": "{q} Lv",
        "mech_pick": "읽을 주제를 선택하세요.", "mech_back": "← 전체 주제",
        "sim_nav": "전투 시뮬", "sim_title": "근접 전투 시뮬레이터",
        "sim_hint": "BN 근접 공식으로 명중률·피해·처치 시간을 추정합니다. 값을 바꾸고 "
                    "실행하세요.",
        "sim_run": "실행", "sim_attacker": "공격자", "sim_weapon": "무기",
        "sim_target": "대상", "sim_str": "체력", "sim_dex": "민첩성", "sim_per": "지각",
        "sim_sk_melee": "근접 스킬", "sim_sk_weapon": "무기 스킬",
        "sim_w_bash": "타격 피해", "sim_w_cut": "베기 피해", "sim_w_stab": "관통 피해",
        "sim_w_hit": "명중률", "sim_w_vol": "부피 (mL)", "sim_w_wt": "무게 (g)",
        "sim_t_dodge": "회피", "sim_a_bash": "방어(타격)", "sim_a_cut": "방어(베기)",
        "sim_a_stab": "방어(관통)", "sim_t_hp": "HP", "sim_size": "크기",
        "sim_size_tiny": "초소형", "sim_size_small": "소형", "sim_size_medium": "보통",
        "sim_size_large": "대형", "sim_size_huge": "초대형",
        "sim_hitchance": "명중 확률", "sim_critchance": "치명타(명중당)",
        "sim_dmg_hit": "피해 / 명중", "sim_dmg_swing": "피해 / 스윙",
        "sim_movecost": "공격 행동력", "sim_dps": "초당 피해", "sim_ttk": "처치 시간",
        "sim_hit_sub": "명중치 {v}", "sim_atk_sub": "{v} /초",
        "sim_dist": "스윙당 피해 분포 ({n}회 시행)",
        "sim_assume": "스태미나 가득·방해도 0·양팔·무술/변이 버프 없음 가정, 양손 보너스 "
                      "미적용. 피해는 타격/베기/관통 실제 굴림을 쓰고, 명중률은 실제 σ=25 "
                      "기준 Φ((명중−회피)/5)입니다.",
        "sim_mode": "모드", "sim_mode_melee": "근접", "sim_mode_ranged": "원거리",
        "sim_gun": "총기", "sim_ammo": "탄약",
        "sim_pick_weapon": "무기 선택", "sim_pick_monster": "몬스터 선택",
        "sim_pick_gun": "총기 선택", "sim_pick_ammo": "탄약 선택",
        "sim_pick_custom": "이름으로 검색…",
        "sim_sk_gun": "총기 스킬", "sim_gun_disp": "분산도 (MoA)",
        "sim_recoil": "반동 (MoA)", "sim_range": "사정거리 (칸)",
        "sim_rng_dmg": "사격 피해", "sim_rng_pen": "장갑관통력",
        "sim_proj_speed": "발사체 속도", "sim_a_bullet": "방어(탄환)",
        "sim_aimed": "정밀타(조준)", "sim_dmg_shot": "피해 / 발",
        "sim_avgdisp": "평균 분산도", "sim_shots_kill": "처치 탄수",
        "sim_dist_shot": "발당 피해 분포 ({n}회 시행)",
        "sim_assume_r": "발당 기준이며 조준 시간·연사를 무시합니다. 몸통 명중 가정"
                        "(severity ≤1.5, 헤드샷 보너스 없음). 분산 = 무기 + 민첩성 + 스킬 + "
                        "반동이고, 흩어짐이 표적 크기 안에 들어오면 명중입니다.",
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
        "all_items": "全アイテム", "cat_any": "全カテゴリ",
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
        "nav_mutations": "変異", "nav_bionics": "バイオニック",
        "nav_professions": "職業", "nav_martial": "武術",
        "nav_techniques": "技", "nav_effects": "効果",
        "nav_spells": "呪文", "nav_vehicles": "車両",
        "nav_vparts": "車両部品", "nav_constructions": "建設",
        "nav_terrain": "地形", "nav_furniture": "家具",
        "nav_materials": "材質",
        "filter_ph": "絞り込み…", "m_other": "その他",
        "trait_pos": "有益", "trait_neu": "中立", "trait_neg": "有害",
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
        "nav_table": "アイテム表", "table_title": "アイテム表",
        "table_hint": "並べ替え可能な表。カテゴリを選ぶとそのタイプのステータス列が追加され、"
            "道具品質の選択・名前での絞り込みが可能。列見出しのクリックで並べ替え。",
        "all_types": "全タイプ", "type_col": "タイプ", "none_quality": "道具品質…",
        "tfilter_ph": "名前で絞り込み…",
        "col_bash": "打撃", "col_cut": "切断", "col_tohit": "命中",
        "col_enc": "かさばり", "col_cov": "範囲(%)", "col_warmth": "保温",
        "col_thick": "厚さ", "col_cal": "カロリー", "col_quench": "水分",
        "col_healthy": "健康", "col_fun": "楽しさ", "col_range": "射程",
        "col_disp": "分散", "qual_lv": "{q} Lv",
        "mech_pick": "トピックを選択してください。", "mech_back": "← 全トピック",
        "sim_nav": "戦闘シミュ", "sim_title": "近接戦闘シミュレーター",
        "sim_hint": "BNの近接式で命中率・ダメージ・撃破時間を推定。値を変えて実行。",
        "sim_run": "実行", "sim_attacker": "攻撃者", "sim_weapon": "武器",
        "sim_target": "対象", "sim_str": "筋力", "sim_dex": "器用", "sim_per": "知覚",
        "sim_sk_melee": "近接スキル", "sim_sk_weapon": "武器スキル",
        "sim_w_bash": "打撃ダメージ", "sim_w_cut": "切断ダメージ", "sim_w_stab": "刺突ダメージ",
        "sim_w_hit": "命中補正", "sim_w_vol": "体積 (mL)", "sim_w_wt": "重量 (g)",
        "sim_t_dodge": "回避", "sim_a_bash": "防御(打撃)", "sim_a_cut": "防御(切断)",
        "sim_a_stab": "防御(刺突)", "sim_t_hp": "HP", "sim_size": "サイズ",
        "sim_size_tiny": "極小", "sim_size_small": "小", "sim_size_medium": "中",
        "sim_size_large": "大", "sim_size_huge": "極大",
        "sim_hitchance": "命中率", "sim_critchance": "クリティカル(命中毎)",
        "sim_dmg_hit": "ダメージ / 命中", "sim_dmg_swing": "ダメージ / 振り",
        "sim_movecost": "攻撃ムーブ", "sim_dps": "毎秒ダメージ", "sim_ttk": "撃破時間",
        "sim_hit_sub": "命中値 {v}", "sim_atk_sub": "{v} /秒",
        "sim_dist": "振り毎ダメージ分布 ({n}回試行)",
        "sim_assume": "スタミナ満タン・かさばり0・両腕・武術/変異バフなしを仮定、両手"
                      "ボーナス未適用。ダメージは打撃/切断/刺突の実ロール、命中率は実σ=25の"
                      "Φ((命中−回避)/5)。",
        "sim_mode": "モード", "sim_mode_melee": "近接", "sim_mode_ranged": "遠距離",
        "sim_gun": "銃", "sim_ammo": "弾薬",
        "sim_pick_weapon": "武器を選択", "sim_pick_monster": "モンスターを選択",
        "sim_pick_gun": "銃を選択", "sim_pick_ammo": "弾薬を選択",
        "sim_pick_custom": "名前で検索…",
        "sim_sk_gun": "銃スキル", "sim_gun_disp": "分散 (MoA)",
        "sim_recoil": "反動 (MoA)", "sim_range": "射程 (マス)",
        "sim_rng_dmg": "ダメージ", "sim_rng_pen": "装甲貫通",
        "sim_proj_speed": "弾速", "sim_a_bullet": "防御(弾)",
        "sim_aimed": "精密(狙撃)", "sim_dmg_shot": "ダメージ / 発",
        "sim_avgdisp": "平均分散", "sim_shots_kill": "撃破弾数",
        "sim_dist_shot": "発毎ダメージ分布 ({n}回試行)",
        "sim_assume_r": "発毎で照準時間・連射を無視。胴命中を仮定(severity ≤1.5、"
                        "ヘッドショット無し)。分散 = 武器 + 器用 + スキル + 反動で、"
                        "散布が対象サイズ内に収まれば命中。",
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



# json item "type" -> readable name, for the item-table type filter.
TYPE_NAMES = {
    "GENERIC": {"en": "Generic", "ko": "일반", "ja": "汎用"},
    "COMESTIBLE": {"en": "Food / Drug", "ko": "음식 / 약물", "ja": "食料 / 薬"},
    "ARMOR": {"en": "Armor", "ko": "방어구", "ja": "防具"},
    "TOOL": {"en": "Tool", "ko": "도구", "ja": "道具"},
    "TOOL_ARMOR": {"en": "Worn tool", "ko": "착용 도구", "ja": "装着道具"},
    "TOOLMOD": {"en": "Tool mod", "ko": "도구 개조", "ja": "道具改造"},
    "GUN": {"en": "Gun", "ko": "총기", "ja": "銃"},
    "GUNMOD": {"en": "Gun mod", "ko": "총기 개조", "ja": "銃改造"},
    "MAGAZINE": {"en": "Magazine", "ko": "탄창", "ja": "弾倉"},
    "AMMO": {"en": "Ammo", "ko": "탄약", "ja": "弾薬"},
    "BOOK": {"en": "Book", "ko": "책", "ja": "本"},
    "BIONIC_ITEM": {"en": "Bionic", "ko": "바이오닉", "ja": "バイオニック"},
    "ENGINE": {"en": "Engine", "ko": "엔진", "ja": "エンジン"},
    "WHEEL": {"en": "Wheel", "ko": "바퀴", "ja": "車輪"},
    "PET_ARMOR": {"en": "Pet armor", "ko": "동물 방어구", "ja": "ペット防具"},
    "CONTAINER": {"en": "Container", "ko": "용기", "ja": "容器"},
    "BATTERY": {"en": "Battery", "ko": "배터리", "ja": "電池"},
}


def type_name(t, lang):
    d = TYPE_NAMES.get(t)
    if not d:
        return (t or "").replace("_", " ").title()
    return d.get(lang) or d["en"]



# in-game item_category id -> readable name (the fine-grained classification used
# for browsing). Unknown ids fall back to a prettified id.
ITEMCAT_NAMES = {
    "weapons": {"en": "Weapons", "ko": "무기", "ja": "武器"},
    "guns": {"en": "Guns", "ko": "총기", "ja": "銃"},
    "ammo": {"en": "Ammo", "ko": "탄약", "ja": "弾薬"},
    "magazines": {"en": "Magazines", "ko": "탄창", "ja": "弾倉"},
    "mods": {"en": "Gun mods", "ko": "총기 개조", "ja": "銃改造"},
    "clothing": {"en": "Clothing", "ko": "의류", "ja": "衣類"},
    "armor": {"en": "Armor", "ko": "방어구", "ja": "防具"},
    "food": {"en": "Food", "ko": "음식", "ja": "食料"},
    "cooking_ingredients": {"en": "Cooking ingredients", "ko": "요리 재료", "ja": "料理材料"},
    "drugs": {"en": "Drugs", "ko": "약물", "ja": "薬"},
    "books": {"en": "Books", "ko": "책", "ja": "本"},
    "tools": {"en": "Tools", "ko": "도구", "ja": "道具"},
    "tools_cooking": {"en": "Cooking tools", "ko": "요리 도구", "ja": "調理道具"},
    "tools_workshop": {"en": "Workshop tools", "ko": "작업장 도구", "ja": "工房道具"},
    "tools_farming": {"en": "Farming tools", "ko": "농사 도구", "ja": "農具"},
    "tools_chemistry": {"en": "Chemistry tools", "ko": "화학 도구", "ja": "化学道具"},
    "tools_entry": {"en": "Entry tools", "ko": "침입 도구", "ja": "侵入道具"},
    "chems": {"en": "Chemicals", "ko": "화학약품", "ja": "化学薬品"},
    "container": {"en": "Containers", "ko": "용기", "ja": "容器"},
    "electronics": {"en": "Electronics", "ko": "전자기기", "ja": "電子機器"},
    "scrap_electronics": {"en": "Electronic scrap", "ko": "전자 부품", "ja": "電子くず"},
    "scrap_metal": {"en": "Metal scrap", "ko": "금속 부품", "ja": "金属くず"},
    "scrap_fabric": {"en": "Fabric scrap", "ko": "천 조각", "ja": "布くず"},
    "scrap_wood": {"en": "Wood scrap", "ko": "목재 조각", "ja": "木くず"},
    "scrap_plastic": {"en": "Plastic scrap", "ko": "플라스틱 조각", "ja": "プラくず"},
    "scrap_glass": {"en": "Glass scrap", "ko": "유리 조각", "ja": "ガラスくず"},
    "scrap_ceramics": {"en": "Ceramic scrap", "ko": "도자기 조각", "ja": "陶器くず"},
    "veh_parts": {"en": "Vehicle parts", "ko": "차량 부품", "ja": "車両部品"},
    "spare_parts": {"en": "Spare parts", "ko": "예비 부품", "ja": "予備部品"},
    "deployables": {"en": "Deployables", "ko": "설치물", "ja": "設置物"},
    "valuables": {"en": "Valuables", "ko": "귀중품", "ja": "貴重品"},
    "fuel": {"en": "Fuel", "ko": "연료", "ja": "燃料"},
    "battery": {"en": "Batteries", "ko": "배터리", "ja": "電池"},
    "rocks": {"en": "Rocks", "ko": "돌", "ja": "石"},
    "seeds": {"en": "Seeds", "ko": "씨앗", "ja": "種"},
    "mutagen": {"en": "Mutagens", "ko": "변이원", "ja": "変異原"},
    "bionics": {"en": "Bionics", "ko": "바이오닉", "ja": "バイオニック"},
    "soil": {"en": "Soil", "ko": "흙", "ja": "土"},
    "maps": {"en": "Maps", "ko": "지도", "ja": "地図"},
    "artifacts": {"en": "Artifacts", "ko": "유물", "ja": "アーティファクト"},
    "manuals": {"en": "Manuals", "ko": "설명서", "ja": "マニュアル"},
    "currency": {"en": "Currency", "ko": "화폐", "ja": "通貨"},
    "other": {"en": "Other", "ko": "기타", "ja": "その他"},
}


def itemcat_name(cid, lang):
    d = ITEMCAT_NAMES.get(cid)
    if not d:
        return (cid or "other").replace("_", " ").title()
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
         "<b>행동력(이동점수)</b>를 받고(보통 사람 100), 행동에 소비하다가 행동력가 떨어지면 "
         "그 1초가 흐른다. speed가 높을수록 행동력가 많아 초당 더 많이 행동한다. 한 칸 이동은 "
         "그 지형의 이동비용(평지 ≈100)이라, speed 100이면 한 걸음이 약 1초.</p>"
         "<p>플레이어 근접 공격의 행동력 비용은 이렇게 쌓인다(BN 소스 기준):</p><ul>"
         "<li>무기 기본 = <code>65 + 부피/62.5 mL + 무게/60 g</code> (크고 무거울수록 "
         "느림)</li>"
         "<li><code>기본 / 2</code>에서 시작 → 몸통+양손 평균 <b>방해도(encumbrance)</b>을 "
         "더함 → <b>스태미나</b> 페널티 곱함(평소 1배, 스태미나 25% 미만에서 최대 2배)</li>"
         "<li><b>스킬</b> 항 <code>(기본/2) × (15 − 근접스킬) / 15</code> 더함(스킬 15면 "
         "사라짐), 그다음 <b>민첩성</b>을 뺌</li>"
         "<li>마지막으로 무술·변이 보정, 결과는 최소 25행동력 아래로는 안 내려감</li></ul>"
         "<p>speed 100에서 100행동력 = 1초이므로, 100행동력 공격은 초당 1회다. 가볍고·숙련되고·"
         "민첩성할수록 행동력가 줄어 빨라진다. 몬스터는 이 계산을 거치지 않고 JSON에 "
         "<code>attack_cost</code>(행동력)를 직접 가진다.</p>"),
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


# ---------------------------------------------------------------------------
# Combat formulas, split into topics. The mechanics page is a topic list; each
# topic renders its own sections. Formula <pre> blocks are language-neutral
# (math / engine identifiers) and shared by every language; only the headings
# and surrounding prose are localized. Japanese bodies fall back to English
# (see mech_sections); topic titles below are localized in all three.
# Source: Cataclysm: Bright Nights C++ at the commit your build was made from
# (VERSION.txt). Line refs live in docs/combat-formulas.md.
# ---------------------------------------------------------------------------
MECH_TOPICS = [
    ("basics",     {"en": "Data & crafting basics", "ko": "데이터·제작 기초", "ja": "データ・製作の基礎"}),
    ("rng",        {"en": "RNG & constants", "ko": "난수·상수", "ja": "乱数・定数"}),
    ("melee_hit",  {"en": "Melee: hit & dodge", "ko": "근접: 명중·회피", "ja": "近接: 命中・回避"}),
    ("melee_crit", {"en": "Melee: critical hits", "ko": "근접: 치명타", "ja": "近接: クリティカル"}),
    ("melee_dmg",  {"en": "Melee: damage", "ko": "근접: 피해", "ja": "近接: ダメージ"}),
    ("defense",    {"en": "Damage application & armor", "ko": "피해 적용·방어구", "ja": "ダメージ適用・防具"}),
    ("melee_cost", {"en": "Attack speed & stamina", "ko": "공격 속도·스태미나", "ja": "攻撃速度・スタミナ"}),
    ("ranged",     {"en": "Ranged combat", "ko": "원거리 전투", "ja": "遠距離戦闘"}),
    ("monster",    {"en": "Monster combat", "ko": "몬스터 전투", "ja": "モンスター戦闘"}),
]


# shared, language-neutral formula blocks --------------------------------------
_F_DICE = (
    "<pre class=mechcode>dice(n, sides)     = sum of n rolls of rng(1..sides)\n"
    "rng_float(lo, hi)  = uniform real in [lo, hi)\n"
    "normal_roll(m, s)  = Normal(mean m, stddev s)   # 2nd arg IS the stddev\n"
    "rng_normal(lo, hi) = clamp(normal_roll((lo+hi)/2, (hi-lo)/4), lo, hi)\n"
    "roll_remainder(x)  = probabilistic rounding (1.3 -> 1 at 70%, 2 at 30%)\n"
    "one_in(n)          = true with probability 1/n</pre>")
_F_CONST = (
    "<pre class=mechcode>iso_tangent(d, theta) = sqrt(2*d^2*(1-cos theta)) = 2*d*sin(theta/2)\n\n"
    "MAX_SKILL = 10    BIO_CQB_LEVEL = 5    MAX_RECOIL = 3000 MoA\n"
    "accuracy_roll_stddev = 5.0\n"
    "accuracy bands:  headshot .1   crit .2   goodhit .5   standard .8   graze 1.0</pre>")
_F_TOHIT = (
    "<pre class=mechcode>get_hit_base   = dex/4\n"
    "get_hit_weapon = skill_w/3 + skill_melee/2 + weapon.to_hit + weapon.hit_bonus\n"
    "                 (skill_w = weapon's melee skill; CQB floors it at 5)\n"
    "get_melee_hit  = get_hit_base + get_hit_weapon + mabuff_tohit\n"
    "                 HYPEROPIC (uncorrected): -2 ;  bouldering: x0.75\n"
    "                 x max(0.25, 1 - torso_enc/100)</pre>")
_F_HITROLL = (
    "<pre class=mechcode>hit_roll   = melee_hit_range(hit) = normal_roll(hit*5, 25)\n"
    "hit_spread = hit_roll - dodge_roll - size_penalty   # hit if >= 0\n"
    "dodge_roll = get_dodge() * 5\n"
    "IMMOBILE target: hit_spread += 40\n"
    "size_penalty: tiny +30  small +15  medium 0  large -10  huge -20</pre>")
_F_DISC_A = ("<pre class=mechcode>melee_hit_range(acc) = normal_roll(acc*5, 5*5)  ->  N(mean 5*acc, stddev 25)</pre>")
_F_DISC_B = ("<pre class=mechcode>hit_chance(acc) = 0.5*(1 + erf(-acc/sqrt2)) = Phi(-acc)  ->  assumes N(5*acc, 5)</pre>")
_F_DISC_P = ("<pre class=mechcode>m = hit - dodge\nP(hit) = Phi(5m / sigma);   actual sigma=25 -> Phi(m/5);   intended sigma=5 -> Phi(m)</pre>")
_F_DISC_TBL = (
    "<table class=mecht><tr><th>m = hit-dodge</th><th>actual (&sigma;=25)</th>"
    "<th>intended (&sigma;=5)</th></tr>"
    "<tr><td>-5</td><td>15.9%</td><td>0.00003%</td></tr>"
    "<tr><td>-2</td><td>34.5%</td><td>2.3%</td></tr>"
    "<tr><td>0</td><td>50%</td><td>50%</td></tr>"
    "<tr><td>+2</td><td>65.5%</td><td>97.7%</td></tr>"
    "<tr><td>+5</td><td>84.1%</td><td>99.99997%</td></tr></table>")
_F_CRIT = (
    "<pre class=mechcode>scored_crit = ( rng_float(0,1) < crit_chance )\n\n"
    "weapon_cc = 0.5  (unarmed: 0.5 + 0.05*skill_unarmed)\n"
    "  ath = weapon.to_hit + weapon.hit_bonus\n"
    "  ath>0: weapon_cc = max(weapon_cc, 0.5 + 0.1*ath);  ath<0: weapon_cc += 0.1*ath\n"
    "  weapon_cc = clamp(weapon_cc, 0, 1)\n"
    "stat_cc   = clamp(0.25 + 0.01*dex + 0.02*per, 0, 1)\n"
    "sk        = skill_w (CQB->5) + skill_melee/2.5\n"
    "skill_cc  = clamp(0.25 + 0.025*sk, 0, 1)\n\n"
    "triple = weapon_cc * stat_cc * skill_cc            # always a crit\n"
    "if hit_roll > 1.5*target_dodge:\n"
    "  double = 0.5*(wc*sc + sc*kc + wc*kc - 3*triple)\n"
    "  crit_chance = triple + double\n"
    "else:\n"
    "  crit_chance = triple</pre>")
_F_BASH = (
    "<pre class=mechcode>skill = bashing (unarmed skill if unarmed weapon); CQB->5;  stat = str\n"
    "stat_bonus = bonus_damage + mabuff(BASH);  bonus_damage = rng_float(str/2, str)\n"
    "weap_dam   = weapon.damage_melee(BASH) + stat_bonus  (+ skill if unarmed)\n"
    "bash_cap   = 2*stat + 2*skill\n"
    "bash_mul   = skill<5 ? 0.8+0.08*skill : 0.96+0.04*skill\n"
    "if bash_cap < weap_dam and weapon != null: bash_mul *= (1 + bash_cap/weap_dam)/2\n"
    "low_cap    = min(1, str/20);  bash_min = low_cap*weap_dam\n"
    "weap_dam   = rng_float(bash_min, weap_dam)\n"
    "crit: bash_mul *= 1.5,  armor_mult *= 0.5   # 50% penetration</pre>")
_F_CUT = (
    "<pre class=mechcode>cut_dam = mabuff(CUT) + weapon.damage_melee(CUT)  (+unarmed bonuses);  skip if <= 0\n"
    "cut_mul = skill_cut<5 ? 0.8+0.08*s : 0.96+0.04*s\n"
    "DIAMOND flag: arpen += cut_dam*0.35 + 10\n"
    "crit: cut_mul *= 1.25,  arpen += 5,  armor_mult = 0.75</pre>")
_F_STAB = (
    "<pre class=mechcode>stab_dam = mabuff(STAB) + weapon.damage_melee(STAB) (+unarmed);  skip if <= 0\n"
    "stab_mul = skill_stab<=5 ? 0.66+0.1*s : 0.86+0.06*s\n"
    "DIAMOND flag: arpen += stab_dam*0.35 + 10\n"
    "crit: stab_mul *= 1 + skill_stab/10,  armor_mult *= 0.66</pre>")
_F_DMG_INST = (
    "<pre class=mechcode>both arms broken:           x0.1\n"
    "polearm hitting adjacent:   x0.7\n"
    "stamina < 25%:              x(0.5 + stamina/max*2)</pre>")
_F_DEF_ORDER = (
    "<pre class=mechcode>1) absorb_hit subtracts armor from each unit's amount\n"
    "2) final = floor( amount_after_armor * damage_multiplier )\n"
    "   -> crit / skill multipliers apply AFTER armor</pre>")
_F_DEF_RESIST = (
    "<pre class=mechcode>effective_resist(du) = max(type_resist - res_pen, 0) * res_mult\n"
    "per layer:  amount -= effective_resist;   res_pen -= type_resist</pre>")
_F_COST = (
    "<pre class=mechcode>item base = 65 + (volume/62.5mL + weight/60g) / count\n\n"
    "b     = base / 2\n"
    "move  = b + torso_enc + (hand_l_enc + hand_r_enc)/2\n"
    "move *= 1 + max((0.25 - stamina_ratio)*4, 0)     # stamina penalty 1x..2x\n"
    "move += b * (15 - skill_melee) / 15              # skill\n"
    "move -= dex\n"
    "if base>100 and one-handable and two arms: move = move^0.975\n"
    "move = move*ma_mult + ma_flat;  *= mutation modifier\n"
    "result = max(25, move)        # 100 moves = 1s at speed 100</pre>")
_F_STUMBLE = (
    "<pre class=mechcode>stumble = volume/125mL + weight/(str*10g + 13g)    (DEFT -> 0)\n"
    "  on miss: move += min(60, stumble)\n\n"
    "stamina cost = (weight/16g + roll_remainder((arm_l+arm_r)*2) - (DEFT?50:0) + 50)\n"
    "             * max(0.667, (30 - skill_melee)/30) * (0.75 + 1/(2 + str*0.25))</pre>")
_F_DISP = (
    "<pre class=mechcode>roll() = (sum rng_float(0, L_i) + sum rng_normal(N_i)) * prod mult_k   # MoA\n\n"
    "weapon_dispersion (normal source) = gun_dispersion()\n"
    "+ ranged_dex_mod = max((20 - dex)*0.5, 0)\n"
    "+ (arm_l_enc + arm_r_enc)/5\n"
    "+ dispersion_from_skill(avgSkill, wd),  avgSkill = min(10, (gun + gun_skill)/2)\n"
    "x0.75 targeting CBM | x0.75 crouch | x0.25 laser-guided\n"
    "underwater mismatch: +150, x4</pre>")
_F_DISP_SKILL = (
    "<pre class=mechcode>dispersion_from_skill(s, wd):\n"
    "  s >= 10:  0\n"
    "  s >= 5 :  3*(10-s) + wd*(10-s)*1.25/5\n"
    "  s < 5  :  3*(10-s) + wd*(1.25 + (5-s)*3.75/5)</pre>")
_F_AIM = (
    "<pre class=mechcode>recoil_total = max(0, recoil + |vehicle velocity|*3/100 + ench)\n"
    "aim_per_move ~ (10 + skill + dex + sight - enc) * vol_mult * 6.5\n"
    "             * (1 - logRange(0, 3000, recoil)),  >= 5</pre>")
_F_PROJ = (
    "<pre class=mechcode>missed_by_tiles = 2*range*sin(dispersion/2)\n"
    "missed_by       = min(1, missed_by_tiles / target_size)\n\n"
    "goodhit = missed_by + clamp(dodge_roll / dice(10, proj.speed), 0, 1)\n"
    "goodhit >= 1  ->  avoided (no damage)</pre>")
_F_SEV = (
    "<pre class=mechcode>goodhit > 0.8: severity = max(0.01, 4*(1-goodhit))   # graze 1-80%\n"
    "goodhit > 0.5: severity = 1.6 - goodhit              # 80-110%\n"
    "goodhit > 0.2: severity = 1.766 - goodhit*4/3        # 110-150%\n"
    "else:          severity = 1.5\n"
    "cap by body part: head <=2.0 (1.5 for characters), torso <=1.5, limbs <=1.25\n"
    "impact.mult_damage(severity, pre_armor = goodhit > 0.8)</pre>")
_F_MON = (
    "<pre class=mechcode>get_hit_base = melee_skill;  hit_roll = melee_hit_range(get_hit)  (/4 bouldering)\n"
    "get_dodge_base = sk_dodge;   dodge_roll = get_dodge() * 5\n"
    "melee_attack(t) = melee_attack(t, get_hit());   moves -= attack_cost\n"
    "damage = melee_damage(fixed)\n"
    "       + dice(melee_dice, melee_sides) BASH + bash_bonus BASH + cut_bonus CUT\n"
    "stability = dice(melee_sides, melee_dice) + size (tiny -7 .. huge +10)</pre>")


# plain-language intros (one per topic, per language) shown first in each topic
_I_HIT_EN = (
    "<p>Your <b>accuracy</b> is one number built from Dexterity, your melee &amp; "
    "weapon skills, and the weapon's to-hit. The game rolls a <b>wide bell curve</b> "
    "around 5&times; that number, and you hit if the roll clears 5&times; the target's "
    "dodge (plus a size adjustment). Because the curve is wide (&sigma;=25), even a "
    "clear accuracy edge is far from a sure hit.</p>"
    "<p><i>Example:</i> DEX 10, melee 3, weapon skill 3, a +1 weapon &rarr; accuracy 6. "
    "Against a zombie with dodge 3 your edge is 3, about a <b>73%</b> chance to hit — "
    "not the ~100% a naive guess suggests.</p>")
_I_HIT_KO = (
    "<p><b>명중치</b>는 민첩성 + 근접·무기 스킬 + 무기 명중보정으로 만들어지는 하나의 "
    "숫자입니다. 게임은 그 값의 5배를 중심으로 <b>폭이 넓은 종형 곡선</b>으로 굴리고, "
    "굴림이 대상 회피의 5배(+크기 보정)를 넘으면 명중합니다. 곡선이 넓어서(&sigma;=25) "
    "명중치가 꽤 앞서도 확정 명중과는 거리가 멉니다.</p>"
    "<p><i>예:</i> 민첩성 10, 근접 3, 무기 3, +1 무기 &rarr; 명중치 6. 회피 3 좀비 상대로 "
    "우위는 3이라 명중 확률은 약 <b>73%</b> — 단순 추정의 ~100%가 아닙니다.</p>")
_I_CRIT_EN = (
    "<p>Every landed hit can <b>critical</b>. The chance is the product of three "
    "sub-chances — weapon, your stats (DEX/PER) and skill — so raising all three "
    "compounds. A hit that clearly beats dodge unlocks an extra bonus chance. Crits "
    "raise damage and partly <b>ignore armor</b>.</p>")
_I_CRIT_KO = (
    "<p>명중한 공격은 모두 <b>치명타</b>가 될 수 있습니다. 확률은 무기·능력치(민첩성/지각)·"
    "스킬 세 하위 확률의 곱이라 셋을 함께 올리면 크게 좋아집니다. 회피를 확실히 넘긴 "
    "명중은 보너스 확률이 추가로 열립니다. 치명타는 피해를 올리고 방어를 일부 "
    "<b>무시</b>합니다.</p>")
_I_DMG_EN = (
    "<p>Damage = the weapon's listed damage + a <b>Strength</b> bonus, then scaled by a "
    "<b>skill multiplier</b> (more skill → harder hits; low stats cap the top end). "
    "Each type — bash, cut, stab — is rolled separately, and <b>armor is subtracted "
    "before</b> that multiplier. Crits add their own multiplier and armor "
    "penetration.</p>")
_I_DMG_KO = (
    "<p>피해 = 무기 표기 피해 + <b>체력</b> 보너스, 여기에 <b>스킬 배수</b>가 곱해집니다"
    "(스킬이 높을수록 강하고, 능력치가 낮으면 상한이 눌립니다). 타격·베기·관통은 각각 "
    "따로 굴려지고, <b>방어구는 배수 적용 전에 먼저 차감</b>됩니다. 치명타는 자체 배수와 "
    "방어 관통을 더합니다.</p>")
_I_DEF_EN = (
    "<p>When you're hit, <b>armor is subtracted from the raw damage first</b>; only "
    "then is the crit/skill multiplier applied to what's left. Penetration lowers the "
    "armor value before subtraction. Worn layers mitigate in turn — outer first — but "
    "a layer counts only if it covers the spot and a coverage roll passes.</p>")
_I_DEF_KO = (
    "<p>피격 시 <b>방어구가 먼저 원시 피해에서 차감</b>되고, 남은 값에만 치명타/스킬 "
    "배수가 곱해집니다. 관통은 차감 전에 방어 수치를 낮춥니다. 착용한 레이어가 겉부터 "
    "차례로 경감하지만, 그 부위를 덮고 범위(coverage) 굴림을 통과해야 작동합니다.</p>")
_I_COST_EN = (
    "<p>Heavier, bulkier weapons swing <b>slower</b>; melee skill and Dexterity make "
    "you faster. The cost is in <b>moves</b> — at normal speed 100, 100 moves = 1 "
    "second — so fewer moves means more swings per second. Low stamina makes every "
    "swing cost more.</p>")
_I_COST_KO = (
    "<p>무겁고 부피 큰 무기는 <b>느리게</b> 휘둘러지고, 근접 스킬과 민첩성이 빠르게 "
    "해줍니다. 비용 단위는 <b>행동력</b>로, 보통 속도 100에서 100행동력 = 1초라 행동력가 "
    "적을수록 초당 공격이 늘어납니다. 스태미나가 낮으면 매 공격 비용이 커집니다.</p>")
_I_RANGED_EN = (
    "<p>A shot scatters by an <b>angle (dispersion)</b> built from the weapon, your gun "
    "skills, Dexterity and current recoil; <b>aiming</b> shrinks it over time. Whether "
    "you hit depends on how far that scatter throws the shot versus the target's size. "
    "The closer to dead-center, the more damage — up to a critical.</p>")
_I_RANGED_KO = (
    "<p>발사된 탄은 무기·총기 스킬·민첩성·현재 반동으로 만들어진 <b>각도(분산)</b>만큼 "
    "흩어지고, <b>조준</b>하면 시간에 따라 줄어듭니다. 명중 여부는 그 흩어짐이 대상 "
    "크기에 비해 얼마나 빗나가게 하는지로 정해집니다. 정중앙에 가까울수록 피해가 커지고 "
    "치명타까지 갑니다.</p>")
_I_MON_EN = (
    "<p>Monsters use the <b>same</b> hit/damage engine, but their numbers come straight "
    "from JSON: accuracy from <code>melee_skill</code>, dodge from <code>sk_dodge</code>, "
    "damage from <code>melee_dice</code> / <code>melee_sides</code> plus bonuses — not "
    "computed from attributes like a character.</p>")
_I_MON_KO = (
    "<p>몬스터도 <b>같은</b> 명중/피해 엔진을 쓰지만, 수치는 JSON에서 바로 옵니다: 명중은 "
    "<code>melee_skill</code>, 회피는 <code>sk_dodge</code>, 피해는 "
    "<code>melee_dice</code> / <code>melee_sides</code> + 보너스이며, 캐릭터처럼 능력치로 "
    "계산하지 않습니다.</p>")

COMBAT_DOC = {
    "en": {
        "rng": [
            ("Source", "<p>These formulas come straight from the Cataclysm: Bright "
             "Nights C++ engine at the commit your build was made from "
             "(<code>VERSION.txt</code>). They describe the engine, not JSON data, so "
             "they don't change with mods. Exact <code>file:line</code> references are "
             "in <code>docs/combat-formulas.md</code>.</p>"),
            ("Dice & random rolls", _F_DICE),
            ("Geometry & constants", _F_CONST),
        ],
        "melee_hit": [
            ("In plain terms", _I_HIT_EN),
            ("To-hit value", _F_TOHIT),
            ("Hit roll, dodge & spread",
             _F_HITROLL + "<p>The attacker hits when the rolled accuracy beats the "
             "target's scaled dodge plus a size penalty.</p>"),
            ("&#9888; Roll standard-deviation mismatch",
             "<p>The constant <code>accuracy_roll_stddev = 5.0</code> is used "
             "inconsistently. The function that produces the <b>actual</b> roll passes "
             "its square as the standard deviation:</p>" + _F_DISC_A +
             "<p>but the AI/display estimator <code>hit_chance</code> assumes a stddev "
             "of 5:</p>" + _F_DISC_B +
             "<p>Because <code>normal_roll</code>'s second argument <i>is</i> the "
             "standard deviation, the real roll is 5&times; wider than the estimator "
             "models. Writing <code>m = hit - dodge</code>:</p>" + _F_DISC_P +
             "<p>So a point of accuracy is worth one fifth of what the estimator "
             "implies, and melee is far swingier. <code>hit_chance</code> is only used "
             "by NPC AI, never in real resolution, so players actually experience the "
             "&sigma;=25 column:</p>" + _F_DISC_TBL),
        ],
        "melee_crit": [
            ("In plain terms", _I_CRIT_EN),
            ("Critical chance", "<p>Three independent chances (weapon, stats, skill) are "
             "combined. The &quot;triple&quot; is a guaranteed crit; the &quot;double&quot; "
             "term is only added when the hit roll clearly beats dodge.</p>" + _F_CRIT),
        ],
        "melee_dmg": [
            ("In plain terms", _I_DMG_EN),
            ("Bash", _F_BASH),
            ("Cut", _F_CUT),
            ("Stab", _F_STAB),
            ("Whole-instance multipliers", "<p>Applied to the rolled instance just "
             "before the hit lands:</p>" + _F_DMG_INST),
        ],
        "defense": [
            ("In plain terms", _I_DEF_EN),
            ("Application order", _F_DEF_ORDER),
            ("Armor mitigation", _F_DEF_RESIST +
             "<p>Worn armor is applied outermost&rarr;innermost; a layer is engaged only "
             "if <code>rng(1,100) &le; coverage</code>. Bash damage is then scaled by "
             "&times;1.4 (LIGHT_BONES) or &times;1.8 (HOLLOW_BONES). Monsters use their "
             "per-type <code>armor_*</code> plus worn and bonuses as the resist.</p>"),
        ],
        "melee_cost": [
            ("In plain terms", _I_COST_EN),
            ("Attack moves", "<p>100 moves = 1 second at speed 100, so attack time "
             "&asymp; moves / speed.</p>" + _F_COST),
            ("Stumble & stamina", _F_STUMBLE),
        ],
        "ranged": [
            ("In plain terms", _I_RANGED_EN),
            ("Dispersion (MoA)", _F_DISP),
            ("Dispersion from skill", _F_DISP_SKILL),
            ("Recoil & aim", _F_AIM),
            ("Projectile aim & dodge", _F_PROJ),
            ("Damage severity & hit location", _F_SEV),
        ],
        "monster": [
            ("In plain terms", _I_MON_EN),
            ("Monster melee", _F_MON),
        ],
    },
    "ko": {
        "rng": [
            ("출처", "<p>이 공식들은 설치 빌드가 만들어진 커밋(<code>VERSION.txt</code>)의 "
             "Cataclysm: Bright Nights C++ 엔진에서 직접 가져온 것입니다. JSON 데이터가 "
             "아니라 엔진 동작이라 모드로 바뀌지 않습니다. 정확한 <code>파일:줄</code> 참조는 "
             "<code>docs/combat-formulas.md</code>에 있습니다.</p>"),
            ("주사위·난수 굴림", _F_DICE),
            ("기하·상수", _F_CONST),
        ],
        "melee_hit": [
            ("쉬운 설명", _I_HIT_KO),
            ("명중치(to-hit)", _F_TOHIT),
            ("명중 굴림·회피·여유치",
             _F_HITROLL + "<p>굴린 명중치가 대상의 (5배) 회피치 + 크기 페널티를 넘으면 "
             "명중합니다.</p>"),
            ("&#9888; 명중 굴림 표준편차 불일치",
             "<p>상수 <code>accuracy_roll_stddev = 5.0</code>이 일관되지 않게 쓰입니다. "
             "<b>실제</b> 굴림을 만드는 함수는 이 값을 제곱해 표준편차로 넘깁니다:</p>" + _F_DISC_A +
             "<p>그러나 AI·표시용 추정 함수 <code>hit_chance</code>는 표준편차 5를 "
             "가정합니다:</p>" + _F_DISC_B +
             "<p><code>normal_roll</code>의 둘째 인자가 바로 표준편차이므로, 실제 굴림은 "
             "추정이 가정한 것보다 5배 넓습니다. <code>m = hit - dodge</code>로 두면:</p>" +
             _F_DISC_P +
             "<p>즉 명중치 1점의 가치가 추정의 1/5이라 근접전이 훨씬 운빨입니다. "
             "<code>hit_chance</code>는 NPC AI에서만 쓰이고 실제 판정에는 쓰이지 않으므로, "
             "플레이어가 실제로 겪는 것은 &sigma;=25 열입니다:</p>" + _F_DISC_TBL),
        ],
        "melee_crit": [
            ("쉬운 설명", _I_CRIT_KO),
            ("치명타 확률", "<p>세 독립 확률(무기·능력치·스킬)을 합성합니다. "
             "&quot;triple&quot;은 무조건 치명타이고, &quot;double&quot; 항은 명중 굴림이 "
             "회피를 확실히 넘을 때만 더해집니다.</p>" + _F_CRIT),
        ],
        "melee_dmg": [
            ("쉬운 설명", _I_DMG_KO),
            ("타격(Bash)", _F_BASH),
            ("베기(Cut)", _F_CUT),
            ("관통(Stab)", _F_STAB),
            ("전체 인스턴스 보정", "<p>굴린 피해 인스턴스에 명중 직전 적용됩니다:</p>" + _F_DMG_INST),
        ],
        "defense": [
            ("쉬운 설명", _I_DEF_KO),
            ("적용 순서", _F_DEF_ORDER),
            ("방어구 경감", _F_DEF_RESIST +
             "<p>착용 방어구는 겉&rarr;속 순으로 적용되며, 각 레이어는 "
             "<code>rng(1,100) &le; 범위(coverage)</code>일 때만 작동합니다. 이후 타격 "
             "피해는 &times;1.4(LIGHT_BONES)/&times;1.8(HOLLOW_BONES)로 곱해집니다. 몬스터는 "
             "타입별 <code>armor_*</code> + 착용 + 보너스를 저항으로 씁니다.</p>"),
        ],
        "melee_cost": [
            ("쉬운 설명", _I_COST_KO),
            ("공격 행동력", "<p>speed 100에서 100행동력 = 1초, 즉 공격 시간 &asymp; 행동력 / "
             "speed.</p>" + _F_COST),
            ("휘청임·스태미나", _F_STUMBLE),
        ],
        "ranged": [
            ("쉬운 설명", _I_RANGED_KO),
            ("분산(MoA)", _F_DISP),
            ("스킬에 의한 분산", _F_DISP_SKILL),
            ("반동·조준", _F_AIM),
            ("발사체 조준·회피", _F_PROJ),
            ("피해 배수(severity)·부위", _F_SEV),
        ],
        "monster": [
            ("쉬운 설명", _I_MON_KO),
            ("몬스터 근접", _F_MON),
        ],
    },
}


def mech_topic_title(topic, lang):
    for tid, names in MECH_TOPICS:
        if tid == topic:
            return names.get(lang) or names["en"]
    return topic


def mech_sections(lang, topic):
    """The (heading, body) sections for a mechanics topic, English-fallback."""
    if topic == "basics":
        return MECH_DOC.get(lang) or MECH_DOC["en"]
    by_lang = COMBAT_DOC.get(lang) or {}
    return by_lang.get(topic) or COMBAT_DOC["en"].get(topic, [])

