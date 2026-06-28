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
