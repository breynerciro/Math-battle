"""
art_hero.py — El Héroe: "Matías el Matemático"
==============================================

Dibuja a 32×32 (se escala ×4 a 128×128 en pantalla) un estudiante-aventurero
que lucha con las matemáticas:

  - **Armadura azul** con un emblema dorado `π` en el pecho.
  - **Capa carmesí** ondeando a la izquierda (mira a la derecha).
  - **Bastón de cristal** en la mano derecha: es su "arma".
  - **Libro de hechizos** en la mano izquierda, con una hoja que asoma.

Filosofía (skill `pixel-art-sprites`):

- **Silueta primero.** La silueta completa es "persona + bastón alto + capa
  que ondea". Se lee de un vistazo, incluso en negro sólido.
- **Pocos frames, decisivos.** `attack` tiene las 4 fases clásicas:
  anticipación → golpe → impacto → recuperación. Un frame por fase.
- **Anticipación antes, seguimiento después** (skill `game-juice`): el
  bastón se recoge, se lanza, y el cuerpo se queda 1 frame en la posición
  de contacto para que el golpe se sienta con peso.
- **Un solo tamaño de píxel** en todo el juego (×4), nunca escalado.
"""

from __future__ import annotations

from . import palettes as P
from .pixel import Canvas

W = 32
H = 32
SCALE = 4

# Geometría fija del personaje (coordenadas del lienzo de 32×32).
# Los pies quedan en la última fila para anclarlos al suelo en batalla.
CX = 15          # eje vertical del cuerpo
HEAD_CY = 8.0    # centro de la cabeza
FOOT_Y = 31      # suela de las botas


# ---------------------------------------------------------------------------
#  Piezas
# ---------------------------------------------------------------------------
def _cape(c: Canvas, sway: int, lift: int = 0) -> None:
    """Capa carmesí que ondea a la izquierda. `sway` = amplitud del vuelo.

    Es la mitad de la silueta del personaje, así que va GENEROSA: arranca
    en los hombros y cae más allá de las rodillas, con el borde inferior
    recortado en dos puntas para que se lea el movimiento.
    """
    top = 12 - lift
    bot = top + 16
    far = CX - 10 - sway                     # punta más lejana de la capa
    # Silueta: hombro → borde exterior → dos puntas → vuelta al cuerpo
    c.poly([
        (CX - 2, top),
        (CX - 6, top + 1),
        (far + 2, top + 6),
        (far, top + 11),
        (far - 1, bot - 3),                  # punta trasera
        (far + 3, bot - 1),                  # valley entre las dos puntas
        (far + 2, bot),                      # punta delantera
        (far + 5, top + 10),
        (CX - 2, top + 6),
    ], P.HERO["R"])
    # Luz cenital en el borde superior y el vuelo.
    c.poly([
        (CX - 2, top), (CX - 6, top + 1), (far + 2, top + 6),
        (far + 2, top + 7), (CX - 5, top + 3), (CX - 2, top + 2),
    ], P.HERO["r"])
    c.line(far + 4, top + 8, far + 3, top + 10, P.HERO["m"])
    # Sombra profunda del pliegue interior: le da grosor al tela.
    c.line(CX - 3, top + 4, far + 5, top + 12, P.HERO["R"], thickness=2)
    c.line(far + 5, top + 12, far + 3, bot - 2, P.HERO["R"], thickness=2)


def _legs(c: Canvas, stance: int = 0, crouch: int = 0) -> None:
    """Piernas. `stance` +1 = piernas separadas (ataque)."""
    top = 20 + crouch
    knee = top + 4
    foot = FOOT_Y - crouch
    lx, rx_ = CX - 3 - stance, CX + 2 + stance
    for x, boot in ((lx, lx - 1), (rx_, rx_ + 1)):
        c.fill_rect(x, top, 3, knee - top, P.HERO["B"])
        c.fill_rect(x, knee, 3, foot - knee, P.HERO["B"])
        # Espinilla con luz: separa las piernas de la sombra del suelo.
        c.vline(x + 2, top + 1, foot - 2, P.HERO["c"])
        # Bota de cuero: 4 px de ancho para no tocar el bastón.
        c.fill_rect(boot, foot - 3, 4, 3, P.HERO["N"])
        c.hline(boot, boot + 3, foot - 3, P.HERO["i"])
        c.hline(boot, boot + 3, foot, P.HERO["N"])
        c.put(boot + 1, foot - 2, P.HERO["y"])   # hebilla dorada
    c.fill_rect(lx, foot - 1, 3, 1, P.HERO["B"])


