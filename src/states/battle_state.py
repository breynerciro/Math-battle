"""
battle_state.py — La pantalla de combate
========================================

Orquesta todo lo que se ve en una batalla, en una sola pantalla:

- SECCIÓN SUPERIOR: fondo del nivel, héroe (izquierda) con su barra de
  HP, enemigo (derecha) con la suya, HUD, mensajes y efectos.
- SECCIÓN INFERIOR: panel RPG clásico con la pregunta matemática, las
  4 opciones (A, B, C, D) y, a la derecha, los botones de menú
  ATACAR / MAGIA / OBJETOS / HUIR. La esquina inferior derecha guarda
  el panel de feedback ("CORRECT: MAGIC 25 DMG" / "INCORRECT: ...").

El flujo de turnos lo calcula CombatSystem; esta clase solo lo
"dibuja y lo hace bonito".
"""

import pygame

from .. import config
from ..combat.combat_system import CombatSystem
from ..combat.effects import FloatingText, HitStop, ParticleSystem, ScreenShake, FlashEffect
from ..entities.enemies import get_level_enemies
from ..entities.player import Player
from ..ui.scenario import Scenario
from ..ui.hud import HUD
from ..ui.sound_manager import SoundManager
from ..ui.transition import Transition
from ..ui.button import Button
from .base_state import BaseState

LETTERS = "ABCD"


