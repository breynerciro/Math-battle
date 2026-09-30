"""
effects.py — Efectos visuales de combate mejorados con game-juice
=================================================================

Efectos visuales que hacen que el combate se sienta vivo:
- FloatingText: números con easing y animaciones
- ScreenShake: shake direccional con decay exponencial
- Particles: partículas con física y variedad visual
- HitStop: pausa de acción en impactos
- FlashEffect: flash de pantalla en eventos importantes
"""

import math
import random

import pygame

from .. import config


def ease_out_cubic(t):
    """Curva "sale rápido y frena suave" (para textos que suben)."""
    return 1 - pow(1 - t, 3)


def ease_out_elastic(t):
    """Curva elástica: el texto entra rebotando como una goma."""
    if t == 0 or t == 1:
        return t
    return pow(2, -10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1


class FloatingText:
    """Texto que flota con easing y animación de escala."""

    def __init__(self, text, x, y, color=config.WHITE, size=None):
        """Crea el texto flotante en la posición (x, y)."""
        self.text = text
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.life = 1.0
        self.max_life = 1.0
        self.font_size = size or config.FONT_SIZE_MEDIUM
        self.scale = 0.0
        self.target_scale = 1.0

    def update(self, dt):
        """Un frame: sube, crece con rebote y se va apagando.

        Devuelve False cuando ya murió (para quitarlo de la lista).
        """
        self.life -= dt * 0.9
        if self.life <= 0:
            return False

        progress = 1 - (self.life / self.max_life)
        self.y = self.start_y - 60 * ease_out_cubic(progress)

        if progress < 0.2:
            self.scale = ease_out_elastic(progress / 0.2)
        else:
            self.scale = 1.0

        return True

    def render(self, screen, font_getter):
        """Dibuja el texto con su escala actual y transparencia."""
        font = font_getter(self.font_size)
        surface = font.render(self.text, True, self.color)

        if self.scale != 1.0:
            new_size = max(1, int(surface.get_width() * self.scale))
            new_height = max(1, int(surface.get_height() * self.scale))
            surface = pygame.transform.scale(surface, (new_size, new_height))

        surface.set_alpha(int(255 * max(0, self.life)))
        rect = surface.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(surface, rect)


class ScreenShake:
    """Screen shake direccional con decay exponencial."""

    def __init__(self):
        """Shake apagado: sin duración ni intensidad."""
        self.time_left = 0.0
        self.duration = 0.0
        self.intensity = 0
        self.direction_x = 0
        self.direction_y = 0

    def trigger(self, duration=0.3, intensity=6, direction=None):
        """Activa el temblor: cuánto dura, cuánto tiembla y hacia dónde.

        `direction` es un par (dx, dy); si no se da, elige una al azar.
        """
        self.duration = duration
        self.time_left = duration
        self.intensity = intensity

        if direction:
            self.direction_x, self.direction_y = direction
            length = math.sqrt(self.direction_x**2 + self.direction_y**2)
            if length > 0:
                self.direction_x /= length
                self.direction_y /= length
        else:
            angle = random.uniform(0, 2 * math.pi)
            self.direction_x = math.cos(angle)
            self.direction_y = math.sin(angle)

    def update(self, dt):
        """Un frame: va gastando el tiempo que queda de temblor."""
        if self.time_left > 0:
            self.time_left -= dt

    def get_offset(self):
        """Desplazamiento de ESTE frame: grande al principio y decayendo
        (cuadrático) hasta quedar en cero."""
        if self.time_left <= 0:
            return 0, 0

        progress = self.time_left / self.duration
        decay = math.pow(progress, 2)
        current = self.intensity * decay

        random_factor = random.uniform(0.7, 1.0)
        offset = current * random_factor

        return (int(self.direction_x * offset + random.uniform(-2, 2)),
                int(self.direction_y * offset + random.uniform(-2, 2)))


class HitStop:
    """Pausa de acción en impactos importantes."""

    def __init__(self):
        """Hit-stop apagado (sin pausa)."""
        self.time_left = 0.0

    def trigger(self, duration=0.05):
        """Pausa la acción unos segundos: da más peso al golpe."""
        self.time_left = duration

    def update(self, dt):
        """Un frame: descuenta la pausa. Devuelve True mientras dure."""
        if self.time_left > 0:
            self.time_left -= dt
            return True
        return False

    def active(self):
        """True mientras el juego está pausado por el impacto."""
        return self.time_left > 0


class FlashEffect:
    """Flash de pantalla para eventos importantes."""

    def __init__(self):
        """Flash apagado."""
        self.alpha = 0
        self.color = config.WHITE
        self.decay_speed = 400

    def trigger(self, color=config.WHITE, intensity=150):
        """Lanza el destello: color y opacidad inicial (intensity 0-255)."""
        self.alpha = intensity
        self.color = color

    def update(self, dt):
        """Un frame: el destello se apaga poco a poco."""
        if self.alpha > 0:
            self.alpha -= self.decay_speed * dt
            if self.alpha < 0:
                self.alpha = 0

    def render(self, screen):
        """Pinta una capa de color transparente sobre TODO (si aún se ve)."""
        if self.alpha > 0:
            flash = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            flash.fill((*self.color, int(self.alpha)))
            screen.blit(flash, (0, 0))


class ParticleSystem:
    """Sistema de partículas mejorado con variedad visual."""

    def __init__(self):
        """Lista vacía de partículas."""
        self.particles = []

    def burst(self, x, y, color=config.YELLOW, count=14, speed=120, particle_type="spark"):
        """Explosión de `count` chispas saliendo en todas las direcciones
        desde el punto (x, y) con velocidades aleatorias."""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            v = random.uniform(speed * 0.4, speed)
            self.particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(angle) * v,
                "vy": math.sin(angle) * v,
                "color": color,
                "life": random.uniform(0.4, 0.8),
                "max_life": random.uniform(0.4, 0.8),
                "size": random.randint(2, 5),
                "type": particle_type,
                "rotation": random.uniform(0, 360),
                "rotation_speed": random.uniform(-180, 180),
            })

    def trail(self, x, y, color=config.YELLOW, count=3):
        """Estela suave: poquitas partículas lentas alrededor de (x, y)."""
        for _ in range(count):
            self.particles.append({
                "x": x + random.uniform(-5, 5),
                "y": y + random.uniform(-5, 5),
                "vx": random.uniform(-20, 20),
                "vy": random.uniform(-20, 20),
                "color": color,
                "life": random.uniform(0.2, 0.4),
                "max_life": random.uniform(0.2, 0.4),
                "size": random.randint(1, 3),
                "type": "trail",
                "rotation": 0,
                "rotation_speed": 0,
            })

    def update(self, dt):
        """Un frame: mueve cada partícula, les aplica gravedad (160 px/s²)
        y descarta las que se quedaron sin vida."""
        alive = []
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 160 * dt
            p["life"] -= dt
            p["rotation"] += p["rotation_speed"] * dt

            if p["type"] == "spark":
                p["vx"] *= 0.95
                p["vy"] *= 0.95

            if p["life"] > 0:
                alive.append(p)
        self.particles = alive

    def render(self, screen):
        """Dibuja cada partícula; cuanto más vieja, más pequeña se ve."""
        for p in self.particles:
            life_ratio = p["life"] / p["max_life"]
            size = max(1, int(p["size"] * life_ratio * 2))

            if p["type"] == "spark":
                color = p["color"]
                pygame.draw.rect(screen, color,
                               (int(p["x"]), int(p["y"]), size, size))
            elif p["type"] == "trail":
                alpha = int(200 * life_ratio)
                trail_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (*p["color"], alpha),
                                 (size, size), size)
                screen.blit(trail_surface, (int(p["x"] - size), int(p["y"] - size)))
