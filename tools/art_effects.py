"""Efectos transitorios que acompañan al combate.

De momento solo la estrella de impacto: 3 frames a 18 FPS que el juego
muestra cuando una respuesta es correcta. El impacto es la única vez que
el juego premia al jugador, así que tiene que NOTARSE por encima de todo
lo demás — de ahí que sea blanca y de 3 frames muy separados (crece rápido,
desaparece rápido) en vez de un brillo continuo.
"""

from __future__ import annotations

from . import palettes as P
from .pixel import Canvas

SIZE = 32
CX, CY = 16, 16
FRAMES = 3


def star(frame: int) -> Canvas:
    """Estrella de impacto, frame 0..2.

    Los tres frames son EL MISMO dibujo a distinto tamaño y con distinto
    número de puntas visibles. Redibujar la estrella con un factor de
    escala libre produce bordes sucios; aquí la punta más larga y las
    cortas, se dibujan píxeles sueltos en vez de escalarse.

    - frame 0: la chispa compacta, 1 frame de anticipación.
    - frame 1: la estrella abierta, el pico de la animación.
    - frame 2: solo el halo residual, sin puntas: se está apagando.
    """
    c = Canvas(SIZE, SIZE)
    w = P.WHITE
    hot = (255, 255, 255, 255)
    gold = P.GOLD
    if frame == 0:
        # Chispa: un rombo pequeño con un halo mínimo.
        c.radial_glow(CX, CY, 7, gold, 0.45, levels=3, blank_only=True)
        c.put(CX, CY - 2, hot)
        c.hline(CX - 1, CX + 1, CY - 1, hot)
        c.hline(CX - 2, CX + 2, CY, w)
        c.hline(CX - 1, CX + 1, CY + 1, hot)
        c.put(CX, CY + 2, hot)
    elif frame == 1:
        # Estrella abierta: 4 puntas largas en cruz y 4 cortas en diagonal.
        c.radial_glow(CX, CY, 12, gold, 0.5, levels=3, blank_only=True)
        c.radial_glow(CX, CY, 7, hot, 0.55, levels=2, blank_only=True)
        for dx, dy in ((0, -9), (0, 9), (-9, 0), (9, 0)):
            for i in range(1, 8):
                c.put(CX + dx * i // 9, CY + dy * i // 9, w)
        for dx, dy in ((-5, -5), (5, -5), (-5, 5), (5, 5)):
            for i in range(1, 4):
                c.put(CX + dx * i // 5, CY + dy * i // 5, gold)
        # Núcleo: blanco puro, es lo que da el "pico" de brillo.
        c.fill_rect(CX - 2, CY - 2, 5, 5, w)
        c.fill_rect(CX - 1, CY - 1, 3, 3, hot)
    else:
        # Frame de apagado: un anillo que se expande, sin núcleo. Las
        # puntas han desaparecido y solo queda la onda; un disco lleno de
        # oro se leería como un segundo impacto, no como una disipación.
        for dx, dy in ((-11, 0), (11, 0), (0, -11), (0, 11),
                       (-8, -8), (8, -8), (-8, 8), (8, 8)):
            c.put(CX + dx, CY + dy, w)
        c.radial_glow(CX, CY, 9, gold, 0.26, levels=3, blank_only=True)
    return c


def build() -> dict:
    """Los 3 frames del efecto, listos para guardar."""
    return {"star": [star(i) for i in range(FRAMES)]}
