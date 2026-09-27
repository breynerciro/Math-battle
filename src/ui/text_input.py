"""
text_input.py — Campo de texto para escribir las respuestas
===========================================================

Un input de texto simple estilo retro:
- Aparece un cursor que parpadea (|)
- Enter confirma la respuesta
- Solo acepta los caracteres válidos para matemáticas
"""

import pygame

from .. import config


class TextInput:
    """Caja de texto donde el jugador escribe su respuesta."""

    # Caracteres que tienen sentido en una respuesta matemática
    ALLOWED = "0123456789.-/ "

    def __init__(self, x, y, w, h, font_size=config.FONT_SIZE_MEDIUM):
        self.rect = pygame.Rect(x, y, w, h)
        self.font_size = font_size
        self.text = ""
        self.active = True          # ¿está recibiendo teclas?
        self.cursor_visible = True
        self._cursor_timer = 0.0
        self.on_submit = None       # función a llamar cuando se presiona Enter

    # ------------------------------------------------------------------ #
    def handle_event(self, event):
        """Procesa un evento de teclado. Llama a on_submit al presionar Enter."""
        if not self.active or event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            if self.text and self.on_submit:
                self.on_submit(self.text)
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.text = ""          # limpiar rápido con Esc
        elif event.unicode:
            # Solo aceptamos caracteres matemáticamente útiles
            if event.unicode in self.ALLOWED and len(self.text) < 12:
                self.text += event.unicode

    # ------------------------------------------------------------------ #
    def update(self, dt):
        """Hace parpadear el cursor."""
        self._cursor_timer += dt
        if self._cursor_timer >= 0.5:      # parpadea cada medio segundo
            self._cursor_timer = 0.0
            self.cursor_visible = not self.cursor_visible

    # ------------------------------------------------------------------ #
    def render(self, screen, font):
        """Dibuja la caja, el texto y el cursor parpadeante."""
        # Caja con borde
        pygame.draw.rect(screen, config.BLACK, self.rect, border_radius=4)
        border = config.YELLOW if self.active else config.GRAY
        pygame.draw.rect(screen, border, self.rect, 2, border_radius=4)

        # Texto + cursor
        shown = self.text + ("|" if self.cursor_visible else "")
        surface = font.render(shown, True, config.WHITE)
        text_rect = surface.get_rect(midleft=(self.rect.x + 12, self.rect.centery))
        screen.blit(surface, text_rect)

    def clear(self):
        """Limpia el texto (para la siguiente pregunta)."""
        self.text = ""

    def get_text(self):
        return self.text.strip()
