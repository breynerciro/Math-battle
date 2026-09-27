"""
level1_enemies.py — Bosque Aritmético (Nivel 1)
===============================================

Tema matemático: operaciones básicas (+, −, ×, ÷)
Enemigos: Slime → Goblin → Boss: Dragón Básico

Los sprites viven en assets/sprites/enemies/<nombre>/ (por convención,
el nombre de la clase en snake_case: Slime → slime). Esta capa solo
define las ESTADÍSTICAS de cada enemigo.
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class Slime(Enemy):
    """Enemigo débil del primer nivel."""

    def __init__(self) -> None:
        super().__init__("Slime", hp=40, attack=10,
                         math_topic=MathTopic.OPERATIONS, difficulty=1)


class Goblin(Enemy):
    def __init__(self) -> None:
        super().__init__("Goblin", hp=60, attack=14,
                         math_topic=MathTopic.OPERATIONS, difficulty=2)


class BasicDragon(Enemy):
    """BOSS del nivel 1."""

    def __init__(self) -> None:
        super().__init__("Dragón Básico", hp=120, attack=22,
                         math_topic=MathTopic.OPERATIONS, difficulty=3,
                         is_boss=True)
