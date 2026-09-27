"""
transition.py — Transiciones con fade entre pantallas
=====================================================

Un "velo" negro que se oscurece y aclara. Se usa así:

    transition = Transition()
    transition.start(callback=mi_funcion)
    # en update:  transition.update(dt)   → llama al callback a mitad del fade
    # en render:  transition.render(screen)  (¡al final, para tapar todo!)
"""

import pygame

from .. import config


class Transition:
    """Fade a negro → ejecuta un callback → fade de vuelta."""

    FADE_IN = 0    # oscureciéndose
    OUT = 1        # aclarándose
    DONE = 2

    def __init__(self, duration=0.4):
        self.duration = duration
        self.phase = self.DONE
        self.alpha = 0
        self.callback = None

    def start(self, callback):
        """Inicia la transición. El callback corre cuando la pantalla
        está totalmente negra (momento perfecto para cambiar de estado)."""
        self.callback = callback
        self.phase = self.FADE_IN
        self.alpha = 0

    def active(self):
        return self.phase != self.DONE

    # ------------------------------------------------------------------ #
    def update(self, dt):
        if not self.active():
            return
        speed = 255 / self.duration       # alpha por segundo
        if self.phase == self.FADE_IN:
            self.alpha += speed * dt
            if self.alpha >= 255:
                self.alpha = 255
                if self.callback:
                    self.callback()        # cambio de estado en negro
                    self.callback = None
                self.phase = self.OUT
        else:
            self.alpha -= speed * dt
            if self.alpha <= 0:
                self.alpha = 0
                self.phase = self.DONE

    # ------------------------------------------------------------------ #
    def render(self, screen):
        if self.alpha > 0:
            veil = pygame.Surface(screen.get_size())
            veil.fill(config.BLACK)
            veil.set_alpha(int(self.alpha))
            screen.blit(veil, (0, 0))
