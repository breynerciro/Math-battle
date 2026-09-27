"""
level5_enemies.py — Fortaleza Geométrica (Nivel 5)
==================================================

Tema matemático: geometría (áreas, perímetros, ángulos)
Enemigos: Sombra → Archimago → Boss final: Dragón Supremo
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class Shadow(Enemy):
    def __init__(self) -> None:
        super().__init__("Sombra", hp=170, attack=28,
                         math_topic=MathTopic.GEOMETRY, difficulty=5)


class Archmage(Enemy):
    def __init__(self) -> None:
        super().__init__("Archimago", hp=190, attack=30,
                         math_topic=MathTopic.GEOMETRY, difficulty=5)


class SupremeDragon(Enemy):
    """BOSS FINAL del juego."""

    def __init__(self) -> None:
        super().__init__("Dragón Supremo", hp=350, attack=45,
                         math_topic=MathTopic.GEOMETRY, difficulty=5,
                         is_boss=True)
