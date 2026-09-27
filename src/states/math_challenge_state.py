"""
math_challenge_state.py — La pregunta matemática
================================================

Se APILA sobre la batalla: la batalla se congela detrás y aquí
el jugador ve la pregunta, escribe su respuesta y el timer corre.

Al responder, este estado calcula el resultado (a través del
CombatSystem) y devuelve el control a la batalla con un "paquete"
de datos para animar el turno.
"""

import pygame

from .. import config
from ..ui.text_input import TextInput
from ..ui.sound_manager import SoundManager
from .base_state import BaseState


class MathChallengeState(BaseState):
    """Overlay de pregunta + input + timer."""

    def __init__(self, game, combat, enemy):
        super().__init__(game)
        self.combat = combat        # CombatSystem compartido con la batalla
        self.enemy = enemy
        self.sounds = SoundManager()
        self.result = None          # lo que devolveremos a la batalla
        self.feedback = ""          # "¡Correcto!" / "¡Incorrecto!" / "¡Tiempo!"
        self.feedback_color = config.WHITE
        self.showing_feedback = False
        self.feedback_timer = 0.0

        cx = config.SCREEN_WIDTH // 2
        panel_w, panel_h = 640, 220
        self.panel_rect = pygame.Rect(cx - panel_w // 2, 150, panel_w, panel_h)

        # Campo de texto centrado dentro del panel
        self.input = TextInput(cx - 140, self.panel_rect.bottom - 70,
                               280, 44, font_size=config.FONT_SIZE_MEDIUM)
        self.input.on_submit = self._on_submit

    def enter(self):
        self.sounds.play_music("boss" if self.enemy.is_boss else "battle")
        # Pide el reto al CombatSystem (que a su vez lo pide al motor math)
        self.challenge = self.combat.start_challenge(self.enemy)
        self.input.clear()
        self.input.active = True

    # ------------------------------------------------------------------ #
    def _on_submit(self, text):
        """El jugador presionó Enter: evaluar la respuesta."""
        if self.showing_feedback:
            return
        self.result = self.combat.submit_answer(text)
        self.input.active = False
        # Valor bonito de la respuesta ("11/12", "12 cm²"...) — ver display()
        answer_value = self.challenge.display()

        if self.result["correct"]:
            self.feedback = f"¡CORRECTO!  +{self.result['points']} pts"
            self.feedback_color = config.GREEN
            self.sounds.play("correct")
        elif self.result["timeout"]:
            # En un juego educativo, ver la respuesta correcta es lo importante
            self.feedback = f"¡TIEMPO AGOTADO!   Era {answer_value}"
            self.feedback_color = config.ORANGE
            self.sounds.play("timeout")
        else:
            self.feedback = f"¡INCORRECTO!   Era {answer_value}"
            self.feedback_color = config.RED
            self.sounds.play("wrong")
        self.showing_feedback = True
        self.feedback_timer = 1.1       # mostrar el mensaje 1.1 segundos

    # ------------------------------------------------------------------ #
    def handle_events(self, events):
        for event in events:
            if self.showing_feedback:
                # Cualquier tecla acelera el cierre del feedback
                if event.type == pygame.KEYDOWN:
                    self.feedback_timer = 0.0
            else:
                self.input.handle_event(event)

    def update(self, dt):
        self.input.update(dt)

        # Timer de la pregunta (solo mientras se puede responder)
        if not self.showing_feedback:
            self.combat.update(dt)
            if self.combat.challenge_time >= self.challenge.time_limit:
                # Se acabó el tiempo: contar como respuesta vacía
                self._on_submit("")

        if self.showing_feedback:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self._close()

    def _close(self):
        """Devuelve el control a la batalla junto con el resultado.

        El estado de la batalla está justo DEBAJO en la pila
        (game.states[-2]); le entregamos el resultado para que anime
        el turno antes de quitarnos de encima.
        """
        if len(self.game.states) >= 2:
            below = self.game.states[-2]
            if hasattr(below, "_receive_result") and self.result is not None:
                below._receive_result(self.result)
        # Solo nos quitamos de la pila si SEGUIMOS arriba: si el jugador
        # murió, la batalla ya reemplazó toda la pila y no hay que hacer pop.
        if self.game.states and self.game.states[-1] is self:
            self.game.pop_state()

    # ------------------------------------------------------------------ #
    def render(self, screen):
        # Panel central con borde
        pygame.draw.rect(screen, config.BLACK, self.panel_rect, border_radius=10)
        pygame.draw.rect(screen, config.YELLOW, self.panel_rect, 3, border_radius=10)

        cx = config.SCREEN_WIDTH // 2

        # Pregunta (ajustada por PÍXELES al ancho del panel, no por letras)
        lines = self._wrap(self.challenge.question, config.FONT_SIZE_MEDIUM,
                           self.panel_rect.width - 40)
        y = self.panel_rect.y + 26
        for line in lines:
            self.draw_text(screen, line, config.FONT_SIZE_MEDIUM,
                           config.WHITE, cx, y, center=True)
            y += 26

        # Pista (más pequeña, gris)
        if self.challenge.hint:
            hint_lines = self._wrap(f"Pista: {self.challenge.hint}",
                                    config.FONT_SIZE_SMALL,
                                    self.panel_rect.width - 40)
            for line in hint_lines[:2]:
                self.draw_text(screen, line, config.FONT_SIZE_SMALL,
                               config.LIGHT_GRAY, cx, y + 4, center=True)
                y += 18

        # Etiqueta de respuesta (encima del campo, sin montarse sobre él)
        self.draw_text(screen, "Respuesta:", config.FONT_SIZE_SMALL,
                       config.CYAN, self.input.rect.x + 8,
                       self.input.rect.y - 16)
        self.input.render(screen, self.game.get_font(self.input.font_size))

        # Timer: barra que se encoge y cambia a rojo al final
        remaining = self.combat.time_remaining()
        ratio = remaining / self.challenge.time_limit if self.challenge.time_limit else 0
        bar_w = int(200 * ratio)
        bar_color = config.GREEN if ratio > 0.5 else (
            config.YELLOW if ratio > 0.25 else config.RED)
        pygame.draw.rect(screen, config.DARK_GRAY,
                         (cx - 100, self.panel_rect.bottom - 16, 200, 8),
                         border_radius=4)
        if bar_w > 0:
            pygame.draw.rect(screen, bar_color,
                             (cx - 100, self.panel_rect.bottom - 16, bar_w, 8),
                             border_radius=4)
        self.draw_text(screen, f"{int(remaining)}s", config.FONT_SIZE_SMALL,
                       config.WHITE, cx + 115, self.panel_rect.bottom - 22)

        # Feedback (correcto/incorrecto/tiempo)
        if self.showing_feedback:
            self.draw_text(screen, self.feedback, config.FONT_SIZE_LARGE,
                           self.feedback_color, cx,
                           self.panel_rect.centery + 10, center=True)
