"""
menu_state.py — Menú principal (pantalla de inicio)
===================================================

La primera pantalla de Math Battle. Composición:

- Fondo con degradado en bandas (estilo retro, sin mezclas suaves),
  suelo en el que apoya el héroe y símbolos matemáticos flotando.
- PLACA DE TÍTULO con el nombre del juego, borde amarillo y sombra.
- El héroe animado a la izquierda, con su sombra y su nombre.
- Cuatro botones: JUGAR / CRÉDITOS / SALIR y el interruptor MÚSICA
  (esquina superior derecha) que apaga la música y lo guarda.
- Panel inferior con el récord guardado y el progreso (nivel más alto).
"""

import math
import random

import pygame

from .. import config
from ..ui.button import Button
from ..ui.sound_manager import SoundManager
from .base_state import BaseState
from .credits_state import CreditsState
from .level_select_state import LevelSelectState

# Suelo de la escena: los pies del héroe y la línea del horizonte
GROUND_TOP = 636
HERO_X = 176                 # centro del héroe (izquierda de la escena)
TITLE = "MATH BATTLE"
SUBTITLE = "COMBATE POR TURNOS CON MATEMÁTICAS"


class MenuState(BaseState):
    """Pantalla de inicio del juego."""

    def __init__(self, game):
        """Crea los botones (incluido el de música) y los símbolos flotantes."""
        super().__init__(game)
        self.sounds = SoundManager()
        self.time = 0.0
        self.save_data = game.save_system.load()

        center_x = config.SCREEN_WIDTH // 2
        self.buttons = [
            Button(center_x - 160, 300, 320, 56, "JUGAR",
                   on_click=self._start_game, font_size=config.FONT_SIZE_LARGE,
                   color=(36, 120, 64), hover_color=config.GREEN),
            Button(center_x - 160, 372, 320, 56, "CRÉDITOS",
                   on_click=self._go_credits, font_size=config.FONT_SIZE_LARGE,
                   color=config.DARK_BLUE, hover_color=config.BLUE),
            Button(center_x - 160, 444, 320, 56, "SALIR",
                   on_click=self.game.quit, font_size=config.FONT_SIZE_LARGE,
                   color=(96, 44, 44), hover_color=config.RED),
        ]

        # Botón de MÚSICA (esquina superior derecha): apaga/enciende la
        # música de fondo y guarda la preferencia en save_data.json.
        self.music_button = Button(config.SCREEN_WIDTH - 224, 56, 200, 44,
                                   "MÚSICA: SÍ", on_click=self._toggle_music,
                                   font_size=config.FONT_SIZE_MEDIUM)
        self._refresh_music_button()

        # Símbolos matemáticos flotando de fondo (solo decoración).
        # Se les da distinto tono y tamaño para que no todos se lean igual.
        self.symbols = []
        for i in range(18):
            self.symbols.append({
                "char": random.choice("+-×÷=√π"),
                "x": random.uniform(0, config.SCREEN_WIDTH),
                "y": random.uniform(0, config.SCREEN_HEIGHT),
                "speed": random.uniform(12, 34),
                "size": random.choice([config.FONT_SIZE_SMALL,
                                       config.FONT_SIZE_MEDIUM]),
                "bright": i % 4 == 0,      # uno de cada cuatro es cálido
            })

    # ------------------------------------------------------------------ #
    def enter(self):
        """Al entrar: aplica la preferencia de música, la melodía y el récord."""
        # 1) Progreso guardado (cada vez que volvemos al menú)
        self.save_data = self.game.save_system.load()
        # 2) Música: si el jugador la apagó, se queda apagada
        SoundManager.set_muted(not self.save_data.get("music_on", True))
        self._refresh_music_button()
        # 3) Melodía del menú (si está apagada, solo se anota la pista)
        self.sounds.play_music("menu")

    # ------------------------------------------------------------------ #
    def _toggle_music(self):
        """Música ON/OFF: silencia, actualiza el botón y lo guarda."""
        muted = SoundManager.toggle_mute()
        self._refresh_music_button()
        self.sounds.play("click")          # los efectos NO se silencian
        self.save_data["music_on"] = not muted
        self.game.save_system.save(self.save_data)

    def _refresh_music_button(self):
        """Texto y colores del botón según el estado actual de la música."""
        muted = SoundManager.is_muted()
        self.music_button.text = "MÚSICA: NO" if muted else "MÚSICA: SÍ"
        self.music_button.color = (96, 44, 44) if muted else (36, 120, 64)
        self.music_button.hover_color = config.RED if muted else config.GREEN

    # ------------------------------------------------------------------ #
    def _start_game(self):
        """JUGAR → pasa al mapa de selección de niveles."""
        self.sounds.play("click")
        self.game.change_state(LevelSelectState(self.game))

    def _go_credits(self):
        """CRÉDITOS → muestra la pantalla de créditos."""
        self.sounds.play("click")
        self.game.change_state(CreditsState(self.game))

    # ------------------------------------------------------------------ #
    def handle_events(self, events):
        """Pasa cada evento a los 4 botones (ellos solos detectan el clic)."""
        for event in events:
            for button in (*self.buttons, self.music_button):
                button.handle_event(event)

    def update(self, dt):
        """Un frame: avanza botones, símbolos y la animación del héroe."""
        self.time += dt
        for button in (*self.buttons, self.music_button):
            button.update(dt)

        # Los símbolos flotan hacia arriba y reaparecen por abajo
        for s in self.symbols:
            s["y"] -= s["speed"] * dt
            if s["y"] < -20:
                s["y"] = config.SCREEN_HEIGHT + 20
                s["x"] = random.uniform(0, config.SCREEN_WIDTH)

        # El héroe respira en su idle
        if self.game.player is None:
            from ..entities.player import Player
            self.game.player = Player()
        self.game.player.update(dt)

    # ------------------------------------------------------------------ #
    #  Dibujo por capas
    # ------------------------------------------------------------------ #
    def _render_background(self, screen):
        """Cielo en bandas horizontales + suelo con línea de horizonte."""
        top, bottom = (8, 10, 26), (30, 40, 86)
        bands = 14
        h = config.SCREEN_HEIGHT // bands
        for i in range(bands):
            t = i / (bands - 1)
            col = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
            y = i * h
            height = h if i < bands - 1 else config.SCREEN_HEIGHT - y
            pygame.draw.rect(screen, col, (0, y, config.SCREEN_WIDTH, height))

        # Estrellas tenues en la franja alta (parpadean suavemente)
        for i in range(26):
            x = int((i * 97) % config.SCREEN_WIDTH)
            y = int((i * 53) % 240)
            tw = int(90 + 70 * math.sin(self.time * 2 + i))
            pygame.draw.circle(screen, (200, 210, 255, tw), (x, y),
                               1 + (i % 2))

        # Símbolos matemáticos de fondo
        for s in self.symbols:
            color = (140, 118, 46) if s["bright"] else (46, 62, 122)
            self.draw_text(screen, s["char"], s["size"], color,
                           s["x"], s["y"])

        # Suelo: franja oscura con doble línea de luz
        pygame.draw.rect(screen, (34, 32, 50),
                         (0, GROUND_TOP, config.SCREEN_WIDTH,
                          config.SCREEN_HEIGHT - GROUND_TOP))
        pygame.draw.line(screen, (92, 88, 120),
                         (0, GROUND_TOP), (config.SCREEN_WIDTH, GROUND_TOP), 3)
        pygame.draw.line(screen, (54, 52, 72), (0, GROUND_TOP + 7),
                         (config.SCREEN_WIDTH, GROUND_TOP + 7), 1)

    def _render_title(self, screen):
        """Placa central con el título del juego (sombra + borde amarillo)."""
        cx = config.SCREEN_WIDTH // 2
        plate = pygame.Rect(cx - 400, 58, 800, 118)
        pygame.draw.rect(screen, (16, 18, 44), plate, border_radius=12)
        pygame.draw.rect(screen, config.YELLOW, plate, 4, border_radius=12)
        inner = plate.inflate(-12, -12)
        pygame.draw.rect(screen, (74, 78, 146), inner, 2, border_radius=8)

        # Gemas decorativas a los lados de la placa
        for gx in (plate.x + 26, plate.right - 36):
            pygame.draw.rect(screen, config.CYAN, (gx, plate.centery - 6, 12, 12))
            pygame.draw.rect(screen, config.WHITE,
                             (gx, plate.centery - 6, 12, 12), 2)

        # Título con sombra dura (estilo pixel art)
        self.draw_text(screen, TITLE, config.FONT_SIZE_TITLE, config.BLACK,
                       cx + 5, 110, center=True)
        self.draw_text(screen, TITLE, config.FONT_SIZE_TITLE, config.YELLOW,
                       cx, 105, center=True)
        self.draw_text(screen, SUBTITLE, config.FONT_SIZE_SMALL, config.CYAN,
                       cx, 150, center=True)

    def _render_hero(self, screen):
        """El héroe de pie sobre el suelo, con sombra y cartela con su nombre."""
        if self.game.player is None:
            from ..entities.player import Player
            self.game.player = Player()
        player = self.game.player

        # Sombra elíptica bajo los pies (superficie con alfa)
        shadow = pygame.Surface((160, 34), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 110), (0, 0, 160, 34))
        screen.blit(shadow, (HERO_X - 80, GROUND_TOP - 16))

        # Sprite centrado por su centro, con los pies EXACTAMENTE en el suelo
        sprite = player.sprites.get(player.current_animation)
        half_h = (sprite.height_px() // 2) if sprite else 80
        player.draw(screen, HERO_X, GROUND_TOP - half_h)

        # Nombre del héroe sobre el suelo
        self.draw_text(screen, player.name.upper(), config.FONT_SIZE_SMALL,
                       config.LIGHT_GRAY, HERO_X, GROUND_TOP + 34, center=True)

    def _render_info(self, screen):
        """Panel con récord y progreso + pista de controles al pie."""
        cx = config.SCREEN_WIDTH // 2
        high = self.save_data.get("high_score", 0)
        highest = self.save_data.get("highest_level", 1)

        panel = pygame.Rect(cx - 340, 556, 680, 52)
        pygame.draw.rect(screen, (16, 18, 44), panel, border_radius=8)
        pygame.draw.rect(screen, config.GRAY, panel, 2, border_radius=8)
        # Dos medallas laterales con el acento del color de progreso
        pygame.draw.rect(screen, config.YELLOW, (panel.x, panel.y, 6, panel.h))
        pygame.draw.rect(screen, config.CYAN, (panel.right - 6, panel.y,
                                               6, panel.h))

        self.draw_text(screen, f"RÉCORD: {high} PTS", config.FONT_SIZE_SMALL,
                       config.YELLOW, cx - 160, panel.centery, center=True)
        pygame.draw.line(screen, config.GRAY, (cx, panel.y + 10),
                         (cx, panel.bottom - 10), 2)
        self.draw_text(screen,
                       f"PROGRESO: NIVEL {highest}/{config.TOTAL_LEVELS}",
                       config.FONT_SIZE_SMALL, config.CYAN,
                       cx + 170, panel.centery, center=True)

    def render(self, screen):
        """Dibuja todas las capas: fondo, título, héroe, botones y panel."""
        self._render_background(screen)
        self._render_title(screen)
        self._render_hero(screen)
        for button in (*self.buttons, self.music_button):
            button.render(screen, self.game.get_font(button.font_size))
        self._render_info(screen)
