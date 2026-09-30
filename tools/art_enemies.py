"""Los enemigos de Math Battle, dibujados píxel a píxel.

Todos ocupan un lienzo de 32x32 y se guardan escalados x4 (128x128), con
la misma convención que el héroe: la luz cae de ARRIBA a la izquierda, la
sombra baja a la derecha y el contorno se pasa al final.

Los frames de `idle` son 2 y los de `hurt` 1, que es lo que espera el
carga-sprites del juego. El frame de `hurt` no se dibuja a mano: se
genera lavando el de `idle` con `Canvas.flushed()`, que mantiene la
silueta y solo cambia el color. Así el golpe nunca descuadra al enemigo.

Las paletas están en `palettes.py`, una por criatura. Cada paleta trae
varias bandas de tonos (sombra -> medio -> luz) más los colores de
acento: ojos, vetas de magma,Cristal arcano... En cada criatura hay un
comentario con el significado de las letras, porque los tonos comparten
letras entre bandas y conviene recordarlo al tocar el código.
"""

from __future__ import annotations

from . import palettes as P
from .pixel import Canvas

SIZE = 32
CX = 16          # centro horizontal del cuerpo
GROUND = 30      # última fila que toca el suelo
HURT_FLASH = (255, 146, 146, 255)


# ---------------------------------------------------------------------------
#  Piezas compartidas
# ---------------------------------------------------------------------------
def ground_shadow(c: Canvas, w: int = 11, y: int = GROUND + 1) -> None:
    """Sombra de contacto: elipse plana bajo los pies.

    Sin ella los enemigos flotan: da el contacto con el suelo aunque el
    juego no dibuje sombras.
    """
    half = w / 2.0
    for i in range(-w // 2, w // 2 + 1):
        t = 1.0 - abs(i) / (half + 0.5)
        depth = max(1, int(t * 2.2))
        for j in range(depth):
            c.blend(CX + i, y + j, (0, 0, 0, 115))


def eyes(c: Canvas, x: int, y: int, gap: int = 3, pupil=(24, 20, 36, 255),
         iris=None, angry: bool = False) -> None:
    """Par de ojos mirando a la izquierda (el héroe está a su izquierda).

    `iris` pinta el iris en color brillante: es lo que marca a los
    enemigos mágicos y hace legible su mirada sobre una silueta oscura.
    La pupila y el iris van en las DOS filas del globo ocular; si solo se
    pintan en la de arriba, la de abajo queda blanca y el ojo se lee como
    una banda brillante en vez de como un ojo.
    """
    for ex in (x, x + gap):
        c.fill_rect(ex, y, 2, 2, (255, 255, 255, 255))
        c.put(ex, y, pupil)
        c.put(ex, y + 1, pupil)
        if iris:
            c.put(ex + 1, y, iris)
            c.put(ex + 1, y + 1, iris)
    if angry:
        # Cejas en diagonal hacia abajo: enfado sin gastar 2 colores más.
        c.line(x - 1, y - 1, x + 1, y, pupil)
        c.line(x + gap - 1, y, x + gap + 1, y - 1, pupil)


def limb(c: Canvas, x0, y0, x1, y1, color, thickness: int = 2, hand=None):
    """Extremidad cónica: gruesa en la raíz, fina en la punta.

    Las extremidades que son palos de 1 px parecen alambre; estrechar la
    punta es lo que las hace leer como músculo.
    """
    steps = max(int(max(abs(x1 - x0), abs(y1 - y0))), 1)
    for i in range(steps + 1):
        t = i / steps
        th = max(1, int(round(thickness * (1.0 - 0.5 * t))))
        px = int(round(x0 + (x1 - x0) * t))
        py = int(round(y0 + (y1 - y0) * t))
        c.fill_rect(px, py, th, th, color)
    if hand:
        c.fill_rect(int(x1) - 1, int(y1) - 1, 3, 3, hand)


def horn(c: Canvas, x, y, sgn: int, color, tip=None, curve: int = 3) -> None:
    """Cuerno curvo que sale del cráneo hacia fuera y arriba."""
    for i in range(curve + 1):
        px = x + sgn * i
        py = y - i
        c.fill_rect(px, py, max(1, 2 - i // 2), 1, color)
    if tip:
        c.put(x + sgn * curve, y - curve, tip)


def hurt_frame(canvas: Canvas) -> Canvas:
    """Frame de daño: la silueta se lava de blanco-rojo.

    Se hace sobre el frame 0 de `idle`, así que la pose no cambia y el
    enemigo no "teletransporta" al recibir el golpe.
    """
    return canvas.flashed(HURT_FLASH, 0.78, levels=3)


# ---------------------------------------------------------------------------
#  1. Slime — el primer enemigo. Gelatinoso, sin patas, con un núcleo.
#     SLIME: G sombra, t cuerpo, g luz, e borde, h veta, v núcleo, w blanco
# ---------------------------------------------------------------------------
def slime(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.SLIME
    squish = 1.0 if phase == 0 else 0.88
    ground_shadow(c, 16)
    rx = 11.0 if phase == 0 else 12.0
    ry = 9.0 * squish
    cy = GROUND - ry - 1
    c.ellipse(CX, cy + 1, rx, ry, p["e"])            # borde oscuro
    c.ellipse(CX, cy, rx - 1, ry - 1, p["G"])
    c.ellipse(CX, cy - 0.5, rx - 1.5, ry - 1.5, p["t"])
    c.ellipse(CX - 1, cy - 1, rx - 4, ry - 3.5, p["g"])
    # Núcleo suspendido: da la sensación de "dentro de algo".
    c.ellipse(CX + 1, cy + 3, 2.5, 2.0, p["h"])
    c.put(CX + 1, cy + 2, p["v"])
    c.put(CX, cy + 3, p["v"])
    # Vetas arcanas: dosramas cortas, no un rayado aleatorio.
    c.put(CX - 6, cy + 4, p["h"])
    c.put(CX - 7, cy + 5, p["h"])
    c.put(CX + 6, cy + 2, p["h"])
    c.put(CX + 7, cy + 1, p["h"])
    # Brillo especular: el punto de luz de la viscosidad.
    for dx, dy in ((-5, -3), (-4, -3), (-4, -4), (-3, -3)):
        c.put(CX + dx, int(cy) + dy, p["w"])
    eyes(c, CX - 4, int(cy) - 1, gap=5, iris=p["v"])
    if phase == 0:
        c.hline(CX - 1, CX + 2, int(cy) + 5, p["e"])   # boca abierta
    else:
        c.hline(CX, CX + 1, int(cy) + 5, p["e"])
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  2. Goblin — bajo,orzudo y con un garrote. El primer humanoide.
#     GOBLIN: G sombra, t piel, o piel-luz, d túnica, c túnica-luz,
#             f cuero, z cuero-luz, y ojos, w blanco
# ---------------------------------------------------------------------------
def goblin(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.GOBLIN
    dy = 1 if phase else 0
    ground_shadow(c, 13)
    # Piernas cortas y anchas.
    for lx in (CX - 5, CX + 2):
        c.fill_rect(lx, 20 + dy, 3, GROUND - 20 - dy, p["G"])
        c.fill_rect(lx, 20 + dy, 1, GROUND - 20 - dy, p["t"])
        c.fill_rect(lx - 1, GROUND - 2, 4, 2, p["f"])   # pie
    # Torso en cuña: pecho ancho, cintura fina.
    c.poly([(CX - 6, 13 + dy), (CX + 6, 13 + dy), (CX + 4, 21 + dy),
            (CX - 4, 21 + dy)], p["G"])
    c.poly([(CX - 5, 14 + dy), (CX + 5, 14 + dy), (CX + 3, 20 + dy),
            (CX - 3, 20 + dy)], p["d"])
    c.poly([(CX - 5, 14 + dy), (CX - 1, 14 + dy), (CX - 2, 20 + dy),
            (CX - 3, 20 + dy)], p["t"])
    # Peto de cuero con una hebilla.
    c.fill_rect(CX - 3, 16 + dy, 6, 4, p["f"])
    c.hline(CX - 3, CX + 2, 16 + dy, p["z"])
    c.put(CX, 18 + dy, p["y"])
    # Brazo derecho en alto, sujetando el garrote.
    limb(c, CX - 6, 15 + dy, CX - 8, 21 + dy, p["G"], 2)
    limb(c, CX + 5, 15 + dy, CX + 7, 12 + dy, p["G"], 2)
    c.line(CX + 7, GROUND - 1, CX + 8, 8 + dy, p["f"], thickness=2)
    c.put(CX + 8, 7 + dy, p["z"])                       # nudo del garrote
    # Cabeza y orejas largas: lo que lo hace goblin.
    hy = 9 + dy
    c.ellipse(CX, hy, 5, 4, p["G"])
    c.ellipse(CX, hy - 0.5, 4, 3, p["t"])
    for sgn in (-1, 1):
        c.poly([(CX + sgn * 4, hy), (CX + sgn * 9, hy - 3),
                (CX + sgn * 9, hy + 1), (CX + sgn * 4, hy + 2)], p["t"])
        c.line(CX + sgn * 5, hy + 1, CX + sgn * 8, hy - 1, p["G"])
    c.ellipse(CX - 1, hy - 2, 3, 2, p["f"])             # pelo ralo
    eyes(c, CX - 3, hy, gap=4, iris=p["y"], angry=True)
    c.put(CX - 1, hy + 3, p["w"])                       # dientes salidos
    c.put(CX + 1, hy + 3, p["w"])
    c.outline(P.INK, diagonal=True)
    # Luz de borde por el lado izquierdo, como en el resto de la hoja. El
    # goblin es verde medio sobre un castillo casi negro y su contorno se
    # perdía; estas líneas separan hombro, cabeza y pierna del fondo.
    c.line(CX - 6, 14 + dy, CX - 4, 20 + dy, p["t"])    # hombro -> cadera
    c.line(CX - 5, 5 + dy, CX - 5, 11 + dy, p["t"])     # sien
    c.line(CX - 5, 21 + dy, CX - 5, GROUND - 3, p["t"]) # pierna
    c.put(CX - 9, 5 + dy, p["t"])                       # punta de la oreja
    return c


# ---------------------------------------------------------------------------
#  3. Esqueleto — puro hueso, con las costillas marcadas.
#     SKELETON: r hueso-sombra, m hueso, c hueso-luz, n hueso-luz, s hueco,
#               e brasa, o brasa-brillo, B marrón, b marrón-luz
# ---------------------------------------------------------------------------
def skeleton(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.SKELETON
    dy = 1 if phase else 0
    ground_shadow(c, 11)
    # Tibias.
    for lx in (CX - 4, CX + 3):
        c.fill_rect(lx, 21 + dy, 2, GROUND - 21 - dy, p["m"])
        c.put(lx, 22 + dy, p["c"])
        c.fill_rect(lx - 1, GROUND - 1, 3, 1, p["m"])
    # Columna.
    c.fill_rect(CX - 1, 12 + dy, 2, 10, p["m"])
    c.hline(CX - 4, CX + 4, 20 + dy, p["m"])           # pelvis
    # Caja torácica: 4 arcos que se estrecian hacia abajo.
    for i in range(4):
        wdt = 6 - i
        y = 13 + dy + i * 2
        c.hline(CX - wdt, CX + wdt, y, p["m"])
        c.hline(CX - wdt + 1, CX + wdt - 1, y, p["c"])
        if i < 3:
            c.fill_rect(CX - wdt, y, 1, 2, p["m"])
            c.fill_rect(CX + wdt, y, 1, 2, p["m"])
    c.fill_rect(CX - 1, 13 + dy, 2, 6, p["r"])         # esternón
    # Brazos colgantes.
    limb(c, CX - 6, 14 + dy, CX - 9, 19 + dy, p["m"], 2)
    limb(c, CX + 6, 14 + dy, CX + 9, 19 + dy, p["m"], 2)
    c.fill_rect(CX - 10, 19 + dy, 2, 2, p["m"])        # manos
    c.fill_rect(CX + 8, 19 + dy, 2, 2, p["m"])
    # Cráneo: cuencas oscuras con brasa dentro.
    hy = 8 + dy
    c.ellipse(CX, hy, 4, 4, p["m"])
    c.ellipse(CX, hy - 1, 3, 3, p["c"])
    c.fill_rect(CX - 2, hy + 2, 7, 3, p["m"])
    c.put(CX - 1, hy + 2, p["n"])
    c.put(CX + 2, hy + 2, p["n"])
    c.fill_rect(CX - 2, hy - 1, 2, 2, p["s"])          # cuencas
    c.fill_rect(CX + 1, hy - 1, 2, 2, p["s"])
    c.put(CX - 2, hy, p["o"])                          # brasas encendidas
    c.put(CX + 2, hy, p["o"])
    c.put(CX + 2, hy + 1, p["e"])
    c.put(CX, hy + 3, p["s"])                          # nariz
    c.hline(CX - 2, CX + 2, hy + 5, p["s"])            # dentadura
    for x in range(CX - 2, CX + 3, 2):
        c.vline(x, hy + 4, hy + 5, p["m"])
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  4. Bruja — sombrero puntiagudo y varita con estrella.
#     WITCH: P túnica-sombra, p túnica, m túnica-luz, L túnica-luz,
#            n piel, k piel-luz, v varita, b oro, s verde, w blanco
# ---------------------------------------------------------------------------
def witch(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.WITCH
    dy = 1 if phase else 0
    ground_shadow(c, 13)
    # Túnico: campana que se abre hacia el suelo.
    c.poly([(CX - 4, 13 + dy), (CX + 4, 13 + dy), (CX + 9, GROUND),
            (CX - 9, GROUND)], p["P"])
    c.poly([(CX - 3, 14 + dy), (CX + 3, 14 + dy), (CX + 7, GROUND - 1),
            (CX - 7, GROUND - 1)], p["p"])
    for x in (CX - 4, CX, CX + 4):                     # pliegues
        c.vline(x, 17 + dy, GROUND - 1, p["P"])
    c.vline(CX - 1, 16 + dy, GROUND - 2, p["m"])
    c.hline(CX - 8, CX + 8, GROUND - 1, p["P"])        # dobladillo
    # Brazo con la varita.
    limb(c, CX + 4, 15 + dy, CX + 8, 13 + dy, p["p"], 2)
    c.line(CX + 8, 14 + dy, CX + 9, 6 + dy, p["b"], thickness=2)
    c.put(CX + 9, 5 + dy, p["v"])                       # estrella
    c.put(CX + 8, 5 + dy, p["v"])
    c.put(CX + 9, 4 + dy, p["w"])
    # Cabeza: solo cara, el sombrero la envuelve.
    hy = 11 + dy
    c.ellipse(CX, hy, 3, 3, p["n"])
    c.ellipse(CX + 1, hy, 2, 2, p["k"])
    eyes(c, CX - 2, hy - 1, gap=3, iris=p["v"])
    # Sombrero puntiagudo con ala ancha: la silueta de la bruja.
    c.ellipse(CX, hy - 3, 7, 1.6, p["P"])
    c.poly([(CX - 4, hy - 3), (CX + 4, hy - 3), (CX + 3, hy - 12),
            (CX - 1, hy - 12)], p["P"])
    c.poly([(CX - 3, hy - 4), (CX + 3, hy - 4), (CX + 2, hy - 12),
            (CX - 1, hy - 12)], p["p"])
    c.vline(CX - 2, hy - 7, hy - 11, p["m"])
    c.fill_rect(CX - 3, hy - 6, 6, 1, p["s"])          # cinta
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  5. Gólem de piedra — bloques, grietas de magma, ninguna cara.
#     STONE_GOLEM: q piedra-sombra, r piedra, n piedra-luz, p piedra-luz,
#                  e magma, E magma-brillo, m musgo, i musgo-luz, R junta
# ---------------------------------------------------------------------------
def stone_golem(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.STONE_GOLEM
    dy = 1 if phase else 0
    ground_shadow(c, 18)
    # Piernas de bloque.
    for lx in (CX - 8, CX + 4):
        c.fill_rect(lx, 22 + dy, 5, GROUND - 22 - dy, p["q"])
        c.fill_rect(lx, 22 + dy, 1, GROUND - 22 - dy, p["r"])
    # Torso: dos bloques de distinto tamaño, no un óvalo.
    c.fill_rect(CX - 8, 12 + dy, 16, 11, p["q"])
    c.fill_rect(CX - 7, 13 + dy, 14, 9, p["r"])
    c.fill_rect(CX - 7, 13 + dy, 2, 9, p["n"])         # luz en el borde
    c.hline(CX - 8, CX + 7, 20 + dy, p["R"])            # junta entre bloques
    # Grietas de magma: la única fuente cálida del cuerpo.
    for gx, gy in ((CX - 4, 15), (CX + 2, 17), (CX - 1, 20), (CX + 5, 14)):
        c.put(gx, gy, p["e"])
        c.put(gx + 1, gy, p["E"])
    c.line(CX - 4, 16, CX - 3, 18, p["e"])
    c.line(CX + 2, 18, CX + 3, 20, p["e"])
    c.put(CX - 4, 18, p["E"])
    c.put(CX + 3, 20, p["E"])
    # Musgo: rompe la piedra y le da antigüedad.
    c.put(CX - 6, 14 + dy, p["m"])
    c.put(CX - 5, 14 + dy, p["i"])
    c.put(CX + 6, 20 + dy, p["m"])
    # Brazos-columna, pesados.
    for sgn in (-1, 1):
        ax = CX + sgn * 8
        c.fill_rect(ax - 1, 13 + dy, 4, 8, p["q"])
        c.fill_rect(ax, 14 + dy, 2, 6, p["r"])
        c.fill_rect(ax - 1, 20 + dy, 5, 4, p["q"])      # puño
        c.fill_rect(ax, 21 + dy, 3, 2, p["r"])
        c.put(ax + 1, 19 + dy, p["e"])                  # brasa en el puño
    # Cabeza: bloque con una única rendija de magma por ojo.
    c.fill_rect(CX - 5, 4 + dy, 10, 8, p["q"])
    c.fill_rect(CX - 4, 5 + dy, 8, 6, p["r"])
    c.fill_rect(CX - 4, 5 + dy, 2, 6, p["n"])
    c.hline(CX - 3, CX + 3, 8 + dy, p["e"])             # rendija
    c.put(CX, 8 + dy, p["E"])
    c.put(CX + 2, 8 + dy, p["E"])
    c.hline(CX - 3, CX + 3, 5 + dy, p["m"])             # musgo en la frente
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  6. Fantasma — no tiene pies; la cola se disuelve en dientes.
#     GHOST: w sombra, g sombra, e medio, v medio-luz, h luz, s luz, k
#            blanco-hueso, c arcano, a blanco
# ---------------------------------------------------------------------------
def ghost(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.GHOST
    dy = 2 if phase else 0
    # Ondulación inferior: 4 dientes desiguales, la marca del fantasma.
    hem = [(CX - 8, 24), (CX - 4, 28), (CX, 23), (CX + 4, 28), (CX + 8, 24)]
    c.poly([(CX - 8, 12 + dy), (CX + 8, 12 + dy)] + [(x, y + dy)
                                                     for x, y in hem], p["e"])
    # Volumen: la tela es más clara en el centro-derecha (luz de frente).
    c.poly([(CX - 7, 13 + dy), (CX + 4, 13 + dy), (CX + 7, 24 + dy),
            (CX - 6, 24 + dy)], p["v"])
    c.ellipse(CX, 9 + dy, 8, 7, p["e"])
    c.ellipse(CX, 8 + dy, 7, 6, p["v"])
    c.ellipse(CX - 1, 7 + dy, 4, 3, p["h"])
    # Un halo corto en la frente, no un óvalo claro en medio de la cara:
    # un óvalo grande se lee como un agujero y no como un rostro.
    c.ellipse(CX - 1, 5 + dy, 2, 1, p["s"])
    # Ojos: agujeros oscuros con un punto de brasa dentro.
    for ex in (CX - 3, CX + 2):
        c.fill_rect(ex, 8 + dy, 2, 3, p["w"])
        c.put(ex, 9 + dy, p["c"])
    c.fill_rect(CX - 1, 13 + dy, 3, 2, p["w"])          # boca que grita
    c.put(CX, 13 + dy, p["c"])
    # Dibujo de niebla: halo suave por fuera, sin bites duros.
    c.radial_glow(CX, 18 + dy, 12, p["v"], 0.30, levels=3, blank_only=True)
    c.outline(p["g"])
    return c


# ---------------------------------------------------------------------------
#  7. Diablo menor — cornudo, alado y con cola.
#     LESSER_DEMON: b piel-sombra, m piel, Z piel-luz, h cuerno, E cuerno
#                   punta, R cuerpo-sombra, r cuerpo, w ala, q garra
# ---------------------------------------------------------------------------
def lesser_demon(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.LESSER_DEMON
    dy = 1 if phase else 0
    ground_shadow(c, 14)
    # Alas membranosas detrás del torso. Van en `w` con las costillas en `h`
    # y NO tocan el borde del lienzo: unas alas que llenan el sprite
    # entierran al cuerpo y la criatura deja de leerse.
    for sgn in (-1, 1):
        c.poly([(CX + sgn * 4, 12 + dy), (CX + sgn * 10, 8 + dy),
                (CX + sgn * 10, 15 + dy), (CX + sgn * 6, 19 + dy)], p["w"])
        c.poly([(CX + sgn * 5, 13 + dy), (CX + sgn * 9, 10 + dy),
                (CX + sgn * 9, 14 + dy), (CX + sgn * 6, 17 + dy)], p["R"])
        for k in range(2):                                # costillas alares
            c.line(CX + sgn * (5 + k * 2), 12 + dy,
                   CX + sgn * (9 + k), 8 + k * 2 + dy, p["h"])
    # Piernas con rodillas.
    for lx in (CX - 5, CX + 3):
        c.fill_rect(lx, 21 + dy, 3, GROUND - 21 - dy, p["R"])
        c.fill_rect(lx, 21 + dy, 1, GROUND - 21 - dy, p["r"])
        c.fill_rect(lx, GROUND - 1, 3, 1, p["b"])
    # Torso musculoso.
    c.poly([(CX - 6, 12 + dy), (CX + 6, 12 + dy), (CX + 4, 22 + dy),
            (CX - 4, 22 + dy)], p["R"])
    c.poly([(CX - 4, 13 + dy), (CX + 4, 13 + dy), (CX + 3, 21 + dy),
            (CX - 3, 21 + dy)], p["r"])
    c.poly([(CX - 4, 13 + dy), (CX - 1, 13 + dy), (CX - 1, 21 + dy),
            (CX - 3, 21 + dy)], p["m"])
    # Brazos con garras.
    limb(c, CX - 6, 14 + dy, CX - 9, 20 + dy, p["R"], 2, hand=p["q"])
    limb(c, CX + 6, 14 + dy, CX + 9, 19 + dy, p["R"], 2, hand=p["q"])
    # Cuernos curvos hacia fuera.
    for sgn in (-1, 1):
        horn(c, CX + sgn * 3, 6 + dy, sgn, p["h"], tip=p["E"], curve=3)
    # Cabeza.
    hy = 9 + dy
    c.ellipse(CX, hy, 4, 4, p["R"])
    c.ellipse(CX, hy - 1, 3, 3, p["m"])
    c.ellipse(CX, hy - 2, 2, 2, p["Z"])
    eyes(c, CX - 2, hy - 1, gap=3, iris=p["E"], angry=True)
    c.hline(CX - 1, CX + 2, hy + 2, p["Z"])            # colmillos
    c.put(CX - 1, hy + 3, p["b"])
    c.put(CX + 2, hy + 3, p["b"])
    # Cola en S con punta afilada.
    c.line(CX + 4, 24 + dy, CX + 8, 25 + dy, p["R"], thickness=2)
    c.line(CX + 8, 25 + dy, CX + 9, 22 + dy, p["R"], thickness=1)
    c.put(CX + 9, 21 + dy, p["E"])                      # punta
    c.outline(P.INK_WARM, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  8. Fénix — las plumas son fuego: la rampa va de brasa a blanco caliente.
#     PHOENIX: C sombra, r cuerpo, t luz, c luz, Y brasa, F blanco-caliente,
#              z pico, u ala-borde, K contorno, m/q piel
# ---------------------------------------------------------------------------
def phoenix(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.PHOENIX
    dy = 1 if phase else 0
    ground_shadow(c, 10)
    # Cola larga en plumas: 4 plumas que menguan hacia abajo.
    for i, (fx, fy) in enumerate(((CX + 4, 24), (CX + 6, 27), (CX + 8, 29),
                                  (CX + 1, 27))):
        c.fill_rect(fx, fy, 2, GROUND - fy, p["C"] if i % 2 else p["r"])
    # Cuerpo ovoide.
    c.ellipse(CX - 1, 17 + dy, 6, 7, p["C"])
    c.ellipse(CX - 1, 16 + dy, 5, 6, p["r"])
    c.ellipse(CX - 1, 15 + dy, 3, 4, p["t"])
    c.ellipse(CX - 1, 15 + dy, 2, 2, p["Y"])           # pecho encendido
    # Alas: dos, en penacho hacia arriba (el fénix renace de las cenizas).
    for sgn in (-1, 1):
        c.poly([(CX - 1 + sgn * 2, 15 + dy), (CX + sgn * 11, 3 + dy),
                (CX + sgn * 13, 12 + dy), (CX + sgn * 5, 19 + dy)], p["r"])
        c.poly([(CX + sgn * 3, 14 + dy), (CX + sgn * 9, 6 + dy),
                (CX + sgn * 10, 12 + dy), (CX + sgn * 5, 17 + dy)], p["t"])
        for k in range(3):                             # plumas sueltas
            c.line(CX + sgn * (4 + k * 2), 13 + dy,
                   CX + sgn * (10 + k), 4 + k * 2 + dy, p["Y"])
    # Cabeza y cresta.
    hy = 10 + dy
    c.ellipse(CX - 1, hy, 3, 3, p["r"])
    c.ellipse(CX - 1, hy - 1, 2, 2, p["t"])
    for i in range(3):                                 # cresta de plumas
        c.put(CX - 2 + i, hy - 3 - (i == 1), p["Y"])
    c.poly([(CX + 2, hy), (CX + 6, hy + 1), (CX + 2, hy + 2)], p["z"])  # pico
    c.put(CX + 1, hy - 1, (20, 16, 12, 255))           # ojo
    c.put(CX + 1, hy, p["F"])
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  9. Caballero oscuro — armadura negra con visera encendida y penacho.
#     DARK_KNIGHT: U armadura-sombra, u armadura, v armadura-luz, s brillo,
#                  r tela-sombra, q tela, E visera, G adorno, R plume
# ---------------------------------------------------------------------------
def dark_knight(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.DARK_KNIGHT
    dy = 1 if phase else 0
    ground_shadow(c, 14)
    # Grebas.
    for lx in (CX - 5, CX + 2):
        c.fill_rect(lx, 21 + dy, 4, GROUND - 21 - dy, p["U"])
        c.fill_rect(lx, 21 + dy, 1, GROUND - 21 - dy, p["u"])
        c.fill_rect(lx - 1, GROUND - 2, 5, 2, p["U"])   # sabata
    # Torso: peto con muslo y faldón.
    c.poly([(CX - 6, 12 + dy), (CX + 6, 12 + dy), (CX + 5, 20 + dy),
            (CX - 5, 20 + dy)], p["U"])
    c.poly([(CX - 4, 13 + dy), (CX + 4, 13 + dy), (CX + 3, 19 + dy),
            (CX - 3, 19 + dy)], p["u"])
    c.vline(CX, 13 + dy, 19 + dy, p["v"])               # línea central
    c.poly([(CX - 5, 20 + dy), (CX + 5, 20 + dy), (CX + 6, 25 + dy),
            (CX - 6, 25 + dy)], p["R"])                  # faldón
    c.hline(CX - 5, CX + 5, 20 + dy, p["G"])            # cinturón de adorno
    # Espaldar y hombreras. El hombro derecho llega hasta la empuñadura:
    # si el brazo se dibuja demasiado lejos del torso, la espada queda
    # flotando separada de la figura.
    c.fill_rect(CX - 7, 12 + dy, 3, 4, p["u"])
    c.fill_rect(CX + 4, 11 + dy, 4, 5, p["u"])
    c.put(CX - 6, 12 + dy, p["s"])
    c.put(CX + 5, 11 + dy, p["s"])
    # Brazo que empuña la espada, y espada en alto.
    limb(c, CX + 6, 15 + dy, CX + 7, 12 + dy, p["U"], 2)
    c.line(CX + 8, 11 + dy, CX + 11, 2 + dy, p["v"], thickness=2)
    c.put(CX + 11, 1 + dy, p["s"])                      # punta de la hoja
    c.line(CX + 6, 13 + dy, CX + 10, 11 + dy, p["s"])   # guarda
    c.put(CX + 8, 12 + dy, p["E"])                      # gema de la empuñadura
    # Yunque + visera encendida: el rostro del caballero.
    c.fill_rect(CX - 4, 4 + dy, 8, 8, p["U"])
    c.fill_rect(CX - 3, 5 + dy, 6, 6, p["u"])
    c.fill_rect(CX - 3, 8 + dy, 6, 2, (10, 8, 14, 255))  # ranura de la visera
    c.put(CX - 2, 8 + dy, p["E"])
    c.put(CX, 8 + dy, p["E"])
    c.put(CX + 2, 8 + dy, p["E"])
    c.put(CX, 9 + dy, p["q"])
    c.vline(CX, 5 + dy, 7 + dy, p["v"])                 # nasal
    c.put(CX + 1, 6 + dy, p["s"])
    # Penacho: plumas rojas que framing la cabeza.
    for i in range(4):
        c.put(CX - 4 + i, 3 + dy - (i // 2), p["r"])
        c.put(CX + 4 - i, 3 + dy - (i // 2), p["q"])
    c.put(CX, 2 + dy, p["E"])
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  10. Mago — capucha, túnica y orbe arcano flotante.
#      MAGE: s piel-sombra, q piel, k piel-luz, M túnica-sombra, m túnica,
#            u túnica-luz, v orbe, b cayado, o túnica-borde
# ---------------------------------------------------------------------------
def mage(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.MAGE
    dy = 1 if phase else 0
    ground_shadow(c, 13)
    # Túnica larga con vuelo: la campana se ensancha al llegar al suelo.
    c.poly([(CX - 4, 13 + dy), (CX + 4, 13 + dy), (CX + 9, GROUND),
            (CX - 9, GROUND)], p["M"])
    c.poly([(CX - 3, 14 + dy), (CX + 3, 14 + dy), (CX + 7, GROUND - 1),
            (CX - 7, GROUND - 1)], p["m"])
    c.poly([(CX - 3, 14 + dy), (CX, 14 + dy), (CX - 1, GROUND - 2),
            (CX - 5, GROUND - 1)], p["u"])
    c.hline(CX - 8, CX + 8, GROUND - 1, p["M"])        # dobladillo
    # Manos salientes de las mangas.
    c.fill_rect(CX - 9, 20 + dy, 3, 2, p["q"])
    c.fill_rect(CX + 6, 20 + dy, 3, 2, p["q"])
    # Capucha: dos cuernos de tela con la cara en la sombra.
    hy = 10 + dy
    c.poly([(CX - 5, 14 + dy), (CX - 6, 6 + dy), (CX - 2, 2 + dy),
            (CX + 3, 3 + dy), (CX + 6, 7 + dy), (CX + 5, 14 + dy)], p["M"])
    c.ellipse(CX, hy, 4, 4, p["M"])
    c.ellipse(CX + 1, hy + 1, 2, 3, p["m"])
    c.put(CX, hy, p["k"])
    c.put(CX + 2, hy, p["k"])
    c.put(CX, hy + 1, p["k"])
    c.put(CX + 2, hy + 1, p["k"])
    eyes(c, CX, hy, gap=2, iris=p["v"])
    c.vline(CX - 3, 4 + dy, 12 + dy, p["m"])            # borde de la capucha
    # Cayado con orbe: el orbe se dibuja DESPUÉS del halo.
    c.line(CX + 8, GROUND - 1, CX + 8, 12 + dy, p["b"], thickness=2)
    ox, oy = CX + 8, 8 + dy
    c.radial_glow(ox, oy, 4, p["v"], 0.55, levels=3, blank_only=True)
    c.circle(ox, oy, 2, p["v"])
    c.put(ox, oy, (255, 255, 255, 255))
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  11. Hidra — cinco cuellos y cinco cabezas. El rival que exige acertar.
#      HYDRA: W cuerpo-sombra, g cuerpo, t luz, p luz, k vientre, Y ojo,
#             F brasa, K contorno
# ---------------------------------------------------------------------------
def hydra(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.HYDRA
    sway = 1 if phase else -1
    ground_shadow(c, 20)
    # Tronco compacto y bajo, con las patas asomando por debajo.
    c.ellipse(CX, 24, 12, 5, p["W"])
    c.ellipse(CX, 23, 11, 4, p["g"])
    c.ellipse(CX - 1, 22, 7, 2, p["t"])                  # lomo iluminado
    for lx in (CX - 9, CX - 3, CX + 5):
        c.fill_rect(lx, 26, 3, 4, p["W"])
        c.fill_rect(lx, 26, 1, 4, p["g"])
        c.fill_rect(lx - 1, GROUND - 1, 4, 1, p["W"])   # garra
    # Cinco cuellos en abanico, cada uno más claro que el anterior para
    # que se separen del tronco. La diferencia de altura es lo que da la
    # silueta en peine: todos a la misma altura serían una valla.
    #
    # El abanico se mantiene dentro de x=3..29 porque `outline` añade un
    # píxel más: con el abanico más abierto los hocicos y las chispas de
    # aliento se dibujaban fuera del lienzo y se perdían.
    necks = ((-6, 14, -2), (-3, 10, -1), (0, 7, 0), (3, 11, 1), (6, 15, 2))
    for i, (dx, ny, tilt) in enumerate(necks):
        bx, by = CX + dx, 24
        hx, hy = bx + tilt, ny + sway * (1 if i % 2 else 0)
        c.line(bx, by, hx, hy + 2, p["W"], thickness=3)
        c.line(bx, by, hx, hy + 2, p["g"], thickness=1)
        # La cabeza central es un pelo mayor: da un punto de foco al
        # abanico en lugar de cinco cabezas del mismo tamaño.
        r = 4 if i == 2 else 3
        c.ellipse(hx, hy, r, 2, p["W"])
        c.ellipse(hx, hy - 1, r - 1, 1, p["g"])
        d = 1 if dx >= 0 else -1
        c.put(hx + d * r, hy, p["t"])                   # hocico
        c.put(hx + d * (r - 1), hy - 1, p["Y"])        # ojo
        # Aliento: dos chispas de fuego saliendo de la boca.
        c.put(hx + d * (r + 1), hy, p["F"])
        c.put(hx + d * (r + 2), hy - 1, p["F"])
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  12. Sombra — una figura de vacío con dos ojos violeta y nada más.
#      SHADOW: e vacío, U cuerpo, u cuerpo-luz, v borde, k niebla, c brasa,
#              w blanco
# ---------------------------------------------------------------------------
def shadow(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.SHADOW
    dy = 1 if phase else 0
    # No lleva sombra de contacto: flota.
    # Aura de vacío: un óvalo grande y translúcido detrás de la figura.
    c.radial_glow(CX, 17 + dy, 13, p["U"], 0.55, levels=4, blank_only=True)
    # Manto que se deshace en hilos en vez de terminar recto.
    hem = [(CX - 9, 26), (CX - 5, 29), (CX - 2, 25), (CX + 1, 29),
           (CX + 4, 25), (CX + 7, 29), (CX + 9, 25)]
    c.poly([(CX - 7, 10 + dy), (CX + 7, 10 + dy)] + hem, p["e"])
    c.poly([(CX - 5, 11 + dy), (CX + 3, 11 + dy), (CX + 5, 25 + dy),
            (CX - 5, 25 + dy)], p["U"])
    c.vline(CX - 3, 13 + dy, 24 + dy, p["u"])
    c.vline(CX + 2, 13 + dy, 24 + dy, p["U"])
    # Capucha con la nada dentro.
    c.poly([(CX - 5, 13 + dy), (CX - 5, 5 + dy), (CX, 1 + dy),
            (CX + 5, 5 + dy), (CX + 5, 13 + dy)], p["e"])
    c.ellipse(CX, 7 + dy, 4, 4, (8, 6, 14, 255))      # vacío de la capucha
    for ex in (CX - 2, CX + 1):
        c.put(ex, 6 + dy, p["c"])
        c.put(ex, 7 + dy, p["c"])
    c.put(CX, 5 + dy, p["k"])                          # destello del borde
    # Manos: dos garras que se deshacen.
    for sgn in (-1, 1):
        for k in range(3):
            c.put(CX + sgn * 8, 17 + dy + k, p["u"] if k < 2 else p["k"])
    c.outline(p["u"])
    # LUZ DE BORDE. El manto es casi negro y los fondos también lo son, así
    # que sin esto la Sombra se fundía con el castillo: se medía una
    # diferencia de luminancia de 25/255, por debajo de lo que el ojo
    # separa. Una línea clara por el lado iluminado recorta la silueta
    # contra el fondo sin tener que aclarar el cuerpo y perder el "vacío".
    # Se dibuja sobre el contorno ya hecho, no antes.
    c.line(CX - 5, 5 + dy, CX, 1 + dy, p["v"])          # capucha, izquierda
    c.line(CX - 5, 5 + dy, CX - 5, 12 + dy, p["v"])
    c.line(CX - 7, 11 + dy, CX - 5, 17 + dy, p["v"])    # hombro y manto
    c.line(CX - 5, 17 + dy, CX - 4, 24 + dy, p["u"])
    for hx, hy in hem[:4]:                              # borde del vuelo
        c.put(hx, hy - 1, p["v"])
    return c


# ---------------------------------------------------------------------------
#  13. Archimago — el jefe de los humanos: alto, capucha y báculo arcano.
#      ARCHMAGE: P túnica-sombra, p túnica, L túnica-luz, v túnica-luz,
#                V brillo, b piel, m piel, n piel-luz, g oro, E oro-luz
# ---------------------------------------------------------------------------
def archmage(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.ARCHMAGE
    dy = 1 if phase else 0
    ground_shadow(c, 14)
    # Túnica que llega al suelo, con galón dorado.
    c.poly([(CX - 4, 12 + dy), (CX + 4, 12 + dy), (CX + 10, GROUND),
            (CX - 10, GROUND)], p["P"])
    c.poly([(CX - 3, 13 + dy), (CX + 3, 13 + dy), (CX + 8, GROUND - 1),
            (CX - 8, GROUND - 1)], p["p"])
    c.poly([(CX - 3, 13 + dy), (CX, 13 + dy), (CX - 1, GROUND - 2),
            (CX - 6, GROUND - 1)], p["L"])
    c.hline(CX - 9, CX + 9, GROUND - 1, p["P"])
    for y in (17, 21, 25):                             # galones
        c.hline(CX - 6, CX + 6, y + dy, p["g"])
    # Hombreras y capucha.
    c.fill_rect(CX - 7, 11 + dy, 4, 3, p["L"])
    c.fill_rect(CX + 4, 11 + dy, 4, 3, p["L"])
    hy = 9 + dy
    c.poly([(CX - 6, 13 + dy), (CX - 7, 4 + dy), (CX - 3, 0 + dy),
            (CX + 4, 1 + dy), (CX + 7, 5 + dy), (CX + 6, 13 + dy)], p["P"])
    c.poly([(CX - 4, 12 + dy), (CX - 4, 6 + dy), (CX, 2 + dy),
            (CX + 3, 5 + dy), (CX + 4, 12 + dy)], p["p"])
    # Rostro en sombra: solo la nariz y los ojos.
    c.ellipse(CX + 1, hy, 3, 3, p["b"])
    c.ellipse(CX + 1, hy, 2, 3, p["n"])
    eyes(c, CX, hy - 1, gap=2, iris=p["V"])
    c.put(CX + 1, hy + 2, p["n"])
    # Báculo: vara, anillos y gema. La gema va tras el halo.
    c.line(CX + 9, GROUND - 1, CX + 9, 10 + dy, p["g"], thickness=2)
    for i in range(3):                                 # anillos del báculo
        c.circle(CX + 9, 7 + dy - i * 2, 2 - (i == 2), p["p"])
    c.put(CX + 9, 4 + dy, p["E"])
    c.radial_glow(CX + 9, 4 + dy, 5, p["V"], 0.6, levels=3, blank_only=True)
    c.circle(CX + 9, 4 + dy, 1, p["E"])
    c.put(CX + 9, 4 + dy, (255, 255, 255, 255))
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
#  14. Dragón básico — BUSTO: cabeza grande y cuello coiled, con las puntas
#      de las alas asomando por detrás de los hombros.
#
#      Se probó primero la versión de cuerpo entero con cuatro patas y cola
#      y no funcionaba: a 32 px el ala, el cuerpo y las patas se enciman en
#      una sola masa y la figura deja de leerse. Un busto con la cabeza
#      ocupando la mitad del lienzo sí se lee, y de paso la cara del
#      enemigo es lo más grande de la pantalla, que es justo lo que debe
#      ser un jefe.
#      BASIC_DRAGON: W sombra, g cuerpo, t luz, k cuello, H cuerno,
#                    Y ojo, E fuego, r ala
# ---------------------------------------------------------------------------
def basic_dragon(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.BASIC_DRAGON
    dy = 1 if phase else 0
    ground_shadow(c, 20)
    # PUNTAS DE ALA: dos triangles detrás de los hombros. Solo la punta:
    # es lo único del ala que sobrevive a 32 px sin ensuciar la silueta.
    for sgn in (-1, 1):
        c.poly([(CX + sgn * 4, 24 + dy), (CX + sgn * 12, 14 + dy),
                (CX + sgn * 9, 24 + dy)], p["r"])
    # COLLAR: dos filas de escamas que separan cabeza de cuerpo.
    c.ellipse(CX, 24 + dy, 9, 4, p["W"])
    c.ellipse(CX, 23 + dy, 8, 3, p["g"])
    for k in range(-2, 3):                              # escamas del collar
        c.put(CX + k * 3, 21 + dy, p["H"])
        c.put(CX + k * 3, 22 + dy, p["H"])
    # CUELLO: dos pliegues que suben hacia la cabeza.
    c.poly([(CX - 7, 25 + dy), (CX - 5, 17 + dy), (CX + 5, 17 + dy),
            (CX + 7, 25 + dy)], p["W"])
    c.poly([(CX - 5, 24 + dy), (CX - 4, 18 + dy), (CX + 4, 18 + dy),
            (CX + 5, 24 + dy)], p["k"])
    # CABEZA: cráneo ancho. Las proporciones (20 de ancho por 12 de alto)
    # son las que pide un morro de dragón: hocico bajo y frente ancha.
    c.ellipse(CX, 11 + dy, 10, 6, p["W"])
    c.ellipse(CX, 10 + dy, 9, 5, p["g"])
    c.ellipse(CX - 1, 8 + dy, 6, 2, p["t"])             # frente iluminada
    # Hocico: bloque bajo y ancho, con la boca abierta.
    c.fill_rect(CX - 7, 12 + dy, 14, 5, p["W"])
    c.fill_rect(CX - 6, 12 + dy, 12, 3, p["g"])
    c.hline(CX - 7, CX + 6, 16 + dy, p["W"])            # interior de la boca
    for k in range(-3, 4, 3):                           # dientes
        c.put(CX + k, 16 + dy, p["H"])
        c.put(CX + k, 15 + dy, p["H"])
    # Ojos: cuencas hundidas bajo un ceño fruncido.
    c.fill_rect(CX - 6, 9 + dy, 4, 2, (16, 12, 20, 255))
    c.fill_rect(CX + 2, 9 + dy, 4, 2, (16, 12, 20, 255))
    c.put(CX - 5, 9 + dy, p["Y"])
    c.put(CX - 5, 10 + dy, p["Y"])
    c.put(CX + 3, 9 + dy, p["Y"])
    c.put(CX + 3, 10 + dy, p["Y"])
    c.line(CX - 7, 7 + dy, CX - 2, 8 + dy, p["W"])       # cejas
    c.line(CX + 6, 7 + dy, CX + 1, 8 + dy, p["W"])
    # Narinas y surco del morro.
    c.put(CX - 2, 13 + dy, p["W"])
    c.put(CX + 1, 13 + dy, p["W"])
    # Cuernos: dos, gruesos, curvados hacia fuera.
    for sgn in (-1, 1):
        horn(c, CX + sgn * 7, 6 + dy, sgn, p["W"], curve=4)
        horn(c, CX + sgn * 7, 6 + dy, sgn, p["H"], curve=3)
        c.put(CX + sgn * 11, 3 + dy, p["E"])            # punta encendida
    # Aliento: chispas de fuego saliendo de la boca.
    for dx, dy2 in ((-10, 20), (-11, 19), (10, 20), (11, 19)):
        c.put(CX + dx, dy2, p["E"])
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  15. Dragón supremo — el jefe final: misma pose de busto, pero con
#      corona de seis cuernos, escamas de rubí y fuego interior. La
#      diferencia con el básico tiene que verse SIN leer el nombre: más
#      cuernos, color más saturado y grietas de magma por la cara.
#      SUPREME_DRAGON: R sombra, r cuerpo, q luz, d cuello, H cuerno,
#                      F blanco-caliente, Y oro, E fuego
# ---------------------------------------------------------------------------
def supreme_dragon(phase: int = 0) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = P.SUPREME_DRAGON
    dy = 1 if phase else 0
    ground_shadow(c, 21)
    # ALAS: puntas más grandes y con tres muescas, para marcar jerarquía.
    for sgn in (-1, 1):
        c.poly([(CX + sgn * 4, 24 + dy), (CX + sgn * 13, 11 + dy),
                (CX + sgn * 10, 24 + dy)], p["R"])
        c.poly([(CX + sgn * 5, 23 + dy), (CX + sgn * 11, 14 + dy),
                (CX + sgn * 10, 22 + dy)], p["q"])
    # COLLAR de placas.
    c.ellipse(CX, 24 + dy, 10, 4, p["R"])
    c.ellipse(CX, 23 + dy, 9, 3, p["r"])
    for k in range(-2, 3):
        c.put(CX + k * 4, 21 + dy, p["H"])
        c.put(CX + k * 4, 22 + dy, p["H"])
        c.put(CX + k * 4, 20 + dy, p["Y"])
    # CUELLO.
    c.poly([(CX - 8, 25 + dy), (CX - 6, 17 + dy), (CX + 6, 17 + dy),
            (CX + 8, 25 + dy)], p["R"])
    c.poly([(CX - 6, 24 + dy), (CX - 5, 18 + dy), (CX + 5, 18 + dy),
            (CX + 6, 24 + dy)], p["d"])
    # CABEZA imponente.
    c.ellipse(CX, 11 + dy, 11, 7, p["R"])
    c.ellipse(CX, 10 + dy, 10, 6, p["r"])
    c.ellipse(CX - 1, 8 + dy, 6, 2, p["q"])
    c.fill_rect(CX - 8, 12 + dy, 16, 6, p["R"])
    c.fill_rect(CX - 7, 12 + dy, 14, 4, p["r"])
    c.hline(CX - 8, CX + 7, 17 + dy, p["R"])            # boca abierta
    for k in range(-4, 5, 4):                           # dientes
        c.put(CX + k, 17 + dy, p["F"])
        c.put(CX + k, 16 + dy, p["F"])
    # Grietas de magma cruzando la cara: la firma del rey.
    for gx, gy in ((CX - 3, 8), (CX + 4, 10), (CX - 6, 13), (CX + 2, 15)):
        c.put(gx, gy, p["E"])
        c.put(gx + 1, gy, p["Y"])
    # Ojos: brasas con el centro blanco, más fierce que el dragón básico.
    c.fill_rect(CX - 7, 9 + dy, 5, 3, (24, 10, 22, 255))
    c.fill_rect(CX + 2, 9 + dy, 5, 3, (24, 10, 22, 255))
    for ex in (CX - 6, CX + 3):
        c.put(ex, 9 + dy, p["E"])
        c.put(ex, 10 + dy, p["Y"])
        c.put(ex, 11 + dy, p["F"])
    c.line(CX - 8, 6 + dy, (CX - 2), 8 + dy, p["R"])    # cejas
    c.line(CX + 7, 6 + dy, (CX + 1), 8 + dy, p["R"])
    # Corona de SEIS cuernos, decrecientes hacia fuera.
    for dx, curve, tip in ((6, 3, "F"), (3, 4, "F"), (0, 5, "F"),
                           (-3, 4, "F"), (-6, 3, "Y")):
        horn(c, CX + dx, 5 + dy, 1 if dx >= 0 else -1, p["R"], curve=curve)
        horn(c, CX + dx, 5 + dy, 1 if dx >= 0 else -1, p["H"], curve=curve)
        c.put(CX + dx + (curve if dx >= 0 else -curve), 5 + dy - curve,
              p[tip])
    # Aliento: llamas a ambos lados, más grandes que en el básico.
    for sgn in (-1, 1):
        c.put(CX + sgn * 11, 20 + dy, p["E"])
        c.put(CX + sgn * 12, 19 + dy, p["Y"])
        c.put(CX + sgn * 12, 21 + dy, p["F"])
    c.outline(P.INK, diagonal=True)
    return c


# ---------------------------------------------------------------------------
#  16. Genérico — respaldo para cualquier enemigo no listado. Deliberadamente
#      neutro: un espectro sin rasgos, para que nunca se confunda con un
#      enemigo real ni rompa la lectura de la pantalla.
#      GENÉRICO: reutiliza SHADOW con un aro claro en la cabeza.
# ---------------------------------------------------------------------------
def generic(phase: int = 0) -> Canvas:
    c = shadow(phase)
    p = P.SHADOW
    # Un aro claro alrededor de la cabeza: la marca del "desconocido".
    c.ellipse(CX, 7 + (1 if phase else 0), 6, 6, p["k"], fill=False)
    return c
