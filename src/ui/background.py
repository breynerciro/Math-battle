"""
background.py — Fondos de batalla por nivel (dibujados con código)
==================================================================

Cada nivel tiene un fondo simple pero atmosférico: colores planos,
siluetas y detalles pixelados. Se genera UNA vez y se cachea.
"""

import random

import pygame

from .. import config


def _build_background(level: int) -> pygame.Surface:
    """Construye el fondo pixel art del nivel indicado."""
    surf = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    rng = random.Random(level * 1000)     # semilla fija: mismo fondo siempre

    base = config.LEVEL_COLORS.get(level, config.DARK_BLUE)
    surf.fill(base)

    # Franja de suelo (donde "pisan" los personajes)
    ground_y = config.GROUND_Y
    ground = tuple(max(0, c - 30) for c in base)
    pygame.draw.rect(surf, ground, (0, ground_y, config.SCREEN_WIDTH,
                                    config.SCREEN_HEIGHT - ground_y))
    # Línea del horizonte
    pygame.draw.line(surf, config.BLACK, (0, ground_y),
                     (config.SCREEN_WIDTH, ground_y), 3)

    # Detalles por nivel (siluetas decorativas)
    detail = tuple(max(0, c - 55) for c in base)
    light = tuple(min(255, c + 25) for c in base)

    if level == 1:      # Bosque: árboles triangulares
        for _ in range(14):
            x = rng.randint(0, config.SCREEN_WIDTH - 40)
            h = rng.randint(60, 130)
            w = rng.randint(30, 50)
            y = ground_y - h
            pygame.draw.polygon(surf, detail,
                                [(x + w // 2, y), (x, y + h), (x + w, y + h)])
            pygame.draw.rect(surf, (90, 60, 30),
                             (x + w // 2 - 4, ground_y - 12, 8, 12))
    elif level == 2:    # Cueva: estalactitas y cristales
        for x in range(0, config.SCREEN_WIDTH, 30):
            h = rng.randint(20, 70)
            pygame.draw.polygon(surf, detail,
                                [(x, 0), (x + 30, 0), (x + 15, h)])
        for _ in range(10):
            x = rng.randint(20, config.SCREEN_WIDTH - 20)
            h = rng.randint(25, 60)
            pygame.draw.polygon(surf, config.CYAN,
                                [(x, ground_y), (x - 8, ground_y - h),
                                 (x + 8, ground_y - h)])
    elif level == 3:    # Torre: ventanas con "nubes"
        for wx in range(80, config.SCREEN_WIDTH, 180):
            for wy in range(60, ground_y - 60, 120):
                pygame.draw.rect(surf, detail, (wx, wy, 46, 66), border_radius=6)
                pygame.draw.rect(surf, config.YELLOW, (wx + 10, wy + 16, 26, 34),
                                 border_radius=6)
        for _ in range(6):
            x = rng.randint(0, config.SCREEN_WIDTH - 120)
            y = rng.randint(30, 160)
            pygame.draw.ellipse(surf, light, (x, y, 120, 34))
    elif level == 4:    # Pantano: burbujas y juncos
        for _ in range(22):
            x = rng.randint(0, config.SCREEN_WIDTH)
            y = rng.randint(ground_y + 8, config.SCREEN_HEIGHT - 10)
            r = rng.randint(3, 7)
            pygame.draw.circle(surf, light, (x, y), r, 2)
        for _ in range(16):
            x = rng.randint(0, config.SCREEN_WIDTH - 6)
            h = rng.randint(30, 80)
            pygame.draw.line(surf, detail, (x, ground_y), (x + rng.randint(-8, 8),
                                                           ground_y - h), 4)
    else:               # Fortaleza: almenas y banderas
        pygame.draw.rect(surf, detail,
                         (0, ground_y - 150, config.SCREEN_WIDTH, 150))
        for x in range(0, config.SCREEN_WIDTH, 60):
            pygame.draw.rect(surf, detail, (x, ground_y - 180, 36, 36))
        for _ in range(5):
            x = rng.randint(40, config.SCREEN_WIDTH - 40)
            pygame.draw.line(surf, config.DARK_GRAY, (x, ground_y - 150),
                             (x, ground_y - 210), 3)
            pygame.draw.polygon(surf, config.RED,
                                [(x, ground_y - 210), (x + 26, ground_y - 202),
                                 (x, ground_y - 194)])
    return surf


# Cache: el fondo de cada nivel se construye una sola vez
_cache = {}


def get_background(level: int) -> pygame.Surface:
    """Devuelve el fondo del nivel (construido y guardado en cache)."""
    if level not in _cache:
        _cache[level] = _build_background(level)
    return _cache[level]
