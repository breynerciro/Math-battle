"""
equations.py — Ecuaciones lineales (Niveles 4 y 5)
===================================================

Truco para que las respuestas siempre sean bonitas (enteras):
generamos PRIMERO la solución x y DESPUÉS construimos la ecuación.

    d1: x + b = c
    d2: a·x = c   /   x − b = c
    d3: a·x + b = c
    d4: a·x − b = c   /   a·(x + b) = c
    d5: a·x + b = c·x + d  (con x a los dos lados)
"""

import random

from .challenge import MathChallenge
from .. import config


def generate(difficulty: int) -> MathChallenge:
    """Genera un reto de ecuaciones según la dificultad (1-5)."""
    generators = {
        1: _gen_level1,
        2: _gen_level2,
        3: _gen_level3,
        4: _gen_level4,
        5: _gen_level5,
    }
    return generators.get(difficulty, _gen_level1)(difficulty)


def generate_first_degree(difficulty: int) -> MathChallenge:
    """Ecuaciones de primer grado sencillas (Nivel 4: x − 15 = 30)."""
    func = random.choice([_gen_level1, _gen_level2, _gen_level3])
    return func(difficulty)


def generate_algebra(difficulty: int) -> MathChallenge:
    """Álgebra intermedia (Nivel 5: 4(x + 2) − 7 = 21, x a dos lados)."""
    func = random.choice([_gen_level3, _gen_level4, _gen_level5])
    return func(difficulty)


def _make(question, x, difficulty, hint):
    """Empaqueta el reto con la configuración común del nivel 2."""
    return MathChallenge(
        question=question,
        answer=x,
        time_limit=config.TIME_LIMIT_EQUATIONS,
        points=config.POINTS_BASE,
        difficulty=difficulty,
        hint=hint,
    )


def _gen_level1(difficulty):
    """x + b = c  →  x = c − b"""
    x = random.randint(1, 15)
    b = random.randint(2, 20)
    c = x + b
    return _make(f"Si x + {b} = {c}, ¿cuánto vale x?", x, difficulty,
                 f"Pasa el {b} restando: x = {c} − {b}")


def _gen_level2(difficulty):
    """a·x = c  o  x − b = c"""
    if random.random() < 0.5:
        x = random.randint(1, 12)
        a = random.randint(2, 9)
        c = a * x
        return _make(f"Si {a}x = {c}, ¿cuánto vale x?", x, difficulty,
                     f"Divide los dos lados entre {a}.")
    x = random.randint(5, 25)
    b = random.randint(2, x - 1)
    c = x - b
    return _make(f"Si x - {b} = {c}, ¿cuánto vale x?", x, difficulty,
                 f"Pasa el {b} sumando: x = {c} + {b}")


def _gen_level3(difficulty):
    """a·x + b = c  →  x = (c − b) / a"""
    x = random.randint(1, 12)
    a = random.randint(2, 9)
    b = random.randint(1, 20)
    c = a * x + b
    return _make(f"Si {a}x + {b} = {c}, ¿cuánto vale x?", x, difficulty,
                 f"Primero resta {b}, luego divide entre {a}.")


def _gen_level4(difficulty):
    """a·x − b = c  o  a·(x + b) = c"""
    if random.random() < 0.5:
        x = random.randint(2, 15)
        a = random.randint(2, 9)
        b = random.randint(1, 15)
        c = a * x - b
        return _make(f"Si {a}x - {b} = {c}, ¿cuánto vale x?", x, difficulty,
                     f"Primero suma {b}, luego divide entre {a}.")
    x = random.randint(1, 10)
    a = random.randint(2, 6)
    b = random.randint(1, 9)
    c = a * (x + b)
    return _make(f"Si {a}(x + {b}) = {c}, ¿cuánto vale x?", x, difficulty,
                 f"Divide entre {a} y luego resta {b}.")


def _gen_level5(difficulty):
    """a·x + b = c·x + d  (x aparece a ambos lados)

    Verificación algebraica:  a·x + b = c·x + d
                              (a − c)·x = d − b
    Así que generamos d = b + (a − c)·x  y la solución es exactamente x.
    """
    x = random.randint(1, 10)
    a = random.randint(3, 9)
    c = random.randint(1, a - 1)          # así (a − c) > 0
    b = random.randint(1, 15)
    d = b + (a - c) * x                    # garantiza que la solución sea x
    question = f"Si {a}x + {b} = {c}x + {d}, ¿cuánto vale x?"
    hint = "Agrupa las x a un lado y los números al otro."
    return _make(question, x, difficulty, hint)
