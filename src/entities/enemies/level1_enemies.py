"""
level1_enemies.py — Bosque Aritmético (Nivel 1)
===============================================

Tema matemático: operaciones básicas (+, −, ×, ÷)
Enemigos: Slime → Goblin → Boss: Dragón Básico
"""

from ..enemy import Enemy
from ..sprites import PALETTE_GREEN
from ...math_engine.challenge import MathTopic
from ... import config

SLIME_SPRITES = {
    "idle": [
        [
            "....GGGG....",
            "..GGGGGGGG..",
            ".GGGGGGGGGG.",
            ".GGWGGGGWGG.",
            ".GGKGGGGKGG.",
            "GGGGGGGGGGGG",
            "GGGGGGGGGGGG",
            "GgGGGGGGGGgG",
            ".gggggggggg.",
        ],
        [
            "............",
            "....GGGG....",
            "..GGGGGGGG..",
            ".GGWGGGGWGG.",
            ".GGKGGGGKGG.",
            "GGGGGGGGGGGG",
            "GGGGGGGGGGGG",
            "GgGGGGGGGGgG",
            ".gggggggggg.",
        ],
    ],
    "hurt": [
        [
            "....GGGG....",
            "..GGGGGGGG..",
            ".GGRGGGGRGG.",
            ".GGWGGGGWGG.",
            ".GGKGGGGKGG.",
            "GGGGGGGGGGGG",
            "GGGGGGGGGGGG",
            "GgGGGGGGGGgG",
            ".gggggggggg.",
        ],
    ],
}


class Slime(Enemy):
    SPRITES = SLIME_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Slime", hp=40, attack=10,
                         math_topic=MathTopic.OPERATIONS, difficulty=1)


GOBLIN_SPRITES = {
    "idle": [
        [
            "...G...G....",
            "...GGGGG....",
            "..GGGGGGG...",
            "..GWGGGWG...",
            "..GKGGGKG...",
            "..GGgggGG...",
            "...GGGGG..R.",
            "..GGGGGGG.R.",
            ".G.GGG.G.R..",
            "...G...G....",
            "...G...G....",
        ],
        [
            "...G...G....",
            "...GGGGG....",
            "..GGGGGGG...",
            "..GWGGGWG...",
            "..GKGGGKG...",
            "..GGgggGG...",
            "...GGGGG..R.",
            "..GGGGGGG.R.",
            ".G.GGG.G.R..",
            "...G....G...",
            "...G....G...",
        ],
    ],
    "hurt": [
        [
            "...G...G....",
            "...GRGGG....",
            "..GWGGGWG...",
            "..GKGGGKG...",
            "..GGgggGG...",
            "...GGGGG..R.",
            "..GGGGGGG.R.",
            ".G.GGG.G.R..",
            "...G...G....",
            "...G...G....",
        ],
    ],
}


class Goblin(Enemy):
    SPRITES = GOBLIN_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Goblin", hp=60, attack=14,
                         math_topic=MathTopic.OPERATIONS, difficulty=2)


DRAGON_BASIC_SPRITES = {
    "idle": [
        [
            "..R.....R...",
            "..RR...RR...",
            "..RRR.RRR...",
            "...RRRRR....",
            "..RRWWWRR...",
            "..RRKWKWR...",
            "..RRRRRRR.Y.",
            ".RRRRRRRR.Y.",
            "RRRRRRRRRRY.",
            ".RR.RR.RR...",
            "..R..R..R...",
        ],
        [
            "..R.....R...",
            "..RR...RR...",
            "..RRR.RRR...",
            "...RRRRR....",
            "..RRWWWRR...",
            "..RRKWKWR...",
            "..RRRRRRR..Y",
            ".RRRRRRRR..Y",
            "RRRRRRRRRR.Y",
            ".RR.RR.RR...",
            "..R..R..R...",
        ],
    ],
    "hurt": [
        [
            "..R.....R...",
            "..RR...RR...",
            "..RRR.RRR...",
            "...RWRWR....",
            "..RWWWWWRR..",
            "..RRKWKWR...",
            "..RRRRRRR.Y.",
            ".RRRRRRRR.Y.",
            "RRRRRRRRRRY.",
            ".RR.RR.RR...",
            "..R..R..R...",
        ],
    ],
}


class BasicDragon(Enemy):
    """BOSS del nivel 1."""
    SPRITES = DRAGON_BASIC_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Dragón Básico", hp=120, attack=22,
                         math_topic=MathTopic.OPERATIONS, difficulty=3,
                         is_boss=True)
