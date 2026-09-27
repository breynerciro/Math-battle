"""
level2_enemies.py — Cueva de Ecuaciones (Nivel 2)
=================================================

Tema matemático: ecuaciones lineales (ax + b = c)
Enemigos: Esqueleto → Bruja → Boss: Gólem de Piedra
"""

from ..enemy import Enemy
from ..sprites import PALETTE_GREEN
from ...math_engine.challenge import MathTopic

SKELETON_SPRITES = {
    "idle": [
        [
            "...WWWWW....",
            "..WWWWWWW...",
            "..WKWWWKW...",
            "..WWWWWWW...",
            "...W.W.W....",
            "....WWW.....",
            "...WWWWW....",
            "..W.WWW.W...",
            "..W.WWW.W...",
            "....W.W.....",
            "....W.W.....",
        ],
        [
            "...WWWWW....",
            "..WWWWWWW...",
            "..WKWWWKW...",
            "..WWWWWWW...",
            "...W.W.W....",
            "....WWW.....",
            "...WWWWW....",
            "..W.WWW.W...",
            "..W.WWW.W...",
            "...W..W.....",
            "...W..W.....",
        ],
    ],
    "hurt": [
        [
            "...WWWWW....",
            "..WRWWWWW...",
            "..WKWWWKW...",
            "..WWWWWWW...",
            "...W.W.W....",
            "....WWW.....",
            "...WWWWW....",
            "..W.WWW.W...",
            "..W.WWW.W...",
            "....W.W.....",
            "....W.W.....",
        ],
    ],
}


class Skeleton(Enemy):
    SPRITES = SKELETON_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Esqueleto", hp=80, attack=16,
                         math_topic=MathTopic.EQUATIONS, difficulty=2)


WITCH_SPRITES = {
    "idle": [
        [
            ".....P......",
            "....PPP.....",
            "...PPPPP....",
            "..PPPPPPP...",
            "...LLLLL....",
            "...LKPKL....",
            "...LLLLL....",
            "..PPPPPPP...",
            ".PLPPPPPLP..",
            "..PPPPPPP...",
            "..PP...PP...",
        ],
        [
            ".....P......",
            "....PPP.....",
            "...PPPPP....",
            "..PPPPPPP...",
            "...LLLLL....",
            "...LKPKL....",
            "...LLLLL....",
            "..PPPPPPP...",
            ".PLPPPPPLP..",
            "..PPPPPPP...",
            "..PP...PP...",
        ],
    ],
    "hurt": [
        [
            ".....P......",
            "....PPP.....",
            "...PPPPP....",
            "..PPPPPPP...",
            "...LRLRL....",
            "...LKPKL....",
            "...LLLLL....",
            "..PPPPPPP...",
            ".PLPPPPPLP..",
            "..PPPPPPP...",
            "..PP...PP...",
        ],
    ],
}


class Witch(Enemy):
    SPRITES = WITCH_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Bruja", hp=100, attack=18,
                         math_topic=MathTopic.EQUATIONS, difficulty=3)


GOLEM_SPRITES = {
    "idle": [
        [
            "..TTTTTTTT..",
            ".TTTTTTTTTT.",
            ".TTWTTTTWTT.",
            ".TTKTTTTKTT.",
            ".TTTTggTTTT.",
            "TTTTTTTTTTTT",
            "TTTTTTTTTTTT",
            "TT.TTTTTT.TT",
            "TT.TTTTTT.TT",
            "TT..TT.TT.TT",
            "....TT..TT..",
        ],
        [
            "..TTTTTTTT..",
            ".TTTTTTTTTT.",
            ".TTWTTTTWTT.",
            ".TTKTTTTKTT.",
            ".TTTTggTTTT.",
            "TTTTTTTTTTTT",
            "TTTTTTTTTTTT",
            "TT.TTTTTT.TT",
            "TT.TTTTTT.TT",
            ".TT.TT.TT.TT",
            "...TT..TT...",
        ],
    ],
    "hurt": [
        [
            "..TTTTTTTT..",
            ".TTRTTTTRTT.",
            ".TTWTTTTWTT.",
            ".TTKTTTTKTT.",
            ".TTTTggTTTT.",
            "TTTTTTTTTTTT",
            "TTTTTTTTTTTT",
            "TT.TTTTTT.TT",
            "TT.TTTTTT.TT",
            "TT..TT.TT.TT",
            "....TT..TT..",
        ],
    ],
}


class StoneGolem(Enemy):
    """BOSS del nivel 2."""
    SPRITES = GOLEM_SPRITES
    PALETTE = PALETTE_GREEN

    def __init__(self):
        super().__init__("Gólem de Piedra", hp=180, attack=28,
                         math_topic=MathTopic.EQUATIONS, difficulty=4,
                         is_boss=True)
