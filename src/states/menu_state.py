"""
menu_state.py — Menú principal
==============================

La primera pantalla: título, botones JUGAR / CRÉDITOS / SALIR
y el héroe animado saludando. Muestra el récord guardado.
"""

import random

import pygame

from .. import config
from ..ui.button import Button
from ..ui.sound_manager import SoundManager
from .base_state import BaseState
from .credits_state import CreditsState
from .level_select_state import LevelSelectState


class MenuState(BaseState):
    """Pantalla de inicio del juego."""

    def __init__(self, game):
        super().__init__(game)
        self.sounds = SoundManager()

        center_x = config.SCREEN_WIDTH // 2
        self.buttons = [
            Button(center_x - 120, 340, 240, 52, "JUGAR",
                   on_click=self._start_game, font_size=config.FONT_SIZE_LARGE),
            Button(center_x - 120, 410, 240, 52, "CRÉDITOS",
                   on_click=self._go_credits, font_size=config.FONT_SIZE_LARGE),
            Button(center_x - 120, 480, 240, 52, "SALIR",
                   on_click=self.game.quit, font_size=config.FONT_SIZE_LARGE),
        ]

        # Símbolos matemáticos flotando de fondo (solo decoración)
        self.symbols = []
        for _ in range(14):
            self.symbols.append({
                "char": random.choice("+-×÷=√π"),
                "x": random.uniform(0, config.SCREEN_WIDTH),
                "y": random.uniform(0, config.SCREEN_HEIGHT),
                "speed": random.uniform(15, 40),
                "size": random.choice([config.FONT_SIZE_SMALL,
                                       config.FONT_SIZE_MEDIUM]),
            })

    # ------------------------------------------------------------------ #
    def enter(self):
        self.sounds.play_music("menu")
        # Cargamos (o recargamos) el récord cada vez que volvemos al menú
        self.save_data = self.game.save_system.load()

    # ------------------------------------------------------------------ #
    def _start_game(self):
        self.sounds.play("click")
        self.game.change_state(LevelSelectState(self.game))

    def _go_credits(self):
        self.sounds.play("click")
        self.game.change_state(CreditsState(self.game))

    # ------------------------------------------------------------------ #
    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)

    def update(self, dt):
        for button in self.buttons:
            button.update(dt)
        # Los símbolos flotan hacia arriba y reaparecen por abajo
        for s in self.symbols:
            s["y"] -= s["speed"] * dt
            if s["y"] < -20:
                s["y"] = config.SCREEN_HEIGHT + 20
                s["x"] = random.uniform(0, config.SCREEN_WIDTH)

    def render(self, screen):
        # Fondo degradado simple con franjas retro
        screen.fill(config.DARK_BLUE)
        pygame.draw.rect(screen, config.DARK_GRAY,
                         (0, config.SCREEN_HEIGHT - 90,
                          config.SCREEN_WIDTH, 90))

        # Símbolos matemáticos de fondo
        for s in self.symbols:
            self.draw_text(screen, s["char"], s["size"], (60, 80, 140),
                           s["x"], s["y"])

        # Título con sombra
        title = "EL HÉROE DE LAS MATEMÁTICAS"
        self.draw_text(screen, title, config.FONT_SIZE_TITLE,
                       config.BLACK, config.SCREEN_WIDTH // 2 + 4, 114,
                       center=True)
        self.draw_text(screen, title, config.FONT_SIZE_TITLE,
                       config.YELLOW, config.SCREEN_WIDTH // 2, 110, center=True)
        self.draw_text(screen, "¡Combate por turnos con matemáticas!",
                       config.FONT_SIZE_MEDIUM, config.LIGHT_GRAY,
                       config.SCREEN_WIDTH // 2, 172, center=True)

        # Héroe animado al lado del título
        if self.game.player is None:
            from ..entities.player import Player
            self.game.player = Player()
        self.game.player.update(0.016)
        self.game.player.draw(screen, 200, 440)

        # Récord guardado
        high = self.save_data.get("high_score", 0)
        if high > 0:
            self.draw_text(screen, f"Récord: {high} pts", config.FONT_SIZE_SMALL,
                           config.YELLOW, config.SCREEN_WIDTH // 2, 600,
                           center=True)

        for button in self.buttons:
            button.render(screen, self.game.get_font(button.font_size))
