"""
background.py — Fondos de batalla (imágenes PNG)
================================================

Los fondos se GENERAN UNA VEZ con tools/generate_sprites.py y quedan
guardados como PNG en assets/backgrounds/level<N>.png. Aquí solo se
CARGAN (con cache: una vez por nivel y por sesión).

Para personalizar un fondo, reemplaza su PNG (960x540) o edita la
receta en tools/art_backgrounds.py y regenera con
tools/generate_sprites.py.
"""

from pathlib import Path

import pygame

from .. import config

BACKGROUNDS_DIR = Path(config.BACKGROUNDS_DIR)

# Cache: el fondo de cada nivel se carga una sola vez
_cache: dict[int, pygame.Surface] = {}


def get_background(level: int) -> pygame.Surface:
    """Devuelve el fondo PNG del nivel, ya escalado a la ventana.

    Los PNG se generan a 960x540 (escala entera del lienzo de 480x270);
    aquí se reescalan una sola vez a la resolución real del juego y se
    cachean, de modo que el blit de cada frame es directo.
    """
    if level not in _cache:
        png_path = BACKGROUNDS_DIR / f"level{level}.png"
        if png_path.exists():
            image = pygame.image.load(str(png_path)).convert()
            size = (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
            if image.get_size() != size:
                image = pygame.transform.smoothscale(image, size)
            _cache[level] = image
        else:
            _cache[level] = _emergency_background(level)
    return _cache[level]


def _emergency_background(level: int) -> pygame.Surface:
    """Fondo plano de respaldo si falta el PNG (llano, sin detalles)."""
    surface = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    base_color = config.LEVEL_COLORS.get(level, config.DARK_BLUE)
    surface.fill(base_color)
    ground_color = tuple(max(0, channel - 30) for channel in base_color)
    pygame.draw.rect(surface, ground_color,
                     (0, config.GROUND_Y, config.SCREEN_WIDTH,
                      config.SCREEN_HEIGHT - config.GROUND_Y))
    return surface
