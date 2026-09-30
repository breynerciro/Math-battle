"""
level3_enemies.py — El Templo de las Fracciones (Nivel 3)
=========================================================

Tema matemático: operaciones con fracciones
Enemigos: Demonio Menor → Fénix → BOSS: Golem de Piedra Rúnica (HP 120)
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class LesserDemon(Enemy):
    """Demonio Menor: 80 HP, guarda el templo azul."""

    def __init__(self) -> None:
        """Demonio Menor: 80 HP, retos de fracciones con dificultad 3."""
        super().__init__("Demonio Menor", hp=80, attack=20,
                         math_topic=MathTopic.FRACCIONES, difficulty=3)


class Phoenix(Enemy):
    """Fénix: 95 HP, renace de las cenizas y de las fracciones."""

    def __init__(self) -> None:
        """Fénix: 95 HP, retos de fracciones con dificultad 3."""
        super().__init__("Fénix", hp=95, attack=24,
                         math_topic=MathTopic.FRACCIONES, difficulty=3)


class GolemRunico(Enemy):
    """BOSS del nivel 3: el Golem de Piedra Rúnica (HP 120)."""

    SPRITE_NAME = "stone_golem"

    def __init__(self) -> None:
        """Golem Rúnico: 120 HP, jefe del nivel 3 (diseño del juego)."""
        super().__init__("Golem de Piedra Rúnica", hp=120, attack=30,
                         math_topic=MathTopic.FRACCIONES, difficulty=4,
                         is_boss=True)
