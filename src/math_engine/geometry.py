"""
geometry.py — Nivel 5: Geometría
================================

Áreas, perímetros y ángulos. Todas las figuras usan números enteros
para que las respuestas sean limpias.

    d1: perímetro de rectángulos y cuadrados
    d2: área de rectángulos y cuadrados
    d3: área de triángulos
    d4: perímetro y área de círculos (con π ≈ 3.14)
    d5: ángulos interiores de triángulos y suplementarios
"""

import math
import random

from .challenge import MathChallenge
from .. import config

PI_APROX = 3.14   # Usamos 3.14 como en el colegio (no math.pi)


def generate(difficulty: int) -> MathChallenge:
    """Genera un reto de geometría según la dificultad (1-5)."""
    generators = {
        1: _gen_perimeter,
        2: _gen_area_rect,
        3: _gen_area_triangle,
        4: _gen_circle,
        5: _gen_angles,
    }
    return generators.get(difficulty, _gen_perimeter)(difficulty)


def _make(question, answer, difficulty, hint, answer_display=""):
    return MathChallenge(
        question=question,
        answer=answer,
        answer_display=answer_display,
        time_limit=config.TIME_LIMIT_GEOMETRY,
        points=config.POINTS_BASE,
        difficulty=difficulty,
        hint=hint,
    )


def _gen_perimeter(difficulty):
    """Perímetro de rectángulo o cuadrado."""
    if random.random() < 0.5:
        base = random.randint(3, 15)
        height = random.randint(2, 12)
        answer = 2 * (base + height)
        return _make(
            f"¿Cuál es el perímetro de un rectángulo de {base} cm × {height} cm?",
            answer, difficulty,
            "Perímetro = 2 × (base + altura)", f"{answer} cm")
    side = random.randint(3, 15)
    answer = 4 * side
    return _make(f"¿Cuál es el perímetro de un cuadrado de lado {side} cm?",
                 answer, difficulty,
                 "Los 4 lados miden lo mismo.", f"{answer} cm")


def _gen_area_rect(difficulty):
    """Área de rectángulo o cuadrado."""
    if random.random() < 0.5:
        base = random.randint(3, 14)
        height = random.randint(2, 12)
        return _make(
            f"¿Cuál es el área de un rectángulo de {base} cm × {height} cm?",
            base * height, difficulty,
            "Área = base × altura", f"{base * height} cm²")
    side = random.randint(3, 13)
    return _make(f"¿Cuál es el área de un cuadrado de lado {side} cm?",
                 side * side, difficulty,
                 "Área = lado × lado", f"{side * side} cm²")


def _gen_area_triangle(difficulty):
    """Área de triángulo: (base × altura) / 2. Siempre da número entero o .5."""
    base = random.randint(4, 16)
    height = random.randint(3, 14)
    answer = base * height / 2
    return _make(
        f"¿Cuál es el área de un triángulo con base {base} cm y altura {height} cm?",
        answer, difficulty,
        "Área = (base × altura) ÷ 2", f"{answer:g} cm²")


def _gen_circle(difficulty):
    """Círculos con π ≈ 3.14: perímetro (circunferencia) o área."""
    radius = random.randint(2, 10)
    if random.random() < 0.5:
        # Perímetro = 2·π·r  (usamos múltiplos de 5 para que salga limpio)
        radius = random.choice([5, 10, 20, 50])
        answer = round(2 * PI_APROX * radius, 2)
        return _make(
            f"¿Cuál es la circunferencia de un círculo de radio {radius} cm? (π ≈ 3.14)",
            answer, difficulty,
            "Circunferencia = 2 × π × radio", f"{answer:g} cm")
    # Área = π·r² (con radio que da resultado limpio con 3.14)
    radius = random.choice([10, 20, 5])
    answer = round(PI_APROX * radius * radius, 2)
    return _make(
        f"¿Cuál es el área de un círculo de radio {radius} cm? (π ≈ 3.14)",
        answer, difficulty,
        "Área = π × radio²", f"{answer:g} cm²")


def _gen_angles(difficulty):
    """Ángulos: suplementarios o suma de los ángulos internos del triángulo."""
    if random.random() < 0.5:
        # Los 3 ángulos internos de un triángulo suman 180°
        a = random.randint(30, 80)
        b = random.randint(20, min(80, 150 - a))
        c = 180 - a - b
        if c <= 0:
            c = 180 - a - b if 180 - a - b > 0 else 180 - a
            b = 180 - a - c
        return _make(
            f"En un triángulo, dos ángulos miden {a}° y {b}°. ¿Cuánto mide el tercero?",
            c, difficulty,
            "Los 3 ángulos internos de un triángulo suman 180°", f"{c}°")
    # Ángulo suplementario (suman 180°)
    a = random.randint(20, 160)
    return _make(f"¿Cuánto mide el suplemento de un ángulo de {a}°?",
                 180 - a, difficulty,
                 "Suplemento = 180° - ángulo", f"{180 - a}°")
