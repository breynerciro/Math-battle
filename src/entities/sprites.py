"""
sprites.py — Pixel art dibujado con código
==========================================

Cada sprite es una lista de "cuadrículas" (una por frame). Cada carácter
de la cuadrícula es un píxel de un color definido en la paleta.
El punto "." significa transparente.

Este archivo es el lugar PERFECTO para que los estudiantes cambien
los personajes: solo editan las letras de las cuadrículas. También se
pueden reemplazar por imágenes reales más adelante.
"""

# ==========================================================================
#  HÉROE MATEMÁTICO (14 x 14 píxeles aprox)
#  S=piel  H=pelo  A=armadura  D=armadura oscura  R=capa  W=blanco  K=negro
# ==========================================================================
PALETTE_HERO = {
    "S": (235, 180, 140),   # piel
    "H": (90, 60, 30),      # pelo
    "A": (70, 130, 230),    # armadura azul
    "D": (40, 70, 150),     # armadura oscura
    "R": (220, 60, 60),     # capa
    "W": (245, 245, 245),   # blanco
    "K": (25, 25, 30),      # contorno/negro
    "Y": (250, 210, 60),    # detalles dorados
}

HERO_IDLE = [
    [
        "......HHH.....",
        ".....HHHHH....",
        ".....HSSSH....",
        ".....SSSSS....",
        "......SSS.....",
        "....AAAAAAA...",
        "...AAADDDAA...",
        "...SAADADAAS..",
        "...SAAADAAS...",
        "....AAAAAA....",
        "....DD..DD....",
        "....DD..DD....",
        "....KK..KK....",
        "..............",
    ],
    [
        "......HHH.....",
        ".....HHHHH....",
        ".....HSSSH....",
        ".....SSSSS....",
        "......SSS.....",
        "....AAAAAAA...",
        "...AAADDDAA...",
        "...SAADADAAS..",
        "...SAAADAAS...",
        "....AAAAAA....",
        "....DD..DD....",
        "....DD..DD....",
        "...KK....KK...",
        "..............",
    ],
]

HERO_ATTACK = [
    [
        "......HHH.....",
        ".....HHHHH....",
        ".....HSSSH....",
        ".....SSSSS....",
        "......SSS.....",
        "....AAAAAAA...",
        "...AAADDDAA..Y",
        "...SAADADAAS.Y",
        "...SAAADAAS..Y",
        "....AAAAAA...Y",
        "....DD..DD....",
        "....DD..DD....",
        "....KK..KK....",
        "..............",
    ],
    [
        "..Y..HHH......",
        "..Y.HHHHH.....",
        "..Y.HSSSH.....",
        "..YSSSSS......",
        "..Y.SSS.......",
        "..YAAAAAA.....",
        "..AADDDAAA....",
        "..AADADAAS....",
        "...AADAAS.....",
        "....AAAA......",
        "....DD.DD.....",
        "....DD.DD.....",
        "....KK.KK.....",
        "..............",
    ],
]

HERO_HURT = [
    [
        "......HHH.....",
        ".....HHHHH....",
        ".....HSSSH....",
        ".....SWSTS....",
        "......SSS.....",
        "....AAAAAAA...",
        "...AAADDDAA...",
        "...SAADADAAS..",
        "...SAAADAAS...",
        "....AAAAAA....",
        "....DD..DD....",
        "....DD..DD....",
        "....KK..KK....",
        "..............",
    ],
    [
        "..............",
        "......HHH.....",
        ".....HHHHH....",
        ".....HSSSH....",
        ".....SWSTS....",
        "....AAAAAAA...",
        "...AAADDDAA...",
        "...SAADADAAS..",
        "...SAAADAAS...",
        "....AAAAAA....",
        "....DD..DD....",
        "....DD..DD....",
        "..............",
        "..............",
    ],
]

HERO_VICTORY = [
    [
        "......HHH.....",
        ".....HHHHH....",
        ".....HSSSH....",
        ".....SSSSS....",
        "......SSS.....",
        "..Y.AAAAAAA.Y.",
        "..YAAADDDAAY..",
        "..YSAADADAASY.",
        "...SAAADAAS...",
        "....AAAAAA....",
        "....DD..DD....",
        "....DD..DD....",
        "....KK..KK....",
        "..............",
    ],
    [
        "......HHH.....",
        ".....HHHHH....",
        ".....HSSSH....",
        ".....SSSSS....",
        "......SSS.....",
        "....AAAAAAA...",
        "..YAAADDDAAY..",
        "..YSAADADAASY.",
        "...SAAADAAS...",
        "....AAAAAA....",
        "....DD..DD....",
        "....DD..DD....",
        "....KK..KK....",
        "..............",
    ],
]


# ==========================================================================
#  EFECTOS (estrellitas de golpe)
# ==========================================================================
PALETTE_EFFECTS = {
    "Y": (250, 210, 60),
    "W": (255, 255, 255),
    "O": (240, 140, 40),
}

EFFECT_STAR = [
    [
        "....Y....",
        "....W....",
        "...YWY...",
        "..YWWWY..",
        "YYYWWWYYY",
        "..YWWWY..",
        "...YWY...",
        "....W....",
        "....Y....",
    ],
    [
        ".........",
        "....Y....",
        "....W....",
        "...YWY...",
        "..YWWWY..",
        "...YWY...",
        "....W....",
        "....Y....",
        ".........",
    ],
    [
        ".........",
        ".........",
        "....Y....",
        "....W....",
        "...YWY...",
        "....W....",
        "....Y....",
        ".........",
        ".........",
    ],
]


# ==========================================================================
#  Paletas de ENEMIGOS (se combinan con las cuadrículas de cada nivel)
# ==========================================================================
PALETTE_GREEN = {
    "G": (80, 200, 100), "g": (50, 140, 70), "W": (245, 245, 245),
    "K": (25, 25, 30), "R": (220, 60, 60), "B": (70, 130, 230),
    "Y": (250, 210, 60), "P": (150, 80, 220), "O": (240, 140, 40),
    "C": (80, 220, 220), "S": (200, 200, 210), "D": (60, 60, 75),
    "N": (120, 80, 50), "b": (110, 70, 45), "M": (170, 60, 200),
    "L": (220, 180, 240), "E": (255, 150, 50), "F": (255, 220, 120),
    "T": (100, 100, 115), "U": (40, 40, 55), "X": (90, 40, 40),
    "w": (180, 180, 190),
}
