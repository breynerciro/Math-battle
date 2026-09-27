"""
Registro de enemigos por nivel
==============================

get_level_enemies(level) devuelve la lista de enemigos del nivel,
EN ORDEN: primero los normales y AL FINAL el boss.

Cada entrada es una CLASE (no una instancia): así cada vez que se
reintenta un nivel se crean enemigos frescos con toda su vida.
"""

from .level1_enemies import Slime, Goblin, BasicDragon
from .level2_enemies import Skeleton, Witch, StoneGolem
from .level3_enemies import Ghost, LesserDemon, Phoenix
from .level4_enemies import DarkKnight, Mage, Hydra
from .level5_enemies import Shadow, Archmage, SupremeDragon

LEVEL_ENEMIES = {
    1: [Slime, Goblin, BasicDragon],
    2: [Skeleton, Witch, StoneGolem],
    3: [Ghost, LesserDemon, Phoenix],
    4: [DarkKnight, Mage, Hydra],
    5: [Shadow, Archmage, SupremeDragon],
}


def get_level_enemies(level: int):
    """Lista de INSTANCIAS frescas de los enemigos del nivel (boss al final)."""
    classes = LEVEL_ENEMIES.get(level, LEVEL_ENEMIES[1])
    return [cls() for cls in classes]