def _torso(c: Canvas, dy: int = 0, lean: int = 0) -> None:
    """Torso con peto, cinturón y emblema `π`."""
    top = 12 + dy
    bot = 20 + dy
    x0, x1 = CX - 4 + lean, CX + 4 + lean
    c.fill_rect(x0, top, x1 - x0, bot - top, P.HERO["c"])
    # Placas: brillo arriba, sombra en la cintura.
    c.hline(x0, x1, top, P.HERO["+"])
    c.fill_rect(x0, top + 1, 1, bot - top - 1, P.HERO["B"])
    c.fill_rect(x1 - 1, top + 2, 1, bot - top - 2, P.HERO["B"])
    c.hline(x0 + 1, x1 - 2, bot - 1, P.HERO["B"])
    # Cuello
    c.fill_rect(x0 + 1, top - 1, 5, 2, P.HERO["s"])
    # Emblema: la letra π en oro sobre un disco oscuro.
    c.fill_rect(CX - 2 + lean, top + 3, 5, 4, P.HERO["g"])
    c.hline(CX - 2 + lean, CX + 2 + lean, top + 3, P.HERO["y"])
    c.vline(CX - 1 + lean, top + 3, top + 6, P.HERO["y"])
    c.vline(CX + 1 + lean, top + 3, top + 6, P.HERO["y"])
    # Cinturón
    c.fill_rect(x0 - 1, bot, x1 - x0 + 2, 2, P.HERO["g"])
    c.hline(x0 - 1, x1, bot, P.HERO["y"])
    c.fill_rect(CX - 1 + lean, bot, 3, 2, P.HERO["y"])


def _head(c: Canvas, dy: int = 0, blink: bool = False,
          squint: bool = False) -> None:
    """Cabeza con pelo, ojos y expresión. Mira a la derecha (3/4)."""
    cy = HEAD_CY + dy
    c.ellipse(CX, cy, 4.4, 4.5, P.HERO["s"])
    c.ellipse(CX + 1, cy + 1, 3.5, 3.7, P.HERO["a"])   # lado iluminado
    # Mandíbula
    c.fill_rect(CX - 2, cy + 2, 5, 2, P.HERO["a"])
    # Pelo: casquete + mechones laterales.
    # El pelo se queda en tonos bajos (h/j/f) para no fundirse con la piel.
    c.ellipse(CX, cy - 2.6, 4.6, 2.6, P.HERO["h"])
    c.ellipse(CX, cy - 2.8, 4.0, 2.0, P.HERO["j"])
    c.put(CX - 1, cy - 3.4, P.HERO["f"])                 # brillo del pelo
    c.put(CX, cy - 3.4, P.HERO["f"])
    c.put(CX + 1, cy - 3.4, P.HERO["f"])
    c.fill_rect(CX - 4, cy - 0.5, 1, 3, P.HERO["h"])
    c.fill_rect(CX - 5, cy + 0.5, 1, 2, P.HERO["h"])
    c.fill_rect(CX + 4, cy - 0.5, 1, 2, P.HERO["h"])
    # Ojos
    ey = int(cy) + 1
    for ex in (CX - 2, CX + 2):
        if blink:
            c.hline(ex - 1, ex, ey, P.HERO["e"])
            c.hline(ex - 1, ex, ey + 1, P.HERO["w"])
        elif squint:
            c.put(ex, ey, P.HERO["w"])
            c.put(ex + 1, ey, P.HERO["e"])
            c.put(ex, ey + 1, P.HERO["e"])
        else:
            c.put(ex, ey, P.HERO["w"])
            c.put(ex + 1, ey, P.HERO["e"])
            c.put(ex, ey + 1, P.HERO["w"])
            c.put(ex + 1, ey + 1, P.HERO["e"])
    # Boca
    c.hline(CX, CX + 1, ey + 2, P.HERO["q"])


