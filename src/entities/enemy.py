"""
enemy.py — Clase base de todos los enemigos
===========================================

Un enemigo sabe:
- cuánta vida tiene y qué daño hace,
- qué TEMA matemático usa para sus retos y con qué dificultad,
- cómo dibujarse (sprites por código) y animarse.
"""

import pygame

from .. import config
from ..math_engine.challenge import MathTopic
from ..ui.animated_sprite import AnimatedSprite
from .sprites import PALETTE_GREEN, EFFECT_STAR, PALETTE_EFFECTS


class Enemy:
    """Enemigo genérico. Los de cada nivel pasan sus propios sprites."""

    # Sprites por defecto (los hijos pueden sobreescribirlos)
    SPRITES = None       # dict {"idle": [...], "hurt": [...]}
    PALETTE = PALETTE_GREEN

    def __init__(self, name, hp, attack, math_topic, difficulty, is_boss=False,
                 pixel_size=7):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.math_topic = math_topic            # MathTopic de sus retos
        self.difficulty = difficulty             # 1 a 5
        self.is_boss = is_boss
        self.pixel_size = 8 if is_boss else pixel_size

        # Construye sus animaciones a partir de SPRITES (cuadrículas)
        grids = self.SPRITES or ENEMY_GENERIC
        self.sprites = {}
        for anim_name, frames in grids.items():
            self.sprites[anim_name] = AnimatedSprite(
                frames, self.PALETTE, pixel_size=self.pixel_size,
                fps=3 if anim_name == "idle" else 10,
                loop=(anim_name == "idle"))
        self.current_animation = "idle"

        # Efecto de estrella que aparece al recibir un golpe
        self.hit_effect = AnimatedSprite(EFFECT_STAR, PALETTE_EFFECTS,
                                         pixel_size=6, fps=18, loop=False)

    # ------------------------------------------------------------------ #
    def play(self, animation):
        if animation in self.sprites:
            self.current_animation = animation
            self.sprites[animation].reset()

    def take_damage(self, damage):
        """Recibe daño y muestra el efecto de golpe. Devuelve el daño real."""
        self.hp = max(0, self.hp - damage)
        self.play("hurt")
        self.hit_effect.reset()
        return damage

    def is_dead(self):
        return self.hp <= 0

    # ------------------------------------------------------------------ #
    def update(self, dt):
        sprite = self.sprites[self.current_animation]
        sprite.update(dt)
        if sprite.finished and self.current_animation == "hurt":
            self.current_animation = "idle"
        self.hit_effect.update(dt)

    def draw(self, screen, x, y):
        sprite = self.sprites[self.current_animation]
        sprite.render(screen, x, y)
        # Si la estrella de golpe está activa, dibujarla sobre el enemigo
        if not self.hit_effect.finished and self.hit_effect.surfaces:
            self.hit_effect.render(screen, x, y - 20)

    # ------------------------------------------------------------------ #
    #  Sprites genéricos de respaldo (un "blob" morado con ojos)
    # ------------------------------------------------------------------ #
    ENEMY_GENERIC = [
        [
            "....PPPP....",
            "...PPPPPP...",
            "..PPPPPPPP..",
            "..PPWPPWPP..",
            "..PPKPPKPP..",
            ".PPPPPPPPPP.",
            ".PPPPPPPPPP.",
            ".P.PP.PP.PP.",
            "..P..P..P...",
        ],
    ]
