"""
sprites.py — Carga de los sprites del juego
===========================================

Todos los personajes viven como PNG en assets/sprites/:

    assets/sprites/hero/<animación>/frame<N>.png
    assets/sprites/enemies/<enemigo>/<animación>/frame<N>.png
    assets/sprites/effects/star/frame<N>.png

Este archivo solo SABE DÓNDE están y cómo cargarlos. Para cambiar el
aspecto del juego:

1. Reemplaza los PNG (mismo nombre de archivo), o
2. Edita las cuadrículas de tools/sprite_data.py y regenera:

       ./venv/bin/python tools/generate_sprites.py

¿Pixel art propio? Exporta cada frame como frame0.png, frame1.png...
(resolución libre: el PNG se dibuja tal cual en pantalla).
"""

from pathlib import Path

from .. import config
from ..ui.animated_sprite import AnimatedSprite


def to_snake(class_name: str) -> str:
    """BasicDragon → basic_dragon (nombre de carpeta del sprite)."""
    result = []
    for index, char in enumerate(class_name):
        if char.isupper() and index > 0:
            result.append("_")
        result.append(char.lower())
    return "".join(result)


# Carpetas de sprites (definidas en config.py)
HERO_DIR = Path(config.SPRITES_DIR) / "hero"
ENEMIES_DIR = Path(config.SPRITES_DIR) / "enemies"
EFFECTS_DIR = Path(config.SPRITES_DIR) / "effects"

# Especificación de animaciones: nombre → (fps, ¿se repite en bucle?)
HERO_ANIM_SPECS: dict[str, tuple[float, bool]] = {
    "idle": (4.0, True),
    "attack": (12.0, False),
    "hurt": (10.0, False),
    "victory": (6.0, True),
}

ENEMY_ANIM_SPECS: dict[str, tuple[float, bool]] = {
    "idle": (3.0, True),
    "hurt": (10.0, False),
}

HIT_STAR_FPS = 18.0


def load_entity(base_dir: Path,
                specs: dict[str, tuple[float, bool]],
                fallback_dir: Path | None = None) -> dict:
    """Carga las animaciones de una entidad según su especificación.

    Args:
        base_dir:     carpeta con una subcarpeta por animación
        specs:        {nombre_animación: (fps, ¿bucle?)}
        fallback_dir: carpeta a usar si base_dir no existe (respaldo)
    """
    if fallback_dir is not None and not base_dir.exists():
        base_dir = fallback_dir
    return {
        anim_name: AnimatedSprite.load(base_dir / anim_name,
                                       fps=fps, loop=loop)
        for anim_name, (fps, loop) in specs.items()
    }
