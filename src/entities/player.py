"""
player.py — El Héroe Matemático
===============================

Guarda todo el estado del jugador: vida, score, combo, vidas, progreso.
Los SPRITES del héroe se dibujan con cuadrículas de caracteres
(ver sprites.py y animated_sprite.py).

Leyenda de colores del héroe (ver sprites.py):
    S = piel, H = pelo, A = armadura azul, D = azul oscuro,
    R = capa roja, W = blanco, K = negro/contorno
"""

from .. import config
from ..ui.animated_sprite import AnimatedSprite
from .sprites import (PALETTE_HERO, HERO_IDLE, HERO_ATTACK, HERO_HURT,
                      HERO_VICTORY)


class Player:
    """El héroe que controla el estudiante."""

    def __init__(self):
        self.name = "Héroe Matemático"
        self.max_hp = config.PLAYER_MAX_HP
        self.hp = self.max_hp
        self.attack = config.PLAYER_ATTACK
        self.defense = config.PLAYER_DEFENSE
        self.lives = config.PLAYER_LIVES
        self.score = 0
        self.combo = 0              # respuestas correctas seguidas
        self.max_combo = 0          # récord de combo de esta partida
        self.correct_count = 0      # total de aciertos
        self.wrong_count = 0        # total de errores
        self.level_unlocked = 1     # progreso

        # -- Sprites animados (se crean con código, sin imágenes) ---------
        self.sprites = {
            "idle": AnimatedSprite(HERO_IDLE, PALETTE_HERO, pixel_size=8, fps=4),
            "attack": AnimatedSprite(HERO_ATTACK, PALETTE_HERO, pixel_size=8,
                                     fps=12, loop=False),
            "hurt": AnimatedSprite(HERO_HURT, PALETTE_HERO, pixel_size=8,
                                   fps=10, loop=False),
            "victory": AnimatedSprite(HERO_VICTORY, PALETTE_HERO, pixel_size=8, fps=6),
        }
        self.current_animation = "idle"

    # ------------------------------------------------------------------ #
    #  Acciones de combate
    # ------------------------------------------------------------------ #
    def play(self, animation):
        """Cambia de animación y la reinicia desde el primer frame."""
        if animation in self.sprites:
            self.current_animation = animation
            self.sprites[animation].reset()

    def take_damage(self, damage):
        """Recibe daño (la defensa lo reduce un poco). Devuelve el daño real."""
        real = max(1, damage - self.defense)
        self.hp = max(0, self.hp - real)
        self.play("hurt")
        return real

    def heal(self, amount):
        """Recupera vida sin pasarse del máximo."""
        self.hp = min(self.max_hp, self.hp + amount)

    def is_dead(self):
        return self.hp <= 0

    # ------------------------------------------------------------------ #
    #  Puntuación y combos
    # ------------------------------------------------------------------ #
    def register_correct(self, challenge, response_time):
        """Suma puntos por respuesta correcta: base + velocidad + combo.

        Args:
            challenge:     el MathChallenge respondido
            response_time: segundos que tardó el jugador
        """
        points = challenge.points
        # Bonus por velocidad: mientras más rápido, más puntos (hasta +50)
        speed_bonus = int(config.SPEED_BONUS_MAX *
                          max(0.0, 1.0 - response_time / challenge.time_limit))
        # Bonus por combo: +20 por cada respuesta en racha (máx 10)
        combo_bonus = min(self.combo, config.MAX_COMBO) * config.COMBO_BONUS_PER
        total = points + speed_bonus + combo_bonus
        self.score += total
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.correct_count += 1
        return total

    def register_wrong(self):
        """Registra un error: rompe el combo."""
        self.combo = 0
        self.wrong_count += 1

    # ------------------------------------------------------------------ #
    def draw(self, screen, x, y):
        """Dibuja al héroe con su animación actual."""
        sprite = self.sprites[self.current_animation]
        sprite.render(screen, x, y)

    def update(self, dt):
        sprite = self.sprites[self.current_animation]
        sprite.update(dt)
        # Las animaciones de golpe/ataque vuelven a "idle" al terminar
        if sprite.finished and self.current_animation in ("hurt", "attack"):
            self.current_animation = "idle"
