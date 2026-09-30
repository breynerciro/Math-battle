"""
palettes.py — Paletas del juego con *hue shift*
================================================

El error clásico del pixel art es oscurecer un color bajándole el brillo:
el resultado queda plano, como un cojín. Aquí cada material es una `Ramp`
en la que la sombra vira a frío (azul/morado) y la luz a cálido
(amarillo/naranja), así que los cuerpos tienen volumen.

CONVENCIÓN DE LETRAS (para que las rejillas sean legibles)
----------------------------------------------------------
Cada material recibe 3 letras **de sombra a luz**:

    letra 1  = sombra    (fría, vira a azul/morado)
    letra 2  = tono medio (el color base de la superficie)
    letra 3  = luz       (cálida, vira a amarillo)

Eventuales extras: `+` cuarto tono (brillo especular), `*` acento cálido,
`&` acento frío (magia, cristal, energía), `K` contorno.

Reglas de la skill `pixel-art-sprites` respetadas aquí:
- Pocos colores: 6-9 tonos por sprite, nunca 24.
- Un único contorno para todo el juego (azul-negro frío), para que todos
  los personajes compartan familia visual.
"""

from __future__ import annotations

from .pixel import Ramp

# --- colores fijos compartidos ---------------------------------------------
INK = (22, 24, 42, 255)        # contorno frío universal
INK_WARM = (36, 18, 28, 255)   # contorno para lo demoníaco/carmesí
INK_DEEP = (13, 13, 28, 255)   # contorno para lo espectral
BONE = (240, 234, 216, 255)
GOLD = (255, 206, 92, 255)
ARCANE = (198, 124, 255, 255)
ARCANE_HOT = (242, 178, 255, 255)
ARCANE_DEEP = (116, 54, 188, 255)
WHITE = (250, 250, 252, 255)
PITCH_DARK = (26, 28, 46, 255)


def band(chars: str, base, steps: int | None = None, **kwargs) -> dict:
    """Convierte una rampa con hue shift en un dict letra → color.

    `chars` se recorre de sombra a luz: la primera letra es el tono más
    oscuro y la última el más claro. Por defecto hay un tono por letra.

        **band("Bcb", (58, 104, 198))   # B sombra, c medio, b luz
    """
    steps = steps or len(chars)
    if len(set(chars)) != len(chars):
        raise ValueError(f"band({chars!r}): letras repetidas")
    ramp = Ramp(base, steps=steps, **kwargs)
    if len(chars) > steps:
        raise ValueError(f"{chars!r} pide más letras que tonos ({steps})")
    return {ch: ramp[i] for i, ch in enumerate(chars)}


def _palette(name: str, spec: dict) -> dict:
    """Valida que no haya letras repetidas y devuelve el dict."""
    seen: dict = {}
    for ch, color in spec.items():
        if ch in seen:
            raise ValueError(f"{name}: letra {ch!r} repetida "
                             f"({seen[ch]} y {color})")
        seen[ch] = color
    return spec


# ===========================================================================
#  HÉROE MATEMÁTICO — armadura azul, capa carmesí, pelo castaño
# ===========================================================================
HERO = _palette("HERO", {
    "K": INK,
    # piel
    **band("qsa", (204, 154, 116), shadow_hue=252, light_hue=34),
    # Pelo castaño. Se queda en 3 tonos BAJOS (hi=0.52): si el pelo sube a
    # beige claro se confunde con la piel y la cara desaparece.
    **band("hjf", (120, 78, 44), shadow_hue=266, light_hue=42, hi=0.52),
    # armadura azul
    **band("Bcb", (58, 108, 200), shadow_hue=250, light_hue=198),
    # capa carmesí
    **band("Rrm", (206, 58, 76), shadow_hue=268, light_hue=18),
    # oro (libro, adornos, bastón)
    **band("gyo", (234, 196, 104), shadow_hue=44, light_hue=48),
    # cuero oscuro (botas, cinturón, correa del libro). Tonos bajos a
    # propósito: unas botas doradas se fundirían con el bastón.
    **band("Nil", (96, 64, 42), shadow_hue=252, light_hue=40, hi=0.55),
    # cristal del bastón
    "v": (128, 214, 240, 255),
    "w": WHITE,          # brillo de ojos
    "e": PITCH_DARK,     # pupilas
    "+": (150, 200, 250, 255),   # brillo especular de armadura
})

