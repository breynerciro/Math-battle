"""
hud.py — HUD (Heads-Up Display) del combate
===========================================

Estilo RPG clásico: la información de CADA personaje vive en SU esquina
superior (héroe a la izquierda, enemigo a la derecha), con el nombre
encima de su barra de vida. El centro muestra puntos, nivel y combo.
"""

import pygame

from .. import config

# Posiciones de los paneles (esquinas superiores)
BAR_W = 280
BAR_H = 22
HERO_PANEL = (24, 64)          # esquina superior izquierda
ENEMY_PANEL = (config.SCREEN_WIDTH - 24 - BAR_W, 64)   # arriba a la derecha


class HUD:
    """Dibuja toda la información del combate."""

    def __init__(self, game):
        """Guarda la referencia al Game (para acceder a las fuentes)."""
        self.game = game

    # ------------------------------------------------------------------ #
    def _draw_bar(self, screen, x, y, w, h, ratio, color_front, label=""):
        """Dibuja una barra de vida con borde y texto 'hp/max'."""
        ratio = max(0.0, min(1.0, ratio))
        # Fondo (vida perdida)
        pygame.draw.rect(screen, config.DARK_RED, (x, y, w, h), border_radius=3)
        # Vida actual
        if ratio > 0:
            pygame.draw.rect(screen, color_front,
                             (x, y, int(w * ratio), h), border_radius=3)
        # Borde
        pygame.draw.rect(screen, config.WHITE, (x, y, w, h), 2, border_radius=3)
        if label:
            font = self.game.get_font(config.FONT_SIZE_SMALL)
            surface = font.render(label, True, config.WHITE)
            screen.blit(surface, (x + 4, y + 2))

    # ------------------------------------------------------------------ #
    def render(self, screen, player, enemy, level, enemy_index, total_enemies):
        """Dibuja el HUD completo.

        Args:
            player:       objeto Player
            enemy:        objeto Enemy actual (o None)
            level:        nivel actual (1-5)
            enemy_index:  índice del enemigo actual (0-based)
            total_enemies: cuántos enemigos tiene el nivel
        """
        font_small = self.game.get_font(config.FONT_SIZE_SMALL)
        font_med = self.game.get_font(config.FONT_SIZE_MEDIUM)

        # --- Franja superior -------------------------------------------------
        pygame.draw.rect(screen, config.BLACK, (0, 0, config.SCREEN_WIDTH, 44))
        pygame.draw.line(screen, config.YELLOW, (0, 44),
                         (config.SCREEN_WIDTH, 44), 2)

        # --- Panel del héroe (arriba a la izquierda) --------------------------
        hx, hy = HERO_PANEL
        name_surf = font_small.render(player.name, True, config.WHITE)
        screen.blit(name_surf, (hx, hy))
        self._draw_bar(screen, hx, hy + 20, BAR_W, BAR_H,
                       player.hp / player.max_hp,
                       config.GREEN, f"{player.hp}/{player.max_hp}")

        # --- Panel del enemigo (arriba a la derecha) ---------------------------
        if enemy is not None:
            ex, ey = ENEMY_PANEL
            prefix = "BOSS: " if enemy.is_boss else ""
            name_surf = font_small.render(prefix + enemy.name, True, config.WHITE)
            # Alineado a la derecha para que quede sobre su barra
            screen.blit(name_surf, (ex + BAR_W - name_surf.get_width(), ey))
            self._draw_bar(screen, ex, ey + 20, BAR_W, BAR_H,
                           enemy.hp / enemy.max_hp,
                           config.RED, f"{enemy.hp}/{enemy.max_hp}")

        # --- Centro: corazones, puntos, nivel ----------------------------------
        hearts = "♥" * player.lives + "·" * max(0, config.PLAYER_LIVES - player.lives)
        surface = font_med.render(hearts, True, config.RED)
        screen.blit(surface, (16, 12))

        surface = font_med.render(f"★ {player.score}", True, config.YELLOW)
        score_rect = surface.get_rect()
        score_rect.centerx = config.SCREEN_WIDTH // 2 - 70
        score_rect.y = 12
        screen.blit(surface, score_rect)

        # Nivel + progreso de enemigos, centrado en el hueco derecho
        # (el panel del enemigo empieza más abajo: y=52, aquí hay espacio)
        surface = font_med.render(
            f"Nivel {level}  •  {min(enemy_index + 1, total_enemies)}/{total_enemies}",
            True, config.WHITE)
        lvl_rect = surface.get_rect()
        lvl_rect.centerx = config.SCREEN_WIDTH // 2 + 150
        lvl_rect.y = 12
        screen.blit(surface, lvl_rect)

        # Combo (solo si hay racha activa), parpadea junto a los corazones
        if player.combo >= 2 and (pygame.time.get_ticks() // 300) % 2 == 0:
            surface = font_small.render(f"COMBO x{player.combo}!", True,
                                        config.ORANGE)
            screen.blit(surface, (24, 116))
