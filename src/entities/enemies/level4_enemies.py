"""
level4_enemies.py — El Puente Hacia el Caos (Nivel 4)
======================================================

Tema matemático: geometría básica (perímetros, áreas) y ecuaciones
de primer grado (x − 15 = 30)
Enemigos: Caballero Oscuro → Hidra → BOSS: Maestro de la Geometría (HP 180)
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class DarkKnight(Enemy):
    """Caballero Oscuro: 115 HP, patrulla el puente."""

    def __init__(self) -> None:
        """Caballero Oscuro: 115 HP, geometría con dificultad 3."""
        super().__init__("Caballero Oscuro", hp=115, attack=24,
                         math_topic=MathTopic.GEOMETRIA, difficulty=3)


class Hydra(Enemy):
    """Hidra: 140 HP, tres cabezas y tres ecuaciones por turno."""

    def __init__(self) -> None:
        """Hidra: 140 HP, geometría y ecuaciones con dificultad 3."""
        super().__init__("Hidra", hp=140, attack=28,
                         math_topic=MathTopic.GEOMETRIA, difficulty=3)


class MaestroGeometria(Enemy):
    """BOSS del nivel 4: el Maestro de la Geometría (HP 180)."""

    SPRITE_NAME = "mage"

    def __init__(self) -> None:
        """Maestro de la Geometría: 180 HP, jefe del nivel 4 (diseño)."""
        super().__init__("Maestro de la Geometría", hp=180, attack=34,
                         math_topic=MathTopic.GEOMETRIA, difficulty=4,
                         is_boss=True)
