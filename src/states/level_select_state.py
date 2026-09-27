"""
level_select_state.py — Mapa de selección de niveles
====================================================

Muestra las 5 tarjetas de nivel. Los niveles bloqueados (que aún no
se han desbloqueado jugando) se ven grises con un candado.
"""

import pygame

from .. import config
from ..ui.button import Button
from ..ui.sound_manager import SoundManager
from .base_state import BaseState
from .battle_state import BattleState

LEVEL_INFO = {
    1: ("Bosque Aritmético", "+, -, ×, ÷"),
    2: ("Cueva de Ecuaciones", "ax + b = c"),
    3: ("Torre de Potencias", "potencias y raíces"),
    4: ("Pantano de Fracciones", "½ + ¼ ..."),
    5: ("Fortaleza Geométrica", "áreas y ángulos"),
}


class LevelSelectState(BaseState):
    """Selección de nivel con desbloqueo progresivo."""

    # Cuadrícula 3+2: 3 tarjetas arriba, 2 abajo (5 en fila no caben a 960px)
    CARD_W, CARD_H = 200, 170
    GAP = 24

    def __init__(self, game):
        super().__init__(game)
        self.sounds = SoundManager()

    def enter(self):
        self.sounds.play_music("menu")
        self.save_data = self.game.save_system.load()
        self.highest = self.save_data.get("highest_level", 1)

        # Construir las tarjetas de nivel y el botón de volver
        self.cards = []
        rows = ([1, 2, 3], [4, 5])
        for row_idx, levels in enumerate(rows):
            total_w = len(levels) * self.CARD_W + (len(levels) - 1) * self.GAP
            x = (config.SCREEN_WIDTH - total_w) // 2
            y = 118 + row_idx * (self.CARD_H + self.GAP)
            for level in levels:
                rect = pygame.Rect(x, y, self.CARD_W, self.CARD_H)
                self.cards.append({"level": level, "rect": rect,
                                   "unlocked": level <= self.highest})
                x += self.CARD_W + self.GAP

        self.back_button = Button(config.SCREEN_WIDTH - 190,
                                  config.SCREEN_HEIGHT - 66, 170, 48,
                                  "← VOLVER", on_click=self._go_menu,
                                  font_size=config.FONT_SIZE_MEDIUM)

    # ------------------------------------------------------------------ #
    def _go_menu(self):
        self.sounds.play("click")
        from .menu_state import MenuState
        self.game.change_state(MenuState(self.game))

    def _start_level(self, level):
        self.sounds.play("click")
        # Al empezar partida nueva, el héroe recupera todo
        self.game.player = None
        self.game.current_level = level
        self.game.change_state(BattleState(self.game, level))

    # ------------------------------------------------------------------ #
    def handle_events(self, events):
        for event in events:
            self.back_button.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for card in self.cards:
                    if card["rect"].collidepoint(event.pos):
                        if card["unlocked"]:
                            self._start_level(card["level"])
                        else:
                            self.sounds.play("wrong")   # ¡bloqueado!
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._go_menu()

    def update(self, dt):
        self.back_button.update(dt)

    # ------------------------------------------------------------------ #
    def render(self, screen):
        screen.fill(config.DARK_BLUE)
        self.draw_text(screen, "SELECCIONA NIVEL", config.FONT_SIZE_LARGE,
                       config.YELLOW, config.SCREEN_WIDTH // 2, 52, center=True)
        self.draw_text(screen,
                       f"Récord: {self.save_data.get('high_score', 0)} pts   •   "
                       f"Progreso: nivel {self.highest}",
                       config.FONT_SIZE_SMALL, config.LIGHT_GRAY,
                       config.SCREEN_WIDTH // 2, 92, center=True)

        mouse = pygame.mouse.get_pos()
        for card in self.cards:
            rect = card["rect"]
            unlocked = card["unlocked"]
            level = card["level"]
            hovered = unlocked and rect.collidepoint(mouse)

            # Tarjeta
            color = config.LEVEL_COLORS[level] if unlocked else config.DARK_GRAY
            border = config.YELLOW if hovered else config.LIGHT_GRAY
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, border, rect, 3, border_radius=10)

            name, topic = LEVEL_INFO[level]
            cx = rect.centerx
            # Número gigante o candado
            if unlocked:
                self.draw_text(screen, str(level), config.FONT_SIZE_TITLE,
                               config.WHITE, cx, rect.y + 36, center=True)
            else:
                self.draw_text(screen, "X", config.FONT_SIZE_LARGE,
                               config.GRAY, cx, rect.y + 36, center=True)
            # Nombre y tema envueltos para que no desborden la tarjeta
            ny = rect.y + 66
            for line in self._wrap(name, config.FONT_SIZE_SMALL, self.CARD_W - 16):
                self.draw_text(screen, line, config.FONT_SIZE_SMALL,
                               config.WHITE if unlocked else config.GRAY,
                               cx, ny, center=True)
                ny += 18
            for line in self._wrap(topic, config.FONT_SIZE_SMALL, self.CARD_W - 16):
                self.draw_text(screen, line, config.FONT_SIZE_SMALL,
                               config.LIGHT_GRAY if unlocked else config.GRAY,
                               cx, ny + 4, center=True)
                ny += 16
            self.draw_text(screen, "★" * level, config.FONT_SIZE_SMALL,
                           config.YELLOW, cx, rect.bottom - 24, center=True)

        self.back_button.render(screen, self.game.get_font(
            self.back_button.font_size))
