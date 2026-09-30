"""
level_select_state.py — Mapa de selección de niveles mejorado
=============================================================

Tarjetas de nivel con animaciones, efectos de hover y feedback visual
aplicando principios de game-juice.
"""

import math
import pygame

from .. import config
from ..ui.button import Button
from ..ui.sound_manager import SoundManager
from .base_state import BaseState
from .battle_state import BattleState

LEVEL_INFO = {
    1: ("El Bosque de las Sumas", "sumas y restas"),
    2: ("La Mina de la Multiplicación", "multiplicación y división"),
    3: ("El Templo de las Fracciones", "operaciones con fracciones"),
    4: ("El Puente Hacia el Caos", "geometría y ecuaciones"),
    5: ("El Castillo del Caos", "álgebra"),
}

LEVEL_ICONS = {
    1: "🌳",
    2: "⛏️",
    3: "🏛️",
    4: "🌉",
    5: "🏰",
}


class LevelCard:
    """Tarjeta de nivel con animaciones y efectos de hover."""

    def __init__(self, level, rect, unlocked):
        self.level = level
        self.rect = rect
        self.unlocked = unlocked
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.bounce_offset = 0.0
        self.bounce_time = 0.0
        self.glow_pulse = 0.0
        self.glow_speed = 2.0 + level * 0.3

    def set_hovered(self, hovered):
        self.target_scale = 1.08 if hovered else 1.0

    def trigger_bounce(self):
        self.bounce_time = 0.0

    def update(self, dt):
        self.hover_scale += (self.target_scale - self.hover_scale) * 8 * dt
        self.glow_pulse += self.glow_speed * dt

        if self.bounce_time < 0.3:
            self.bounce_time += dt
            t = self.bounce_time / 0.3
            self.bounce_offset = math.sin(t * math.pi) * 8 * (1 - t)
        else:
            self.bounce_offset = 0.0

    def get_render_rect(self):
        scale = self.hover_scale
        w = int(self.rect.width * scale)
        h = int(self.rect.height * scale)
        x = self.rect.centerx - w // 2
        y = self.rect.centery - h // 2 - self.bounce_offset
        return pygame.Rect(x, y, w, h)


class LevelSelectState(BaseState):
    """Selección de nivel con tarjetas animadas y feedback visual."""

    CARD_W, CARD_H = 200, 170
    GAP = 24

    def __init__(self, game):
        super().__init__(game)
        self.sounds = SoundManager()
        self.cards = []
        self.time = 0.0

    def enter(self):
        self.sounds.play_music("menu")
        self.save_data = self.game.save_system.load()
        self.highest = self.save_data.get("highest_level", 1)
        self.time = 0.0

        self.cards = []
        rows = ([1, 2, 3], [4, 5])
        for row_idx, levels in enumerate(rows):
            total_w = len(levels) * self.CARD_W + (len(levels) - 1) * self.GAP
            x = (config.SCREEN_WIDTH - total_w) // 2
            y = 150 + row_idx * (self.CARD_H + self.GAP)
            for level in levels:
                rect = pygame.Rect(x, y, self.CARD_W, self.CARD_H)
                card = LevelCard(level, rect, level <= self.highest)
                self.cards.append(card)
                x += self.CARD_W + self.GAP

        self.back_button = Button(config.SCREEN_WIDTH - 190,
                                  config.SCREEN_HEIGHT - 66, 170, 48,
                                  "← VOLVER", on_click=self._go_menu,
                                  font_size=config.FONT_SIZE_MEDIUM)

    def _go_menu(self):
        self.sounds.play("click")
        from .menu_state import MenuState
        self.game.change_state(MenuState(self.game))

    def _start_level(self, level):
        self.sounds.play("click")
        for card in self.cards:
            if card.level == level:
                card.trigger_bounce()
        self.game.player = None
        self.game.current_level = level
        self.game.change_state(BattleState(self.game, level))

    def handle_events(self, events):
        for event in events:
            self.back_button.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for card in self.cards:
                    if card.rect.collidepoint(event.pos):
                        if card.unlocked:
                            self._start_level(card.level)
                        else:
                            self.sounds.play("wrong")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._go_menu()

    def update(self, dt):
        self.time += dt
        self.back_button.update(dt)

        mouse = pygame.mouse.get_pos()
        for card in self.cards:
            hovered = card.unlocked and card.rect.collidepoint(mouse)
            card.set_hovered(hovered)
            card.update(dt)

    def render(self, screen):
        self._render_background(screen)

        self.draw_text(screen, "SELECCIONA NIVEL", config.FONT_SIZE_LARGE,
                       config.YELLOW, config.SCREEN_WIDTH // 2, 62, center=True)
        self.draw_text(screen,
                       f"Récord: {self.save_data.get('high_score', 0)} pts   •   "
                       f"Progreso: nivel {self.highest}",
                       config.FONT_SIZE_SMALL, config.LIGHT_GRAY,
                       config.SCREEN_WIDTH // 2, 104, center=True)

        for card in self.cards:
            self._render_card(screen, card)

        self.back_button.render(screen, self.game.get_font(
            self.back_button.font_size))

    def _render_background(self, screen):
        screen.fill(config.DARK_BLUE)

        for i in range(30):
            x = int((i * 73 + self.time * 10) % config.SCREEN_WIDTH)
            y = int((i * 47 + math.sin(self.time + i) * 5) % config.SCREEN_HEIGHT)
            size = 1 + (i % 3)
            alpha = int(100 + 50 * math.sin(self.time * 2 + i))
            star_color = (*config.WHITE, alpha)
            pygame.draw.circle(screen, star_color, (x, y), size)

    def _render_card(self, screen, card):
        render_rect = card.get_render_rect()
        unlocked = card.unlocked
        level = card.level

        glow_intensity = int(40 + 20 * math.sin(card.glow_pulse))
        if unlocked:
            glow_color = config.LEVEL_COLORS[level]
            glow_surface = pygame.Surface((render_rect.width + 20, render_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*glow_color, glow_intensity),
                           (0, 0, render_rect.width + 20, render_rect.height + 20),
                           border_radius=14)
            screen.blit(glow_surface, (render_rect.x - 10, render_rect.y - 10))

        color = config.LEVEL_COLORS[level] if unlocked else config.DARK_GRAY
        border = config.YELLOW if unlocked else config.GRAY
        border_width = 4 if unlocked else 2

        pygame.draw.rect(screen, color, render_rect, border_radius=10)
        pygame.draw.rect(screen, border, render_rect, border_width, border_radius=10)

        name, topic = LEVEL_INFO[level]
        cx = render_rect.centerx

        if unlocked:
            self.draw_text(screen, str(level), config.FONT_SIZE_TITLE,
                           config.WHITE, cx, render_rect.y + 36, center=True)
        else:
            self.draw_text(screen, "🔒", config.FONT_SIZE_LARGE,
                           config.GRAY, cx, render_rect.y + 36, center=True)

        ny = render_rect.y + 66
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

        stars = "★" * level
        self.draw_text(screen, stars, config.FONT_SIZE_SMALL,
                       config.YELLOW if unlocked else config.GRAY,
                       cx, render_rect.bottom - 24, center=True)