# ===========================================================================
#  ENEMIGOS
# ===========================================================================
SLIME = _palette("SLIME", {
    "K": INK,
    **band("Gtge", (62, 198, 126), shadow_hue=196, light_hue=92),
    "h": (128, 84, 184, 255),   # veta arcana que recorre el cuerpo
    "v": ARCANE,
    "w": WHITE,
    "e": (22, 40, 34, 255),
})

GOBLIN = _palette("GOBLIN", {
    "K": INK,
    **band("Gtop", (120, 188, 76), shadow_hue=180, light_hue=78),
    **band("dc", (78, 122, 52), shadow_hue=214, light_hue=92),   # túnica
    **band("fz", (166, 134, 92), shadow_hue=250, light_hue=40),   # cuero
    "y": (240, 208, 110, 255),   # ojos amarillos
    "w": WHITE,
    "e": (24, 34, 22, 255),
})

SKELETON = _palette("SKELETON", {
    "K": INK_DEEP,
    **band("Bbn", (214, 210, 190), shadow_hue=240, light_hue=48),   # hueso
    **band("smc", (146, 150, 166), shadow_hue=252, light_hue=210),  # acero oxidado
    "r": (94, 88, 80, 255),      # óxido
    "e": (255, 116, 66, 255),    # llama en las cuencas
    "o": (255, 214, 128, 255),
})

WITCH = _palette("WITCH", {
    "K": INK_DEEP,
    **band("PpL", (128, 62, 188), shadow_hue=258, light_hue=296),   # túnica
    **band("Gsk", (110, 188, 122), shadow_hue=186, light_hue=92),  # piel
    **band("Bbn", (232, 228, 214), shadow_hue=250, light_hue=46),  # pelo
    **band("lmz", (78, 78, 98), shadow_hue=254, light_hue=40),     # bastón
    "v": ARCANE,
    "w": WHITE,
    "e": (28, 22, 40, 255),
})

STONE_GOLEM = _palette("STONE_GOLEM", {
    "K": INK_DEEP,
    **band("Rrp", (138, 140, 156), shadow_hue=246, light_hue=48),   # piedra
    **band("Mmi", (88, 148, 68), shadow_hue=196, light_hue=96),     # musgo
    **band("qQn", (152, 128, 92), shadow_hue=252, light_hue=40),    # mineral veteado
    "E": (255, 216, 100, 255),   # ojos de energía
    "e": (188, 116, 44, 255),
})

GHOST = _palette("GHOST", {
    "K": (16, 16, 32, 255),
    **band("wvs", (212, 226, 246), shadow_hue=250, light_hue=202),  # velo
    **band("ghk", (150, 176, 216), shadow_hue=252, light_hue=212),  # velo sombra
    "c": ARCANE,
    "a": WHITE,
    "e": (30, 38, 66, 255),
})

LESSER_DEMON = _palette("LESSER_DEMON", {
    "K": INK_WARM,
    **band("Rrm", (200, 64, 58), shadow_hue=290, light_hue=16),     # piel
    **band("HhZ", (236, 220, 196), shadow_hue=252, light_hue=44),   # cuerno
    **band("Wwq", (96, 40, 68), shadow_hue=290, light_hue=330),     # ala
    "E": (255, 198, 74, 255),    # ojos
    "b": (22, 16, 22, 255),      # boca / grieta
})

PHOENIX = _palette("PHOENIX", {
    "K": (46, 18, 26, 255),
    **band("Otu", (244, 132, 46), shadow_hue=286, light_hue=26),   # cuerpo
    **band("Rrm", (198, 58, 44), shadow_hue=300, light_hue=12),     # rojo profundo
    **band("Ddq", (124, 34, 52), shadow_hue=310, light_hue=340),    # membrana de ala
    "Y": (255, 212, 80, 255),     # fuego
    "F": (255, 246, 180, 255),    # fuego blanco
    **band("Ccz", (250, 216, 158), shadow_hue=250, light_hue=44),   # pecho
    "T": (234, 174, 94, 255),     # pico
    "e": (58, 22, 30, 255),
})

