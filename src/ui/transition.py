"""
transition.py — Transiciones temáticas con easing
==================================================

Transiciones mejoradas con game-juice:
- Easing curves (ease-in-out-cubic)
- Estilos temáticos por nivel
- Efectos de partículas durante la transición
- Variación visual según el contexto
"""

import math
import random

import pygame

from .. import config


def ease_in_out_cubic(t):
    """Curva de easing suave para transiciones naturales."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


class Transition:
    """Transición temática con easing y efectos visuales."""

    FADE_IN = 0
    OUT = 1
    DONE = 2

    def __init__(self, duration=0.5, style="default"):
        """Crea una transición apagada (duration en segundos)."""
        self.duration = duration
        self.style = style
        self.phase = self.DONE
        self.alpha = 0
        self.progress = 0.0
        self.callback = None
        self.particles = []

    def start(self, callback, style=None):
        """Arranca el fundido: `callback` se llama al llegar al negro
        (ahí es donde el juego cambia de pantalla)."""
        if style:
            self.style = style
        self.callback = callback
        self.phase = self.FADE_IN
        self.alpha = 0
        self.progress = 0.0
        self.particles = []
        self._spawn_transition_particles()

    def active(self) -> bool:
        """True mientras el fundido sigue en marcha."""
        return self.phase != self.DONE

    def _spawn_transition_particles(self):
        """Crea las partículas que revolotean durante el fundido."""
        for _ in range(20):
            self.particles.append({
                "x": random.randint(0, config.SCREEN_WIDTH),
                "y": random.randint(0, config.SCREEN_HEIGHT),
                "vx": random.uniform(-100, 100),
                "vy": random.uniform(-100, 100),
                "size": random.randint(2, 6),
                "life": random.uniform(0.3, 0.8),
                "max_life": random.uniform(0.3, 0.8),
            })

    def update(self, dt):
        """Un frame: primer medio tiempo oscureciendo, segundo claro."""
        if not self.active():
            return

        if self.phase == self.FADE_IN:
            self.progress += dt / (self.duration * 0.5)
            self.progress = min(1.0, self.progress)
            self.alpha = int(255 * ease_in_out_cubic(self.progress))

            if self.progress >= 1.0:
                self.alpha = 255
                if self.callback:
                    self.callback()
                    self.callback = None
                self.phase = self.OUT
                self.progress = 0.0
        else:
            self.progress += dt / (self.duration * 0.5)
            self.progress = min(1.0, self.progress)
            self.alpha = int(255 * (1 - ease_in_out_cubic(self.progress)))

            if self.progress >= 1.0:
                self.alpha = 0
                self.phase = self.DONE

        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]

    def render(self, screen):
        """Dibuja el velo de color (y sus partículas) sobre la pantalla."""
        if self.alpha <= 0:
            return

        color = self._get_transition_color()
        veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        veil.fill((*color, self.alpha))
        screen.blit(veil, (0, 0))

        for p in self.particles:
            alpha = int(200 * (p["life"] / p["max_life"]))
            particle_color = (*color, alpha)
            pygame.draw.rect(screen, particle_color,
                           (int(p["x"]), int(p["y"]), p["size"], p["size"]))

    def _get_transition_color(self):
        """Color del velo: uno por nivel (verde, cian, púrpura...)."""
        color_map = {
            1: config.GREEN,
            2: config.CYAN,
            3: config.PURPLE,
            4: config.DARK_GREEN,
            5: config.RED,
        }
        if isinstance(self.style, int):
            return color_map.get(self.style, config.BLACK)
        return config.BLACK
