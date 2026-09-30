"""
button.py — Botón reutilizable con hover y clic
===============================================

Un botón retro: rectángulo con borde grueso que se "enciende"
(cambia de color) cuando el mouse pasa por encima.

Uso:
    btn = Button(100, 200, 200, 50, "JUGAR", on_click=mi_funcion)
    # en handle_events:  btn.handle_event(event)
    # en update:         btn.update(dt)
    # en render:         btn.render(screen, font)
"""

import pygame

from .. import config


class Button:
    """Botón rectangular con texto, hover y callback."""

    def __init__(self, x, y, w, h, text, on_click=None,
                 color=config.DARK_BLUE, hover_color=config.BLUE,
                 text_color=config.WHITE, font_size=config.FONT_SIZE_MEDIUM):
        """Crea el botón en la posición (x, y) con su texto y colores.

        `on_click` es la función que se llama al hacer clic (o None).
        """
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.on_click = on_click
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.hovered = False
        self.enabled = True

    # ------------------------------------------------------------------ #
    def handle_event(self, event):
        """Reacciona al clic izquierdo cuando el mouse está encima."""
        if not self.enabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.on_click:
                self.on_click()

    def update(self, dt=None):
        """Detecta si el mouse está encima (para el efecto hover)."""
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.enabled and self.rect.collidepoint(mouse_pos)

    # ------------------------------------------------------------------ #
    def render(self, screen, font):
        """Dibuja el botón. Se ve más claro cuando el mouse está encima."""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        pygame.draw.rect(screen, config.WHITE, self.rect, 2, border_radius=6)

        surface = font.render(self.text, True, self.text_color)
        text_rect = surface.get_rect(center=self.rect.center)
        screen.blit(surface, text_rect)
