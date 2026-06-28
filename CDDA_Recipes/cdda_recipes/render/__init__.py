"""Page renderers, split by page type. Public renderers are re-exported
here so callers use a stable ``render.render_*`` API regardless of which
submodule defines them."""
from .item import render_item
from .group import render_group
from .search import render_search, suggest_json
from .pages import (render_landing, render_category, render_settings,
                    render_loot, render_mechanics, render_flag,
                    render_skill, render_quality, render_monster,
                    render_monsters_list, render_skills_list,
                    render_qualities_list, render_flags_list)
