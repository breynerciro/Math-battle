"""
config.py — Constantes globales de Math Battle
================================================

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
# 960x540 = doble de 480x270. Trabajamos "a escala 2x" para que el pixel art
# se vea grande y nítido sin inventar detalles de más.
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60
TITLE = "Math Battle"
GROUND_Y = 400    # línea del suelo en la batalla (los pies de los personajes)

# Nombres de archivo de fuentes (si existen en assets/fonts/ se usan)
FONT_PIXEL_NAME = "PressStart2P.ttf"   # Descargable de Google Fonts
FONT_FALLBACK = None                    # pygame usa la fuente por defecto

# Tamaños de fuente (en la fuente pixel, 16 px ya se lee bien a 960px)
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
    1: (34, 100, 34),    # Bosque: verde
    2: (40, 40, 70),     # Cueva: azul oscuro
    3: (120, 60, 140),   # Torre: púrpura
    4: (50, 90, 40),     # Pantano: verde pálido
    5: (90, 40, 40),     # Fortaleza: rojo oscuro
}

# ---------------------------------------------------------------------------
# Jugador
# ---------------------------------------------------------------------------
PLAYER_MAX_HP = 100
PLAYER_ATTACK = 15
PLAYER_DEFENSE = 5
PLAYER_LIVES = 3
HEAL_BETWEEN_ENEMIES = 25     # HP que recupera el jugador al vencer un enemigo
MAX_COMBO = 10                # Combo máximo que se cuenta para el bonus

# ---------------------------------------------------------------------------
# Enemigos y combate
# ---------------------------------------------------------------------------
ENEMY_ATTACK_MIN = 10         # Daño mínimo de enemigos normales
ENEMY_ATTACK_MAX = 30
BOSS_ATTACK_MIN = 20          # Daño de los bosses
BOSS_ATTACK_MAX = 50
TIMEOUT_DAMAGE_MULTIPLIER = 0.5  # Si se agota el tiempo, el golpe duele la mitad

# ---------------------------------------------------------------------------
# Retos matemáticos (timers en segundos)
# ---------------------------------------------------------------------------
TIME_LIMIT_BASE = 30          # Nivel 1: operaciones
TIME_LIMIT_EQUATIONS = 45     # Nivel 2: ecuaciones
TIME_LIMIT_POWERS = 45        # Nivel 3: potencias y raíces
TIME_LIMIT_FRACTIONS = 60     # Nivel 4: fracciones
TIME_LIMIT_GEOMETRY = 60      # Nivel 5: geometría

# Puntos base por respuesta correcta (se suman bonus por velocidad y combo)
POINTS_BASE = 100
SPEED_BONUS_MAX = 50          # Bonus máximo por responder muy rápido
COMBO_BONUS_PER = 20          # Puntos extra por cada nivel de combo

# ---------------------------------------------------------------------------
# Generales del juego
# ---------------------------------------------------------------------------
TOTAL_LEVELS = 5
QUESTIONS_PER_BATTLE = 99    # El combate termina por HP, no por número de retos