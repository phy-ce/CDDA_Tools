import os

HOME = os.path.expanduser("~")



GAMES_ROOT = os.path.join(HOME, "Games")



GAME_SUBDIRS = ["Cataclysm-DDA", "Cataclysm-BN"]



# object "type" values that are real items (searchable, can have item pages)
ITEM_TYPES = {"GENERIC", "COMESTIBLE", "ARMOR", "TOOL", "TOOL_ARMOR", "TOOLMOD",
              "GUN", "GUNMOD", "MAGAZINE", "AMMO", "BOOK", "BIONIC_ITEM",
              "ENGINE", "WHEEL", "PET_ARMOR", "CONTAINER", "BATTERY"}



# in-memory app settings (single local user). Set from the Settings page.
SETTINGS = {"npc_loot": False}

