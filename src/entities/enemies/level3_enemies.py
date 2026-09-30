"""
level3_enemies.py — El Templo de las Fracciones (Nivel 3)
=========================================================

Tema matemático: operaciones con fracciones
Enemigos: Demonio Menor → Fénix → BOSS: Golem de Piedra Rúnica (HP 120)
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class LesserDemon(Enemy):
    def __init__(self) -> None:
        super().__init__("Demonio Menor", hp=80, attack=20,
                         math_topic=MathTopic.FRACCIONES, difficulty=3)


class Phoenix(Enemy):
    def __init__(self) -> None:
        super().__init__("Fénix", hp=95, attack=24,
                         math_topic=MathTopic.FRACCIONES, difficulty=3)


class GolemRunico(Enemy):
    """BOSS del nivel 3: el Golem de Piedra Rúnica (HP 120)."""

    SPRITE_NAME = "stone_golem"

    def __init__(self) -> None:
        super().__init__("Golem de Piedra Rúnica", hp=120, attack=30,
                         math_topic=MathTopic.FRACCIONES, difficulty=4,
                         is_boss=True)
