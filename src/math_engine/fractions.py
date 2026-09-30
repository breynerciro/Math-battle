"""
fractions.py — Nivel 4: Fracciones
==================================

Usamos la clase Fraction de Python: ella simplifica automáticamente
(el resultado de 2/3 + 1/4 se guarda como 11/12, ya reducido).

    d1: fracciones equivalentes / comparación de valor simple
    d2: suma con igual denominador
    d3: suma y resta con distinto denominador
    d4: multiplicación de fracciones
    d5: división de fracciones
"""

import random
from fractions import Fraction

from .challenge import MathChallenge
from .. import config


def generate(difficulty: int) -> MathChallenge:
    """Genera un reto de fracciones según la dificultad (1-5)."""
    generators = {
        1: _gen_equivalent,
        2: _gen_same_denominator,
        3: _gen_different_denominator,
        4: _gen_multiplication,
        5: _gen_division,
    }
    return generators.get(difficulty, _gen_equivalent)(difficulty)


def _rand_fraction(max_den=6):
    """Fracción aleatoria propia (numerador < denominador, no cero)."""
    den = random.randint(2, max_den)
    num = random.randint(1, den - 1)
    return Fraction(num, den)


def _make(question, answer: Fraction, difficulty, hint):
    """Empaqueta el reto de fracciones con su texto bonito (a/b)."""
    # Si el resultado es entero (6/1) se muestra como "6": una fracción
    # sobre 1 no es la respuesta bonita que queremos enseñar.
    display = (str(answer.numerator) if answer.denominator == 1
               else f"{answer.numerator}/{answer.denominator}")
    return MathChallenge(
        question=question,
        answer=answer,
        answer_display=display,
        time_limit=config.TIME_LIMIT_FRACTIONS,
        points=config.POINTS_BASE,
        difficulty=difficulty,
        hint=hint,
    )


def _gen_equivalent(difficulty):
    """¿Cuánto es a/b de N? (fracción de una cantidad entera)."""
    den = random.randint(2, 6)
    num = random.randint(1, den - 1)
    whole = den * random.randint(2, 6)
    answer = Fraction(num, den) * whole
    return _make(f"¿Cuánto es {num}/{den} de {whole}?", answer, difficulty,
                 f"Divide {whole} entre {den} y multiplica por {num}.")


def _gen_same_denominator(difficulty):
    """Suma/resta con el MISMO denominador: solo se suman los numeradores."""
    den = random.randint(3, 8)
    a = random.randint(1, den - 1)
    b = random.randint(1, den - 1)
    if random.random() < 0.6:
        answer = Fraction(a, den) + Fraction(b, den)
        return _make(f"¿Cuánto es {a}/{den} + {b}/{den}?", answer, difficulty,
                     "Mismo denominador: suma solo los numeradores.")
    if b > a:
        a, b = b, a
    answer = Fraction(a, den) - Fraction(b, den)
    return _make(f"¿Cuánto es {a}/{den} - {b}/{den}?", answer, difficulty,
                 "Mismo denominador: resta solo los numeradores.")


def _gen_different_denominator(difficulty):
    """Suma/resta con DISTINTO denominador: hay que buscar común denominador."""
    f1 = _rand_fraction(6)
    f2 = _rand_fraction(6)
    if random.random() < 0.6:
        answer = f1 + f2
        return _make(f"¿Cuánto es {f1} + {f2}?", answer, difficulty,
                     "Busca un denominador común (mcm) y luego suma.")
    if f2 > f1:
        f1, f2 = f2, f1
    answer = f1 - f2
    return _make(f"¿Cuánto es {f1} - {f2}?", answer, difficulty,
                 "Busca un denominador común (mcm) y luego resta.")


def _gen_multiplication(difficulty):
    """Multiplicación: numerador × numerador, denominador × denominador."""
    f1 = _rand_fraction(6)
    f2 = _rand_fraction(6)
    answer = f1 * f2
    return _make(f"¿Cuánto es {f1} × {f2}?", answer, difficulty,
                 "Multiplica en línea: arriba con arriba, abajo con abajo.")


def _gen_division(difficulty):
    """División: multiplicar por el recíproco (voltear la segunda)."""
    f1 = _rand_fraction(5)
    f2 = _rand_fraction(5)
    answer = f1 / f2
    return _make(f"¿Cuánto es {f1} ÷ {f2}?", answer, difficulty,
                 "Voltea la segunda fracción y multiplica.")