class BattleState(BaseState):
    """El combate por turnos contra los enemigos de un nivel."""

    # Posiciones en pantalla: centro horizontal de cada personaje.
    # La vertical se calcula siempre desde el suelo (GROUND_Y) para que
    # estén DE PIE sobre la línea del horizonte, sin tapar las barras.
    HERO_X = 340
    ENEMY_X = 940

    def __init__(self, game, level):
        """Prepara el combate del `level`: enemigos, panel y botones."""
        super().__init__(game)
        self.level = level
        self.sounds = SoundManager()
        self.transition = Transition()

        # Componentes del combate
        self.hud = HUD(game)
        self.particles = ParticleSystem()
        self.shake = ScreenShake()
        self.hitstop = HitStop()
        self.flash = FlashEffect()
        self.floating = []                     # textos flotantes activos
        self.scenario = Scenario(level)        # escenario dinámico con parallax

        # Si venimos de un reintento, el héroe se recupera por completo
        if self.game.player is None or self.game.player.lives <= 0:
            self.game.player = Player()

        # Cola de enemigos del nivel (boss al final)
        self.enemies = get_level_enemies(level)
        self.enemy_index = 0
        self.current_enemy = self.enemies[0]

        # Sistema de combate (la lógica de turnos)
        self.combat = CombatSystem(self.game.player, self.game.challenge_generator)

        # -- Sección inferior: panel de acción -------------------------------
        self.question_active = False      # hay una pregunta en pantalla
        self.challenge = None             # reto del turno actual
        self.feedback = ""                # texto del panel de feedback
        self.feedback_color = config.WHITE
        self.feedback_timer = 0.0

        # Botones de menú RPG (derecha del panel)
        def menu(i, text, on_click, color, hover):
            """Crea un botón de la columna derecha: i es su posición (0-3)."""
            return Button(config.MENU_X,
                          config.MENU_Y + i * config.MENU_BTN_STEP,
                          config.MENU_W, config.MENU_BTN_H, text,
                          on_click=on_click, color=color, hover_color=hover,
                          font_size=config.FONT_SIZE_MEDIUM)

        self.attack_button = menu(0, "» ATACAR «", self._open_challenge,
                                  config.DARK_RED, config.RED)
        self.magic_button = menu(1, "MAGIA",
                                 self._not_ready("La magia aún no está lista"),
                                 config.DARK_BLUE, config.BLUE)
        self.items_button = menu(2, "OBJETOS",
                                 self._not_ready("Aún no tienes objetos"),
                                 config.DARK_BLUE, config.BLUE)
        self.flee_button = menu(3, "HUIR", self._flee,
                                config.DARK_GRAY, config.GRAY)
        self.menu_buttons = (self.attack_button, self.magic_button,
                             self.items_button, self.flee_button)

        # 4 opciones de respuesta (A, B, C, D): clic o teclas 1-4
        self.option_buttons = []
        for i in range(4):
            col, row = i % 2, i // 2
            x = config.QUESTION_X + col * (config.OPTION_W + config.OPTION_GAP)
            y = config.OPTIONS_Y + row * (config.OPTION_H + config.OPTION_GAP)
            button = Button(x, y, config.OPTION_W, config.OPTION_H,
                            f"{LETTERS[i]}) —",
                            on_click=lambda idx=i: self._choose_option(idx),
                            color=config.DARK_BLUE, hover_color=config.BLUE,
                            font_size=config.FONT_SIZE_MEDIUM)
            button.enabled = False
            self.option_buttons.append(button)

        self.can_attack = True

        # Mensaje narrativo del combate ("Slime aparece!", "¡Es tu turno!")
        self.message = "¡Aparece un enemigo!"
        self.message_timer = 2.0

        # Pausa entre acciones (da tiempo a ver las animaciones)
        self.wait_timer = 0.0

        # Resultado pendiente de la pregunta (se anima tras una pausa)
        self.pending_result = None

        # Contadores para el resumen de partida
        self.bosses_defeated = 0
        self.intro_shown = False

        # El enemigo muerto se queda un momento en pantalla (no se borra de golpe)
        self.enemy_death_timer = 0.0
        # La derrota se difiere: dejamos ver el golpe final antes del Game Over
        self.death_pending = False

    # ------------------------------------------------------------------ #
    #  Geometría de la escena
    # ------------------------------------------------------------------ #
    def _feet_y(self, entity):
        """Y del CENTRO del sprite para que la entidad quede de pie sobre
        el suelo, sin importar su altura (héroe, slime o boss)."""
        sprite = entity.sprites.get(entity.current_animation)
        half_h = (sprite.height_px() // 2) if sprite else 40
        return config.GROUND_Y - half_h

    # ------------------------------------------------------------------ #
    #  Entrada / salida del estado
    # ------------------------------------------------------------------ #
    def enter(self):
        """Al entrar: música del combate y presentación del primer enemigo."""
        self.sounds.play_music("boss" if self.current_enemy.is_boss else "battle")
        if not self.intro_shown:
            self.message = f"¡{self.current_enemy.name} aparece!"
            self.message_timer = 2.0
            self.intro_shown = True

    # ------------------------------------------------------------------ #
    #  Turno: abrir la pregunta y responder
    # ------------------------------------------------------------------ #
    def _open_challenge(self):
        """ATACAR: plantea el reto matemático con sus 4 opciones."""
        if not self.can_attack or self.question_active or self.transition.active():
            return
        self.sounds.play("click")
        self.challenge = self.combat.start_challenge(self.current_enemy)
        self.question_active = True
        self.can_attack = False
        for i, button in enumerate(self.option_buttons):
            button.text = f"{LETTERS[i]}) {self.challenge.options[i]}"
            button.color = config.DARK_BLUE
            button.hover_color = config.BLUE
            button.enabled = True
        self.message = "¡Responde para lanzar el hechizo!"
        self.message_timer = 1.5

    def _choose_option(self, index):
        """Eligió una opción (0-3) o se agotó el tiempo (index=None)."""
        if not self.question_active or self.pending_result is not None:
            return
        self.question_active = False
        for i, button in enumerate(self.option_buttons):
            button.enabled = False
            if i == self.challenge.correct_index:
                button.color = config.DARK_GREEN       # la correcta, en verde
            elif i == index:
                button.color = config.DARK_RED         # la equivocada, en rojo

        result = self.combat.submit_option(index)

        # Panel de feedback (esquina inferior derecha) — textos del diseño
        if result["correct"]:
            self.feedback = f"CORRECT: MAGIC {config.HERO_DAMAGE} DMG"
            self.feedback_color = config.GREEN
        else:
            self.feedback = f"INCORRECT: MAGIC {config.COUNTER_DAMAGE} DMG"
            self.feedback_color = config.RED
        self.feedback_timer = 3.0

        self._receive_result(result)

    def _not_ready(self, text):
        """MAGIA/OBJETOS: funcionalidad fuera del alcance del prototipo."""
        def handler():
            """Muestra el mensaje de "próximamente" en la pantalla."""
            self.sounds.play("wrong")
            self.message = text
            self.message_timer = 1.5
        return handler

    def _flee(self):
        """HUIR: abandona la batalla y vuelve al mapa de niveles."""
        if self.transition.active() or self.pending_result is not None:
            return
        self.sounds.play("click")
        self.question_active = False
        from .level_select_state import LevelSelectState
        self.game.change_state(LevelSelectState(self.game))

    # ------------------------------------------------------------------ #
    #  Animación del turno
    # ------------------------------------------------------------------ #
    def _receive_result(self, result):
        """Recibe el resultado de la pregunta y arma la animación del turno."""
        self.pending_result = result
        enemy = self.current_enemy
        player = self.game.player

        if result["correct"]:
            player.play("attack")
            self.sounds.play("attack")
            self.particles.burst(self.ENEMY_X, self._feet_y(enemy) - 30,
                                 color=config.YELLOW, count=18, speed=140)
            if result["enemy_died"]:
                self.enemy_death_timer = 1.2
                self.flash.trigger(config.YELLOW, 100)
                self.hitstop.trigger(0.08)
            self.floating.append(FloatingText(
                f"-{result['damage']}", self.ENEMY_X,
                self._feet_y(enemy) - 90, config.YELLOW, config.FONT_SIZE_LARGE))
            self.floating.append(FloatingText(
                f"+{result['points']}", self.HERO_X,
                self._feet_y(player) - 110, config.GREEN, config.FONT_SIZE_SMALL))
            direction = (self.ENEMY_X - self.HERO_X, 0)
            self.shake.trigger(0.25, 6, direction=direction)
            # Pausa para ver el golpe (más larga si el enemigo muere)
            if result["enemy_died"]:
                self.wait_timer = 1.2
            else:
                self.wait_timer = 0.6
        else:
            if result["timeout"]:
                self.sounds.play("timeout")
            player.play("hurt")
            self.sounds.play("hit")
            direction = (self.HERO_X - self.ENEMY_X, 0)
            self.shake.trigger(0.4, 9, direction=direction)
            self.particles.burst(self.HERO_X, self._feet_y(player) - 30,
                                 color=config.RED, count=16, speed=130)
            self.flash.trigger(config.RED, 80)
            self.hitstop.trigger(0.06)
            self.floating.append(FloatingText(
                f"-{result['damage']}", self.HERO_X,
                self._feet_y(player) - 100, config.RED, config.FONT_SIZE_LARGE))
            # Pausa para ver el contraataque (más larga si cae el héroe)
            if result["player_died"]:
                self.death_pending = True
                self.wait_timer = 1.2
            else:
                self.wait_timer = 0.8

    # ------------------------------------------------------------------ #
    #  Muerte y transiciones
    # ------------------------------------------------------------------ #
    def _on_enemy_death(self):
        """El enemigo actual murió: pasar al siguiente o terminar el nivel."""
        if self.current_enemy.is_boss:
            self.bosses_defeated += 1
        self.enemy_index += 1
        if self.enemy_index < len(self.enemies):
            self.current_enemy = self.enemies[self.enemy_index]
            self.game.player.heal(config.HEAL_BETWEEN_ENEMIES)
            self.message = f"¡{self.current_enemy.name} aparece!"
            self.message_timer = 2.0
            self.sounds.play_music("boss" if self.current_enemy.is_boss else "battle")
        else:
            # Nivel completo → victoria
            from .victory_state import VictoryState
            self.game.change_state(VictoryState(
                self.game, self.level, self.game.player,
                last_level=self.level == config.TOTAL_LEVELS,
                bosses_defeated=self.bosses_defeated))

    def _on_player_death(self):
        """El héroe perdió toda su vida: gasta una vida y reintenta (o game over)."""
        player = self.game.player
        player.lives -= 1
        if player.lives > 0:
            # Reintento del MISMO nivel: el héroe se cura por completo
            # (perder la vida ya fue el castigo) y conserva su puntuación.
            player.heal(player.max_hp)
            self.game.change_state(BattleState(self.game, self.level))
        else:
            from .defeat_state import DefeatState
            # Reintentar el MISMO nivel en el que se cayó
            self.game.change_state(DefeatState(self.game, self.game.player,
                                               level=self.level))

    # ------------------------------------------------------------------ #
    #  Ciclo del estado
    # ------------------------------------------------------------------ #
    def handle_events(self, events):
        """Ratón y teclado: opciones 1-4, botones del menú, Enter y Esc."""
        for event in events:
            # Opciones (solo cuando hay pregunta en pantalla)
            if self.question_active:
                for button in self.option_buttons:
                    button.handle_event(event)
                if event.type == pygame.KEYDOWN:
                    key_map = {pygame.K_1: 0, pygame.K_2: 1,
                               pygame.K_3: 2, pygame.K_4: 3,
                               pygame.K_KP1: 0, pygame.K_KP2: 1,
                               pygame.K_KP3: 2, pygame.K_KP4: 3}
                    if event.key in key_map:
                        self._choose_option(key_map[event.key])

            # Botones del menú (ATACAR/MAGIA/OBJETOS/HUIR)
            for button in self.menu_buttons:
                button.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._open_challenge()
                elif event.key == pygame.K_ESCAPE:
                    # Abandonar la batalla (si no hay animación en curso)
                    if self.pending_result is None and not self.transition.active():
                        self._flee()

    def update(self, dt):
        """Un frame: timers del turno, animaciones, partículas y esperas."""
        player = self.game.player
        enemy = self.current_enemy

        # Estado de los botones del panel
        self.attack_button.enabled = (self.can_attack and
                                      not self.question_active)
        if self.feedback_timer > 0:
            self.feedback_timer -= dt

        if self.hitstop.active():
            self.hitstop.update(dt)
            return

        # Timer del reto: si se agota, se cuenta como respuesta perdida
        if self.question_active:
            self.combat.update(dt)
            if self.challenge is not None and \
                    self.combat.challenge_time >= self.challenge.time_limit:
                self._choose_option(None)

        self.transition.update(dt)
        self.shake.update(dt)
        self.particles.update(dt)
        self.flash.update(dt)
        self.scenario.update(dt)
        player.update(dt)
        enemy.update(dt)

        # El enemigo muerto sigue visible mientras se disipa
        if self.enemy_death_timer > 0:
            self.enemy_death_timer -= dt

        # Textos flotantes
        self.floating = [f for f in self.floating if f.update(dt)]

        # Mensaje narrativo
        if self.message_timer > 0:
            self.message_timer -= dt

        # Espera entre acciones (deja respirar las animaciones)
        if self.wait_timer > 0:
            self.wait_timer -= dt
            if self.wait_timer <= 0 and self.pending_result is not None:
                self._resolve_after_wait()

    def _resolve_after_wait(self):
        """Tras la animación del turno: ¿siguiente enemigo, siguiente turno...?"""
        result, self.pending_result = self.pending_result, None
        if result["correct"]:
            if result["enemy_died"]:
                self._on_enemy_death()
            else:
                self.message = "¡Es tu turno!"
                self.message_timer = 1.5
        elif self.death_pending:
            self.death_pending = False
            self._on_player_death()
        self.can_attack = True       # en ambos casos el jugador vuelve a poder atacar

    # ------------------------------------------------------------------ #
    #  Render
    # ------------------------------------------------------------------ #
    def render(self, screen):
        """Dibuja la pantalla completa: escenario, personajes y panel."""
        # Screen shake: desplaza todo el mundo un poco
        offset_x, offset_y = self.shake.get_offset()

        # Escenario dinámico con parallax y partículas ambientales
        self.scenario.render(screen, offset_x, offset_y)

        # Personajes, DE PIE sobre el suelo (anclados por los pies)
        self.game.player.draw(screen, self.HERO_X + offset_x,
                              self._feet_y(self.game.player) + offset_y)
        if not self.current_enemy.is_dead() or self.enemy_death_timer > 0:
            self.current_enemy.draw(screen, self.ENEMY_X + offset_x,
                                    self._feet_y(self.current_enemy) + offset_y)

        # Partículas y textos flotantes
        self.particles.render(screen)
        for f in self.floating:
            f.render(screen, self.game.get_font)

        # HUD (barras de HP arriba)
        self.hud.render(screen, self.game.player, self.current_enemy,
                        self.level, self.enemy_index, len(self.enemies))

        # Mensaje narrativo (desaparece solo)
        if self.message_timer > 0:
            alpha = min(255, int(self.message_timer * 255))
            font = self.game.get_font(config.FONT_SIZE_MEDIUM)
            surface = font.render(self.message, True, config.YELLOW)
            surface.set_alpha(alpha)
            rect = surface.get_rect(center=(config.SCREEN_WIDTH // 2, 150))
            screen.blit(surface, rect)

        # Sección inferior: panel con pregunta, opciones y botones
        self._render_action_panel(screen)

        # Efecto de flash (después de todo lo demás)
        self.flash.render(screen)

        # Transición (velo negro, SIEMPRE al final)
        self.transition.render(screen)

    # ------------------------------------------------------------------ #
    #  Panel de acción (sección inferior)
    # ------------------------------------------------------------------ #
    def _render_action_panel(self, screen):
        """Dibuja la sección INFERIOR: pregunta, opciones A-D, menú y
        el panel de feedback de la esquina inferior derecha."""
        font_med = self.game.get_font(config.FONT_SIZE_MEDIUM)
        font_small = self.game.get_font(config.FONT_SIZE_SMALL)

        # Marco RPG clásico: borde gris grueso + relleno azul oscuro
        panel = pygame.Rect(config.PANEL_X, config.PANEL_Y,
                            config.PANEL_W, config.PANEL_H)
        pygame.draw.rect(screen, config.LIGHT_GRAY, panel, border_radius=8)
        inner = panel.inflate(-8, -8)
        pygame.draw.rect(screen, config.DARK_BLUE, inner, border_radius=6)
        pygame.draw.rect(screen, config.GRAY, inner, 3, border_radius=6)

        # --- Zona izquierda: la pregunta ------------------------------------
        if self.question_active:
            # Máximo 3 líneas de 24 px; debajo, la barra de tiempo y las opciones
            y = 456
            for line in self._wrap(self.challenge.question,
                                   config.FONT_SIZE_MEDIUM,
                                   config.QUESTION_W)[:3]:
                screen.blit(font_med.render(line, True, config.WHITE),
                            (config.QUESTION_X, y))
                y += 24
            # Barra de tiempo del reto (verde → naranja → rojo)
            ratio = 1.0 - (self.combat.challenge_time /
                           max(1.0, self.challenge.time_limit))
            bar = pygame.Rect(config.QUESTION_X, 524, config.QUESTION_W, 8)
            pygame.draw.rect(screen, config.DARK_GRAY, bar, border_radius=4)
            fill = bar.copy()
            fill.width = max(0, int(bar.width * ratio))
            color = (config.GREEN if ratio > 0.5 else
                     config.ORANGE if ratio > 0.25 else config.RED)
            pygame.draw.rect(screen, color, fill, border_radius=4)
        else:
            if self.can_attack:
                prompt = "Pulsa ATACAR para plantear la pregunta del turno"
            else:
                prompt = "¡Resolviendo el turno...!"
            # Se parte en líneas para que nunca se meta debajo de los
            # botones de la derecha (x = MENU_X)
            y = 464
            for line in self._wrap(prompt, config.FONT_SIZE_MEDIUM,
                                   config.QUESTION_W)[:2]:
                screen.blit(font_med.render(line, True, config.LIGHT_GRAY),
                            (config.QUESTION_X, y))
                y += 24

        # --- Las 4 opciones (A, B, C, D) ------------------------------------
        for i, button in enumerate(self.option_buttons):
            if self.question_active:
                button.update()
                button.render(screen, font_med)
            else:
                # Apagadas: solo el marco con su letra
                pygame.draw.rect(screen, config.DARK_GRAY, button.rect,
                                 border_radius=6)
                pygame.draw.rect(screen, config.GRAY, button.rect, 2,
                                 border_radius=6)
                screen.blit(font_med.render(f"{LETTERS[i]})", True, config.GRAY),
                            (button.rect.x + 12,
                             button.rect.y + button.rect.h // 2 - 8))

        # --- Botones de menú (derecha) --------------------------------------
        for button in self.menu_buttons:
            button.update()
            button.render(screen, font_med)

        # --- Panel de feedback (esquina inferior derecha) -------------------
        fb = pygame.Rect(*config.FEEDBACK_RECT)
        pygame.draw.rect(screen, config.BLACK, fb, border_radius=4)
        pygame.draw.rect(screen, config.LIGHT_GRAY, fb, 2, border_radius=4)
        if self.feedback_timer > 0:
            text, color = self.feedback, self.feedback_color
        elif self.question_active:
            text, color = "ELIGE CON CLIC O TECLAS 1-4", config.YELLOW
        else:
            text, color = "LISTO PARA ATACAR", config.LIGHT_GRAY
        surface = font_small.render(text, True, color)
        screen.blit(surface, (fb.x + 8, fb.y + fb.h // 2 -
                              surface.get_height() // 2))
