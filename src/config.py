"""
config.py — Constantes globales de Math Battle
===============================================

Aquí vive TODO lo que se puede ajustar "girando una perilla":
resolución, colores, tiempos, daño, etc.
Si los estudiantes quieren cambiar la dificultad del juego,
este es el primer archivo que deben mirar.
"""

import os

# ---------------------------------------------------------------------------
# Rutas del proyecto
# ---------------------------------------------------------------------------
# Carpeta raíz del proyecto (Math-battle/) → es la carpeta padre de src/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
SAVE_FILE = os.path.join(BASE_DIR, "save_data.json")

# ---------------------------------------------------------------------------
# Ventana y tiempo
# ---------------------------------------------------------------------------
# 1280x720 (16:9), la resolución que pide el diseño del juego. El pixel art
# se dibuja con escala ENTERA (personajes 32x32 → x5 = 160x160) y los fondos
# 480x270 se reescalan a pantalla al cargarlos (ver ui/background.py).
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Math Battle"
GROUND_Y = 418    # línea del suelo en la batalla (los pies de los personajes)

# ---------------------------------------------------------------------------
# Layout del combate (sección inferior = panel de acción RPG)
# ---------------------------------------------------------------------------
# El prompt divide la pantalla en dos: arriba escenario/personajes,
# abajo el panel con la pregunta, las 4 opciones y los botones de menú.
PANEL_X = 16
PANEL_Y = 436
PANEL_W = SCREEN_WIDTH - 2 * PANEL_X      # 1248
PANEL_H = 268                              # 436 + 268 = 704 (margen 16 abajo)

# Zona izquierda del panel: pregunta + opciones (A, B, C, D)
QUESTION_X = PANEL_X + 20                  # 36
QUESTION_W = 740
OPTIONS_Y = 540                            # primera fila de opciones
OPTION_W = 364
OPTION_H = 60
OPTION_GAP = 12

# Zona derecha del panel: botones de menú (ATACAR / HUIR) + feedback
# Solo estos dos botones existen: MAGIA y OBJETOS quedaron fuera del
# diseño, así que el hueco se aprovecha con botones más altos.
MENU_X = 800
MENU_W = SCREEN_WIDTH - PANEL_X - 20 - MENU_X   # 444
MENU_Y = 452
MENU_BTN_H = 64
MENU_BTN_GAP = 16
MENU_BTN_STEP = MENU_BTN_H + MENU_BTN_GAP   # paso vertical entre botones
FEEDBACK_RECT = (MENU_X, 664, MENU_W, 32)  # esquina inferior derecha

# Nombres de archivo de fuentes (si existen en assets/fonts/ se usan)
FONT_PIXEL_NAME = "PressStart2P.ttf"   # Descargable de Google Fonts
FONT_FALLBACK = None                    # pygame usa la fuente por defecto

# Tamaños de fuente (en la fuente pixel, 16 px ya se lee bien a 1280px)
FONT_SIZE_SMALL = 12
FONT_SIZE_MEDIUM = 16
FONT_SIZE_LARGE = 24
FONT_SIZE_TITLE = 40

# ---------------------------------------------------------------------------
# Paleta de colores (R, G, B) — estilo retro 16-bit
# ---------------------------------------------------------------------------
BLACK = (18, 18, 24)
WHITE = (240, 240, 240)
DARK_GRAY = (45, 45, 55)
GRAY = (100, 100, 110)
LIGHT_GRAY = (170, 170, 180)
RED = (220, 60, 60)
DARK_RED = (150, 30, 30)
GREEN = (80, 200, 100)
DARK_GREEN = (30, 110, 50)
BLUE = (70, 130, 230)
DARK_BLUE = (30, 50, 110)
YELLOW = (250, 210, 60)
ORANGE = (240, 140, 40)
PURPLE = (150, 80, 220)
CYAN = (80, 220, 220)
BROWN = (150, 100, 60)

# Colores por nivel (se usan para fondos y acentos)
LEVEL_COLORS = {
    1: (34, 100, 34),    # Bosque de las Sumas: verde
    2: (150, 110, 40),   # Mina de la Multiplicación: dorado
    3: (60, 100, 170),   # Templo de las Fracciones: azul ruina
    4: (70, 60, 130),    # Puente Hacia el Caos: índigo
    5: (130, 50, 60),    # Castillo del Caos: rojo oscuro
}

# ---------------------------------------------------------------------------
# Jugador
# ---------------------------------------------------------------------------
PLAYER_MAX_HP = 100
PLAYER_ATTACK = 15        # (referencia estadística; el daño lo fija HERO_DAMAGE)
PLAYER_DEFENSE = 5
PLAYER_LIVES = 3
HEAL_BETWEEN_ENEMIES = 25     # HP que recupera el jugador al vencer un enemigo
MAX_COMBO = 10                # Combo máximo que se cuenta para el bonus

# ---------------------------------------------------------------------------
# Enemigos y combate
# ---------------------------------------------------------------------------
# Daño FIJO del duelo (lo define el diseño del juego):
#   respuesta correcta → el héroe lanza el hechizo: enemigo -25 HP
#   respuesta incorrecta → el enemigo contraataca: héroe -15 HP
HERO_DAMAGE = 25
COUNTER_DAMAGE = 15

# ---------------------------------------------------------------------------
# Retos matemáticos (timers en segundos)
# ---------------------------------------------------------------------------
TIME_LIMIT_BASE = 30          # Nivel 1: sumas y restas
TIME_LIMIT_EQUATIONS = 45     # Nivel 4/5: ecuaciones y álgebra
TIME_LIMIT_POWERS = 45        # (reserva: potencias y raíces)
TIME_LIMIT_FRACTIONS = 60     # Nivel 3: fracciones
TIME_LIMIT_GEOMETRY = 60      # Nivel 4: geometría
TIME_LIMIT_WORD_PROBLEMS = 40 # Nivel 2: problemas de lógica

# Puntos base por respuesta correcta (se suman bonus por velocidad y combo)
POINTS_BASE = 100
SPEED_BONUS_MAX = 50          # Bonus máximo por responder muy rápido
COMBO_BONUS_PER = 20          # Puntos extra por cada nivel de combo

# ---------------------------------------------------------------------------
# Generales del juego
# ---------------------------------------------------------------------------
TOTAL_LEVELS = 5
QUESTIONS_PER_BATTLE = 99    # El combate termina por HP, no por número de retos