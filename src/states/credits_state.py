"""
credits_state.py — Pantalla de créditos
=======================================

Aquí los estudiantes deben poner SUS nombres y los de su institución:
todo el texto vive en la lista `LINES` de esta clase (y se explica en
el README).

La pantalla sigue el mismo lenguaje visual que el resto del juego:
fondo en bandas con estrellas, placa de título con sombra dura y un
panel central oscuro detrás de los textos, para que todo se lea con
contraste alto.
"""

import math

import pygame

from .. import config
from ..ui.button import Button
from ..ui.sound_manager import SoundManager
from .base_state import BaseState


class CreditsState(BaseState):
    """Créditos del proyecto (editable por los estudiantes)."""

    # Texto de la pantalla: (texto, tamaño, color). Líneas vacías = espacio.
    LINES = [
        ("MATH BATTLE", config.FONT_SIZE_TITLE, config.YELLOW),
        ("", config.FONT_SIZE_SMALL, config.WHITE),
        ("Ponencia para la Jornada del Educador Matemático (JEM)",
         config.FONT_SIZE_SMALL, config.WHITE),
        ("Universidad Pedagógica Nacional",
         config.FONT_SIZE_SMALL, config.WHITE),
        ("", config.FONT_SIZE_SMALL, config.WHITE),
        ("Desarrollado por:", config.FONT_SIZE_MEDIUM, config.CYAN),
        ("[ Estudiante 1 ]  —  [ Estudiante 2 ]",
         config.FONT_SIZE_MEDIUM, config.WHITE),
        ("Grado Noveno  •  [ Nombre de la institución ]",
         config.FONT_SIZE_SMALL, (156, 160, 176)),
        ("", config.FONT_SIZE_SMALL, config.WHITE),
        ("Docente orientador: [ Nombre del docente ]",
         config.FONT_SIZE_SMALL, config.WHITE),
        ("", config.FONT_SIZE_SMALL, config.WHITE),
        ("Python + Pygame  •  Pixel Art",
         config.FONT_SIZE_SMALL, config.LIGHT_GRAY),
        ("Música y sonidos generados",
         config.FONT_SIZE_SMALL, config.LIGHT_GRAY),
    ]

    # Panel central que hace de fondo a los textos
    PANEL = pygame.Rect(config.SCREEN_WIDTH // 2 - 400, 136, 800, 470)

    def __init__(self, game):
        """Crea el botón VOLVER y prepara el fondo estrellado."""
        super().__init__(game)
        self.sounds = SoundManager()
        self.time = 0.0
        self.back_button = Button(
            config.SCREEN_WIDTH // 2 - 100, config.SCREEN_HEIGHT - 80,
            200, 50, "← VOLVER", on_click=self._go_menu,
            font_size=config.FONT_SIZE_MEDIUM)

    def _go_menu(self):
        """VOLVER → regresa al menú principal."""
        self.sounds.play("click")
        from .menu_state import MenuState
        self.game.change_state(MenuState(self.game))

    # ------------------------------------------------------------------ #
    def handle_events(self, events):
        """Clic en VOLVER o tecla Esc para salir."""
        for event in events:
            self.back_button.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._go_menu()

    def update(self, dt):
        """Un frame: anima el fondo y el hover del botón VOLVER."""
        self.time += dt
        self.back_button.update(dt)

    # ------------------------------------------------------------------ #
    def render(self, screen):
        """Dibuja fondo, placa de título, panel con los créditos y VOLVER."""
        self._render_background(screen)
        self._render_title(screen)
        self._render_lines(screen)
        self.back_button.render(screen, self.game.get_font(
            self.back_button.font_size))

    # ------------------------------------------------------------------ #
    def _render_background(self, screen):
        """Cielo en bandas con estrellas que parpadean + suelo."""
        top, bottom = (8, 10, 26), (28, 36, 80)
        bands = 14
        h = config.SCREEN_HEIGHT // bands
        for i in range(bands):
            t = i / (bands - 1)
            col = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
            y = i * h
            height = h if i < bands - 1 else config.SCREEN_HEIGHT - y
            pygame.draw.rect(screen, col, (0, y, config.SCREEN_WIDTH, height))

        for i in range(30):
            x = int((i * 89 + self.time * 6) % config.SCREEN_WIDTH)
            y = int((i * 61 + math.sin(self.time + i) * 4) % 320)
            alpha = int(110 + 60 * math.sin(self.time * 2 + i))
            pygame.draw.circle(screen, (214, 222, 255, alpha), (x, y),
                               1 + (i % 2))

        # Suelo con doble línea de horizonte (igual que el menú)
        pygame.draw.rect(screen, (34, 32, 50),
                         (0, 636, config.SCREEN_WIDTH,
                          config.SCREEN_HEIGHT - 636))
        pygame.draw.line(screen, (92, 88, 120), (0, 636),
                         (config.SCREEN_WIDTH, 636), 3)

    def _render_title(self, screen):
        """Placa con el título de la pantalla (sombra primero, color después)."""
        cx = config.SCREEN_WIDTH // 2
        plate = pygame.Rect(cx - 300, 36, 600, 84)
        pygame.draw.rect(screen, (16, 18, 44), plate, border_radius=10)
        pygame.draw.rect(screen, config.YELLOW, plate, 3, border_radius=10)
        inner = plate.inflate(-10, -10)
        pygame.draw.rect(screen, (74, 78, 146), inner, 2, border_radius=7)

        self.draw_text(screen, "CRÉDITOS", config.FONT_SIZE_LARGE,
                       config.BLACK, cx + 4, 82, center=True)
        self.draw_text(screen, "CRÉDITOS", config.FONT_SIZE_LARGE,
                       config.YELLOW, cx, 78, center=True)

    def _render_lines(self, screen):
        """Panel oscuro con la lista de créditos centrada dentro."""
        # Marco y fondo: sin él los textos se apoyarían directamente en el
        # degradado y los grises claros perderían contraste.
        pygame.draw.rect(screen, (10, 12, 26), self.PANEL, border_radius=10)
        pygame.draw.rect(screen, config.GRAY, self.PANEL, 3, border_radius=10)

        y = self.PANEL.y + 34
        for text, size, color in self.LINES:
            self.draw_text(screen, text, size, color,
                           self.PANEL.centerx, y, center=True)
            if size == config.FONT_SIZE_TITLE:
                y += 60
            elif text == "":
                y += 16
            else:
                y += 32
