"""
level1_enemies.py — El Bosque de las Sumas (Nivel 1)
====================================================

Tema matemático: sumas y restas básicas
Enemigos: Goblin → Skeleton → BOSS: Slime Matemático (HP 40)

Los sprites viven en assets/sprites/enemies/<nombre>/ (por convención,
el nombre de la clase en snake_case: Goblin → goblin; los bosses con
nombre propio fijan SPRITE_NAME). Esta capa solo define las
ESTADÍSTICAS de cada enemigo.
"""

from ...math_engine.challenge import MathTopic
from ..enemy import Enemy


class Goblin(Enemy):
    """Explorador del bosque: insiste hasta que fallas una resta."""

    def __init__(self) -> None:
        super().__init__("Goblin", hp=30, attack=10,
                         math_topic=MathTopic.SUMAS, difficulty=1)


class Skeleton(Enemy):
    def __init__(self) -> None:
        super().__init__("Esqueleto", hp=35, attack=12,
                         math_topic=MathTopic.SUMAS, difficulty=2)


class SlimeMatematico(Enemy):
    """BOSS del nivel 1: el Slime Matemático (HP 40, como manda el diseño)."""

    SPRITE_NAME = "slime"

    def __init__(self) -> None:
        super().__init__("Slime Matemático", hp=40, attack=16,
                         math_topic=MathTopic.SUMAS, difficulty=2,
                         is_boss=True)
