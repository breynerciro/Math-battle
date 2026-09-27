"""
level3_enemies.py — Torre de Potencias (Nivel 3)
================================================

Tema matemático: potencias y raíces
Enemigos: Fantasma → Demonio Menor → Boss: Fénix
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class Ghost(Enemy):
    def __init__(self) -> None:
        super().__init__("Fantasma", hp=110, attack=20,
                         math_topic=MathTopic.POWERS_ROOTS, difficulty=3)


class LesserDemon(Enemy):
    def __init__(self) -> None:
        super().__init__("Demonio Menor", hp=130, attack=22,
                         math_topic=MathTopic.POWERS_ROOTS, difficulty=4)


class Phoenix(Enemy):
    """BOSS del nivel 3."""

    def __init__(self) -> None:
        super().__init__("Fénix", hp=220, attack=32,
                         math_topic=MathTopic.POWERS_ROOTS, difficulty=5,
                         is_boss=True)
