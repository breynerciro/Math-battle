"""
effects.py — Efectos visuales de combate
========================================

Pequeños "adornos" que hacen que el combate se sienta vivo:

- FloatingText: números que suben y se desvanecen ("¡-25!", "+130")
- ScreenShake:  la pantalla tiembla al recibir un golpe
- Particles:    chispitas simples al atacar
"""

import math
import random

import pygame

from .. import config


class FloatingText:
    """Texto que flota hacia arriba y se desvanece."""

    def __init__(self, text, x, y, color=config.WHITE, size=None):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 1.0          # vida de 1.0 a 0.0
        self.font_size = size or config.FONT_SIZE_MEDIUM

    def update(self, dt):
        self.life -= dt * 0.9
        self.y -= 40 * dt        # sube 40 píxeles por segundo
        return self.life > 0

    def render(self, screen, font_getter):
        font = font_getter(self.font_size)
        surface = font.render(self.text, True, self.color)
        surface.set_alpha(int(255 * max(0, self.life)))
        rect = surface.get_rect(center=(self.x, self.y))
        screen.blit(surface, rect)


class ScreenShake:
    """Tiemblo de cámara. Uso: shake.trigger(0.3, 6) → 0.3s de intensidad 6px."""

    def __init__(self):
        self.time_left = 0.0
        self.duration = 0.0
        self.intensity = 0

    def trigger(self, duration=0.3, intensity=6):
        self.duration = duration
        self.time_left = duration
        self.intensity = intensity

    def update(self, dt):
        if self.time_left > 0:
            self.time_left -= dt

    def get_offset(self):
        """Desplazamiento (dx, dy) que se aplicará al dibujar todo."""
        if self.time_left <= 0:
            return 0, 0
        progress = self.time_left / self.duration      # 1 → 0
        current = self.intensity * progress
        return (random.randint(-int(current), int(current)),
                random.randint(-int(current), int(current)))


class ParticleSystem:
    """Chispitas que estallan desde un punto (al golpear o al morir)."""

    def __init__(self):
        self.particles = []       # [ [x, y, vx, vy, color, vida], ... ]

    def burst(self, x, y, color=config.YELLOW, count=14, speed=120):
        """Crea `count` partículas saliendo del punto (x, y)."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            v = random.uniform(speed * 0.4, speed)
            self.particles.append([
                x, y,
                math.cos(angle) * v, math.sin(angle) * v,
                color,
                random.uniform(0.4, 0.8),          # vida en segundos
            ])

    def update(self, dt):
        alive = []
        for p in self.particles:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 160 * dt        # gravedad ligera
            p[5] -= dt
            if p[5] > 0:
                alive.append(p)
        self.particles = alive

    def render(self, screen):
        for x, y, _, _, color, life in self.particles:
            size = max(2, int(4 * life * 2))
            pygame.draw.rect(screen, color, (int(x), int(y), size, size))
