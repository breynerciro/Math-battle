"""
scenario.py — Escenarios dinámicos con parallax y efectos ambientales
=====================================================================

Sistema de escenarios mejorado que aplica principios de game-juice:
- Múltiples capas con parallax (profundidad visual)
- Partículas ambientales temáticas por nivel
- Efectos de iluminación dinámica
- Animaciones continuas de fondo
- Respuesta visual al estado del juego
"""

import math
import random

import pygame

from .. import config
from .background import get_background


class ParallaxLayer:
    """Capa de parallax que se mueve a velocidad variable."""

    def __init__(self, surface, speed_factor=0.1, y_offset=0):
        self.surface = surface
        self.speed_factor = speed_factor
        self.y_offset = y_offset
        self.offset_x = 0.0

    def update(self, dt, camera_movement=0):
        self.offset_x += camera_movement * self.speed_factor * dt
        if self.surface:
            self.offset_x %= self.surface.get_width()

    def render(self, screen, base_x=0, base_y=0):
        if not self.surface:
            return
        x = int(base_x - self.offset_x)
        y = int(base_y + self.y_offset)
        screen.blit(self.surface, (x, y))
        if self.surface.get_width() < config.SCREEN_WIDTH:
            screen.blit(self.surface, (x + self.surface.get_width(), y))


