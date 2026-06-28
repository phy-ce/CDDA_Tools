import os

HOME = os.path.expanduser("~")



GAMES_ROOT = os.path.join(HOME, "Games")



GAME_SUBDIRS = ["Cataclysm-DDA", "Cataclysm-BN"]



# object "type" values that are real items (searchable, can have item pages)
ITEM_TYPES = {"GENERIC", "COMESTIBLE", "ARMOR", "TOOL", "TOOL_ARMOR", "TOOLMOD",
              "GUN", "GUNMOD", "MAGAZINE", "AMMO", "BOOK", "BIONIC_ITEM",
              "ENGINE", "WHEEL", "PET_ARMOR", "CONTAINER", "BATTERY"}



# extra entity types browsable from the sidebar, each via the generic entity
# page (name + description + ASCII art + all JSON fields):
# (json "type", nav-string key, sidebar icon, list route)
BROWSE_TYPES = [
    ("mutation", "nav_mutations", "🧬", "/mutations"),
    ("bionic", "nav_bionics", "🔌", "/bionics"),
    ("profession", "nav_professions", "🧑", "/professions"),
    ("martial_art", "nav_martial", "🥋", "/martialarts"),
    ("technique", "nav_techniques", "🤸", "/techniques"),
    ("effect_type", "nav_effects", "✨", "/effects"),
    ("SPELL", "nav_spells", "🔮", "/spells"),
    ("vehicle", "nav_vehicles", "🚗", "/vehicles"),
    ("vehicle_part", "nav_vparts", "🔩", "/vparts"),
    ("construction_group", "nav_constructions", "🏗", "/constructions"),
    ("terrain", "nav_terrain", "🧱", "/terrain"),
    ("furniture", "nav_furniture", "🪑", "/furniture"),
    ("material", "nav_materials", "🧪", "/materials"),
]
BROWSE_BY_ROUTE = {r: (t, nk) for (t, nk, ic, r) in BROWSE_TYPES}
BROWSE_BY_TYPE = {t: (nk, r) for (t, nk, ic, r) in BROWSE_TYPES}


# in-memory app settings (single local user). Set from the Settings page.
SETTINGS = {"npc_loot": False}

