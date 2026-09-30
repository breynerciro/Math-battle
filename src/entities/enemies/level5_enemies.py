"""
level5_enemies.py — El Castillo del Caos (Nivel 5)
===================================================

Tema matemático: álgebra intermedia (4(x + 2) − 7 = 21, x a ambos lados)
Enemigos: Sombra → Dragón Supremo → BOSS: Archimago del Caos (HP 250)
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class Shadow(Enemy):
    """Sombra: 160 HP, se disuelve en ecuaciones difíciles."""

    def __init__(self) -> None:
        """Sombra: 160 HP, álgebra con dificultad 4."""
        super().__init__("Sombra", hp=160, attack=28,
                         math_topic=MathTopic.ALGEBRA, difficulty=4)


class SupremeDragon(Enemy):
    """Dragón Supremo: 200 HP, la última puerta antes del castillo."""

    def __init__(self) -> None:
        """Dragón Supremo: 200 HP, álgebra con dificultad 4."""
        super().__init__("Dragón Supremo", hp=200, attack=32,
                         math_topic=MathTopic.ALGEBRA, difficulty=4)


class ArchimagoCaos(Enemy):
    """BOSS final: el Archimago del Caos (HP 250)."""

    SPRITE_NAME = "archmage"

    def __init__(self) -> None:
        """Archimago del Caos: 250 HP, JEFE FINAL (diseño del juego)."""
        super().__init__("Archimago del Caos", hp=250, attack=40,
                         math_topic=MathTopic.ALGEBRA, difficulty=5,
                         is_boss=True)
