"""
level2_enemies.py — La Mina de la Multiplicación (Nivel 2)
==========================================================

Tema matemático: multiplicación, división y problemas de lógica
Enemigos: Bruja → Fantasma → BOSS: Duende Calculador (HP 80)
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class Witch(Enemy):
    """Bruja de la mina: 55 HP, te enreda con tablas de multiplicar."""

    def __init__(self) -> None:
        """Bruja: 55 HP, retos de ×, ÷ y lógica con dificultad 2."""
        super().__init__("Bruja", hp=55, attack=16,
                         math_topic=MathTopic.MULTIPLICACION, difficulty=2)


class Ghost(Enemy):
    """Fantasma de las galerías: 65 HP, aparece entre las sombras."""

    def __init__(self) -> None:
        """Fantasma: 65 HP, retos de ×, ÷ y lógica con dificultad 2."""
        super().__init__("Fantasma", hp=65, attack=18,
                         math_topic=MathTopic.MULTIPLICACION, difficulty=2)


class DuendeCalculador(Enemy):
    """BOSS del nivel 2: el Duende Calculador (HP 80)."""

    SPRITE_NAME = "goblin"

    def __init__(self) -> None:
        """Duende Calculador: 80 HP, jefe del nivel 2 (diseño del juego)."""
        super().__init__("Duende Calculador", hp=80, attack=24,
                         math_topic=MathTopic.MULTIPLICACION, difficulty=3,
                         is_boss=True)
