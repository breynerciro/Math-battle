"""
pixel.py — Micro-librería de pixel art sobre Pillow
====================================================

Dibuja el arte a BAJA resolución y escala con NEAREST, de modo que cada
"píxel de dibujo" se convierte en un cuadrado nítido de N píxeles en
pantalla. Nunca hay antialiasing ni bordes suaves: eso es lo que separa
un sprite de una foto borrosa.

Reglas de la skill `pixel-art-sprites` que esta librería aplica por ti:

- **HUE SHIFT** (`Ramp`): la sombra vira a frío (azul/morado) y la luz a
  cálido (amarillo/naranja). Nunca "el mismo color, más oscuro".
- **Silueta primero** (`Canvas.outline`): un contorno de 1 px alrededor
  de la silueta hace que el personaje se lea sobre CUALQUIER fondo.
- **Bordes duros**: los píxeles se escriben enteros o no se escriben.
- **Gradientes y glow** (`vgradient`, `radial_glow`, `bloom`) para la
  energía mágica y los fondos.
- **Escala entera**: `to_image(scale)` solo admite enteros, así los
  píxeles del arte miden lo mismo en todos los sprites del juego.
"""

from __future__ import annotations

import colorsys
import math
from pathlib import Path

from PIL import Image

TRANSPARENT = (0, 0, 0, 0)

# Caracteres disponibles para el previsualizador, del más legible al menos.
_ASCII_RAMP = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" \
              "#$%&*+=<>?@~^!"


# ---------------------------------------------------------------------------
#  Color
# ---------------------------------------------------------------------------
def rgba(color, alpha: int = 255):
    """Normaliza un color a una tupla RGBA."""
    if len(color) == 4:
        return color
    return (color[0], color[1], color[2], alpha)


def mix(c1, c2, t: float):
    """Interpola linealmente dos colores RGB. t=0 → c1, t=1 → c2."""
    t = max(0.0, min(1.0, t))
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(3))


def lerp_hue(h1: float, h2: float, t: float) -> float:
    """Interpola dos tonos por el camino más corto de la rueda cromática."""
    delta = ((h2 - h1 + 180) % 360) - 180
    return (h1 + delta * t) % 360


def luminance(color) -> float:
    r, g, b = color[:3]
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def lighten(color, amount: float = 0.18):
    """Aclara el color mixes hacia blanco (luz especular)."""
    return mix(color, (255, 255, 255), amount)


def darken(color, amount: float = 0.18):
    """Oscurece el color mezclándolo hacia un negro azulado (sombra fría)."""
    return mix(color, (18, 16, 34), amount)