def _staff(c: Canvas, x0, y0, x1, y1, tip_glow: float = 0.0) -> None:
    """Bastón con cristal. El cristal va SIEMPRE en el extremo (x1,y1).

    El halo se pinta ANTES que el cristal: si fuera al revés, el glow
    aclararía el diamante y se vería un manchurrón en vez de una gema.
    """
    c.line(x0, y0, x1, y1, P.HERO["g"], thickness=2)
    c.line(x0, y0, x1, y1, P.HERO["y"])          # filamento de luz
    for t in (0.32, 0.62):                        # envolturas doradas
        mx, my = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        c.put(int(round(mx)), int(round(my)), P.HERO["o"])
    cx, cy = int(round(x1)), int(round(y1))
    if tip_glow > 0:
        c.radial_glow(cx, cy, 4.5, (128, 214, 240), tip_glow, blank_only=True)
    # Cristal: rombo de 5 px con contorno, glow y chispas.
    c.put(cx, cy - 2, P.HERO["v"])
    c.hline(cx - 1, cx + 1, cy - 1, P.HERO["v"])
    c.hline(cx - 2, cx + 2, cy, P.HERO["+"])
    c.hline(cx - 1, cx + 1, cy + 1, P.HERO["v"])
    c.put(cx, cy + 2, P.HERO["v"])
    c.put(cx, cy - 1, (255, 255, 255, 255))      # brillo especular
    c.put(cx - 2, cy, P.HERO["v"])
    c.put(cx + 2, cy, P.HERO["v"])


def _arm(c: Canvas, sx, sy, hx, hy, sleeve: bool = True) -> None:
    """Brazos: hombro → codo → mano."""
    mx, my = (sx + hx) // 2 + (1 if hx > sx else -1), (sy + hy) // 2
    c.line(sx, sy, mx, my, P.HERO["c"], thickness=2)
    c.line(mx, my, hx, hy, P.HERO["c"], thickness=2)
    if sleeve:
        c.put(int(sx), int(sy), P.HERO["+"])
    c.circle(hx, hy, 1.4, P.HERO["a"])            # mano
    c.put(int(hx) - 1, int(hy) + 1, P.HERO["s"])


def _book(c: Canvas, x, y) -> None:
    """Libro de hechizos: tapa dorada, lomo oscuro y una hoja asomando."""
    c.fill_rect(x, y, 6, 5, P.HERO["g"])
    c.hline(x, x + 5, y, P.HERO["o"])
    c.vline(x, y, y + 4, P.HERO["g"])
    c.vline(x + 5, y, y + 4, P.HERO["g"])
    c.fill_rect(x + 1, y + 1, 4, 3, P.HERO["y"])
    c.hline(x + 2, x + 4, y + 2, P.HERO["o"])     # línea de texto
    c.put(x + 6, y - 1, (250, 250, 252, 255))     # hoja al viento
    c.put(x + 6, y, (250, 250, 252, 255))


# ---------------------------------------------------------------------------
#  Frames
# ---------------------------------------------------------------------------
def _idle(dy: int, sway: int, blink: bool, glow: float) -> Canvas:
    """Compone UN frame de descanso con los parámetros dados: cabeceo
    (`dy`), balanceo de capa (`sway`), parpadeo y brillo del bastón."""
    c = Canvas(W, H)
    _cape(c, sway)
    _legs(c, stance=0, crouch=dy)
    _arm(c, CX - 4, 15, CX - 6, 20)               # brazo izq. con el libro
    _book(c, CX - 8, 19)
    _torso(c, dy=dy)
    _staff(c, CX + 9, FOOT_Y, CX + 9, 5, tip_glow=glow)
    _arm(c, CX + 4, 15, CX + 9, 19)               # mano en el bastón
    _head(c, dy=dy, blink=blink)
    c.outline(P.INK, diagonal=True)
    return c


