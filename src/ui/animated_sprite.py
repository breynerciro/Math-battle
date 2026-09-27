"""
animated_sprite.py — Animaciones a partir de archivos PNG
=========================================================

Los sprites del juego NO se dibujan aquí: viven como imágenes PNG en
assets/sprites/ (generadas con tools/generate_sprites.py o hechas a
mano). Esta clase solo los CARGA y los REPRODUCE en secuencia.

Estructura esperada de cada animación (una carpeta = una animación):

    assets/sprites/hero/idle/frame0.png
    assets/sprites/hero/idle/frame1.png
    ...

Para cambiar el aspecto de un personaje no hace falta tocar código:
basta con reemplazar sus PNG conservando los nombres de archivo.
"""

from pathlib import Path

import pygame


class AnimatedSprite:
    """Reproduce una animación cuyos frames son imágenes PNG."""

    # Cache global: cada carpeta de frames se carga UNA sola vez
    _loaded: dict[str, list[pygame.Surface]] = {}

    def __init__(self, surfaces: list[pygame.Surface],
                 fps: float = 6.0, loop: bool = True) -> None:
        """
        Args:
            surfaces: lista de imágenes ya cargadas (una por frame)
            fps:      frames por segundo de la animación
            loop:     ¿repetir en bucle? (False para animaciones de golpe)
        """
        self.surfaces = surfaces
        self.fps = max(1.0, fps)
        self.loop = loop
        self.frame_index = 0
        self.timer = 0.0
        self.finished = not loop and len(surfaces) <= 1

    # ------------------------------------------------------------------ #
    #  Carga
    # ------------------------------------------------------------------ #
    @classmethod
    def load(cls, anim_dir: Path | str, fps: float = 6.0,
             loop: bool = True) -> "AnimatedSprite":
        """Carga los frames (frame0.png, frame1.png, ...) de una carpeta.

        Si la carpeta no existe o está vacía, se usa un cuadro morado
        como marcador visible (fácil de detectar mientras se corrige).
        """
        folder = Path(anim_dir)
        cache_key = str(folder.resolve())
        if cache_key not in cls._loaded:
            cls._loaded[cache_key] = cls._load_frames(folder)
        return cls(cls._loaded[cache_key], fps=fps, loop=loop)

    @staticmethod
    def _load_frames(folder: Path) -> list[pygame.Surface]:
        """Lee los PNG de la carpeta, ordenados por número de frame."""
        frame_paths = sorted(folder.glob("frame*.png"),
                             key=lambda path: int(path.stem.removeprefix("frame") or 0))
        if not frame_paths:
            return [AnimatedSprite._placeholder()]
        return [pygame.image.load(str(path)).convert_alpha()
                for path in frame_paths]

    @staticmethod
    def _placeholder() -> pygame.Surface:
        """Cuadro morado 12x12 que avisa de un sprite faltante."""
        surface = pygame.Surface((12, 12), pygame.SRCALPHA)
        surface.fill((200, 60, 220))
        return surface

    # ------------------------------------------------------------------ #
    #  Información del frame actual
    # ------------------------------------------------------------------ #
    @property
    def current(self) -> pygame.Surface:
        """Imagen del frame que se está mostrando."""
        return self.surfaces[self.frame_index]

    def height_px(self) -> int:
        """Altura en pantalla del frame actual (para anclar a los pies)."""
        return self.current.get_height()

    # ------------------------------------------------------------------ #
    #  Reproducción
    # ------------------------------------------------------------------ #
    def update(self, dt: float) -> None:
        """Avanza la animación según el tiempo transcurrido."""
        if self.finished or len(self.surfaces) <= 1:
            return
        self.timer += dt
        frame_time = 1.0 / self.fps
        while self.timer >= frame_time:
            self.timer -= frame_time
            self.frame_index += 1
            if self.frame_index >= len(self.surfaces):
                if self.loop:
                    self.frame_index = 0
                else:
                    self.frame_index = len(self.surfaces) - 1
                    self.finished = True

    def render(self, screen: pygame.Surface, x: int, y: int,
               center: bool = True) -> None:
        """Dibuja el frame actual. Si center=True, (x, y) es el centro."""
        rect = self.current.get_rect()
        rect.center = (x, y) if center else (x, y)
        screen.blit(self.current, rect)

    def reset(self) -> None:
        """Reinicia la animación desde el primer frame."""
        self.frame_index = 0
        self.timer = 0.0
        self.finished = not self.loop and len(self.surfaces) <= 1
