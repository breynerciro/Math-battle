"""
level3_enemies.py — Torre de Potencias (Nivel 3)
================================================

Tema matemático: potencias, raíces y notación científica
Enemigos: Fantasma → Demonio Menor → Boss: Fénix
"""

from ..enemy import Enemy
from ..sprites import PALETTE_GREEN
from ...math_engine.challenge import MathTopic

GHOST_SPRITES = {
    "idle": [
        [
            "...wwwww....",
            "..wwwwwww...",
            ".wwKwwwKww..",
            ".wwwwwwwww..",
            ".wwwwwwKww..",
            ".wwwwwwwww..",
            ".wwwwwwwww..",
            ".w.ww.ww.w..",
        ],
        [
            "............",
            "...wwwww....",
            "..wwKwwKww..",
            ".wwwwwwwww..",
            ".wwwwwwKww..",
            ".wwwwwwwww..",
            ".wwwwwwwww..",
            ".w.ww.ww.w..",
        ],
    ],
    "hurt": [
        [
            "...wwwww....",
            "..wRwwwww...",
            ".wwKwwwKww..",
            ".wwwwwwwww..",
            ".wwwwwwKww..",
            ".wwwwwwwww..",
            ".wwwwwwwww..",
            ".w.ww.ww.w..",
        ],
    ],
}


class Ghost(Enemy):
    SPRITES = GHOST_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Fantasma", hp=110, attack=20,
                         math_topic=MathTopic.POWERS_ROOTS, difficulty=3)


DEMON_SPRITES = {
    "idle": [
        [
            ".R.......R..",
            ".RR.....RR..",
            "..XXXXXXXX..",
            ".XXKXXXKXXX.",
            ".XXXXXXXXXX.",
            ".XXEXXXEXX..",
            "..XXXXXXXX..",
            "..XX.XX.XX..",
            "..XX.XX.XX..",
        ],
        [
            ".R.......R..",
            ".RR.....RR..",
            "..XXXXXXXX..",
            ".XXKXXXKXXX.",
            ".XXXXXXXXXX.",
            ".XXEXXXEXX..",
            "..XXXXXXXX..",
            "..XX.XX.XX..",
            "..XX.XX.XX..",
        ],
    ],
    "hurt": [
        [
            ".R.......R..",
            ".RR.....RR..",
            "..XRXXXXXX..",
            ".XXKXXXKXXX.",
            ".XXXXXXXXXX.",
            ".XXEXXXEXX..",
            "..XXXXXXXX..",
            "..XX.XX.XX..",
            "..XX.XX.XX..",
        ],
    ],
}


class LesserDemon(Enemy):
    SPRITES = DEMON_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Demonio Menor", hp=130, attack=22,
                         math_topic=MathTopic.POWERS_ROOTS, difficulty=4)


PHOENIX_SPRITES = {
    "idle": [
        [
            "....O..O....",
            "...OOOOOO...",
            "..OOFEEFOO..",
            ".OOFEEEEFOO.",
            "OFOEEYEEEOFO",
            ".OOFEEEEFOO.",
            "..OOFEEFOO..",
            "...OOOOOO...",
            "....O..O....",
        ],
        [
            "....O..O....",
            "...OOOOOO...",
            "..OOFEEFOO..",
            ".OOFEEEEFOO.",
            "OFOEEYEEEOFO",
            ".OOFEEEEFOO.",
            "..OOFEEFOO..",
            "...OOOOOO...",
            "...O....O...",
        ],
    ],
    "hurt": [
        [
            "....O..O....",
            "...OOOOOO...",
            "..OOFERFOO..",
            ".OOFEEEEFOO.",
            "OFOEEYEEEOFO",
            ".OOFEEEEFOO.",
            "..OOFEEFOO..",
            "...OOOOOO...",
            "....O..O....",
        ],
    ],
}


class Phoenix(Enemy):
    """BOSS del nivel 3."""
    SPRITES = PHOENIX_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Fénix", hp=220, attack=32,
                         math_topic=MathTopic.POWERS_ROOTS, difficulty=5,
                         is_boss=True)
