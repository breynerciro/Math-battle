"""
challenge.py — Tipos compartidos del motor matemático
=====================================================

Define las "fichas" que todos los generadores producen:

- MathTopic:    de qué tema es el reto (1 por cada nivel del juego)
- MathChallenge: un reto completo (pregunta, respuesta, tiempo, puntos...)

Separar esto en su propio archivo evita importaciones circulares entre
challenge_generator.py y los módulos de operaciones.
"""

from dataclasses import dataclass, field
from enum import Enum


class MathTopic(Enum):
    """Los 5 temas matemáticos, uno por nivel del juego.

    El orden ES el orden de los niveles de Math Battle:
        1 Bosque de las Sumas          sumas y restas
        2 Mina de la Multiplicación    ×, ÷ y problemas de lógica
        3 Templo de las Fracciones     fracciones
        4 Puente Hacia el Caos         geometría y ecuaciones
        5 Castillo del Caos            álgebra
    """
    SUMAS = 1            # Nivel 1: sumas y restas básicas
    MULTIPLICACION = 2   # Nivel 2: multiplicación, división y lógica
    FRACCIONES = 3       # Nivel 3: operaciones con fracciones
    GEOMETRIA = 4        # Nivel 4: perímetros, áreas y ecuaciones
    ALGEBRA = 5          # Nivel 5: álgebra (ecuaciones lineales)


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
        options:         las 4 opciones A, B, C, D (las llena options.build)
        correct_index:   índice de la correcta dentro de `options`
    """
    question: str
    answer: object                 # int, float o Fraction
    answer_display: str = ""
    time_limit: int = 30
    points: int = 100
    difficulty: int = 1
    hint: str = ""
    options: list = field(default_factory=list)
    correct_index: int = -1

    def check_option(self, index: int) -> bool:
        """¿La opción elegida (0-3) es la correcta?"""
        return index == self.correct_index

    def correct_option(self) -> str:
        """Texto de la opción correcta (para el feedback educativo)."""
        if 0 <= self.correct_index < len(self.options):
            return self.options[self.correct_index]
        return self.answer_display or str(self.answer)

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
