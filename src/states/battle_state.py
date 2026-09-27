"""
battle_state.py — La pantalla de combate
========================================

Orquesta todo lo que se ve en una batalla:
- fondo del nivel, héroe (izquierda) y enemigo (derecha)
- HUD con barras de vida, puntos y vidas
- botón ATACAR (que abre la pregunta matemática)
- animaciones de ataque/daño con pausas de accción

El flujo de turnos lo calcula CombatSystem; esta clase solo lo
"dibuja y lo hace bonito".
"""

import pygame

from .. import config
from ..combat.combat_system import CombatSystem
from ..combat.effects import FloatingText, ParticleSystem, ScreenShake
from ..entities.enemies import get_level_enemies
from ..entities.player import Player
from ..ui.background import get_background
from ..ui.button import Button
from ..ui.hud import HUD
from ..ui.sound_manager import SoundManager
from ..ui.transition import Transition
from .base_state import BaseState


class BattleState(BaseState):
    """El combate por turnos contra los enemigos de un nivel."""

    # Posiciones en pantalla: centro horizontal de cada personaje.
    # La vertical se calcula siempre desde el suelo (GROUND_Y) para que
    # estén DE PIE sobre la línea del horizonte, sin tapar las barras.
    HERO_X = 240
    ENEMY_X = 720

    def __init__(self, game, level):
        super().__init__(game)
        self.level = level
        self.sounds = SoundManager()
        self.transition = Transition()

        # Componentes del combate
        self.hud = HUD(game)
        self.particles = ParticleSystem()
        self.shake = ScreenShake()
        self.floating = []                     # textos flotantes activos

        # Si venimos de un reintento, el héroe se recupera por completo
        if self.game.player is None or self.game.player.lives <= 0:
            self.game.player = Player()

        # Cola de enemigos del nivel (boss al final)
        self.enemies = get_level_enemies(level)
        self.enemy_index = 0
        self.current_enemy = self.enemies[0]

        # Sistema de combate (la lógica de turnos)
        self.combat = CombatSystem(self.game.player, self.game.challenge_generator)

        # Botón de ataque (bloqueado durante las animaciones)
        self.attack_button = Button(
            config.SCREEN_WIDTH // 2 - 90, config.SCREEN_HEIGHT - 80,
            180, 54, "» ATACAR «", on_click=self._open_challenge,
            color=config.DARK_RED, hover_color=config.RED,
            font_size=config.FONT_SIZE_LARGE)
        self.can_attack = True

        # Mensaje narrativo del combate ("Slime aparece!", "¡Es tu turno!")
        self.message = "¡Aparece un enemigo!"
        self.message_timer = 2.0

        # Pausa entre acciones (da tiempo a ver las animaciones)
        self.wait_timer = 0.0

        # Resultado pendiente de la pregunta (llega desde MathChallengeState)
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
        self.sounds.play_music("boss" if self.current_enemy.is_boss else "battle")
        if not self.intro_shown:
            self.message = f"¡{self.current_enemy.name} aparece!"
            self.message_timer = 2.0
            self.intro_shown = True

    # ------------------------------------------------------------------ #
    #  Apertura del reto matemático
    # ------------------------------------------------------------------ #
    def _open_challenge(self):
        if not self.can_attack or self.transition.active():
            return
        self.sounds.play("click")
        self.can_attack = False
        # Import local para evitar imports circulares entre estados
        from .math_challenge_state import MathChallengeState
        self.game.push_state(MathChallengeState(self.game, self.combat,
                                                self.current_enemy))

    def _receive_result(self, result):
        """Recibe el resultado de la pregunta y arma la animación del turno."""
        self.pending_result = result
        enemy = self.current_enemy
        player = self.game.player

        if result["correct"]:
            player.play("attack")
            self.sounds.play("attack")
            self.particles.burst(self.ENEMY_X, self._feet_y(enemy) - 30,
                                 color=config.YELLOW)
            if result["enemy_died"]:
                self.enemy_death_timer = 1.2
            self.floating.append(FloatingText(
                f"-{result['damage']}", self.ENEMY_X,
                self._feet_y(enemy) - 90, config.YELLOW, config.FONT_SIZE_LARGE))
            self.floating.append(FloatingText(
                f"+{result['points']}", self.HERO_X,
                self._feet_y(player) - 110, config.GREEN, config.FONT_SIZE_SMALL))
            self.shake.trigger(0.25, 5)
            if result["enemy_died"]:
                self.wait_timer = 1.2      # deja ver la muerte del enemigo
            else:
                self.wait_timer = 0.6
        else:
            if result["timeout"]:
                self.sounds.play("timeout")
            player.play("hurt")
            self.sounds.play("hit")
            self.shake.trigger(0.4, 8)
            self.particles.burst(self.HERO_X, self._feet_y(player) - 30,
                                 color=config.RED)
            self.floating.append(FloatingText(
                f"-{result['damage']}", self.HERO_X,
                self._feet_y(player) - 100, config.RED, config.FONT_SIZE_LARGE))
            if result["player_died"]:
                self.death_pending = True
                self.wait_timer = 1.2    # deja ver la caída del héroe
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
        for event in events:
            if self.can_attack:
                self.attack_button.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Solo se puede salir si no hay animación en curso
                    if self.can_attack and not self.transition.active():
                        from .level_select_state import LevelSelectState
                        self.game.change_state(LevelSelectState(self.game))

    def update(self, dt):
        player = self.game.player
        enemy = self.current_enemy

        self.transition.update(dt)
        self.shake.update(dt)
        self.particles.update(dt)
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
    def render(self, screen):
        # Screen shake: desplaza todo el mundo un poco
        offset_x, offset_y = self.shake.get_offset()

        # Fondo del nivel (cacheado)
        screen.blit(get_background(self.level), (offset_x, offset_y))

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

        # HUD
        self.hud.render(screen, self.game.player, self.current_enemy,
                        self.level, self.enemy_index, len(self.enemies))

        # Mensaje narrativo (desaparece solo)
        if self.message_timer > 0:
            alpha = min(255, int(self.message_timer * 255))
            font = self.game.get_font(config.FONT_SIZE_MEDIUM)
            surface = font.render(self.message, True, config.YELLOW)
            surface.set_alpha(alpha)
            rect = surface.get_rect(center=(config.SCREEN_WIDTH // 2, 100))
            screen.blit(surface, rect)

        # Botón atacar
        self.attack_button.update()          # hover check cada frame
        self.attack_button.render(screen, self.game.get_font(
            self.attack_button.font_size))

        # Transición (velo negro, SIEMPRE al final)
        self.transition.render(screen)