DARK_KNIGHT = _palette("DARK_KNIGHT", {
    "K": (11, 11, 20, 255),
    **band("Uuvs", (64, 64, 90), shadow_hue=258, light_hue=222),    # armadura
    **band("Rrqm", (162, 30, 46), shadow_hue=300, light_hue=8),     # capa
    "S": (156, 164, 192, 255),    # filo de acero
    "E": (255, 72, 60, 255),      # ojos
    "e": (255, 196, 148, 255),
    "G": (72, 196, 196, 255),     # aura fría
})

MAGE = _palette("MAGE", {
    "K": INK_DEEP,
    **band("Mmuv", (74, 78, 170), shadow_hue=254, light_hue=228),    # túnica
    **band("Bbn", (238, 232, 220), shadow_hue=250, light_hue=46),   # barba
    **band("sqk", (208, 164, 126), shadow_hue=252, light_hue=34),   # piel
    **band("lzo", (98, 68, 48), shadow_hue=252, light_hue=38),      # bastón
    "v": (130, 218, 242, 255),    # cristal
    "e": (24, 26, 46, 255),
})

HYDRA = _palette("HYDRA", {
    "K": (16, 30, 26, 255),
    **band("Ggtp", (78, 168, 92), shadow_hue=190, light_hue=88),    # escama
    **band("Wwk", (226, 232, 202), shadow_hue=200, light_hue=70),   # vientre
    "Y": (255, 206, 72, 255),     # ojo encendido
    "w": (126, 148, 126, 255),    # ojo apagado
    "F": (255, 238, 172, 255),    # colmillo
})

SHADOW = _palette("SHADOW", {
    "K": (11, 9, 18, 255),
    **band("Uuvk", (54, 50, 80), shadow_hue=262, light_hue=280),    # niebla
    "w": (240, 242, 255, 255),    # ojos
    "c": (152, 122, 255, 255),    # brasa
    "e": (16, 12, 26, 255),
})

ARCHMAGE = _palette("ARCHMAGE", {
    "K": (13, 9, 22, 255),
    **band("PpLz", (98, 44, 154), shadow_hue=262, light_hue=300),   # túnica
    **band("Bbn", (238, 232, 226), shadow_hue=250, light_hue=48),   # barba
    **band("sqk", (180, 150, 178), shadow_hue=256, light_hue=330),  # piel
    **band("lmz", (76, 58, 46), shadow_hue=252, light_hue=38),      # bastón
    "v": ARCANE,
    "V": ARCANE_HOT,
    "E": (255, 228, 134, 255),    # ojos
    "g": GOLD,                    # adornos
})

BASIC_DRAGON = _palette("BASIC_DRAGON", {
    "K": (15, 23, 25, 255),
    **band("Ggtp", (58, 172, 92), shadow_hue=186, light_hue=96),    # escama
    **band("Wwk", (220, 230, 200), shadow_hue=200, light_hue=72),   # vientre
    "Y": (255, 206, 72, 255),     # ojo
    "H": (228, 216, 188, 255),    # cuerno
    **band("Rrqm", (160, 46, 52), shadow_hue=300, light_hue=12),    # interior de ala
    "E": (255, 150, 48, 255),     # aliento de fuego
})

SUPREME_DRAGON = _palette("SUPREME_DRAGON", {
    "K": (28, 14, 24, 255),
    **band("Rrqm", (190, 48, 46), shadow_hue=300, light_hue=14),    # escama
    **band("Ddqz", (72, 20, 38), shadow_hue=314, light_hue=340),    # membrana
    "Y": GOLD,                    # vientre / placas de oro
    "F": (255, 246, 178, 255),    # pupila en llama
    "H": (234, 224, 208, 255),    # cuerno
    "E": (255, 160, 56, 255),     # aliento
})

# ===========================================================================
#  EFECTOS
# ===========================================================================
SPARK = _palette("SPARK", {
    "w": (255, 255, 255, 255),
    "a": (246, 214, 255, 255),
    "v": (198, 124, 255, 255),
    "d": (120, 56, 190, 255),
    "y": (255, 206, 92, 255),
    "o": (255, 150, 60, 255),
})
