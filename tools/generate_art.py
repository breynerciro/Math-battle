"""Generador de TODOS los assets de Math Battle.

Este módulo es la única fuente de verdad del arte. Escribe exactamente
las rutas y el número de frames que espera el carga-sprites del juego, así
que se puede borrar `assets/` entero y reconstruirlo con:

    python -m tools.generate_art

No se toca a mano ningún PNG de `assets/`: si hay que cambiar algo, se
cambia el dibujo aquí y se vuelve a generar.

Convenciones que se respetan en todo el set:

- Los personajes van en un lienzo lógico de 32x32 y se guardan a x5
  (160x160), con `Image.NEAREST`. La escala entera es obligatoria: con
  interpolación los píxeles se emborronan y desaparece el aspecto de
  pixel art.
- Los fondos van en 480x270 y se guardan a x2 (960x540); al cargarlos el
  juego los reescala a la ventana (1280x720) con smoothscale.
- Los sprites se anclan abajo (`GROUND`), no centrados: el juego los apoya
  sobre la línea de suelo y los cambia de posición vertical según su
  altura. Un sprite anclado al centro bailaría al animarse.
- `idle` son 2 frames, `hurt` 1. El frame de daño se deriva lavando el de
  `idle`, nunca se dibuja aparte: así la pose no cambia al recibir el
  golpe y el enemigo no da un salto brusco.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permite ejecutarlo como script (python tools/generate_art.py) además de
# como módulo (python -m tools.generate_art); los imports relativos de
# abajo necesitan saber que el paquete es `tools`.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "tools"

from . import art_backgrounds, art_effects, art_enemies, art_hero
from .pixel import Canvas

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

SPRITE_SCALE = 5          # 32x32  -> 160x160 (personajes en 1280x720)
BG_SCALE = art_backgrounds.SCALE   # 480x270 -> 960x540

#: Enemigos en el orden de aparición. La clave es el nombre de carpeta que
#: usa el juego; el valor es la función que lo dibuja.
ENEMIES = {
    "slime": art_enemies.slime,
    "goblin": art_enemies.goblin,
    "skeleton": art_enemies.skeleton,
    "witch": art_enemies.witch,
    "stone_golem": art_enemies.stone_golem,
    "ghost": art_enemies.ghost,
    "lesser_demon": art_enemies.lesser_demon,
    "phoenix": art_enemies.phoenix,
    "dark_knight": art_enemies.dark_knight,
    "mage": art_enemies.mage,
    "hydra": art_enemies.hydra,
    "shadow": art_enemies.shadow,
    "archmage": art_enemies.archmage,
    "basic_dragon": art_enemies.basic_dragon,
    "supreme_dragon": art_enemies.supreme_dragon,
    "generic": art_enemies.generic,
}

HERO_CLIPS = ("idle", "attack", "hurt", "victory")


# ---------------------------------------------------------------------------
#  Escritura
# ---------------------------------------------------------------------------
def _save(canvas: Canvas, path: Path, scale: int, mode: str = "RGBA") -> Path:
    """Guarda un lienzo escalado (y asegura que la carpeta exista)."""
    return canvas.save(path, scale=scale, mode=mode)


def write_hero() -> list[Path]:
    """Escribe los frames del héroe: assets/sprites/hero/<anim>/frameN.png"""
    frames = art_hero.build()
    written = []
    for clip in HERO_CLIPS:
        for i, canvas in enumerate(frames[clip]):
            p = (ASSETS / "sprites" / "hero" / clip / f"frame{i}.png")
            written.append(_save(canvas, p, SPRITE_SCALE))
    return written


def write_enemies() -> list[Path]:
    """Escribe idle (2 frames) y hurt (1 frame) de cada enemigo."""
    written = []
    for slug, draw in ENEMIES.items():
        idle = [draw(0), draw(1)]
        for i, canvas in enumerate(idle):
            written.append(_save(
                canvas, ASSETS / "sprites" / "enemies" / slug / "idle" /
                f"frame{i}.png", SPRITE_SCALE))
        # El frame de daño se lava a partir del 0 de `idle`, así que la
        # silueta y la pose son idénticas a las del descanso.
        written.append(_save(
            art_enemies.hurt_frame(idle[0]),
            ASSETS / "sprites" / "enemies" / slug / "hurt" / "frame0.png",
            SPRITE_SCALE))
    return written


def write_effects() -> list[Path]:
    """Escribe los efectos (la estrella que sale al golpear)."""
    written = []
    for name, frames in art_effects.build().items():
        for i, canvas in enumerate(frames):
            written.append(_save(
                canvas, ASSETS / "sprites" / "effects" / name / f"frame{i}.png",
                SPRITE_SCALE))
    return written


def write_backgrounds() -> list[Path]:
    """Escribe los 5 fondos en RGB (ocupan toda la pantalla, sin alfa)."""
    written = []
    for i, draw in enumerate(art_backgrounds.LEVELS, start=1):
        # Los fondos van en RGB: ocupan toda la pantalla y no usan alfa.
        written.append(_save(draw(), ASSETS / "backgrounds" / f"level{i}.png",
                             BG_SCALE, mode="RGB"))
    return written


# ---------------------------------------------------------------------------
#  Verificación
# ---------------------------------------------------------------------------
def verify() -> list[str]:
    """Comprueba que en disco está todo lo que el juego espera.

    Devuelve una lista de problemas; vacía significa que el set está
    completo. Esto es lo que evita descubrir un PNG que falta en pleno
    combate.
    """
    from PIL import Image
    problems = []
    expected = []

    for clip in HERO_CLIPS:
        expected.append((ASSETS / "sprites" / "hero" / clip,
                         art_hero.build()[clip], SPRITE_SCALE))
    for slug in ENEMIES:
        draw = ENEMIES[slug]
        idle = [draw(0), draw(1)]
        expected.append((ASSETS / "sprites" / "enemies" / slug / "idle",
                         idle, SPRITE_SCALE))
        expected.append((ASSETS / "sprites" / "enemies" / slug / "hurt",
                         [art_enemies.hurt_frame(idle[0])], SPRITE_SCALE))
    for name, frames in art_effects.build().items():
        expected.append((ASSETS / "sprites" / "effects" / name, frames,
                         SPRITE_SCALE))

    for folder, frames, scale in expected:
        for i, canvas in enumerate(frames):
            p = folder / f"frame{i}.png"
            if not p.exists():
                problems.append(f"falta {p.relative_to(ROOT)}")
                continue
            with Image.open(p) as img:
                want = (canvas.w * scale, canvas.h * scale)
                if img.size != want:
                    problems.append(
                        f"{p.relative_to(ROOT)}: {img.size} != {want}")
                if img.mode != "RGBA":
                    problems.append(
                        f"{p.relative_to(ROOT)}: modo {img.mode}, esperaba RGBA")

    for i in range(1, len(art_backgrounds.LEVELS) + 1):
        p = ASSETS / "backgrounds" / f"level{i}.png"
        if not p.exists():
            problems.append(f"falta {p.relative_to(ROOT)}")
            continue
        with Image.open(p) as img:
            want = (art_backgrounds.W * BG_SCALE,
                    art_backgrounds.H * BG_SCALE)
            if img.size != want:
                problems.append(
                    f"{p.relative_to(ROOT)}: {img.size} != {want}")
            if img.mode != "RGB":
                problems.append(
                    f"{p.relative_to(ROOT)}: modo {img.mode}, esperaba RGB")
    return problems


def generate(quiet: bool = False) -> list[Path]:
    """Regenera TODOS los PNG del juego y devuelve la lista de archivos."""
    written = []
    written += write_hero()
    written += write_enemies()
    written += write_effects()
    written += write_backgrounds()
    if not quiet:
        total_kb = sum(p.stat().st_size for p in written) / 1024
        print(f"{len(written)} PNG escritos, {total_kb:.0f} KB en total")
        for p in written:
            print(f"  {p.relative_to(ROOT)}")
    return written


def main(argv=None) -> int:
    """CLI: genera todo (o solo verifica con --verify). Devuelve 0 si OK."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--verify" in argv:
        problems = verify()
        if problems:
            print(f"{len(problems)} problema(s):")
            for p in problems:
                print(f"  - {p}")
            return 1
        print("assets OK: rutas, tamaños y modos correctos")
        return 0
    generate()
    problems = verify()
    if problems:
        print(f"\n{len(problems)} problema(s) tras generar:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("verificación OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
