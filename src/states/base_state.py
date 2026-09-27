"""
base_state.py — Clase base de todos los estados del juego
=========================================================

Math Battle usa una "máquina de estados": en cada momento solo UNA
pantalla está activa (menú, batalla, victoria...). Todas las pantallas
heredan de esta clase y cumplen el mismo "contrato":

- handle_events(): recibe las teclas/clics del jugador
- update(dt):      avanza la lógica (dt = segundos desde el último frame)
- render(screen):  dibuja todo en la pantalla
- enter()/exit():  se ejecutan al entrar y salir del estado
"""

from abc import ABC, abstractmethod


class BaseState(ABC):
    """Contrato común para todas las pantallas del juego."""

    def __init__(self, game):
        # `game` es el objeto Game (game.py): nos da acceso a la pantalla,
        # a la fuente, y a los métodos change_state() / push_state().
        self.game = game

    # -- Ciclo de vida (obligatorios) --------------------------------------
    @abstractmethod
    def handle_events(self, events):
        """Procesa los eventos de Pygame de este frame."""

    @abstractmethod
    def update(self, dt):
        """Actualiza la lógica del estado. `dt` son los segundos transcurridos."""

    @abstractmethod
    def render(self, screen):
        """Dibuja el estado completo en la pantalla."""

    # -- Ganchos opcionales -------------------------------------------------
    def enter(self):
        """Se ejecuta una vez cuando el estado se vuelve activo."""

    def exit(self):
        """Se ejecuta una vez cuando el estado deja de ser activo."""

    def pause(self):
        """Se ejecuta si otro estado se apila encima (ej: la pregunta de math)."""

    def resume(self):
        """Se ejecuta cuando se cierra el estado que estaba encima."""

    # -- Utilidades comunes --------------------------------------------------
    def _wrap(self, text, size, max_w):
        """Parte un texto en líneas que caben en max_w píxeles.

        Mide con la fuente REAL (font.size): la fuente pixel art tiene
        caracteres anchos, así que partir por número de letras desborda.
        """
        font = self.game.get_font(size)
        words = text.split()
        lines, current = [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if font.size(candidate)[0] <= max_w:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines or [text]

    def draw_text(self, screen, text, size, color, x, y, center=False):
        """Atajo para dibujar texto en cualquier estado."""
        font = self.game.get_font(size)
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        screen.blit(surface, rect)
        return rect  # Útil para detectar clics sobre el texto
