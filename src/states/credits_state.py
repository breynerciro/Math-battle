"""
credits_state.py — Pantalla de créditos
=======================================

Aquí los estudiantes deben poner SUS nombres y los de su institución.
"""

import pygame

from .. import config
from ..ui.button import Button
from ..ui.sound_manager import SoundManager
from .base_state import BaseState


class CreditsState(BaseState):
    """Créditos del proyecto (editable por los estudiantes)."""

    LINES = [
        ("MATH BATTLE", config.FONT_SIZE_TITLE, config.YELLOW),
        ("", config.FONT_SIZE_SMALL, config.WHITE),
        ("Ponencia para la Jornada del Educador Matemático (JEM)", config.FONT_SIZE_SMALL, config.WHITE),
        ("Universidad Pedagógica Nacional", config.FONT_SIZE_SMALL, config.WHITE),
        ("", config.FONT_SIZE_SMALL, config.WHITE),
        ("Desarrollado por:", config.FONT_SIZE_MEDIUM, config.CYAN),
        ("[ Estudiante 1 ]  —  [ Estudiante 2 ]", config.FONT_SIZE_MEDIUM, config.WHITE),
        ("Grado Noveno  •  [ Nombre de la institución ]", config.FONT_SIZE_SMALL, config.LIGHT_GRAY),
        ("", config.FONT_SIZE_SMALL, config.WHITE),
        ("Docente orientador: [ Nombre del docente ]", config.FONT_SIZE_SMALL, config.WHITE),
        ("", config.FONT_SIZE_SMALL, config.WHITE),
        ("Hecho con Python + Pygame  •  Pixel art por código", config.FONT_SIZE_SMALL, config.GRAY),
        ("Música y sonidos generados proceduralmente", config.FONT_SIZE_SMALL, config.GRAY),
    ]

    def __init__(self, game):
        super().__init__(game)
        self.sounds = SoundManager()
        self.back_button = Button(
            config.SCREEN_WIDTH // 2 - 100, config.SCREEN_HEIGHT - 80,
            200, 50, "← VOLVER", on_click=self._go_menu,
            font_size=config.FONT_SIZE_MEDIUM)

    def _go_menu(self):
        self.sounds.play("click")
        from .menu_state import MenuState
        self.game.change_state(MenuState(self.game))

    # ------------------------------------------------------------------ #
    def handle_events(self, events):
        for event in events:
            self.back_button.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._go_menu()

    def update(self, dt):
        self.back_button.update(dt)

    def render(self, screen):
        screen.fill(config.BLACK)
        y = 60
        for text, size, color in self.LINES:
            self.draw_text(screen, text, size, color,
                           config.SCREEN_WIDTH // 2, y, center=True)
            if size == config.FONT_SIZE_TITLE:
                y += 60
            elif text == "":
                y += 18
            else:
                y += 34
        self.back_button.render(screen, self.game.get_font(
            self.back_button.font_size))
