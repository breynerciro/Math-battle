"""
game.py — El corazón del juego
==============================

La clase Game:
1. Inicializa Pygame y la ventana.
2. Carga las fuentes.
3. Maneja la MÁQUINA DE ESTADOS (una pila de pantallas).
4. Ejecuta el loop principal: eventos → update → render, 60 veces por segundo.

¿Por qué una PILA de estados? Porque la pregunta matemática se dibuja
ENCIMA de la batalla. La batalla no se destruye: se "pausa" (pause/resume).
"""

import pygame

from . import config
from .math_engine.challenge_generator import ChallengeGenerator
from .save_system import SaveSystem
from .states.menu_state import MenuState


class Game:
    """Encapsula el loop principal y la pila de estados."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # -- Carga de fuentes --------------------------------------------
        # Intentamos usar la fuente pixel art; si no está instalada en
        # assets/fonts/, usamos la fuente por defecto de Pygame.
        import os
        font_path = os.path.join(config.FONTS_DIR, config.FONT_PIXEL_NAME)
        self._fonts = {}
        sizes = (config.FONT_SIZE_SMALL, config.FONT_SIZE_MEDIUM,
                 config.FONT_SIZE_LARGE, config.FONT_SIZE_TITLE)
        if os.path.exists(font_path):
            for size in sizes:
                self._fonts[size] = pygame.font.Font(font_path, size)
        else:
            # Fuente pixel no encontrada → fuente por defecto
            # (se multiplica x2 porque la fuente por defecto es más pequeña)
            for size in sizes:
                self._fonts[size] = pygame.font.Font(None, size * 2)

        # -- Datos compartidos entre estados -------------------------------
        # (¡antes de crear el menú! los estados los necesitan al entrar)
        self.player = None                # Se crea al empezar una partida
        self.current_level = 1
        self.save_system = SaveSystem()   # Guardar/cargar progreso (JSON)
        self.challenge_generator = ChallengeGenerator()  # Motor matemático
        self.save_data = self.save_system.load()

        # -- Pila de estados ----------------------------------------------
        # El estado de arriba de la pila es el que recibe eventos y dibuja.
        self.states = []
        self.push_state(MenuState(self))

    # ------------------------------------------------------------------ #
    #  Gestión de la pila de estados
    # ------------------------------------------------------------------ #
    def change_state(self, new_state):
        """REEMPLAZA el estado actual (ej: menú → selección de nivel)."""
        while self.states:
            self.states.pop().exit()
        self.states.append(new_state)
        new_state.enter()

    def push_state(self, new_state):
        """APILA un estado encima del actual (ej: batalla → pregunta math)."""
        if self.states:
            self.states[-1].pause()
        self.states.append(new_state)
        new_state.enter()

    def pop_state(self):
        """Quita el estado de arriba y reanuda el de abajo."""
        if self.states:
            self.states.pop().exit()
        if self.states:
            self.states[-1].resume()

    def current_state(self):
        return self.states[-1] if self.states else None

    # ------------------------------------------------------------------ #
    #  Utilidades
    # ------------------------------------------------------------------ #
    def get_font(self, size):
        """Devuelve la fuente ya cargada del tamaño pedido."""
        return self._fonts.get(size, self._fonts[config.FONT_SIZE_MEDIUM])

    def quit(self):
        self.running = False

    # ------------------------------------------------------------------ #
    #  BUCLE PRINCIPAL
    # ------------------------------------------------------------------ #
    def run(self):
        while self.running:
            # dt = tiempo (en segundos) entre este frame y el anterior.
            # Sirve para que las animaciones vayan a la misma velocidad
            # en cualquier computador.
            dt = self.clock.tick(config.FPS) / 1000.0

            # 1) Capturar eventos (teclado, mouse, cerrar ventana)
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            state = self.current_state()
            if state is None:
                self.running = False
                break

            # 2) Actualizar lógica y 3) dibujar (solo el estado de arriba)
            state.handle_events(events)
            state.update(dt)
            state.render(self.screen)

            pygame.display.flip()

        pygame.quit()
