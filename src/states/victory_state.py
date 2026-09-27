"""
victory_state.py — Pantalla de victoria
=======================================

Se muestra al vencer a TODOS los enemigos de un nivel.
Muestra puntuación, combo máximo y precisión. Si no es el último
nivel, desbloquea el siguiente y permite continuar.
"""

import pygame

from .. import config
from ..ui.button import Button
from ..ui.sound_manager import SoundManager
from .base_state import BaseState


class VictoryState(BaseState):
    """Resumen al completar un nivel."""

    def __init__(self, game, level, player, last_level=False,
                 bosses_defeated=0):
        super().__init__(game)
        self.level = level
        self.player = player
        self.last_level = last_level
        self.sounds = SoundManager()

        # Guardar progreso: completar el nivel L desbloquea L+1
        self.save_data = self.game.save_system.record_result(
            self.game.save_system.load(),
            score=player.score,
            level_completed=level,
            correct=player.correct_count,
            wrong=player.wrong_count,
            max_combo=player.max_combo,
            bosses_defeated=bosses_defeated)

        self.sounds.play("victory")
        self.sounds.play_music("menu")

        cx = config.SCREEN_WIDTH // 2
        if last_level:
            # ¡Se terminó el juego!
            self.title = "¡VICTORIA TOTAL!"
            self.subtitle = "Derrotaste al Dragón Supremo. ¡Eres un maestro de las matemáticas!"
            self.buttons = [
                Button(cx - 120, 420, 240, 52, "MENÚ PRINCIPAL",
                       on_click=self._go_menu, font_size=config.FONT_SIZE_MEDIUM),
            ]
        else:
            self.title = f"¡NIVEL {level} SUPERADO!"
            self.subtitle = f"Has desbloqueado el nivel {level + 1}"
            self.buttons = [
                Button(cx - 250, 420, 240, 52, "SIGUIENTE NIVEL",
                       on_click=self._next_level, font_size=config.FONT_SIZE_MEDIUM),
                Button(cx + 10, 420, 240, 52, "MENÚ",
                       on_click=self._go_menu, font_size=config.FONT_SIZE_MEDIUM),
            ]

    # ------------------------------------------------------------------ #
    def _next_level(self):
        """Salta directo al siguiente nivel con el héroe restaurado."""
        self.sounds.play("click")
        from .battle_state import BattleState
        # Cada nivel empieza con vida completa y las 3 vidas de nuevo
        self.game.player = None
        self.game.current_level = self.level + 1
        self.game.change_state(BattleState(self.game, self.level + 1))

    def _go_menu(self):
        self.sounds.play("click")
        from .menu_state import MenuState
        self.game.change_state(MenuState(self.game))

    # ------------------------------------------------------------------ #
    def handle_events(self, events):
        for event in events:
            for button in self.buttons:
                button.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Enter = acción principal (siguiente nivel o menú)
                self.buttons[0].on_click()

    def update(self, dt):
        for button in self.buttons:
            button.update(dt)

    # ------------------------------------------------------------------ #
    def render(self, screen):
        screen.fill(config.DARK_GREEN if not self.last_level else config.DARK_BLUE)

        # Título con "glow" simple (doble texto)
        cx = config.SCREEN_WIDTH // 2
        self.draw_text(screen, self.title, config.FONT_SIZE_TITLE,
                       config.BLACK, cx + 4, 114, center=True)
        self.draw_text(screen, self.title, config.FONT_SIZE_TITLE,
                       config.YELLOW, cx, 110, center=True)
        # Subtítulo ajustado por píxeles (el de victoria total es largo)
        y = 168
        for line in self._wrap(self.subtitle, config.FONT_SIZE_MEDIUM, 760):
            self.draw_text(screen, line, config.FONT_SIZE_MEDIUM,
                           config.WHITE, cx, y, center=True)
            y += 24

        # Héroe celebrando
        self.player.play("victory")
        self.player.update(0.016)
        self.player.draw(screen, cx, 280)

        # Estadísticas de la partida
        accuracy = (100 * self.player.correct_count //
                    max(1, self.player.correct_count + self.player.wrong_count))
        stats = [
            f"Puntuación: {self.player.score} pts",
            f"Combo máximo: x{self.player.max_combo}",
            f"Precisión: {accuracy}%",
        ]
        y = 350
        for line in stats:
            self.draw_text(screen, line, config.FONT_SIZE_MEDIUM,
                           config.WHITE, cx, y, center=True)
            y += 24

        for button in self.buttons:
            button.render(screen, self.game.get_font(button.font_size))
