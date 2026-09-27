"""
level4_enemies.py — Pantano de Fracciones (Nivel 4)
===================================================

Tema matemático: fracciones
Enemigos: Caballero Oscuro → Mago → Boss: Hidra de 3 Cabezas
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class DarkKnight(Enemy):
    def __init__(self) -> None:
        super().__init__("Caballero Oscuro", hp=150, attack=24,
                         math_topic=MathTopic.FRACTIONS, difficulty=4)


class Mage(Enemy):
    def __init__(self) -> None:
        super().__init__("Mago", hp=140, attack=26,
                         math_topic=MathTopic.FRACTIONS, difficulty=5)


class Hydra(Enemy):
    """BOSS del nivel 4."""

    def __init__(self) -> None:
        super().__init__("Hidra de 3 Cabezas", hp=280, attack=36,
                         math_topic=MathTopic.FRACTIONS, difficulty=5,
                         is_boss=True)
