"""
test_assets.py — El arte de `assets/` está sincronizado con el generador
========================================================================

Los PNG se generan con Pillow desde `tools/art_*.py`. Estos tests evitan
la forma más fácil de romper el juego sin darse cuenta: editar el dibujo y
olvidarse de regenerar, o regenerar a mano con una versión antigua.

No prueban que un sprite quede bonito (eso no se automaiza), sino las tres
cosas que sí rompen el juego de forma silenciosa:

- que falte un archivo o un frame de más (el juego carga por ruta y la
  animación del enemigo se queda congelada en el último frame),
- que un PNG tenga un tamaño o un modo de color que Pygame no pueda
  componer,
- que un personaje se dibuje parcialmente fuera del lienzo y pierda
  píxeles,
- que un enemigo oscuro desaparezca contra el fondo.

Se importa Pillow, que es dependencia solo de `tools/`. Si no está, los
tests se saltan en lugar de romper la instalación del juego.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytest.importorskip("PIL", reason="Pillow es solo necesario para tools/")

from PIL import Image  # noqa: E402

from tools import art_backgrounds, art_enemies, art_effects  # noqa: E402
from tools import art_hero, generate_art  # noqa: E402
from tools.pixel import Canvas  # noqa: E402

ROOT = generate_art.ROOT
ASSETS = generate_art.ASSETS


def _clip_paths():
    """Rutas de todos los frames de enemigos, con su lienzo esperado."""
    for slug, draw in generate_art.ENEMIES.items():
        idle = [draw(0), draw(1)]
        for i, c in enumerate(idle):
            yield (f"enemies/{slug}/idle/frame{i}.png", c, "RGBA",
                   generate_art.SPRITE_SCALE)
        yield (f"enemies/{slug}/hurt/frame0.png",
               art_enemies.hurt_frame(idle[0]), "RGBA",
               generate_art.SPRITE_SCALE)


def _all_sprites():
    for clip, frames in art_hero.build().items():
        for i, c in enumerate(frames):
            yield (f"hero/{clip}/frame{i}.png", c, "RGBA",
                   generate_art.SPRITE_SCALE)
    yield from _clip_paths()
    for name, frames in art_effects.build().items():
        for i, c in enumerate(frames):
            yield (f"effects/{name}/frame{i}.png", c, "RGBA",
                   generate_art.SPRITE_SCALE)


# ---------------------------------------------------------------------------
def test_no_sprites_pegados_al_borde_lateral():
    """Nada debe tocar x=0 ni x=31: el `outline` añade 1 px y recortaría.

    Un sprite pegado al lateral no está "llenando la caja", está perdido:
    el borde de la silueta queda cortado por el del PNG.
    """
    for slug, draw in generate_art.ENEMIES.items():
        for phase in (0, 1):
            bbox = draw(phase).to_image().getchannel("A").getbbox()
            assert bbox is not None, f"{slug} frame{phase} sale vacío"
            x0, _, x1, _ = bbox
            assert x0 > 0, f"{slug} frame{phase} toca el borde izquierdo"
            assert x1 < draw(phase).w, f"{slug} frame{phase} toca el derecho"


def test_dentro_del_lienzo():
    """Ningún sprite dibuja fuera de su lienzo de 32x32.

    Instrumenta `put` para detectar coordenadas fuera de rango: si un
    dibujo se sale, los píxeles se descartan en silencio y el sprite sale
    con un trozo menos, que es muy difícil de ver en un preview pequeño.
    El parche tiene que estar activo *mientras* se dibuja, así que aquí
    se regeneran los lienzos desde cero en vez de reutilizar los de antes.
    """
    fuera = []
    original = Canvas.put

    def put(self, x, y, color):
        if not (0 <= int(x) < self.w and 0 <= int(y) < self.h):
            fuera.append((int(x), int(y)))
        return original(self, x, y, color)

    Canvas.put = put
    try:
        for slug, draw in generate_art.ENEMIES.items():
            fuera.clear()
            for phase in (0, 1):
                draw(phase)
            assert not fuera, f"{slug} dibuja fuera del lienzo: {fuera[:4]}"

        fuera.clear()
        art_hero.build()
        assert not fuera, f"el héroe dibuja fuera del lienzo: {fuera[:4]}"

        fuera.clear()
        art_effects.build()
        assert not fuera, f"los efectos dibujan fuera: {fuera[:4]}"
    finally:
        Canvas.put = original


def test_contraste_del_cuerpo_contra_el_fondo():
    """El cuerpo de cada enemigo debe separarse del fondo del nivel.

    Los fondos son un castillo muy oscuro por diseño, así que un enemigo
    también oscuro se pierde. Se mide la diferencia media de luminancia
    entre los píxeles del cuerpo (excluyendo el contorno, que solo recorta
    la silueta) y el fondo que queda detrás. Por debajo de 26/255 el
    enemigo no se distingue.
    """
    def lum(c):
        r, g, b = c[:3]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    ink = tuple(art_enemies.P.INK[:3])
    fondos = {
        lvl: Image.open(ASSETS / "backgrounds" / f"level{lvl}.png").load()
        for lvl in range(1, len(art_backgrounds.LEVELS) + 1)
    }
    for slug, draw in generate_art.ENEMIES.items():
        sp = draw(0).to_image()
        sw, sh = sp.size
        sa, sc = sp.getchannel("A").load(), sp.load()
        for lvl, bl in fondos.items():
            acc = n = 0
            for y in range(sh):
                for x in range(sw):
                    if sa[x, y] > 200 and tuple(sc[x, y][:3]) != ink:
                        # el juego ancla abajo: la fila sh-1 cae en GROUND_Y
                        by = 400 - sh + y
                        acc += abs(lum(sc[x, y]) - lum(bl[720 + x - 16, by]))
                        n += 1
            assert n, f"{slug}: sin píxeles de cuerpo que medir"
            assert acc / n >= 26, (
                f"{slug} se confunde con level{lvl}: "
                f"contraste {acc / n:.1f}/255, mínimo 26")


def test_tamanos_y_modos_de_los_png():
    """Cada PNG en disco tiene el tamaño y el modo que espera el juego."""
    assert generate_art.verify() == []


def test_sin_codigo_muerto():
    """Nada inalcanzable tras un `return` dentro de las funciones de dibujo.

    Ya quedó un bloque huérfano en `supreme_dragon` que además usaba
    variables inexistentes (`hx`, `hy`): no petaba porque nunca llegaba a
    ejecutarse, pero indicaba un refactor a medias. Se comprueba con el
    AST para que no vuelva a colarse sin que se note.
    """
    import ast
    for f in sorted((ROOT / "tools").glob("*.py")):
        tree = ast.parse(f.read_text(), str(f))
        for fn in [n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef)]:
            for i, st in enumerate(fn.body[:-1]):
                if isinstance(st, (ast.Return, ast.Raise, ast.Continue,
                                   ast.Break)):
                    for dead in fn.body[i + 1:]:
                        pytest.fail(
                            f"{f.name}:{dead.lineno}: inalcanzable tras "
                            f"'{type(st).__name__.lower()}' en {fn.name}()")


def test_fondo_oscuro_pero_no_negro():
    """Los fondos son oscuros, pero no un bloque negro plano.

    Un fondo de luminancia media ~0 no tiene profundidad ni siluetas, y
    además escondería cualquier detalle del escenario. Se comprueba que la
    imagen tenga recorrido tonal real.
    """
    import statistics
    for lvl in range(1, len(art_backgrounds.LEVELS) + 1):
        im = Image.open(ASSETS / "backgrounds" / f"level{lvl}.png").convert("L")
        vals = list(im.tobytes())
        assert statistics.mean(vals) > 5, f"level{lvl} es negro puro"
        assert max(vals) - min(vals) > 60, (
            f"level{lvl} apenas tiene contraste tonal")
