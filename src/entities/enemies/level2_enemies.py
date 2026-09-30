"""
level2_enemies.py — La Mina de la Multiplicación (Nivel 2)
==========================================================

Tema matemático: multiplicación, división y problemas de lógica
Enemigos: Bruja → Fantasma → BOSS: Duende Calculador (HP 80)
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class Witch(Enemy):
    def __init__(self) -> None:
        super().__init__("Bruja", hp=55, attack=16,
                         math_topic=MathTopic.MULTIPLICACION, difficulty=2)


class Ghost(Enemy):
    def __init__(self) -> None:
        super().__init__("Fantasma", hp=65, attack=18,
                         math_topic=MathTopic.MULTIPLICACION, difficulty=2)


class DuendeCalculador(Enemy):
    """BOSS del nivel 2: el Duende Calculador (HP 80)."""

    SPRITE_NAME = "goblin"

    def __init__(self) -> None:
        super().__init__("Duende Calculador", hp=80, attack=24,
                         math_topic=MathTopic.MULTIPLICACION, difficulty=3,
                         is_boss=True)
