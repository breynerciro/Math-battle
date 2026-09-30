"""
player.py — El Héroe Matemático
===============================

Guarda todo el estado del jugador: vida, score, combo, vidas, progreso.
Sus sprites se cargan desde assets/sprites/hero/ (ver sprites.py).

Leyenda de colores del héroe (PNGs generados con tools/generate_sprites.py):
    S = piel, H = pelo, A = armadura azul, D = azul oscuro,
    R = capa roja, W = blanco, K = negro/contorno
"""

from .. import config
from .sprites import HERO_ANIM_SPECS, HERO_DIR, load_entity


class Player:
    """El héroe que controla el estudiante."""

    def __init__(self) -> None:
        """Crea al héroe con vida, puntuación y animaciones al máximo."""
        # -- Identidad ------------------------------------------------------
        self.name: str = "Matías"

        # -- Combate --------------------------------------------------------
        self.max_hp: int = config.PLAYER_MAX_HP
        self.hp: int = self.max_hp
        self.attack: int = config.PLAYER_ATTACK
        self.defense: int = config.PLAYER_DEFENSE
        self.lives: int = config.PLAYER_LIVES

        # -- Puntuación -------------------------------------------------------
        self.score: int = 0
        self.combo: int = 0              # respuestas correctas seguidas
        self.max_combo: int = 0          # récord de combo de esta partida
        self.correct_count: int = 0      # total de aciertos
        self.wrong_count: int = 0        # total de errores
        self.level_unlocked: int = 1     # progreso

        # -- Animaciones (PNG cargados una sola vez) ------------------------
        self.sprites: dict = load_entity(HERO_DIR, HERO_ANIM_SPECS)
        self.current_animation: str = "idle"

    # ------------------------------------------------------------------ #
    #  Acciones de combate
    # ------------------------------------------------------------------ #
    def play(self, animation: str) -> None:
        """Cambia de animación y la reinicia desde el primer frame."""
        if animation in self.sprites:
            self.current_animation = animation
            self.sprites[animation].reset()

    def take_damage(self, damage: int) -> int:
        """Recibe daño. Devuelve el daño real (es el daño del contraataque)."""
        self.hp = max(0, self.hp - damage)
        self.play("hurt")
        return damage

    def heal(self, amount: int) -> None:
        """Recupera vida sin pasarse del máximo."""
        self.hp = min(self.max_hp, self.hp + amount)

    def is_dead(self) -> bool:
        """True cuando la vida del héroe llegó a 0."""
        return self.hp <= 0

    # ------------------------------------------------------------------ #
    #  Puntuación y combos
    # ------------------------------------------------------------------ #
    def register_correct(self, challenge, response_time: float) -> int:
        """Suma puntos por respuesta correcta: base + velocidad + combo.

        Args:
            challenge:     el MathChallenge respondido
            response_time: segundos que tardó el jugador
        """
        # Bonus por velocidad: mientras más rápido, más puntos (hasta +50)
        speed_bonus = int(config.SPEED_BONUS_MAX *
                          max(0.0, 1.0 - response_time / challenge.time_limit))
        # Bonus por combo: +20 por cada respuesta en racha (máx 10)
        combo_bonus = min(self.combo, config.MAX_COMBO) * config.COMBO_BONUS_PER

        total_points = challenge.points + speed_bonus + combo_bonus
        self.score += total_points

        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.correct_count += 1
        return total_points

    def register_wrong(self) -> None:
        """Registra un error: rompe el combo."""
        self.combo = 0
        self.wrong_count += 1

    # ------------------------------------------------------------------ #
    def draw(self, screen, x: int, y: int) -> None:
        """Dibuja al héroe con su animación actual."""
        self.sprites[self.current_animation].render(screen, x, y)

    def update(self, dt: float) -> None:
        """Un frame: avanza la animación actual del héroe."""
        sprite = self.sprites[self.current_animation]
        sprite.update(dt)
        # Las animaciones de golpe/ataque vuelven a "idle" al terminar
        if sprite.finished and self.current_animation in ("hurt", "attack"):
            self.current_animation = "idle"
