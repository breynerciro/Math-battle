"""Los 5 fondos de batalla, uno por nivel del juego.

Los fondos se pintan sobre un lienzo lógico de 480x270 y se guardan
escalados x2 hasta 960x540; al cargarlos el juego los reescala a la
ventana (1280x720). El héroe y el enemigo se dibujan apoyados en
`GROUND_Y` de pantalla, que en el lienzo lógico es la línea `GROUND`:
todo lo que vaya por debajo es suelo y todo lo de arriba es arquitectura,
cielo y atmósfera.

Los escenarios siguen la temática del diseño de los 5 niveles:

1. **El Bosque de las Sumas** — bosque verde y vibrante a plena luz.
2. **La Mina de la Multiplicación** — vigas, gemas, engranajes y piedra.
3. **El Templo de las Fracciones** — piedra azul mística y runas cian.
4. **El Puente Hacia el Caos** — puente en el espacio, cielo púrpura.
5. **El Castillo del Caos** — interior con portales y símbolos neón.

Dos reglas que se respetan en los cinco niveles:

1. **Bajo contraste.** El fondo no compite con los enemigos. Si el fondo
   tiene más contraste que un sprite, el sprite desaparece. Por eso la
   arquitectura va en tonos casi apagados y la saturación se reserva para
   lo que de verdad debe llamar la atención: portales, gemas y neón.
2. **Nada de degradados suaves.** Cada transición de color va en bandas
   cuantizadas con dithering ordenado. Un `lerp` continuo convertiría el
   PNG en una foto y dispararía su peso.
"""

from __future__ import annotations

import math

from . import palettes as P
from .pixel import Canvas, mix

W, H = 480, 270
GROUND = 156          # línea del suelo en el lienzo lógico (los pies de
                      # los personajes: 418 px de pantalla a 1280x720)
SCALE = 2              # 480x270 -> 960x540 (luego el juego escala a 1280x720)


# ---------------------------------------------------------------------------
#  Glifos matemáticos: rejillas de 5x5 que se dibujan a cualquier tamaño.
#  Son el motivo visual del juego, así que se dibujan con huecos de 1 px
#  reales y no con trazos continuos: a x2 un trazo de 1 px se ve, a x1
#  desaparece.
# ---------------------------------------------------------------------------
GLYPHS = {
    "pi":    (".###.", "##.##", "#####", "..#..", "..#.."),
    "sqrt":  ("....#", "...##", "#.#.#", "#.#.#", ".###."),
    "sum":   (".####", "#....", ".##..", "#....", ".####"),
    "int":   (".###.", "..#..", "..#..", "..#..", ".###."),
    "neq":   ("##..#", "#####", ".....", "#####", "#..##"),
    "inf":   (".....", ".....", "##.##", "#.#.#", "....."),
    "times": (".....", "#...#", ".#.#.", "#...#", "....."),
    "div":   (".....", "..#..", "#####", "..#..", "....."),
    "pm":    ("..#..", "#####", "..#..", ".....", "#####"),
    "theta": (".###.", "#...#", "#.#.#", "#...#", ".###."),
    "delta": ("..#..", ".#.#.", "#.#.#", "#####", "....."),
    "alpha": (".##..", "#..#.", "#..#.", "#.##.", "##..."),
}


def stamp_glyph(c: Canvas, name: str, x: int, y: int, scale: int,
                color, glow=None) -> None:
    """Pega un glifo matemático con `scale` píxeles por celda, centrado en x, y.

    El halo va ANTES del glifo y con `blank_only`: si el resplandor se
    mezcla con las runas ya pintadas inventa colores y las letras se
    emborronan. Pasa el glifo primero y el halo después y el símbolo se ve
    borroso, que es justo lo contrario de lo que queremos.
    """
    rows = GLYPHS[name]
    n = len(rows)
    w = n * scale
    x0 = x - w // 2
    y0 = y - w // 2
    if glow is not None:
        c.radial_glow(x, y, w, glow, 0.5, levels=3, blank_only=True)
    for gy, row in enumerate(rows):
        for gx, ch in enumerate(row):
            if ch == ".":
                continue
            c.fill_rect(x0 + gx * scale, y0 + gy * scale, scale, scale, color)