class AmbientParticle:
    """Partícula ambiental con comportamiento temático."""

    def __init__(self, x, y, particle_type, level):
        self.x = x
        self.y = y
        self.type = particle_type
        self.level = level
        self.life = random.uniform(3.0, 8.0)
        self.max_life = self.life
        
        if particle_type == "leaf":
            self.vx = random.uniform(-20, -5)
            self.vy = random.uniform(15, 35)
            self.rotation = random.uniform(0, 360)
            self.rotation_speed = random.uniform(-90, 90)
            self.size = random.randint(3, 6)
            self.color = random.choice([config.GREEN, config.DARK_GREEN, (60, 150, 60)])
        elif particle_type == "bubble":
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(-30, -15)
            self.size = random.randint(2, 5)
            self.color = config.CYAN
            self.wobble = random.uniform(0, math.pi * 2)
        elif particle_type == "spark":
            self.vx = random.uniform(-15, 15)
            self.vy = random.uniform(-40, -20)
            self.size = random.randint(2, 4)
            self.color = random.choice([config.YELLOW, config.ORANGE, config.RED])
        elif particle_type == "dust":
            self.vx = random.uniform(-10, 10)
            self.vy = random.uniform(-5, 5)
            self.size = random.randint(1, 3)
            self.color = config.LIGHT_GRAY
        elif particle_type == "crystal":
            self.vx = 0
            self.vy = 0
            self.size = random.randint(2, 4)
            self.color = config.CYAN
            self.pulse = random.uniform(0, math.pi * 2)
            self.pulse_speed = random.uniform(2, 4)

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            return False

        if self.type == "leaf":
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.rotation += self.rotation_speed * dt
            self.vx += math.sin(self.y * 0.01) * 10 * dt
        elif self.type == "bubble":
            self.wobble += dt * 3
            self.x += self.vx * dt + math.sin(self.wobble) * 0.5
            self.y += self.vy * dt
        elif self.type == "spark":
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.vy += 80 * dt
        elif self.type == "dust":
            self.x += self.vx * dt
            self.y += self.vy * dt
        elif self.type == "crystal":
            self.pulse += self.pulse_speed * dt

        if self.x < -10 or self.x > config.SCREEN_WIDTH + 10:
            return False
        if self.y < -10 or self.y > config.SCREEN_HEIGHT + 10:
            return False
        return True

    def render(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        
        if self.type == "leaf":
            size = self.size
            leaf_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(leaf_surface, (*self.color, alpha), (0, 0, size * 2, size))
            rotated = pygame.transform.rotate(leaf_surface, self.rotation)
            screen.blit(rotated, (int(self.x), int(self.y)))
        elif self.type == "bubble":
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
            highlight = (min(255, self.color[0] + 50), 
                        min(255, self.color[1] + 50), 
                        min(255, self.color[2] + 50))
            pygame.draw.circle(screen, highlight, 
                             (int(self.x - self.size * 0.3), int(self.y - self.size * 0.3)), 
                             max(1, self.size // 3))
        elif self.type == "spark":
            pygame.draw.rect(screen, self.color, 
                           (int(self.x), int(self.y), self.size, self.size))
        elif self.type == "dust":
            pygame.draw.circle(screen, self.color, 
                             (int(self.x), int(self.y)), self.size)
        elif self.type == "crystal":
            brightness = int(128 + 127 * math.sin(self.pulse))
            color = (min(255, self.color[0] + brightness // 4),
                    min(255, self.color[1] + brightness // 4),
                    min(255, self.color[2] + brightness // 4))
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)


class Scenario:
    """Escenario dinámico con capas de parallax y partículas ambientales."""

    def __init__(self, level):
        self.level = level
        self.base_background = get_background(level)
        self.layers = []
        self.particles = []
        self.particle_timer = 0.0
        self.time = 0.0
        self.light_effects = []
        
        self._setup_layers()
        self._setup_ambient_particles()
        self._setup_light_effects()

    def _setup_layers(self):
        # Colores por tema del nivel: bosque, mina, templo azul,
        # puente nocturno y castillo del caos.
        config_map = {
            1: {"layers": [0.05, 0.1, 0.2], "colors": [(20, 70, 20), (30, 90, 30), (40, 110, 40)]},
            2: {"layers": [0.03, 0.08, 0.15], "colors": [(50, 40, 26), (62, 50, 32), (74, 60, 40)]},
            3: {"layers": [0.04, 0.09, 0.18], "colors": [(30, 52, 96), (38, 64, 116), (46, 76, 136)]},
            4: {"layers": [0.06, 0.12, 0.22], "colors": [(24, 24, 72), (32, 32, 92), (40, 40, 112)]},
            5: {"layers": [0.05, 0.1, 0.2], "colors": [(52, 26, 52), (64, 32, 62), (76, 38, 72)]},
        }
        
        cfg = config_map.get(self.level, config_map[1])
        
        for i, (speed, color) in enumerate(zip(cfg["layers"], cfg["colors"])):
            layer_surface = self._create_parallax_layer(color, i)
            self.layers.append(ParallaxLayer(layer_surface, speed, i * 20))

    def _create_parallax_layer(self, color, depth):
        surface = pygame.Surface((config.SCREEN_WIDTH * 2, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        surface.fill((*color, 80 - depth * 20))
        
        if self.level == 1:
            for _ in range(8 - depth * 2):
                x = random.randint(0, surface.get_width() - 60)
                h = random.randint(80, 150 - depth * 20)
                w = random.randint(40, 60)
                y = config.GROUND_Y - h
                dark_color = tuple(max(0, c - 20) for c in color)
                pygame.draw.polygon(surface, (*dark_color, 150),
                                  [(x + w // 2, y), (x, y + h), (x + w, y + h)])
        elif self.level == 2:
            for x in range(0, surface.get_width(), 40 + depth * 10):
                h = random.randint(30, 80 - depth * 15)
                dark_color = tuple(max(0, c - 15) for c in color)
                pygame.draw.polygon(surface, (*dark_color, 120),
                                  [(x, 0), (x + 40, 0), (x + 20, h)])
        elif self.level == 3:
            for wx in range(100, surface.get_width(), 200 - depth * 30):
                for wy in range(80, config.GROUND_Y - 80, 140 - depth * 20):
                    dark_color = tuple(max(0, c - 25) for c in color)
                    pygame.draw.rect(surface, (*dark_color, 100),
                                   (wx, wy, 50, 70), border_radius=8)
        elif self.level == 4:
            for _ in range(12 - depth * 3):
                x = random.randint(0, surface.get_width() - 10)
                h = random.randint(40, 100 - depth * 20)
                dark_color = tuple(max(0, c - 20) for c in color)
                pygame.draw.line(surface, (*dark_color, 130),
                               (x, config.GROUND_Y),
                               (x + random.randint(-10, 10), config.GROUND_Y - h), 5)
        else:
            for x in range(0, surface.get_width(), 70 + depth * 10):
                dark_color = tuple(max(0, c - 20) for c in color)
                pygame.draw.rect(surface, (*dark_color, 110),
                               (x, config.GROUND_Y - 160 + depth * 20, 40, 40))
        
        return surface

    def _setup_ambient_particles(self):
        # Partícula temática de cada nivel:
        #   1 bosque (hojas) · 2 mina (polvo) · 3 templo (chispas de runa)
        #   4 puente (estrellas fugaces) · 5 castillo (cristales de neón)
        particle_types = {
            1: "leaf",
            2: "dust",
            3: "spark",
            4: "spark",
            5: "crystal"
        }
        self.particle_type = particle_types.get(self.level, "dust")

    def _setup_light_effects(self):
        if self.level == 2:
            # Vetas de gemas brillando en la mina
            for _ in range(5):
                x = random.randint(50, config.SCREEN_WIDTH - 50)
                y = random.randint(config.GROUND_Y - 100, config.GROUND_Y - 20)
                self.light_effects.append({
                    "type": "crystal_glow",
                    "x": x, "y": y,
                    "radius": random.randint(15, 25),
                    "pulse": random.uniform(0, math.pi * 2),
                    "speed": random.uniform(1.5, 3)
                })

    def update(self, dt, camera_movement=0):
        self.time += dt
        
        for layer in self.layers:
            layer.update(dt, camera_movement)
        
        self.particle_timer += dt
        spawn_rate = 0.3 if self.level == 4 else 0.5
        if self.particle_timer > spawn_rate:
            self.particle_timer = 0
            self._spawn_particle()
        
        self.particles = [p for p in self.particles if p.update(dt)]
        
        for effect in self.light_effects:
            effect["pulse"] += effect["speed"] * dt

    def _spawn_particle(self):
        if self.particle_type == "leaf":
            x = random.randint(config.SCREEN_WIDTH, config.SCREEN_WIDTH + 100)
            y = random.randint(0, config.GROUND_Y - 50)
            self.particles.append(AmbientParticle(x, y, "leaf", self.level))
        elif self.particle_type == "bubble":
            x = random.randint(0, config.SCREEN_WIDTH)
            y = random.randint(config.GROUND_Y + 20, config.SCREEN_HEIGHT)
            self.particles.append(AmbientParticle(x, y, "bubble", self.level))
        elif self.particle_type == "spark":
            x = random.randint(0, config.SCREEN_WIDTH)
            y = random.randint(config.GROUND_Y - 150, config.GROUND_Y - 50)
            self.particles.append(AmbientParticle(x, y, "spark", self.level))
        elif self.particle_type == "dust":
            x = random.randint(0, config.SCREEN_WIDTH)
            y = random.randint(100, config.GROUND_Y - 50)
            self.particles.append(AmbientParticle(x, y, "dust", self.level))
        elif self.particle_type == "crystal":
            x = random.randint(0, config.SCREEN_WIDTH)
            y = random.randint(config.GROUND_Y - 80, config.GROUND_Y)
            self.particles.append(AmbientParticle(x, y, "crystal", self.level))

    def render(self, screen, offset_x=0, offset_y=0):
        screen.blit(self.base_background, (offset_x, offset_y))
        
        for layer in self.layers:
            layer.render(screen, offset_x, offset_y)
        
        for effect in self.light_effects:
            self._render_light_effect(screen, effect, offset_x, offset_y)
        
        for particle in self.particles:
            particle.render(screen)

    def _render_light_effect(self, screen, effect, offset_x, offset_y):
        x = int(effect["x"] + offset_x)
        y = int(effect["y"] + offset_y)
        radius = effect["radius"]
        
        if effect["type"] == "crystal_glow":
            brightness = int(0.5 + 0.5 * math.sin(effect["pulse"]))
            glow_radius = radius + brightness * 8
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            alpha = int(80 * brightness)
            pygame.draw.circle(glow_surface, (*config.CYAN, alpha),
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (x - glow_radius, y - glow_radius))