class Ramp:
    """Rampa de color con *hue shift*.

    Los pasos oscuros rotan el tono hacia `shadow_hue` (frío) y los claros
    hacia `light_hue` (cálido). Así un verde de 4 tonos tiene una sombra
    azul-verdosa y una luz amarillenta: el volumen aparece sin gradients.

    Uso:
        r = Ramp((70, 200, 110), steps=5)
        r[0]  # sombra más oscura
        r[2]  # tono medio
        r[4]  # luz más clara
    """

    def __init__(self, base, steps: int = 5, *, shadow_hue: float = 232.0,
                 light_hue: float = 48.0, shift: float = 0.42,
                 sat_boost: float = 0.10, lo: float = 0.17, hi: float = 0.74):
        self.colors: list[tuple[int, int, int, int]] = []
        # colorsys trabaja con tono en vueltas [0,1); aquí se usa en grados.
        h, lum, sat = colorsys.rgb_to_hls(*[v / 255.0 for v in base[:3]])
        h *= 360.0
        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0.0
            # Curva de luminosidad: un pelín más de luz en las altas.
            l = lo + (hi - lo) * (t ** 0.85)
            # La saturación crece en los medios tonos y cae en los
            # extremos: los blancos se ensucian si se saturan de más.
            s = sat * (1.0 + sat_boost * (1.0 - abs(t - 0.5) * 2.0))
            s *= 1.0 - 0.30 * max(0.0, t - 0.5) * 2.0
            s = max(0.0, min(1.0, s))
            if t < 0.5:
                hue = lerp_hue(h, shadow_hue, (0.5 - t) * 2.0 * shift)
            else:
                hue = lerp_hue(h, light_hue, (t - 0.5) * 2.0 * shift)
            r, g, b = colorsys.hls_to_rgb(hue / 360.0, l, s)
            self.colors.append((int(r * 255), int(g * 255), int(b * 255), 255))

    def __len__(self) -> int:
        return len(self.colors)

    def __getitem__(self, index: int):
        if index < 0:
            index += len(self.colors)
        return self.colors[max(0, min(len(self.colors) - 1, index))]

    @property
    def darkest(self):
        return self[0]

    @property
    def mid(self):
        return self[len(self) // 2]

    @property
    def light(self):
        return self[-1]

    def hexes(self) -> list[str]:
        return ["#%02X%02X%02X" % c[:3] for c in self.colors]


# ---------------------------------------------------------------------------
#  Lienzo
# ---------------------------------------------------------------------------
class Canvas:
    """Rejilla de píxeles RGBA con primitivas de dibujo."""

    def __init__(self, width: int, height: int, fill=TRANSPARENT):
        self.w = width
        self.h = height
        row = [rgba(fill)] * width
        self.px = [list(row) for _ in range(height)]

    # -- acceso ------------------------------------------------------------
    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def put(self, x, y, color):
        """Escribe un píxel. `color=None` o alfa 0 = transparente.

        Las coordenadas se truncan: las primitivas elípticas y las líneas
        trabajan en coma flotante y no obligan a castear en cada llamada.
        """
        if color is None:
            return
        x, y = int(x), int(y)
        if not self.inside(x, y):
            return
        if len(color) == 4 and color[3] == 0:
            self.px[y][x] = TRANSPARENT
        else:
            self.px[y][x] = rgba(color)

    def get(self, x, y):
        x, y = int(x), int(y)
        return self.px[y][x] if self.inside(x, y) else TRANSPARENT

    def is_empty_px(self, x: int, y: int) -> bool:
        p = self.get(x, y)
        return p[3] == 0

    def blend(self, x, y, color):
        """Mezcla `color` sobre un píxel respetando ambos alfas.

        Es lo que usan las sombras de contacto y los halos: en vez de
        reemplazar el píxel, lo tiñe. Si el píxel está vacío escribe el
        color con su alfa (no compondría sobre negro y lo oscurecería).
        """
        x, y = int(x), int(y)
        if not self.inside(x, y):
            return
        sa = color[3] / 255.0 if len(color) > 3 else 1.0
        if sa <= 0:
            return
        da = self.px[y][x][3] / 255.0
        sr, sg, sb = color[:3]
        if da == 0:
            self.px[y][x] = rgba(color)
            return
        a = sa + da * (1.0 - sa)
        def f(s, d):
            return int(round((s * sa + d * da * (1.0 - sa)) / a))
        self.px[y][x] = (f(sr, self.px[y][x][0]),
                         f(sg, self.px[y][x][1]),
                         f(sb, self.px[y][x][2]),
                         int(round(a * 255)))

    # -- construcción desde rejilla de letras --------------------------------
    @classmethod
    def from_grid(cls, rows, palette: dict, unknown="."):
        """Crea el lienzo desde una rejilla de letras (igual que el sistema
        antiguo, pero renderizado con PIL y con pos-procesado disponible).

        Cada letra es un color de `palette`; `unknown` es transparencia.
        """
        if isinstance(rows, str):
            rows = rows.splitlines()
        height = len(rows)
        width = max(len(r) for r in rows) if rows else 0
        canvas = cls(width, height)
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == unknown:
                    continue
                if ch in palette:
                    canvas.put(x, y, palette[ch])
        return canvas

    # -- primitivas ---------------------------------------------------------
    def fill_rect(self, x, y, w, h, color):
        for yy in range(int(y), int(y + h)):
            for xx in range(int(x), int(x + w)):
                self.put(xx, yy, color)

    def rect(self, x, y, w, h, color):
        self.hline(x, x + w - 1, y, color)
        self.hline(x, x + w - 1, y + h - 1, color)
        self.vline(x, y, y + h - 1, color)
        self.vline(x + w - 1, y, y + h - 1, color)

    def hline(self, x0, x1, y, color):
        if x1 < x0:
            x0, x1 = x1, x0
        for x in range(int(x0), int(x1) + 1):
            self.put(x, y, color)

    def vline(self, x, y0, y1, color):
        if y1 < y0:
            y0, y1 = y1, y0
        for y in range(int(y0), int(y1) + 1):
            self.put(x, y, color)

    def line(self, x0, y0, x1, y1, color, thickness: int = 1):
        """Línea de Bresenham. `thickness` se aplica con un cuadrado."""
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if thickness <= 1:
                self.put(x0, y0, color)
            else:
                r = thickness // 2
                self.fill_rect(x0 - r, y0 - r, thickness, thickness, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, cx, cy, rx, ry, color, fill: bool = True):
        """Elipse centrada en (cx, cy) con radios fraccionarios."""
        if rx <= 0 or ry <= 0:
            return
        inner = 0.0
        if not fill:
            smallest = min(rx, ry)
            k = max(0.0, 1.0 - 1.6 / smallest)
            inner = k * k
        for y in range(int(math.floor(cy - ry)) - 1, int(math.ceil(cy + ry)) + 2):
            for x in range(int(math.floor(cx - rx)) - 1, int(math.ceil(cx + rx)) + 2):
                dx = (x + 0.5 - cx) / rx
                dy = (y + 0.5 - cy) / ry
                d = dx * dx + dy * dy
                if d <= 1.0 and (fill or d > inner):
                    self.put(x, y, color)

    def circle(self, cx, cy, r, color, fill: bool = True):
        self.ellipse(cx, cy, r, r, color, fill)

    def poly(self, points, color):
        """Rellena un polígono por líneas de barrido (regla par-impar)."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        y0 = max(0, int(math.floor(min(ys))))
        y1 = min(self.h - 1, int(math.ceil(max(ys))))
        n = len(points)
        for y in range(y0, y1 + 1):
            yc = y + 0.5
            xs = []
            for i in range(n):
                ax, ay = points[i]
                bx, by = points[(i + 1) % n]
                if (ay <= yc < by) or (by <= yc < ay):
                    xs.append(ax + (bx - ax) * (yc - ay) / (by - ay))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(round(xs[i])), int(round(xs[i + 1])), y, color)

    def tri(self, p0, p1, p2, color):
        self.poly([p0, p1, p2], color)

    def blit(self, other: "Canvas", x: int, y: int, skip_transparent: bool = True):
        """Pega otro lienzo. Por defecto no pisa píxeles transparentes."""
        for yy in range(other.h):
            for xx in range(other.w):
                c = other.px[yy][xx]
                if skip_transparent and c[3] == 0:
                    continue
                self.put(x + xx, y + yy, c)

    # -- transformaciones ----------------------------------------------------
    def copy(self) -> "Canvas":
        c = Canvas(self.w, self.h)
        c.px = [list(r) for r in self.px]
        return c

    def shift(self, dx: int, dy: int) -> "Canvas":
        out = Canvas(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x][3] != 0:
                    out.put(x + dx, y + dy, self.px[y][x])
        return out

    def flipped_x(self) -> "Canvas":
        out = Canvas(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                out.px[y][self.w - 1 - x] = self.px[y][x]
        return out

    def scaled(self, factor: int) -> "Canvas":
        """Reescala con vecino más cercano (sin interpolar)."""
        out = Canvas(self.w * factor, self.h * factor)
        for y in range(self.h):
            for x in range(self.w):
                c = self.px[y][x]
                if c[3] == 0:
                    continue
                out.fill_rect(x * factor, y * factor, factor, factor, c)
        return out

    def squashed(self, sx: float, sy: float) -> "Canvas":
        """Escala no uniforme con vecino más cercano — squash & stretch."""
        w = max(1, int(round(self.w * sx)))
        h = max(1, int(round(self.h * sy)))
        out = Canvas(w, h)
        for y in range(h):
            sy_src = min(self.h - 1, int(y / sy))
            for x in range(w):
                sx_src = min(self.w - 1, int(x / sx))
                out.px[y][x] = self.px[sy_src][sx_src]
        return out

    def trim(self) -> "Canvas":
        """Recorta al contenido (deja 1 px de margen)."""
        x0, y0, x1, y1 = self.bbox()
        if x0 is None:
            return self.copy()
        pad = 1
        x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
        x1 = min(self.w - 1, x1 + pad); y1 = min(self.h - 1, y1 + pad)
        out = Canvas(x1 - x0 + 1, y1 - y0 + 1)
        for y in range(out.h):
            for x in range(out.w):
                out.px[y][x] = self.px[y0 + y][x0 + x]
        return out

    # -- efectos -------------------------------------------------------------
    def outline(self, color, diagonal: bool = False, replace_inner: bool = False):
        """Contorno de 1 px alrededor de la silueta.

        Es el truco más barato para que un sprite se lea contra fondos
        oscuros: separa la figura del entorno sin robarle atención.
        """
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if diagonal:
            offsets += [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        targets = []
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x][3] != 0:
                    continue
                for dx, dy in offsets:
                    nx, ny = x + dx, y + dy
                    if not self.inside(nx, ny):
                        continue
                    if self.px[ny][nx][3] != 0:
                        targets.append((x, y))
                        break
        for x, y in targets:
            self.px[y][x] = rgba(color)

    def vgradient(self, top, bottom, y0=None, y1=None, only_content=False,
                  steps: int = 0):
        """Gradiente vertical. `only_content` no toca los píxeles vacíos.

        `steps` > 0 cuantiza el degradado a ese número de bandas con
        dithering ordenado. Es OBLIGATORIO en fondos: interpolar de forma
        suave entre dos colores genera cientos de tonos distintos y el
        resultado deja de ser pixel art (y dispara el peso del PNG).
        """
        y0 = 0 if y0 is None else y0
        y1 = self.h - 1 if y1 is None else y1
        span = max(1, y1 - y0)
        for y in range(y0, min(self.h, y1 + 1)):
            base = max(0.0, min(1.0, (y - y0) / span))
            for x in range(self.w):
                if self.px[y][x][3] == 0:
                    continue
                t = base
                if steps and steps > 1:
                    exact = base * (steps - 1)
                    low = int(exact)
                    frac = exact - low
                    thresh = (self._BAYER4[y % 4][x % 4] + 0.5) / 16.0
                    band = low + (1 if frac > thresh else 0)
                    t = min(steps - 1, band) / (steps - 1)
                self.px[y][x] = rgba(mix(top, bottom, t))

    def shade_columns(self, light_x, amount: float = 0.22):
        """Luz direccional: aclara el lado cercano a `light_x`, oscurece
        el opuesto. Da volumen a superficies planas (cuerpos, muros)."""
        span = max(1.0, self.w - 1.0)
        for y in range(self.h):
            for x in range(self.w):
                c = self.px[y][x]
                if c[3] == 0:
                    continue
                t = abs((x / span) - (light_x / span))
                factor = (t - 0.5) * 2.0 * amount
                if factor >= 0:
                    self.px[y][x] = rgba(darken(c[:3], factor))
                else:
                    self.px[y][x] = rgba(lighten(c[:3], -factor))

    # Matriz de Bayer 4x4: reparte los tonos medios en un patrón ordenado
    # (nunca ruido) — así un degradado se ve como pixel art, no como un
    # halo suave de alta gama.
    _BAYER4 = (
        (0, 8, 2, 10),
        (12, 4, 14, 6),
        (3, 11, 1, 9),
        (15, 7, 13, 5),
    )

    def radial_glow(self, cx, cy, radius, color, strength: float = 0.9,
                    levels: int = 4, falloff: str = "smooth",
                    blank_only: bool = False):
        """Halo radial **cuantizado**.

        En pixel art un degradado suave es un error: genera cientos de
        colores y el sprite deja de belongcer a la paleta. Aquí la
        intensidad se corta en `levels` escalones y los intermedios se
        reparten con dithering ordenado: el halo sigue siendo pixel art
        (bloques), no un degradado suave.

        - Sobre píxeles vacíos escribe el color con alfa discreto.
        - Sobre píxeles opacos suma la luz conservando su alfa.

        `blank_only=True` lo dibuja SÓLO sobre píxeles vacíos, sin tocar
        lo ya pintado. Es lo que hay que usar para el resplandor de un
        arma o una explosión: al mezclarse con el cuerpo genera colores
        nuevos, ensucia la paleta y el sprite deja de leerse.
        """
        cr, cg, cb = color[:3]
        for y in range(int(cy - radius) - 1, int(cy + radius) + 2):
            for x in range(int(cx - radius) - 1, int(cx + radius) + 2):
                if not self.inside(x, y):
                    continue
                if blank_only and self.px[y][x][3] != 0:
                    continue
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / max(0.001, radius)
                if d > 1.0:
                    continue
                if falloff == "smooth":
                    a = (1.0 - d) ** 2
                elif falloff == "sharp":
                    a = (1.0 - d) ** 4
                else:
                    a = 1.0 - d
                a *= strength
                if a <= 0.02:
                    continue
                # Cuantización + dithering ordenado.
                steps = max(1, levels)
                exact = a * steps
                low = int(exact)
                frac = exact - low
                thresh = (self._BAYER4[y % 4][x % 4] + 0.5) / 16.0
                q = low + (1 if frac > thresh else 0)
                q = max(1, min(steps, q))
                a = q / steps
                base = self.px[y][x]
                if base[3] == 0:
                    self.px[y][x] = (cr, cg, cb, int(a * 255))
                else:
                    self.px[y][x] = (
                        min(255, base[0] + int(cr * a)),
                        min(255, base[1] + int(cg * a)),
                        min(255, base[2] + int(cb * a)),
                        base[3],
                    )

    def additive_blob(self, cx, cy, radius, color, strength: float = 0.7):
        """Mancha de luz que respeta el alfa existente (para brillos)."""
        cr, cg, cb = color[:3]
        for y in range(int(cy - radius) - 1, int(cy + radius) + 2):
            for x in range(int(cx - radius) - 1, int(cx + radius) + 2):
                if not self.inside(x, y):
                    continue
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy) / max(0.001, radius)
                if d > 1.0:
                    continue
                k = (1.0 - d) ** 1.6 * strength
                if k <= 0.01:
                    continue
                base = self.px[y][x]
                self.px[y][x] = (
                    min(255, int(base[0] + cr * k)),
                    min(255, int(base[1] + cg * k)),
                    min(255, int(base[2] + cb * k)),
                    base[3],
                )

    def replace(self, old, new):
        old = rgba(old)
        new = rgba(new)
        for y in range(self.h):
            row = self.px[y]
            for x in range(self.w):
                if row[x][:3] == old[:3] and (old[3] == 0) == (row[x][3] == 0):
                    row[x] = new

    def speckle(self, x0, y0, x1, y1, color, density: float = 0.12, seed: int = 1):
        """Salpica píxeles sueltos: textura de piedra, musgo, óxido."""
        state = seed & 0xFFFFFFFF
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                state = (1103515245 * state + 12345) & 0x7FFFFFFF
                if (state % 1000) / 1000.0 < density:
                    if self.inside(x, y) and self.px[y][x][3] != 0:
                        self.px[y][x] = rgba(color)

    def bbox(self):
        """Caja contenida del contenido: (x0, y0, x1, y1) o (None, ...)."""
        x0 = y0 = None
        x1 = y1 = -1
        for y in range(self.h):
            for x in range(self.w):
                if self.px[y][x][3] != 0:
                    if x0 is None or x < x0:
                        x0 = x
                    if x > x1:
                        x1 = x
                    if y0 is None or y < y0:
                        y0 = y
                    if y > y1:
                        y1 = y
        return (x0, y0, x1, y1)

    def opaque_count(self) -> int:
        return sum(1 for y in range(self.h) for x in range(self.w)
                   if self.px[y][x][3] != 0)

    def color_histogram(self) -> dict:
        hist: dict = {}
        for y in range(self.h):
            for x in range(self.w):
                c = self.px[y][x]
                if c[3] == 0:
                    continue
                hist[c[:3]] = hist.get(c[:3], 0) + 1
        return hist

    # -- exportación ---------------------------------------------------------
    def to_image(self, scale: int = 1, mode: str = "RGBA") -> Image.Image:
        """Convierte a imagen PIL. `scale` debe ser un entero ≥ 1.

        `mode="RGB"` aplasta el canal alfa contra el fondo indicado por
        `flatten`. Se usa para los fondos, que ocupan toda la pantalla y
        no necesitan transparencia: un PNG RGB pesa menos y evita que el
        motor tenga que componer una capa opaca que no aporta nada.
        """
        scale = max(1, int(round(scale)))
        img = Image.new("RGBA", (self.w, self.h))
        img.putdata([c for row in self.px for c in row])
        if scale > 1:
            img = img.resize((self.w * scale, self.h * scale), Image.NEAREST)
        if mode != "RGBA":
            img = img.convert(mode, Image.Dither.NONE)
        return img

    def save(self, path, scale: int = 1, mode: str = "RGBA") -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.to_image(scale, mode=mode).save(path, "PNG", optimize=True)
        return path

    def flashed(self, color=(255, 120, 120), amount: float = 0.72,
                levels: int = 3) -> "Canvas":
        """Copia del lienzo con un lavado de color: el frame de "hurt".

        Mezcla `color` sobre los píxeles ya pintados manteniendo su alfa
        (y sin tocar los vacíos), que es el aspecto de un impacto. La
        mezcla se **cuantiza en `levels` escalones**: un lavado suave
        generaría un color por píxel y reventaría la paleta.
        """
        out = self.copy()
        steps = max(1, levels)
        exact = amount * steps
        base_a = int(exact)
        for y in range(self.h):
            for x in range(self.w):
                r, g, b, a = self.px[y][x]
                if a == 0:
                    continue
                t = (base_a + (1 if (exact - base_a) > 0.5 else 0)) / steps
                out.px[y][x] = (
                    int(r + (color[0] - r) * t),
                    int(g + (color[1] - g) * t),
                    int(b + (color[2] - b) * t),
                    a,
                )
        return out

    def squash_to(self, k: float = 0.82, widen: float = 1.0) -> "Canvas":
        """Aplasta la silueta en Y (y opcionalmente la ensancha en X).

        `k` = factor de altura, `widen` = factor de anchura. A diferencia
        de `squashed()`, NO cambia el tamaño del lienzo y ancla el origen
        en el pie: la criatura se aplasta contra el suelo en vez de
        hundirse por el centro, y los frames conservan las mismas
        dimensiones que espera el carga-sprites.
        """
        out = Canvas(self.w, self.h)
        bottom = self.h - 1
        while bottom >= 0 and all(c[3] == 0 for c in self.px[bottom]):
            bottom -= 1
        if bottom <= 0:
            return out
        span = bottom
        for y in range(bottom + 1):
            src = self.px[y]
            if all(c[3] == 0 for c in src):
                continue
            dst_y = int(span - (span - y) * k)
            if not (0 <= dst_y < self.h):
                continue
            if widen == 1.0:
                out.px[dst_y] = list(src)
                continue
            # Re-muestreo horizontal: cada píxel de origen ocupa `widen` px.
            for x, c in enumerate(src):
                if c[3] == 0:
                    continue
                x0 = int(x * widen)
                x1 = max(x0 + 1, int((x + 1) * widen))
                for dx in range(x0, min(x1, self.w)):
                    out.px[dst_y][dx] = c
        return out


# ---------------------------------------------------------------------------
#  Previsualización en terminal (para iterar sin abrir un visor)
# ---------------------------------------------------------------------------
def ascii_art(canvas_or_path, chars: str = _ASCII_RAMP) -> str:
    """Vuelca un lienzo como texto: un carácter por píxel.

    Los caracteres se ordenan de más claro a más oscuro para que la
    estructura de valores se lea de un vistazo, y cada carácter se
    documenta en la leyenda con su color exacto.

    Si el lienzo tiene más colores que caracteres disponibles, los
    sobrantes se agrupan en `?` y la leyenda avisa: eso suele significar
    que hay un degradado suave donde debería haber dithering.
    """
    if isinstance(canvas_or_path, (str, Path)):
        img = Image.open(canvas_or_path).convert("RGBA")
        c = Canvas(img.width, img.height)
        c.px = [[img.getpixel((x, y)) for x in range(img.width)]
                for y in range(img.height)]
    else:
        c = canvas_or_path

    palette: list[tuple] = []
    for color in sorted(c.color_histogram(), key=lambda col: -luminance(col)):
        if color not in palette:
            palette.append(color)

    overflow = max(0, len(palette) - len(chars))
    legend: dict = {}
    for i, color in enumerate(palette):
        legend[color] = chars[i] if i < len(chars) else "?"

    lines = []
    for y in range(c.h):
        row = []
        for x in range(c.w):
            px = c.px[y][x]
            row.append(" " if px[3] == 0 else legend.get(px[:3], "?"))
        lines.append("".join(row))
    body = "\n".join(lines)
    key = "  ".join(f"{legend[col]}=#{col[0]:02X}{col[1]:02X}{col[2]:02X}"
                    for col in palette[:len(chars)])
    header = f"{c.w}x{c.h}, {len(palette)} colores"
    if overflow:
        header += f"  [!] {overflow} colores fuera de la paleta ('?')"
    return f"{body}\n  [{header}]\n  [{key}]"
