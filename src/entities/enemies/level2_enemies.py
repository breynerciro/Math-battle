"""
level2_enemies.py — Cueva de Ecuaciones (Nivel 2)
=================================================

Tema matemático: ecuaciones lineales (ax + b = c)
Enemigos: Esqueleto → Bruja → Boss: Gólem de Piedra
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class Skeleton(Enemy):
    def __init__(self) -> None:
        super().__init__("Esqueleto", hp=80, attack=16,
                         math_topic=MathTopic.EQUATIONS, difficulty=2)


class Witch(Enemy):
    def __init__(self) -> None:
        super().__init__("Bruja", hp=100, attack=18,
                         math_topic=MathTopic.EQUATIONS, difficulty=3)


class StoneGolem(Enemy):
    """BOSS del nivel 2."""

    def __init__(self) -> None:
        super().__init__("Gólem de Piedra", hp=180, attack=28,
                         math_topic=MathTopic.EQUATIONS, difficulty=4,
                         is_boss=True)
