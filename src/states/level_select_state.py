"""
level_select_state.py — Mapa de selección de niveles
====================================================

Las 5 tarjetas del juego, una por nivel. Cada tarjeta es una "ventana"
al escenario de ese nivel: la miniatura ES el fondo de batalla real
(assets/backgrounds/level<N>.png), así que el jugador reconoce el sitio
antes de entrar.

Efectos aplicados (game-juice): resplandor pulsante, ampliación al
pasar el ratón, rebote al hacer clic y bloqueo visible de los niveles
que aún no se han desbloqueado.
"""

import math

import pygame

from .. import config
from ..ui.button import Button
from ..ui.background import get_background
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

# Miniaturas cacheadas: se escalan UNA vez por nivel y por sesión
_thumbs: dict = {}


def _thumb(level: int, w: int, h: int):
    """Miniatura del fondo del nivel, escalada a (w, h) y cacheada."""
    key = (level, w, h)
    if key not in _thumbs:
        _thumbs[key] = pygame.transform.smoothscale(get_background(level),
                                                    (w, h))
    return _thumbs[key]


class LevelCard:
    """Tarjeta de nivel con animaciones y efectos de hover."""

    def __init__(self, level, rect, unlocked):
        """Crea la tarjeta en reposo (sin hover ni rebote)."""
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
        """Si el ratón está encima, la tarjeta se agranda un 8%."""
        self.target_scale = 1.08 if hovered else 1.0

    def trigger_bounce(self):
        """Reinicio el rebote: se dispara al hacer clic en la tarjeta."""
        self.bounce_time = 0.0

    def update(self, dt):
        """Un frame: acerca la escala al objetivo y anima el rebote."""
        self.hover_scale += (self.target_scale - self.hover_scale) * 8 * dt
        self.glow_pulse += self.glow_speed * dt

        if self.bounce_time < 0.3:
            self.bounce_time += dt
            t = self.bounce_time / 0.3
            self.bounce_offset = math.sin(t * math.pi) * 8 * (1 - t)
        else:
            self.bounce_offset = 0.0

    def get_render_rect(self):
        """Rectángulo real a dibujar (con la escala y el rebote aplicados)."""
        scale = self.hover_scale
        w = int(self.rect.width * scale)
        h = int(self.rect.height * scale)
        x = self.rect.centerx - w // 2
        y = self.rect.centery - h // 2 - self.bounce_offset
        return pygame.Rect(x, y, w, h)


