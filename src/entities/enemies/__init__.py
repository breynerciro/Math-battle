"""
Registro de enemigos por nivel
==============================

get_level_enemies(level) devuelve la lista de enemigos del nivel,
EN ORDEN: primero los normales y AL FINAL el boss del diseño:

    Nivel 1  El Bosque de las Sumas        → Slime Matemático (40)
    Nivel 2  La Mina de la Multiplicación  → Duende Calculador (80)
    Nivel 3  El Templo de las Fracciones   → Golem Rúnico (120)
    Nivel 4  El Puente Hacia el Caos       → Maestro de la Geometría (180)
    Nivel 5  El Castillo del Caos          → Archimago del Caos (250)

Cada entrada es una CLASE (no una instancia): así cada vez que se
reintenta un nivel se crean enemigos frescos con toda su vida.
"""

from .level1_enemies import Goblin, Skeleton, SlimeMatematico
from .level2_enemies import DuendeCalculador, Witch, Ghost
from .level3_enemies import GolemRunico, LesserDemon, Phoenix
from .level4_enemies import DarkKnight, Hydra, MaestroGeometria
from .level5_enemies import ArchimagoCaos, Shadow, SupremeDragon

LEVEL_ENEMIES = {
    1: [Goblin, Skeleton, SlimeMatematico],
    2: [Witch, Ghost, DuendeCalculador],
    3: [LesserDemon, Phoenix, GolemRunico],
    4: [DarkKnight, Hydra, MaestroGeometria],
    5: [Shadow, SupremeDragon, ArchimagoCaos],
}


def get_level_enemies(level: int):
    """Lista de INSTANCIAS frescas de los enemigos del nivel (boss al final)."""
    classes = LEVEL_ENEMIES.get(level, LEVEL_ENEMIES[1])
    return [cls() for cls in classes]
