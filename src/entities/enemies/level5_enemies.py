"""
level5_enemies.py — Fortaleza Geométrica (Nivel 5)
==================================================

Tema matemático: geometría (áreas, perímetros, ángulos)
Enemigos: Sombra → Archimago → Boss: Dragón Supremo
"""

from ..enemy import Enemy
from ..sprites import PALETTE_GREEN
from ...math_engine.challenge import MathTopic

SHADOW_SPRITES = {
    "idle": [
        [
            "...UUUUU....",
            "..UUUUUUU...",
            ".UUWUUWUUU..",
            ".UUUUUUUUU..",
            ".UUUUUUUUU..",
            "..UUUUUUU...",
            ".U.UUUUU.U..",
            "..U.U.U.U...",
        ],
        [
            "............",
            "...UUUUU....",
            "..UWUUWUUU..",
            ".UUUUUUUUU..",
            ".UUUUUUUUU..",
            "..UUUUUUU...",
            ".U.UUUUU.U..",
            "..U.U.U.U...",
        ],
    ],
    "hurt": [
        [
            "...UUUUU....",
            "..URUUUUU...",
            ".UUWUUWUUU..",
            ".UUUUUUUUU..",
            ".UUUUUUUUU..",
            "..UUUUUUU...",
            ".U.UUUUU.U..",
            "..U.U.U.U...",
        ],
    ],
}


class Shadow(Enemy):
    SPRITES = SHADOW_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Sombra", hp=170, attack=28,
                         math_topic=MathTopic.GEOMETRY, difficulty=5)


ARCHMAGE_SPRITES = {
    "idle": [
        [
            ".....M......",
            "....MMM.....",
            "...MMMMM....",
            "..MMMMMMM...",
            "...LWLLL....",
            "...LKMLK....",
            "...LLLLL....",
            "..MMMMMMM...",
            ".MLMCCCMLM..",
            "..MMMMMMM...",
            "..MM...MM...",
        ],
        [
            ".....M......",
            "....MMM.....",
            "...MMMMM....",
            "..MMMMMMM...",
            "...LWLLL....",
            "...LKMLK....",
            "...LLLLL....",
            "..MMMMMMM...",
            ".MLMCCCMLM..",
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
            "...LRWLL....",
            "...LKMLK....",
            "...LLLLL....",
            "..MMMMMMM...",
            ".MLMCCCMLM..",
            "..MMMMMMM...",
            "..MM...MM...",
        ],
    ],
}


class Archmage(Enemy):
    SPRITES = ARCHMAGE_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Archimago", hp=190, attack=30,
                         math_topic=MathTopic.GEOMETRY, difficulty=5)


SUPREME_DRAGON_SPRITES = {
    "idle": [
        [
            "..X.....X...",
            "..XX...XX...",
            "..XXX.XXX...",
            "...XXXXX....",
            "..XXWFWXX...",
            "..XXKFKXX...",
            "..XXXXXXX.Y.",
            ".XXXXCCCX.Y.",
            "XXXXCCCEXXY.",
            ".XX.XX.XX...",
            "..X..X..X...",
        ],
        [
            "..X.....X...",
            "..XX...XX...",
            "..XXX.XXX...",
            "...XXXXX....",
            "..XXWFWXX...",
            "..XXKFKXX...",
            "..XXXXXXX..Y",
            ".XXXXCCCX..Y",
            "XXXXCCCEXX.Y",
            ".XX.XX.XX...",
            "..X..X..X...",
        ],
    ],
    "hurt": [
        [
            "..X.....X...",
            "..XX...XX...",
            "..XXX.XXX...",
            "...XWFWX....",
            "..XWFFFWXX..",
            "..XXKFKXX...",
            "..XXXXXXX.Y.",
            ".XXXXCCCX.Y.",
            "XXXXCCCEXXY.",
            ".XX.XX.XX...",
            "..X..X..X...",
        ],
    ],
}


class SupremeDragon(Enemy):
    """BOSS FINAL del juego."""
    SPRITES = SUPREME_DRAGON_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Dragón Supremo", hp=350, attack=45,
                         math_topic=MathTopic.GEOMETRY, difficulty=5,
                         is_boss=True)