# ---------------------------------------------------------------------------
#  Escenario parametrizado
# ---------------------------------------------------------------------------
def _sky(c: Canvas, top, bottom, steps=6) -> None:
    """Cielo en bandas + estrellas deterministas."""
    for y in range(GROUND):
        c.put(0, y, (0, 0, 0, 255))          # semilla opaca para el degradado
        for x in range(W):
            c.px[y][x] = (0, 0, 0, 255)
    c.vgradient(top, bottom, 0, GROUND - 1, steps=steps)


def _stars(c: Canvas, count: int, seed: int, color, y_max=140) -> None:
    """Estrellas con parpadeo fijo (determinista: el fondo no parpadea
    entre recargas, solo cambia de nivel)."""
    state = seed & 0x7FFFFFFF
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        x = state % W
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        y = state % y_max
        c.put(x, y, color)
        # Una de cada cinco tiene un brillo de 1 px: da profundidad.
        if state % 5 == 0:
            c.put(x + 1, y, color)


def _moon(c: Canvas, x: int, y: int, r: int, color, halo) -> None:
    """Luna con halo cuantizado: el único cuerpo celeste de la escena."""
    c.radial_glow(x, y, r * 3, halo, 0.30, levels=4, blank_only=True)
    c.circle(x, y, r, color)
    c.circle(x + 1, y - 1, r - 2, mix(color, (255, 255, 255), 0.35))
    c.circle(x - r // 2, y + r // 3, max(1, r // 4), mix(color, (0, 0, 0), 0.12))


def _portal(c: Canvas, x: int, base: int, w: int, h: int, inner, rim,
            glow, arcs=3) -> None:
    """Portal con arco apuntado: el motivo central de la escena.

    El interior es un degradado vertical en 4 bandas, no un fade suave. Un
    portal con degradado continuo parece una foto pegada encima del pixel
    art y rompe el conjunto.
    """
    # Halo detrás del arco (vacío solamente).
    c.radial_glow(x + w // 2, base - h // 2, int(w * 1.5), glow, 0.28,
                  levels=4, blank_only=True)
    # Cuerpo del arco: rectángulo + remate ojival.
    c.fill_rect(x, base - h, w, h, rim)
    c.ellipse(x + w // 2, base - h, w // 2, w // 4, rim)
    # Hueco interior, con degradado en bandas hacia el suelo.
    iw, ih = w - 4, h - 6
    ix, iy = x + 2, base - h + 4
    c.fill_rect(ix, iy, iw, ih, inner)
    c.ellipse(x + w // 2, iy, iw // 2, w // 4, inner)
    for i in range(4):
        t = i / 3.0
        c.fill_rect(ix, iy + int(ih * t), iw, max(1, ih // 6),
                    mix(inner, rim, 0.22 * (1 - t)))
    # Jambas: dos aristas claras que enmarcan la entrada.
    c.vline(ix - 1, iy, base - 1, mix(rim, (255, 255, 255), 0.30))
    c.vline(ix + iw, iy, base - 1, mix(rim, (0, 0, 0), 0.30))
    # Arcos concéntricos: la "grieta" que hace legible la profundidad.
    for k in range(arcs):
        t = 1.0 - k * 0.26
        ax = int(iw * t / 2)
        ay = int(ih * 0.22 * k)
        col = mix(inner, glow, 0.30 + 0.22 * k)
        c.hline(ix + ax, ix + iw - ax, iy + ay, col)
        if k:
            c.hline(ix + ax, ix + iw - ax, iy + ay + 1, mix(col, inner, 0.5))
    # Sillares del suelo delante del portal.
    c.hline(x, x + w - 1, base, mix(rim, (0, 0, 0), 0.35))
    c.hline(x, x + w - 1, base - 1, rim)


def _floor(c: Canvas, top_color, near_color, edge, tile=16) -> None:
    """Suelo de losas en perspectiva falsa.

    Las juntas convergen hacia un punto de fuga alto: eso da profundidad
    sin necesidad de dibujar nada en 3D. Se aplican tres bandas de color
    (lejos / medio / cerca) en vez de un degradado.
    """
    for y in range(GROUND, H):
        t = (y - GROUND) / float(H - GROUND)
        band = 0 if t < 0.33 else (1 if t < 0.66 else 2)
        col = (top_color, near_color, mix(near_color, edge, 0.35))[band]
        for x in range(W):
            c.px[y][x] = (*col, 255)
    # Línea de contacto con la arquitectura: separa fondo y suelo.
    c.hline(0, W - 1, GROUND, mix(edge, (0, 0, 0), 0.2))
    c.hline(0, W - 1, GROUND - 1, edge)
    # Juntas horizontales, espaciadas más cuanto más cerca (perspectiva).
    y = GROUND + 5
    step = 5
    while y < H:
        c.hline(0, W - 1, y, mix(col_tone(c, y), (0, 0, 0), 0.22))
        step += max(1, step // 3)
        y += step
    # Juntas verticales radiales hacia el punto de fuga.
    vpx, vpy = W // 2, GROUND
    for k in range(-9, 10):
        x_end = vpx + k * 42
        steps = 26
        for i in range(1, steps + 1):
            f = i / steps
            yy = int(vpy + (H - vpy) * f)
            xx = int(vpx + (x_end - vpx) * f)
            c.put(xx, yy, mix(col_tone(c, yy), (0, 0, 0), 0.18))


def col_tone(c: Canvas, y: int):
    """Tono del suelo en la fila `y` (para las juntas)."""
    t = max(0.0, min(1.0, (y - GROUND) / float(H - GROUND)))
    if t < 0.33:
        return P.PITCH_DARK
    return P.INK


def _runes(c: Canvas, placements, color, glow, scale=3) -> None:
    """Runas flotantes: los símbolos matemáticos de la referencia.

    Se colocan en la mitad superior para no interferir con los enemigos,
    que se dibujan sobre la línea de suelo.
    """
    for name, x, y, s in placements:
        stamp_glyph(c, name, x, y, scale, color, glow)


def _fog(c: Canvas, y: int, h: int, color, strength=0.5, bands: int = 3) -> None:
    """Niebla baja: hunde la base de la arquitectura y da profundidad.

    El alfa va en `bands` escalones, no continuo. Tiñendo píxel a píxel con
    un alfa distinto en cada fila se generan decenas de colores nuevos por
    fila; con tres escalones la niebla sigue leyéndose como niebla y el
    número de colores se queda controlado.
    """
    for i in range(h):
        band = min(bands - 1, int((h - i) * bands / float(h)))
        if band < 0:
            continue
        a = int(255 * strength * (band + 0.5) / bands * 0.5)
        for x in range(W):
            c.blend(x, y + i, (*color, a))


def _vignette(c: Canvas, color=(0, 0, 0), strength=0.34, bands: int = 4) -> None:
    """Viñeta: oscurece las esquinas para que la mirada vaya al centro,
    que es donde están el héroe y el enemigo.

    Igual que la niebla, el alfa se cuantiza en `bands` escalones: un
    oscurecimiento progresivo por píxel convertiría el fondo en un
    degradado continuo.
    """
    cx, cy = W / 2.0, H / 2.0
    maxd = math.hypot(cx, cy)
    for y in range(H):
        row = []
        for x in range(W):
            d = math.hypot(x - cx, y - cy) / maxd
            if d < 0.42:
                row.append(0)
                continue
            t = (d - 0.42) / 0.58
            row.append(min(bands - 1, int(t * bands)))
        for x, band in enumerate(row):
            if band <= 0:
                continue
            c.blend(x, y, (*color, int(255 * strength * (band + 0.5) / bands)))


# ---------------------------------------------------------------------------
#  Helpers de escenario (bosque, mina, templo, puente, interior)
# ---------------------------------------------------------------------------
def _tree(c: Canvas, x: int, base: int, h: int, body, light) -> None:
    """Árbol antiguo: tronco grueso y copa formada por tres elipses."""
    trunk_h = max(8, h // 4)
    trunk_w = max(5, h // 9)          # los árboles antiguos tienen tronco ancho
    trunk = mix(body, (110, 76, 44), 0.55)
    c.fill_rect(x - trunk_w // 2, base - trunk_h, trunk_w, trunk_h, trunk)
    c.vline(x - trunk_w // 2, base - trunk_h, base - 1,
            mix(trunk, (0, 0, 0), 0.3))
    cy = base - trunk_h - h // 3
    c.ellipse(x, cy, h // 3, h // 4, body)
    c.ellipse(x - h // 5, cy + h // 6, h // 4, h // 5, body)
    c.ellipse(x + h // 5, cy + h // 6, h // 4, h // 5, body)
    # Manchita de luz arriba a la izquierda: da volumen sin degradados.
    c.ellipse(x - h // 7, cy - h // 10, h // 7, h // 10, light)


def _ground(c: Canvas, top, near, edge, grain: int = 0) -> None:
    """Suelo natural en tres bandas (césped o roca según los colores).

    `grain` > 0 añade moteado: es la textura de roca de la mina.
    """
    for y in range(GROUND, H):
        t = (y - GROUND) / float(H - GROUND)
        band = 0 if t < 0.33 else (1 if t < 0.66 else 2)
        col = (top, near, mix(near, edge, 0.35))[band]
        for x in range(W):
            c.px[y][x] = (*col, 255)
    c.hline(0, W - 1, GROUND, mix(edge, (0, 0, 0), 0.25))
    c.hline(0, W - 1, GROUND - 1, mix(edge, (0, 0, 0), 0.05))
    if grain:
        c.speckle(0, GROUND + 1, W, H, mix(edge, (0, 0, 0), 0.4),
                  density=grain, seed=41)


def _stalactites(c: Canvas, color, seed: int = 5, count: int = 16,
                 depth: int = 26) -> None:
    """Estalactitas colgando del techo de la mina (deterministas)."""
    state = seed & 0x7FFFFFFF
    for _ in range(count):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        x = state % W
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        h = 8 + state % depth
        w = 3 + (state >> 8) % 4
        c.tri((x, 0), (x - w, h), (x + w, h), color)


def _gear(c: Canvas, cx: int, cy: int, r: int, body, light) -> None:
    """Engranaje de la mina: dientes alrededor del aro y buje central."""
    for k in range(8):
        a = 2 * math.pi * k / 8
        tx = int(cx + math.cos(a) * r)
        ty = int(cy + math.sin(a) * r)
        c.fill_rect(tx - 2, ty - 2, 4, 4, body)
    c.circle(cx, cy, r, body)
    c.circle(cx, cy, r, mix(body, (255, 255, 255), 0.25), fill=False)
    c.circle(cx, cy, max(2, r // 2), mix(body, (0, 0, 0), 0.55))
    c.circle(cx - r // 3, cy - r // 3, max(1, r // 5), light)


def _gem(c: Canvas, cx: int, cy: int, r: int, color, glow) -> None:
    """Gema en forma de diamante con halo (la riqueza de la mina)."""
    c.radial_glow(cx, cy, r * 3, glow, 0.4, levels=3, blank_only=True)
    c.poly([(cx, cy - r), (cx + max(2, r // 2), cy),
            (cx, cy + r), (cx - max(2, r // 2), cy)], color)
    # Faceta de luz en la mitad superior izquierda
    c.poly([(cx, cy - r), (cx + max(2, r // 2), cy), (cx, cy)],
           mix(color, (255, 255, 255), 0.4))
    c.hline(cx - max(2, r // 2) + 1, cx + max(2, r // 2) - 1, cy,
            mix(color, (0, 0, 0), 0.35))


def _column(c: Canvas, x: int, base: int, h: int, body, light) -> None:
    """Columna dórica del templo con capitel, basa y acanaladuras."""
    w = 12
    c.fill_rect(x, base - h, w, h, body)
    c.fill_rect(x - 3, base - h - 5, w + 6, 5, mix(body, (255, 255, 255), 0.14))
    c.fill_rect(x - 2, base - 4, w + 4, 4, mix(body, (255, 255, 255), 0.10))
    c.vline(x, base - h, base - 1, light)
    c.vline(x + w - 1, base - h, base - 1, mix(body, (0, 0, 0), 0.3))
    for fx in (3, 6, 9):
        c.vline(x + fx, base - h + 3, base - 6,
                mix(body, (0, 0, 0), 0.16))


def _bridge_deck(c: Canvas, stone, dark, light) -> None:
    """Losas del puente de piedra: bandas horizontales con juntas
    escalonadas (la trama de losas da la perspectiva de la superficie)."""
    for y in range(GROUND, H):
        t = (y - GROUND) / float(H - GROUND)
        col = (stone, mix(stone, dark, 0.5), dark)[0 if t < 0.4 else
                                                   (1 if t < 0.75 else 2)]
        for x in range(W):
            c.px[y][x] = (*col, 255)
    c.hline(0, W - 1, GROUND, dark)
    # Juntas verticales: desplazadas en cada fila (trama de losas)
    row = 0
    y = GROUND + 3
    while y < H:
        offset = 16 if row % 2 else 0
        for x in range(offset, W, 32):
            c.vline(x, y, min(y + 5, H - 1), mix(dark, (0, 0, 0), 0.3))
        y += 6
        row += 1
    # Canto iluminado de la losa de arriba
    c.hline(0, W - 1, GROUND + 1, light)


def _bridge_rail(c: Canvas, post, rope) -> None:
    """Barandilla del puente: postes y dos cuerdas a diferentes alturas."""
    for x in range(8, W, 34):
        c.fill_rect(x, GROUND - 26, 3, 26, post)
        c.fill_rect(x, GROUND - 27, 5, 2, mix(post, (255, 255, 255), 0.2))
    c.hline(0, W - 1, GROUND - 24, rope)
    c.hline(0, W - 1, GROUND - 23, mix(rope, (255, 255, 255), 0.18))
    c.hline(0, W - 1, GROUND - 13, mix(rope, (0, 0, 0), 0.25))


def _block_wall(c: Canvas, base_color, joint, y0: int = 0,
                y1: int = None) -> None:
    """Muro de sillares: bloques alternados con juntas oscuras."""
    y1 = GROUND if y1 is None else y1
    for y in range(y0, y1):
        for x in range(W):
            c.px[y][x] = (*base_color, 255)
    row_h = 14
    row = 0
    y = y0
    while y < y1:
        c.hline(0, W - 1, y, joint)
        offset = 0 if row % 2 == 0 else 22
        for x in range(offset, W, 44):
            c.vline(x, y, min(y + row_h, y1) - 1, joint)
        y += row_h
        row += 1


# ---------------------------------------------------------------------------
#  Los cinco niveles — los escenarios del "El Héroe de las Matemáticas"
# ---------------------------------------------------------------------------
def level1() -> Canvas:
    """El Bosque de las Sumas: bosque verde y vibrante a plena luz
    ("lush green fantasy forest, bright and vibrant, large ancient trees,
    grass floor")."""
    c = Canvas(W, H)
    # Cielo diurno brillante
    _sky(c, (92, 172, 232), (176, 226, 246), steps=5)
    # Sol con halo cuantizado
    c.radial_glow(78, 36, 40, (255, 246, 186), 0.5, levels=4,
                  blank_only=True)
    c.circle(78, 36, 13, (255, 238, 150))
    c.circle(75, 33, 9, (255, 249, 205))
    # Colinas verdes lejanas
    far = (60, 130, 76)
    c.ellipse(104, GROUND - 6, 132, 34, far)
    c.ellipse(352, GROUND - 4, 148, 30, mix(far, (255, 255, 255), 0.10))
    # ÁRBOLES ANTIGUOS: troncos gruesos y copas enormes flanqueando la escena
    _tree(c, 52, GROUND + 6, 118, (44, 96, 52), (88, 160, 80))
    _tree(c, 438, GROUND + 6, 130, (44, 96, 52), (88, 160, 80))
    _tree(c, 152, GROUND + 8, 76, (40, 88, 50), (78, 148, 72))
    _tree(c, 344, GROUND + 8, 86, (40, 88, 50), (78, 148, 72))
    # Suelo de césped vivo (tono medio: así los enemigos siguen destacando)
    _ground(c, (46, 106, 56), (36, 86, 46), (68, 142, 72))
    # Flores silvestres en la franja de suelo visible
    for fx, col in ((36, (250, 220, 90)), (86, (240, 120, 140)),
                    (196, (250, 244, 210)), (286, (250, 220, 90)),
                    (404, (240, 120, 140)), (452, (255, 250, 230))):
        c.put(fx, 159, col)
        c.put(fx + 1, 159, mix(col, (255, 255, 255), 0.45))
        c.put(fx, 160, mix(col, (0, 0, 0), 0.25))
    _fog(c, GROUND - 8, 10, (170, 230, 200), 0.30)
    _vignette(c, strength=0.24)
    return c


def level2() -> Canvas:
    """La Mina de la Multiplicación: mina enana subterránea con vigas de
    madera, cristales luminosos, engranajes sueltos y suelo de piedra
    ("underground dwarf mine, wooden support beams, glowing crystals and
    scattered gears, stone floor")."""
    c = Canvas(W, H)
    # Subterránea: no hay cielo, solo pared de roca con veteado
    c.vgradient((6, 8, 16), (26, 28, 44), 0, GROUND - 1, steps=6)
    _stalactites(c, (4, 6, 12), seed=11, count=14)
    _stalactites(c, (10, 12, 22), seed=23, count=9, depth=15)
    c.speckle(0, 24, W, GROUND - 6, (34, 36, 56), density=0.05, seed=9)
    # Vigas de madera de sostén: dos marcos, el sello de una mina enana
    wood, wood_edge = (74, 50, 30), (100, 70, 42)
    for bx in (44, 396):
        c.fill_rect(bx, GROUND - 74, 6, 74, wood)
        c.fill_rect(bx + 34, GROUND - 74, 6, 74, wood)
        c.fill_rect(bx - 6, GROUND - 84, 52, 8, wood_edge)
        c.hline(bx - 6, bx + 45, GROUND - 74, mix(wood, (0, 0, 0), 0.35))
        c.vline(bx, GROUND - 74, GROUND - 1, mix(wood, (0, 0, 0), 0.3))
    # Engranajes sueltos del viejo mecanismo de extracción
    _gear(c, 150, 60, 16, (92, 74, 40), (146, 120, 68))
    _gear(c, 180, 84, 10, (78, 62, 34), (126, 104, 60))
    _gear(c, 328, 68, 13, (92, 74, 40), (146, 120, 68))
    # Cristales luminosos: cian, violeta y oro
    _gem(c, 240, 44, 9, (90, 230, 255), (60, 200, 255))
    _gem(c, 100, 122, 7, (200, 130, 255), (170, 100, 255))
    _gem(c, 386, 126, 8, (90, 230, 255), (60, 200, 255))
    _gem(c, 296, 116, 6, (255, 210, 110), (255, 190, 80))
    # Suelo de piedra: losas con juntas en perspectiva falsa
    _floor(c, (54, 52, 62), (40, 38, 48), (72, 70, 84))
    _vignette(c, strength=0.36)
    return c


def level3() -> Canvas:
    """El Templo de las Fracciones: templo antiguo de piedra azul mística
    con runas cian encendidas ("ancient ruined temple, mystical blue stone
    architecture, glowing cyan runes")."""
    c = Canvas(W, H)
    # Cielo nocturno hacia el azul místico del templo
    _sky(c, (6, 16, 48), (26, 66, 124), steps=6)
    _stars(c, 64, seed=31, color=(196, 232, 255, 255), y_max=96)
    _moon(c, 398, 34, 11, (226, 244, 255), (96, 190, 240))
    # Frontón roto del templo (silueta lejana) y muro trasero
    far = (14, 30, 64)
    c.tri((146, 64), (334, 64), (240, 32), far)
    c.fill_rect(150, 64, 180, 8, far)                      # dintel
    c.fill_rect(150, 72, 180, GROUND - 72,
                mix(far, (0, 0, 0), 0.18))                 # muro trasero
    # Pórtico de PIEDRA AZUL: dos columnas enteras, una partida y una rota
    col = (34, 58, 108)
    light = mix(col, (150, 220, 255), 0.30)
    _column(c, 92, GROUND, 94, col, light)
    _column(c, 374, GROUND, 94, col, light)
    _column(c, 176, GROUND, 56, col, light)    # partida por la mitad
    _column(c, 302, GROUND, 40, col, light)    # solo queda la base
    # Friso cian sobre el pórtico: la runa grande del templo
    c.fill_rect(146, 68, 188, 3, mix(col, (0, 0, 0), 0.3))
    stamp_glyph(c, "div", 240, 96, 6, (150, 245, 255, 255),
                (50, 220, 255, 255))
    # Trozo caído y escombros bajo la columna partida
    c.fill_rect(206, GROUND - 11, 46, 10, mix(col, (0, 0, 0), 0.2))
    c.vline(218, GROUND - 11, GROUND - 1, mix(col, (150, 220, 255), 0.24))
    c.speckle(190, GROUND - 12, 336, GROUND, mix(col, (0, 0, 0), 0.4),
              density=0.12, seed=17)
    # Suelo de losas azules
    _floor(c, (32, 52, 96), (22, 36, 70), (56, 88, 140))
    # Runas cian flotando: los símbolos del templo
    _runes(c, [("pm", 66, 96, 3), ("neq", 420, 88, 3),
               ("int", 124, 36, 3), ("theta", 330, 40, 3)],
           (150, 245, 255, 255), (50, 220, 255, 255), scale=3)
    _fog(c, GROUND - 14, 16, (60, 140, 210), 0.5)
    _vignette(c, strength=0.34)
    return c


def _nebula(c: Canvas, cx: int, cy: int, rx: int, ry: int,
            dark, mid, light) -> None:
    """Nube cósmica: tres parches elípticos superpuestos en tonos planos.

    Las nubes púrpura del espacio se resuelven con bandas discretas (como
    el resto del fondo): un degradado suave convertiría el cielo del
    nivel 4 en una fotografía y dispararía el número de colores.
    """
    c.ellipse(cx, cy, rx, ry, dark)
    c.ellipse(cx - rx // 4, cy - ry // 3, max(4, int(rx * 0.60)),
              max(3, int(ry * 0.58)), mid)
    c.ellipse(cx - rx // 3, cy - ry // 3, max(3, int(rx * 0.32)),
              max(2, int(ry * 0.30)), light)
    # Borde superior iluminado: una sola fila de píxeles claros
    c.hline(cx - rx // 2, cx + rx // 2, cy - ry + 1,
            mix(mid, (255, 255, 255), 0.25))


def level4() -> Canvas:
    """El Puente Hacia el Caos: largo puente de piedra suspendido en el
    espacio, cielo estrellado y nubes cósmicas púrpura ("a long dark stone
    bridge suspended in space, starry night sky with purple cosmic
    clouds")."""
    c = Canvas(W, H)
    _sky(c, (4, 3, 18), (48, 24, 96), steps=7)
    _stars(c, 170, seed=47, color=(235, 234, 255, 255), y_max=152)
    # Nubes cósmicas púrpura a ambos lados del puente
    _nebula(c, 102, 56, 82, 26, (42, 16, 76), (76, 32, 126), (114, 58, 172))
    _nebula(c, 378, 42, 66, 20, (38, 14, 70), (68, 28, 116), (104, 50, 158))
    _nebula(c, 258, 78, 54, 16, (34, 12, 64), (62, 26, 108), (96, 46, 148))
    # Resplandor del otro extremo: la grieta del caos hacia la que va el puente
    c.radial_glow(240, GROUND - 30, 64, (160, 74, 230), 0.34,
                  levels=4, blank_only=True)
    # El puente: losas de piedra oscura y barandilla
    _bridge_deck(c, (58, 52, 78), (28, 24, 44), (96, 90, 122))
    _bridge_rail(c, (34, 28, 46), (70, 58, 96))
    # Símbolos matemáticos flotando sobre el vacío
    _runes(c, [("sqrt", 62, 74, 3), ("theta", 306, 54, 3),
               ("inf", 424, 104, 3), ("pi", 176, 40, 3)],
           (214, 208, 255, 255), (150, 110, 255, 255), scale=3)
    _fog(c, GROUND - 10, 12, (96, 52, 168), 0.5)
    _vignette(c, strength=0.40)
    return c


def level5() -> Canvas:
    """El Castillo del Caos: interior, portales y símbolos matemáticos
    neón. El escenario del jefe final."""
    c = Canvas(W, H)
    wall = (18, 10, 30)
    _block_wall(c, wall, mix(wall, (0, 0, 0), 0.35), 0, GROUND)
    # Bóveda gótica: arcos apuntados concéntricos desde las esquinas
    for k in range(3):
        c.ellipse(W // 2, -12 + k * 2, W // 2 - 26 - k * 34, 96 + k * 30,
                  mix(wall, (255, 255, 255), 0.12), fill=False)
        c.ellipse(W // 2, -12 + k * 2, W // 2 - 25 - k * 34, 95 + k * 30,
                  mix(wall, (0, 0, 0), 0.35), fill=False)
    # Pilares góticos: fuste con capitel y pináculo apuntado
    for px in (16, 448):
        c.fill_rect(px, 0, 16, GROUND, mix(wall, (255, 255, 255), 0.06))
        c.vline(px, 0, GROUND - 1, mix(wall, (255, 255, 255), 0.16))
        c.vline(px + 15, 0, GROUND - 1, mix(wall, (0, 0, 0), 0.3))
        c.fill_rect(px - 3, 18, 22, 5, mix(wall, (255, 255, 255), 0.10))
        # Pináculo: dos triángulos (contorno claro + relleno oscuro)
        c.tri((px - 5, 18), (px + 23, 18), (px + 9, -4),
              mix(wall, (255, 255, 255), 0.18))
        c.tri((px - 2, 16), (px + 20, 16), (px + 9, 1),
              mix(wall, (0, 0, 0), 0.25))
    # Portales de neón púrpura: uno grande al centro y dos laterales
    _portal(c, 200, GROUND + 2, 56, 108, (58, 16, 86), (176, 92, 255),
            (150, 80, 255), arcs=4)
    _portal(c, 62, GROUND + 2, 34, 72, (64, 14, 62), (255, 90, 220),
            (255, 120, 235), arcs=3)
    _portal(c, 384, GROUND + 2, 34, 72, (64, 14, 62), (255, 90, 220),
            (255, 120, 235), arcs=3)
    # Suelo pulido con reflejo del neón bajo cada portal
    _floor(c, (26, 16, 40), (18, 10, 28), (44, 28, 62))
    for gx, col in ((228, (170, 96, 255)), (79, (230, 90, 210)),
                    (401, (230, 90, 210))):
        for i in range(10):
            c.blend(gx, GROUND + 3 + i * 2, (*col, max(0, 70 - i * 7)))
    # Símbolos matemáticos neón (cian) ...
    _runes(c, [("pi", 130, 40, 4), ("sum", 330, 44, 4),
               ("sqrt", 240, 24, 3), ("neq", 98, 92, 3),
               ("times", 384, 96, 3), ("theta", 174, 110, 3),
               ("alpha", 302, 110, 3)],
           (120, 240, 255, 255), (40, 200, 255, 255), scale=3)
    # ... y otros en magenta, para el neón de dos colores
    _runes(c, [("div", 428, 62, 3), ("int", 42, 64, 3)],
           (255, 140, 240, 255), (255, 70, 220, 255), scale=3)
    _fog(c, GROUND - 14, 16, (110, 50, 150), 0.5)
    _vignette(c, strength=0.44)
    return c


LEVELS = (level1, level2, level3, level4, level5)
