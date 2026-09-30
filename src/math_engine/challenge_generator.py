"""
challenge_generator.py — El "repartidor" de retos
=================================================

ChallengeGenerator es la puerta de entrada del motor matemático.
El resto del juego SOLO habla con esta clase:

    generator = ChallengeGenerator()
    reto = generator.generate(MathTopic.SUMAS, difficulty=2)
    # reto.options -> ["39", "41", "37", "43"]   reto.correct_index -> 0

Cada tema corresponde a un nivel del juego y puede mezclar varios
generadores (el nivel 2, por ejemplo, reparte entre multiplicaciones
y problemas de lógica). Al final SIEMPRE se añaden las 4 opciones
de respuesta (A, B, C, D) con `options.build`.
"""

import random

from .challenge import MathChallenge, MathTopic
from . import (equations, fractions, geometry, operations, options,
               word_problems)


def _sumas(difficulty):
    """Nivel 1: sumas y restas básicas."""
    return operations.generate_add_sub(difficulty)


def _multiplicacion(difficulty):
    """Nivel 2: multiplicación, división y problemas de lógica."""
    return random.choice([
        operations.generate_mul_div,
        operations.generate_mul_div,
        word_problems.generate,
    ])(difficulty)


def _fracciones(difficulty):
    """Nivel 3: operaciones con fracciones."""
    return fractions.generate(difficulty)


def _geometria(difficulty):
    """Nivel 4: perímetros/áreas y ecuaciones de primer grado."""
    return random.choice([
        geometry.generate,
        geometry.generate,
        equations.generate_first_degree,
    ])(difficulty)


def _algebra(difficulty):
    """Nivel 5: álgebra intermedia."""
    return equations.generate_algebra(difficulty)


#: Tema -> generador del tema (el orden del enum es el orden de niveles)
_DISPATCH = {
    MathTopic.SUMAS: _sumas,
    MathTopic.MULTIPLICACION: _multiplicacion,
    MathTopic.FRACCIONES: _fracciones,
    MathTopic.GEOMETRIA: _geometria,
    MathTopic.ALGEBRA: _algebra,
}


class ChallengeGenerator:
    """Genera retos matemáticos aleatorios por tema y dificultad."""

    def generate(self, topic: MathTopic, difficulty: int = 1) -> MathChallenge:
        """Devuelve un reto aleatorio del tema dado, ya con sus 4 opciones.

        Args:
            topic:      tema matemático (MathTopic, uno por nivel 1-5)
            difficulty: dificultad de 1 (fácil) a 5 (jefe final)
        """
        difficulty = max(1, min(5, int(difficulty)))   # acotar 1..5
        generator = _DISPATCH.get(topic, _sumas)
        challenge = generator(difficulty)
        # Opción múltiple: 4 alternativas (A, B, C, D) barajadas
        challenge.options, challenge.correct_index = options.build(challenge)
        return challenge

    def generate_for_level(self, level: int, difficulty: int = None) -> MathChallenge:
        """Atajo: genera un reto del tema correspondiente al nivel del juego.

        Si no se indica dificultad, usa la del nivel (los bosses la suben).
        """
        topic = MathTopic(level)          # MathTopic.SUMAS == 1, etc.
        if difficulty is None:
            difficulty = level
        return self.generate(topic, difficulty)
