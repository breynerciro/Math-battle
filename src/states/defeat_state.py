"""
defeat_state.py — Pantalla de derrota
=====================================

Cuando el héroe pierde sus 3 vidas. Muestra estadísticas de la
partida y deja reintentar el nivel o volver al menú.
"""

import pygame

from .. import config
from ..ui.button import Button
from ..ui.sound_manager import SoundManager
from .base_state import BaseState


class DefeatState(BaseState):
    """Game over: se acabaron las vidas."""

    def __init__(self, game, player, level=1):
        super().__init__(game)
        self.player = player
        self.level = level
        self.sounds = SoundManager()

        cx = config.SCREEN_WIDTH // 2
        self.buttons = [
            Button(cx - 120, 540, 240, 52, "REINTENTAR",
                   on_click=self._retry, font_size=config.FONT_SIZE_MEDIUM),
            Button(cx - 120, 610, 240, 52, "MENÚ",
                   on_click=self._go_menu, font_size=config.FONT_SIZE_MEDIUM),
        ]

        # Registrar la partida en el guardado (sin desbloquear nada)
        self.save_data = self.game.save_system.record_result(
            self.game.save_system.load(),
            score=player.score,
            level_completed=0,          # 0 = no completó nivel nuevo
            correct=player.correct_count,
            wrong=player.wrong_count,
            max_combo=player.max_combo)
        self.sounds.play("defeat")

    # ------------------------------------------------------------------ #
    def _retry(self):
        """Nueva partida desde el nivel donde se perdió (el héroe se restaura)."""
        self.sounds.play("click")
        from .battle_state import BattleState
        self.game.player = None         # se crea un héroe nuevo
        self.game.current_level = self.level
        self.game.change_state(BattleState(self.game, self.level))

    def _go_menu(self):
        self.sounds.play("click")
        from .menu_state import MenuState
        self.game.player = None
        self.game.change_state(MenuState(self.game))

    # ------------------------------------------------------------------ #
    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._retry()

    def update(self, dt):
        for button in self.buttons:
            button.update(dt)

    def render(self, screen):
        screen.fill(config.BLACK)
        cx = config.SCREEN_WIDTH // 2

        self.draw_text(screen, "GAME OVER", config.FONT_SIZE_TITLE,
                       config.DARK_RED, cx + 4, 134, center=True)
        self.draw_text(screen, "GAME OVER", config.FONT_SIZE_TITLE,
                       config.RED, cx, 130, center=True)
        # Frase motivadora ajustada por píxeles para no desbordar
        y = 195
        for line in self._wrap(
                "Los monstruos temen a quien practica: ¡inténtalo de nuevo!",
                config.FONT_SIZE_SMALL, 760):
            self.draw_text(screen, line, config.FONT_SIZE_SMALL,
                           config.LIGHT_GRAY, cx, y, center=True)
            y += 20

        accuracy = (100 * self.player.correct_count //
                    max(1, self.player.correct_count + self.player.wrong_count))
        stats = [
            f"Puntuación final: {self.player.score} pts",
            f"Combo máximo: x{self.player.max_combo}",
            f"Precisión: {accuracy}%",
        ]
        y = 320
        for line in stats:
            self.draw_text(screen, line, config.FONT_SIZE_MEDIUM,
                           config.WHITE, cx, y, center=True)
            y += 26

        for button in self.buttons:
            button.render(screen, self.game.get_font(button.font_size))