class LevelSelectState(BaseState):
    """Selección de nivel con tarjetas animadas y feedback visual."""

    CARD_W, CARD_H = 216, 200
    GAP = 26
    THUMB_H = 92                 # alto de la miniatura dentro de la tarjeta

    def __init__(self, game):
        """Crea las 5 tarjetas de nivel (una fila de 3 y otra de 2)."""
        super().__init__(game)
        self.sounds = SoundManager()
        self.cards = []
        self.time = 0.0

    def enter(self):
        """Al entrar: música de menú y lectura del nivel desbloqueado."""
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
        """VOLVER → regresa al menú principal."""
        self.sounds.play("click")
        from .menu_state import MenuState
        self.game.change_state(MenuState(self.game))

    def _start_level(self, level):
        """Clic en una tarjeta: rebota y arranca la batalla de ese nivel."""
        self.sounds.play("click")
        for card in self.cards:
            if card.level == level:
                card.trigger_bounce()
        self.game.player = None
        self.game.current_level = level
        self.game.change_state(BattleState(self.game, level))

    def handle_events(self, events):
        """Clics en tarjetas/botón VOLVER y tecla Esc para volver atrás."""
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
        """Un frame: anima tarjetas (hover/rebote) y el fondo estrellado."""
        self.time += dt
        self.back_button.update(dt)

        mouse = pygame.mouse.get_pos()
        for card in self.cards:
            hovered = card.unlocked and card.rect.collidepoint(mouse)
            card.set_hovered(hovered)
            card.update(dt)

    def render(self, screen):
        """Dibuja fondo, cabecera, las 5 tarjetas y el botón VOLVER."""
        self._render_background(screen)
        self._render_header(screen)

        for card in self.cards:
            self._render_card(screen, card)

        self.back_button.render(screen, self.game.get_font(
            self.back_button.font_size))

    # ------------------------------------------------------------------ #
    def _render_background(self, screen):
        """Cielo nocturno en bandas con estrellas que parpadean."""
        top, bottom = (6, 8, 24), (26, 32, 74)
        bands = 14
        h = config.SCREEN_HEIGHT // bands
        for i in range(bands):
            t = i / (bands - 1)
            col = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
            y = i * h
            height = h if i < bands - 1 else config.SCREEN_HEIGHT - y
            pygame.draw.rect(screen, col, (0, y, config.SCREEN_WIDTH, height))

        for i in range(34):
            x = int((i * 73 + self.time * 8) % config.SCREEN_WIDTH)
            y = int((i * 47 + math.sin(self.time + i) * 5) % 300)
            alpha = int(110 + 60 * math.sin(self.time * 2 + i))
            pygame.draw.circle(screen, (214, 222, 255, alpha), (x, y),
                               1 + (i % 2))

    def _render_header(self, screen):
        """Cabecera: placa con el título y el progreso del jugador."""
        cx = config.SCREEN_WIDTH // 2
        plate = pygame.Rect(cx - 340, 26, 680, 96)
        pygame.draw.rect(screen, (16, 18, 44), plate, border_radius=10)
        pygame.draw.rect(screen, config.YELLOW, plate, 3, border_radius=10)
        inner = plate.inflate(-10, -10)
        pygame.draw.rect(screen, (74, 78, 146), inner, 2, border_radius=7)

        # Título con sombra dura: PRIMERO la sombra negra (desplazada)
        # y DESPUÉS el texto amarillo encima. Si se dibujan al revés la
        # sombra tapa las letras y el título se lee negro sobre azul.
        self.draw_text(screen, "SELECCIÓN DE NIVEL", config.FONT_SIZE_LARGE,
                       config.BLACK, cx + 4, 66, center=True)
        self.draw_text(screen, "SELECCIÓN DE NIVEL", config.FONT_SIZE_LARGE,
                       config.YELLOW, cx, 62, center=True)

        high = self.save_data.get("high_score", 0)
        self.draw_text(screen,
                       f"RÉCORD: {high} PTS   ·   "
                       f"NIVEL MÁS ALTO: {self.highest}/{config.TOTAL_LEVELS}",
                       config.FONT_SIZE_SMALL, config.CYAN,
                       cx, 100, center=True)

    def _render_card(self, screen, card):
        """Dibuja UNA tarjeta: resplandor, miniatura, insignia y textos."""
        render_rect = card.get_render_rect()
        unlocked = card.unlocked
        level = card.level
        color = config.LEVEL_COLORS[level] if unlocked else config.GRAY

        # Resplandor pulsante alrededor de las tarjetas desbloqueadas
        if unlocked:
            glow_intensity = int(46 + 24 * math.sin(card.glow_pulse))
            glow = pygame.Surface((render_rect.width + 24,
                                   render_rect.height + 24), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*config.LEVEL_COLORS[level],
                                    glow_intensity),
                             (0, 0, glow.width, glow.height),
                             border_radius=14)
            screen.blit(glow, (render_rect.x - 12, render_rect.y - 12))

        # Cuerpo de la tarjeta (marco del color del nivel)
        body = (26, 28, 58) if unlocked else (36, 36, 46)
        pygame.draw.rect(screen, body, render_rect, border_radius=10)

        # MINIATURA: el fondo real del nivel (el jugador ya sabe a dónde va)
        thumb = pygame.Rect(render_rect.x + 6, render_rect.y + 6,
                            render_rect.w - 12, self.THUMB_H)
        screen.blit(_thumb(level, thumb.w, thumb.h), thumb.topleft)
        pygame.draw.rect(screen, color, thumb, 2)

        # ZONA DE TEXTO SIEMPRE OSCURA: un panel casi negro detrás de nombre,
        # tema y estrellas. Sin él el texto se apoya en el cuerpo de la
        # tarjeta (y en las tarjetas cerradas, en gris sobre gris) y no se
        # lee; con él el contraste es el mismo en las 5 tarjetas.
        scrim = pygame.Rect(render_rect.x + 4, thumb.bottom + 3,
                            render_rect.w - 8,
                            render_rect.bottom - thumb.bottom - 7)
        pygame.draw.rect(screen, (10, 12, 26), scrim, border_radius=8)

        # Marco del nivel, dibujado el último para que quede limpio
        pygame.draw.rect(screen, color, render_rect, 4 if unlocked else 2,
                         border_radius=10)

        if not unlocked:
            veil = pygame.Surface(thumb.size, pygame.SRCALPHA)
            veil.fill((0, 0, 0, 150))
            screen.blit(veil, thumb.topleft)
            label = self.game.get_font(config.FONT_SIZE_SMALL).render(
                "BLOQUEADO", True, (226, 228, 238))
            screen.blit(label, label.get_rect(center=thumb.center))

        # Insignia con el número del nivel (esquina superior izquierda):
        # relleno casi negro + anillo del color del nivel, para que el
        # número se lea igual de bien en los 5 colores.
        badge_center = (thumb.x + 18, thumb.y + 18)
        pygame.draw.circle(screen, (10, 12, 26), badge_center, 15)
        pygame.draw.circle(screen, color, badge_center, 15, 3)
        self.draw_text(screen, str(level), config.FONT_SIZE_SMALL,
                       config.WHITE if unlocked else config.LIGHT_GRAY,
                       *badge_center, center=True)

        # Nombre del nivel y tema matemático (debajo de la miniatura)
        name, topic = LEVEL_INFO[level]
        cx = render_rect.centerx
        name_color = config.WHITE if unlocked else (190, 194, 206)
        topic_color = (206, 212, 228) if unlocked else (156, 160, 176)
        ny = thumb.bottom + 12
        for line in self._wrap(name, config.FONT_SIZE_SMALL,
                               self.CARD_W - 16)[:2]:
            self.draw_text(screen, line, config.FONT_SIZE_SMALL, name_color,
                           cx, ny, center=True)
            ny += 17
        for line in self._wrap(topic, config.FONT_SIZE_SMALL,
                               self.CARD_W - 16)[:2]:
            self.draw_text(screen, line, config.FONT_SIZE_SMALL, topic_color,
                           cx, ny + 2, center=True)
            ny += 17

        # Estrellas del nivel (se ganan al completarlo)
        stars = "★" * level
        self.draw_text(screen, stars, config.FONT_SIZE_SMALL,
                       config.YELLOW if unlocked else (156, 160, 176),
                       cx, render_rect.bottom - 22, center=True)
