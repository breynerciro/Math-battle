"""
animated_sprite.py — Sprites animados sin archivos de imagen
============================================================

Los sprites de Math Battle se DIBUJAN CON CÓDIGO (rects de colores
en una cuadrícula, como el pixel art de verdad). Esta clase:

1. Recibe una LISTA DE FRAMES, donde cada frame es una "cuadrícula"
   (lista de strings) donde cada carácter es un color.
2. Convierte cada cuadrícula en una Surface de Pygame (con cache).
3. Reproduce los frames en secuencia a los FPS de animación indicados.

Ejemplo de cuadrícula (un slime de 8x6 píxeles):
    [
        "........",
        "..GGGG..",
        ".GGGGGG.",
        ".GWGGWG.",     ← W = blanco (ojos)
        ".GGGGGG.",
        ".GGGGGG.",
    ]

La tabla de colores se pasa aparte: {"G": VERDE, "W": BLANCO, ...}
"""

import pygame


class AnimatedSprite:
    """Reproduce una animación hecha de cuadrículas de caracteres."""

    # Cache global: no volver a dibujar una cuadrícula idéntica
    _cache = {}

    def __init__(self, frames, palette, pixel_size=6, fps=6, loop=True):
        """
        Args:
            frames:      lista de cuadrículas (cada una = lista de strings)
            palette:     dict carácter → color (R,G,B)
            pixel_size:  tamaño en pantalla de cada "píxel" del dibujo
            fps:         frames por segundo de la animación
            loop:        ¿repetir en bucle? (False para animaciones de golpe)
        """
        self.pixel_size = pixel_size
        self.fps = max(1, fps)
        self.loop = loop
        self.surfaces = [self._build(f, palette) for f in frames]
        self.frame_index = 0
        self.timer = 0.0
        self.finished = not self.loop and len(self.surfaces) <= 1

    # ------------------------------------------------------------------ #
    @classmethod
    def _build(cls, grid, palette):
        """Convierte una cuadrícula de caracteres en una Surface de Pygame."""
        key = (tuple(grid), tuple(sorted(palette.items())))
        if key in cls._cache:
            return cls._cache[key]

        h = len(grid)
        w = max(len(row) for row in grid)
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        for y, row in enumerate(grid):
            for x, char in enumerate(row):
                if char != "." and char in palette:
                    surface.set_at((x, y), palette[char])
        cls._cache[key] = surface
        return surface

    # ------------------------------------------------------------------ #
    def height_px(self):
        """Altura en pantalla del frame actual (píxeles del dibujo × pixel_size)."""
        return self.surfaces[self.frame_index].get_height() * self.pixel_size

    def scale(self):
        """Devuelve el frame actual escalado al pixel_size, con bordes nítidos."""
        surf = self.surfaces[self.frame_index]
        w = surf.get_width() * self.pixel_size
        h = surf.get_height() * self.pixel_size
        return pygame.transform.scale(surf, (w, h))

    def update(self, dt):
        """Avanza la animación según el tiempo transcurrido."""
        if self.finished or len(self.surfaces) <= 1:
            return
        self.timer += dt
        frame_time = 1.0 / self.fps
        while self.timer >= frame_time:
            self.timer -= frame_time
            self.frame_index += 1
            if self.frame_index >= len(self.surfaces):
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.surfaces) - 1
                    self.finished = True

    def render(self, screen, x, y, center=True):
        """Dibuja el frame actual. Si center=True, (x, y) es el centro."""
        img = self.scale()
        rect = img.get_rect()
        rect.center = (x, y) if center else (x, y)
        screen.blit(img, rect)

    def reset(self):
        """Reinicia la animación desde el primer frame."""
        self.frame_index = 0
        self.timer = 0.0
        self.finished = not self.loop and len(self.surfaces) <= 1
