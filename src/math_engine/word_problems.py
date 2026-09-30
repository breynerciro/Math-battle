"""
word_problems.py — Nivel 2: problemas de lógica (multiplicar y dividir)
=======================================================================

Historias cortas donde hay que elegir la operación correcta. Son los
"Si tienes 6 cajas..." del diseño del juego: no basta con calcular,
hay que decidir QUÉ calcular.

Todas las respuestas son números enteros bonitos: primero se elige la
respuesta y después se construye el enunciado (patrón del motor).
"""

import random

from .challenge import MathChallenge
from .. import config


def generate(difficulty: int) -> MathChallenge:
    """Genera un problema de lógica según la dificultad (1-5)."""
    generators = [
        _gen_boxes,
        _gen_sharing,
        _gen_repeat,
        _gen_price,
    ]
    func = random.choice(generators)
    return func(max(1, min(5, int(difficulty))))


def _make(question: str, answer: int, difficulty: int, hint: str) -> MathChallenge:
    """Empaqueta el problema con su tiempo y sus puntos de nivel 2."""
    return MathChallenge(
        question=question,
        answer=answer,
        time_limit=config.TIME_LIMIT_WORD_PROBLEMS,
        points=config.POINTS_BASE,
        difficulty=difficulty,
        hint=hint,
    )


def _gen_boxes(difficulty):
    """Multiplicar: cajas con unidades."""
    boxes = random.randint(3, 6 + difficulty * 3)
    each = random.randint(4, 8 + difficulty * 4)
    return _make(
        f"Si tienes {boxes} cajas con {each} lápices en cada una, "
        f"¿cuántos lápices tienes en total?",
        boxes * each, difficulty,
        f"Multiplica: {boxes} × {each}")


def _gen_sharing(difficulty):
    """Dividir: repartir en partes iguales."""
    parts = random.randint(3, 6 + difficulty)
    each = random.randint(4, 9 + difficulty * 3)
    total = parts * each
    return _make(
        f"Repartes {total} galletas equitativamente entre {parts} amigos. "
        f"¿Cuántas recibe cada uno?",
        each, difficulty,
        f"Divide: {total} ÷ {parts}")


def _gen_repeat(difficulty):
    """Multiplicar: repetir una cantidad día a día."""
    daily = random.randint(5, 12 + difficulty * 4)
    days = random.randint(4, 9)
    return _make(
        f"Matías resuelve {daily} problemas cada día durante {days} días. "
        f"¿Cuántos problemas resuelve en total?",
        daily * days, difficulty,
        f"Multiplica: {daily} × {days}")


def _gen_price(difficulty):
    """Multiplicar: precio por cantidad."""
    price = random.randint(6, 15 + difficulty * 5)
    qty = random.randint(3, 8)
    return _make(
        f"Un cuaderno cuesta {price} monedas y compras {qty} cuadernos. "
        f"¿Cuántas monedas gastas?",
        price * qty, difficulty,
        f"Multiplica: {price} × {qty}")
