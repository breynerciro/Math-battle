"""
level4_enemies.py — Pantano de Fracciones (Nivel 4)
===================================================

Tema matemático: fracciones (suma, resta, multiplicación, división)
Enemigos: Caballero Oscuro → Mago → Boss: Hidra de 3 cabezas
"""

from ..enemy import Enemy
from ..sprites import PALETTE_GREEN
from ...math_engine.challenge import MathTopic

DARK_KNIGHT_SPRITES = {
    "idle": [
        [
            "...UUUUUU...",
            "..UUUUUUUU..",
            "..UXUUUUXU..",
            "..UUKKKKUU..",
            "...UUUUUU...",
            "..UUUUUUUU..",
            ".UXUUUUUUXU.",
            ".UUUURRRUUU.",
            "..UUUUUUUU..",
            "..UU....UU..",
            "..UU....UU..",
        ],
        [
            "...UUUUUU...",
            "..UUUUUUUU..",
            "..UXUUUUXU..",
            "..UUKKKKUU..",
            "...UUUUUU...",
            "..UUUUUUUU..",
            ".UXUUUUUUXU.",
            ".UUUURRRUUU.",
            "..UUUUUUUU..",
            "..UU....UU..",
            "..UU....UU..",
        ],
    ],
    "hurt": [
        [
            "...UUUUUU...",
            "..URUUUUUU..",
            "..UXUUUUXU..",
            "..UUKKKKUU..",
            "...UUUUUU...",
            "..UUUUUUUU..",
            ".UXUUUUUUXU.",
            ".UUUURRRUUU.",
            "..UUUUUUUU..",
            "..UU....UU..",
            "..UU....UU..",
        ],
    ],
}


class DarkKnight(Enemy):
    SPRITES = DARK_KNIGHT_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Caballero Oscuro", hp=150, attack=24,
                         math_topic=MathTopic.FRACTIONS, difficulty=4)


MAGE_SPRITES = {
    "idle": [
        [
            ".....M......",
            "....MMM.....",
            "...MMMMM....",
            "..MMMMMMM...",
            "...LLLLL....",
            "...LKMLK....",
            "...LLLLL....",
            "..MMMMMMM...",
            ".MLMMMMMLM..",
            "..MMMMMMM...",
            "..MM...MM...",
        ],
        [
            ".....M......",
            "....MMM.....",
            "...MMMMM....",
            "..MMMMMMM...",
            "...LLLLL....",
            "...LKMLK....",
            "...LLLLL....",
            "..MMMMMMM...",
            ".MLMMMMMLM..",
            "..MMMMMMM...",
            "..MM...MM...",
        ],
    ],
    "hurt": [
        [
            ".....M......",
            "....MMM.....",
            "...MMMMM....",
            "..MMMMMMM...",
            "...LRLRL....",
            "...LKMLK....",
            "...LLLLL....",
            "..MMMMMMM...",
            ".MLMMMMMLM..",
            "..MMMMMMM...",
            "..MM...MM...",
        ],
    ],
}


class Mage(Enemy):
    SPRITES = MAGE_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Mago", hp=140, attack=26,
                         math_topic=MathTopic.FRACTIONS, difficulty=5)


HYDRA_HEAD = [
    "..GGGG..",
    ".GGGGGG.",
    ".GWGGWG.",
    ".GKGGKG.",
    ".GGggGG.",
    "..GGGG..",
]
HYDRA_NECK = [
    "..GG..",
    "..GG..",
    "..GG..",
]
HYDRA_BODY = [
    ".GGGGGGGGGG.",
    "GGGGGGGGGGGG",
    "GGgGGGGGGgGG",
    ".GGGGGGGGGG.",
]

HYDRA_SPRITES = {
    "idle": [
        [
            ".GGGG....GGGG....GGGG.",
            ".GGGGGG..GGGGGG..GGGGGG",
            ".GWGGWG..GWGGWG..GWGGWG",
            ".GKGGKG..GKGGKG..GKGGKG",
            "..GGGG....GGGG....GGGG.",
            "..GG......GG......GG...",
            "..GG......GG......GG...",
            ".GGGGGGGGGGGGGGGGGGGGG.",
            "GGGGGGGGGGGGGGGGGGGGGGG",
            "GGgGGGGGGGGGGGGGGGGgGGG",
            ".GGGGGGGGGGGGGGGGGGGGG.",
            "..GG..GG......GG..GG...",
        ],
        [
            ".GGGG....GGGG....GGGG.",
            ".GGGGGG..GGGGGG..GGGGGG",
            ".GWGGWG..GWGGWG..GWGGWG",
            ".GKGGKG..GKGGKG..GKGGKG",
            "..GGGG....GGGG....GGGG.",
            "..GG......GG......GG...",
            "..GG......GG......GG...",
            ".GGGGGGGGGGGGGGGGGGGGG.",
            "GGGGGGGGGGGGGGGGGGGGGGG",
            "GGgGGGGGGGGGGGGGGGGgGGG",
            ".GGGGGGGGGGGGGGGGGGGGG.",
            "...GG..GG..GG..GG......",
        ],
    ],
    "hurt": [
        [
            ".GGGG....GGGG....GGGG.",
            ".GGGGGG..GGGGGG..GGGGGG",
            ".GRGGWG..GWGRWG..GWGGWR",
            ".GKGGKG..GKGGKG..GKGGKG",
            "..GGGG....GGGG....GGGG.",
            "..GG......GG......GG...",
            "..GG......GG......GG...",
            ".GGGGGGGGGGGGGGGGGGGGG.",
            "GGGGGGGGGGGGGGGGGGGGGGG",
            "GGgGGGGGGGGGGGGGGGGgGGG",
            ".GGGGGGGGGGGGGGGGGGGGG.",
            "..GG..GG......GG..GG...",
        ],
    ],
}


class Hydra(Enemy):
    """BOSS del nivel 4."""
    SPRITES = HYDRA_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Hidra de 3 Cabezas", hp=280, attack=36,
                         math_topic=MathTopic.FRACTIONS, difficulty=5,
                         is_boss=True)