def _attack(frame: int) -> Canvas:
    """4 fases: anticipación → golpe → impacto → recuperación."""
    c = Canvas(W, H)
    if frame == 0:
        # ANTICIPACIÓN: bastón bajado hacia atrás, cuerpo encogido.
        _cape(c, -2, lift=1)
        _legs(c, stance=-1, crouch=1)
        _arm(c, CX - 4, 15, CX - 7, 19)
        _book(c, CX - 9, 18)
        _torso(c, dy=1, lean=-1)
        _staff(c, CX + 8, FOOT_Y, CX + 7, 20)
        _arm(c, CX + 3, 15, CX + 7, 22)
        _head(c, dy=1, squint=True)
    elif frame == 1:
        # GOLPE: el bastón se lanza horizontal hacia el enemigo.
        _cape(c, 3, lift=-1)
        _legs(c, stance=2, crouch=0)
        _arm(c, CX - 3, 15, CX - 5, 20)
        _book(c, CX - 7, 19)
        _torso(c, lean=1)
        _staff(c, CX + 7, 18, CX + 13, 14)
        _arm(c, CX + 4, 15, CX + 7, 17)
        _head(c, squint=True)
    elif frame == 2:
        # IMPACTO: máxima extensión + destello en la punta del bastón.
        _cape(c, 4, lift=-2)
        _legs(c, stance=3, crouch=0)
        _arm(c, CX - 2, 15, CX - 4, 20)
        _book(c, CX - 6, 19)
        _torso(c, lean=2)
        _staff(c, CX + 8, 17, CX + 14, 13, tip_glow=0.4)
        _arm(c, CX + 5, 15, CX + 8, 16)
        _head(c, squint=True)
    else:
        # RECUPERACIÓN: vuelve a la guardia.
        c = _idle(0, sway=0, blink=False, glow=0.2)
        return c
    c.outline(P.INK, diagonal=True)
    if frame == 2:
        # Chispas del impacto: destellos en cruz alrededor del cristal.
        # El cristal está en CX+14, tan a la derecha que la cruz se salía
        # del lienzo y se perdían dos chispas. Se acotan al lienzo en vez
        # de acortar la cruz a mano: así un retoque futuro en la posición
        # del bastón no vuelve a perder píxeles en silencio.
        tx, ty = CX + 14, 13
        for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, 3)):
            sx = min(max(tx + dx, 0), c.w - 1)
            sy = min(max(ty + dy, 0), c.h - 1)
            c.put(sx, sy, (222, 246, 255, 255))
        c.radial_glow(tx, ty, 5, (150, 226, 255), 0.5, levels=3, blank_only=True)
    return c


def _hurt(dy: int, blink: bool) -> Canvas:
    """Retroceso: echa el torso hacia atrás, baja el bastón, aprieta los ojos."""
    c = Canvas(W, H)
    _cape(c, 3, lift=1)
    _legs(c, stance=-1, crouch=dy)
    _arm(c, CX - 4, 15, CX - 8, 18)               # brazo izq. alzada
    _book(c, CX - 10, 17)
    _torso(c, dy=dy, lean=-2)
    _staff(c, CX + 7, FOOT_Y, CX + 6, 24)         # bastón caído
    _arm(c, CX + 3, 15, CX + 6, 25)
    _head(c, dy=dy, blink=blink)
    c.outline(P.INK, diagonal=True)
    return c


def _victory(bump: int) -> Canvas:
    """Victoria: bastón al alto, libro en alto y chispas."""
    c = Canvas(W, H)
    _cape(c, 1, lift=-1)
    _legs(c, stance=1)
    _arm(c, CX - 4, 15, CX - 7, 9)                # libro en alto
    _book(c, CX - 9, 7)
    _torso(c)
    _staff(c, CX + 9, FOOT_Y, CX + 9, 2, tip_glow=0.6)
    _arm(c, CX + 4, 14, CX + 9, 8)                # brazo alzado al bastón
    _head(c, dy=-1)
    c.outline(P.INK, diagonal=True)
    # Estrellitas de celebración
    c.radial_glow(CX + 9, 2, 6, (150, 226, 255), 0.8, blank_only=True)
    for sx, sy in ((CX + 14, 4), (CX + 3, 3), (CX + 12, -1)):
        if 0 <= sy < H:
            c.put(sx, sy, (255, 246, 178, 255))
            c.put(sx - 1, sy, (255, 206, 92, 255))
    return c


# ---------------------------------------------------------------------------
#  API
# ---------------------------------------------------------------------------
def build() -> dict[str, list[Canvas]]:
    """Devuelve {animación: [frames]} del héroe."""
    return {
        # Respiración: el torso baja 1 px y parpadea a mitad del ciclo.
        "idle": [_idle(0, sway=1, blink=False, glow=0.35),
                 _idle(1, sway=0, blink=True, glow=0.5)],
        "attack": [_attack(0), _attack(1), _attack(2), _attack(3)],
        "hurt": [_hurt(0, blink=False), _hurt(1, blink=True)],
        "victory": [_victory(0), _victory(1)],
    }
