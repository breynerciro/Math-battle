"""
challenge.py — Tipos compartidos del motor matemático
=====================================================

Define las "fichas" que todos los generadores producen:

- MathTopic:    de qué tema es el reto (1 por cada nivel del juego)
- MathChallenge: un reto completo (pregunta, respuesta, tiempo, puntos...)

Separar esto en su propio archivo evita importaciones circulares entre
challenge_generator.py y los módulos de operaciones.
"""

from dataclasses import dataclass
from enum import Enum


class MathTopic(Enum):
    """Los 5 temas matemáticos, uno por nivel del juego."""
    OPERATIONS = 1      # Nivel 1: +, −, ×, ÷
    EQUATIONS = 2       # Nivel 2: ecuaciones lineales
    POWERS_ROOTS = 3    # Nivel 3: potencias y raíces
    FRACTIONS = 4       # Nivel 4: fracciones
    GEOMETRY = 5        # Nivel 5: áreas, perímetros, ángulos


@dataclass
class MathChallenge:
    """Un reto matemático listo para mostrarse en pantalla.

    Atributos:
        question:        texto de la pregunta ("¿Cuánto es 7 × 8?")
        answer:          respuesta correcta (int o Fraction)
        answer_display:  cómo se muestra la respuesta ("11/12", "12 cm²"...)
        time_limit:      segundos disponibles para responder
        points:          puntos base si se acierta
        difficulty:      nivel de dificultad (1 a 5)
        hint:            pista opcional para el jugador
    """
    question: str
    answer: object                 # int, float o Fraction
    answer_display: str = ""
    time_limit: int = 30
    points: int = 100
    difficulty: int = 1
    hint: str = ""

    def check_answer(self, user_answer) -> bool:
        """Compara la respuesta del jugador con la correcta.

        Acepta int, float o str. Para fracciones también acepta
        el formato "a/b" (ej: "11/12") y decimales cercanos.
        """
        correct = self.answer
        # 1) Intento directo: números
        try:
            if isinstance(correct, int):
                return int(user_answer) == correct
            # round(..., 6) evita falsos negativos por errores de coma flotante
            diff = round(abs(float(user_answer) - float(correct)), 6)
            return diff < 0.01
        except (ValueError, TypeError, OverflowError):
            pass

        # 2) Intento con fracción tipo "a/b" o "a b/c"
        try:
            from fractions import Fraction
            value = Fraction(str(user_answer).strip().replace(" ", "+", 1)
                             if " " in str(user_answer) else str(user_answer))
            return abs(float(value) - float(correct)) < 0.01
        except (ValueError, ZeroDivisionError, TypeError):
            return False

    def display(self) -> str:
        """Texto bonito para mostrar la respuesta correcta."""
        return self.answer_display if self.answer_display else str(self.answer)
