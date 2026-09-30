"""
enemy.py — Clase base de todos los enemigos
===========================================

Un enemigo sabe:
- cuánta vida tiene y qué daño hace,
- qué TEMA matemático usa para sus retos y con qué dificultad,
- cómo dibujarse: carga sus PNG desde assets/sprites/enemies/<nombre>/
  usando el nombre de su clase (BasicDragon → basic_dragon).
"""

import pygame

from ..math_engine.challenge import MathTopic
from ..ui.animated_sprite import AnimatedSprite
from .sprites import (ENEMIES_DIR, ENEMY_ANIM_SPECS, HIT_STAR_FPS,
                      EFFECTS_DIR, load_entity)


class Enemy:
    """Enemigo genérico. Los hijos solo definen estadísticas."""

    # Carpeta de sprites dentro de assets/sprites/enemies/ (opcional).
    # Si es None, se usa el nombre de la clase en snake_case.
    SPRITE_NAME: str | None = None
    # Tamaño en pantalla de los PNG (1 = tal cual el archivo)
    PIXEL_SIZE: int = 1

    def __init__(self, name: str, hp: int, attack: int,
                 math_topic: MathTopic, difficulty: int,
                 is_boss: bool = False) -> None:
        """Crea el enemigo con sus estadísticas y carga sus PNG."""
        # -- Identidad ------------------------------------------------------
        self.name: str = name

        # -- Combate ----------------------------------------------------------
        self.max_hp: int = hp
        self.hp: int = hp
        self.attack: int = attack
        self.math_topic: MathTopic = math_topic   # tema de sus retos
        self.difficulty: int = difficulty          # 1 a 5
        self.is_boss: bool = is_boss

        # -- Animaciones (PNG en assets/sprites/enemies/) -------------------
        sprite_name = self.SPRITE_NAME or to_sprite_name(type(self).__name__)
        sprite_dir = ENEMIES_DIR / sprite_name
        fallback = ENEMIES_DIR / "generic"
        self.sprites: dict = load_entity(sprite_dir, ENEMY_ANIM_SPECS,
                                         fallback_dir=fallback)
        self.current_animation: str = "idle"

        # Efecto de estrella que aparece al recibir un golpe
        self.hit_effect: AnimatedSprite = AnimatedSprite.load(
            EFFECTS_DIR / "star", fps=HIT_STAR_FPS, loop=False)

    # ------------------------------------------------------------------ #
    def play(self, animation: str) -> None:
        """Cambia de animación y la reinicia desde su primer frame."""
        if animation in self.sprites:
            self.current_animation = animation
            self.sprites[animation].reset()

    def take_damage(self, damage: int) -> int:
        """Recibe daño y muestra el efecto de golpe. Devuelve el daño real."""
        self.hp = max(0, self.hp - damage)
        self.play("hurt")
        self.hit_effect.reset()
        return damage

    def is_dead(self) -> bool:
        """True cuando se le acabó la vida (HP <= 0)."""
        return self.hp <= 0

    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        """Un frame: avanza la animación y el efecto de estrella."""
        sprite = self.sprites[self.current_animation]
        sprite.update(dt)
        if sprite.finished and self.current_animation == "hurt":
            self.current_animation = "idle"
        self.hit_effect.update(dt)

    def draw(self, screen: pygame.Surface, x: int, y: int) -> None:
        """Dibuja al enemigo con su animación actual en (x, y)."""
        self.sprites[self.current_animation].render(screen, x, y)
        # Si la estrella de golpe está activa, dibujarla sobre el enemigo
        if not self.hit_effect.finished:
            self.hit_effect.render(screen, x, y - 20)


def to_sprite_name(class_name: str) -> str:
    """BasicDragon → basic_dragon (convención de carpetas de sprites)."""
    result = []
    for index, char in enumerate(class_name):
        if char.isupper() and index > 0:
            result.append("_")
        result.append(char.lower())
    return "".join(result)
