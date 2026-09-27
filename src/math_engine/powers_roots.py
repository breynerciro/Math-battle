"""
powers_roots.py — Nivel 3: Potencias y raíces
=============================================

    d1: cuadrados (n²)
    d2: cubos (n³)
    d3: raíces cuadradas exactas (√n)
    d4: potencias varias (n^k) y raíces cúbicas
    d5: notación científica y potencias de 10
"""

import random

from .challenge import MathChallenge
from .. import config


def generate(difficulty: int) -> MathChallenge:
    """Genera un reto de potencias/raíces según la dificultad (1-5)."""
    generators = {
        1: _gen_squares,
        2: _gen_cubes,
        3: _gen_sqrt,
        4: _gen_powers_mixed,
        5: _gen_scientific,
    }
    return generators.get(difficulty, _gen_squares)(difficulty)


def _make(question, answer, difficulty, hint, answer_display=""):
    return MathChallenge(
        question=question,
        answer=answer,
        answer_display=answer_display,
        time_limit=config.TIME_LIMIT_POWERS,
        points=config.POINTS_BASE,
        difficulty=difficulty,
        hint=hint,
    )


def _gen_squares(difficulty):
    """n² con n de 2 a 15."""
    n = random.randint(2, 12 + difficulty)
    return _make(f"¿Cuánto es {n}²?", n * n, difficulty,
                 f"{n}² = {n} × {n}")


def _gen_cubes(difficulty):
    """n³ con n pequeño (los cubos crecen muy rápido)."""
    n = random.randint(2, 7)
    return _make(f"¿Cuánto es {n}³?", n ** 3, difficulty,
                 f"{n}³ = {n} × {n} × {n}")


def _gen_sqrt(difficulty):
    """√n con raíz exacta: generamos la raíz primero."""
    root = random.randint(2, 15)
    return _make(f"¿Cuánto es la raíz cuadrada de {root * root}?", root, difficulty,
                 "Busca el número que multiplicado por sí mismo da ese valor.")


def _gen_powers_mixed(difficulty):
    """Potencias n^k y raíces cúbicas exactas."""
    if random.random() < 0.6:
        n = random.randint(2, 6)
        k = random.randint(2, 4)
        return _make(f"¿Cuánto es {n}^{k}?", n ** k, difficulty,
                     f"{n}^{k} = {' × '.join([str(n)] * k)}")
    # Raíz cúbica exacta
    root = random.randint(2, 6)
    return _make(f"¿Cuánto es la raíz cúbica de {root ** 3}?", root, difficulty,
                 f"Busca n tal que n × n × n = {root ** 3}")


def _gen_scientific(difficulty):
    """Potencias de 10 y notación científica simplificada."""
    if random.random() < 0.5:
        k = random.randint(2, 5)
        return _make(f"¿Cuánto es 10^{k}?", 10 ** k, difficulty,
                     "Es un 1 seguido de tantos ceros como indica el exponente.")
    # a × 10^k → valor expandido (a entero de 1 a 9)
    a = random.randint(1, 9)
    k = random.randint(2, 4)
    answer = a * (10 ** k)
    return _make(f"¿Cuánto es {a} × 10^{k}?", answer, difficulty,
                 f"Mueve la coma {k} lugares a la derecha.")
