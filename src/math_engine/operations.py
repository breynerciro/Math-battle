"""
operations.py — Nivel 1: Operaciones básicas (+, −, ×, ÷)
=========================================================

La dificultad (1 a 5) controla qué operaciones aparecen y el tamaño
de los números:

    d1: sumas y restas
    d2: multiplicaciones (tablas)
    d3: divisiones exactas
    d4: operaciones combinadas sin paréntesis (¡ojo con el orden!)
    d5: operaciones combinadas con paréntesis
"""

import random

from .challenge import MathChallenge
from .. import config


def generate(difficulty: int) -> MathChallenge:
    """Genera un reto de operaciones según la dificultad (1-5)."""
    generators = {
        1: _gen_add_sub,
        2: _gen_multiplication,
        3: _gen_division,
        4: _gen_combined,
        5: _gen_combined_paren,
    }
    func = generators.get(difficulty, _gen_add_sub)
    return func(difficulty)


def generate_add_sub(difficulty: int) -> MathChallenge:
    """Solo sumas y restas (Nivel 1: El Bosque de las Sumas)."""
    return _gen_add_sub(difficulty)


def generate_mul_div(difficulty: int) -> MathChallenge:
    """Multiplicación o división exacta (Nivel 2: La Mina)."""
    func = random.choice([_gen_multiplication, _gen_division])
    return func(max(2, difficulty))


# ---------------------------------------------------------------------- #
#  Generadores internos (uno por tipo de operación)
# ---------------------------------------------------------------------- #
def _gen_add_sub(difficulty):
    """Sumas y restas. Los números crecen con la dificultad."""
    a = random.randint(10, 30 + difficulty * 25)
    b = random.randint(5, 20 + difficulty * 15)
    if random.random() < 0.5:
        return MathChallenge(
            question=f"¿Cuánto es {a} + {b}?",
            answer=a + b,
            time_limit=config.TIME_LIMIT_BASE,
            points=config.POINTS_BASE,
            difficulty=difficulty,
            hint="Suma las unidades primero, luego las decenas.",
        )
    # En la resta, el primer número SIEMPRE es el mayor (resultado positivo)
    if b > a:
        a, b = b, a
    return MathChallenge(
        question=f"¿Cuánto es {a} - {b}?",
        answer=a - b,
        time_limit=config.TIME_LIMIT_BASE,
        points=config.POINTS_BASE,
        difficulty=difficulty,
        hint="Piensa: ¿cuánto le falta a b para llegar a a?",
    )


def _gen_multiplication(difficulty):
    """Multiplicaciones: tablas pequeñas al inicio, números mayores después."""
    max_factor = 9 + difficulty * 2          # d2 → 13, d5 → 19
    a = random.randint(3, max_factor)
    b = random.randint(3, max_factor)
    return MathChallenge(
        question=f"¿Cuánto es {a} × {b}?",
        answer=a * b,
        time_limit=config.TIME_LIMIT_BASE,
        points=config.POINTS_BASE,
        difficulty=difficulty,
        hint=f"Descompón: {a} × {b} = {a} × {b - 1} + {a}",
    )


def _gen_division(difficulty):
    """Divisiones EXACTAS: generamos el cociente primero y multiplicamos."""
    quotient = random.randint(3, 8 + difficulty * 2)
    divisor = random.randint(2, 6 + difficulty)
    dividend = quotient * divisor            # así la división es exacta
    return MathChallenge(
        question=f"¿Cuánto es {dividend} ÷ {divisor}?",
        answer=quotient,
        time_limit=config.TIME_LIMIT_BASE,
        points=config.POINTS_BASE,
        difficulty=difficulty,
        hint=f"Busca el número que multiplicado por {divisor} da {dividend}.",
    )


def _gen_combined(difficulty):
    """Operaciones combinadas sin paréntesis: respeta el orden (×,÷ antes que +,−)."""
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    c = random.randint(2, 30)
    if random.random() < 0.5:
        # a × b + c   o   a × b − c
        op = "+" if random.random() < 0.6 else "-"
        answer = a * b + c if op == "+" else a * b - c
        question = f"¿Cuánto es {a} × {b} {op} {c}?"
        hint = "Primero multiplica, después suma o resta."
    else:
        # a + b × c
        answer = a + b * c
        question = f"¿Cuánto es {a} + {b} × {c}?"
        hint = "La multiplicación va ANTES que la suma."
    return MathChallenge(
        question=question,
        answer=answer,
        time_limit=config.TIME_LIMIT_BASE,
        points=config.POINTS_BASE + 20,
        difficulty=difficulty,
        hint=hint,
    )


def _gen_combined_paren(difficulty):
    """Operaciones combinadas CON paréntesis: el paréntesis se resuelve primero."""
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    c = random.randint(2, 9)
    # (a + b) × c   o   (a − b) × c
    if random.random() < 0.5:
        inner = a + b
        question = f"¿Cuánto es ({a} + {b}) × {c}?"
        hint = "Resuelve primero el paréntesis."
    else:
        if a < b:
            a, b = b, a
        inner = a - b
        question = f"¿Cuánto es ({a} - {b}) × {c}?"
        hint = "Paréntesis primero, multiplicación después."
    return MathChallenge(
        question=question,
        answer=inner * c,
        time_limit=config.TIME_LIMIT_BASE,
        points=config.POINTS_BASE + 40,
        difficulty=difficulty,
        hint=hint,
    )
