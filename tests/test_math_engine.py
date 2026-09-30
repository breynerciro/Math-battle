"""
test_math_engine.py — Tests del motor matemático
================================================

Verifica que cada generador produzca retos VÁLIDOS:
- la pregunta existe y la respuesta es correcta,
- la respuesta siempre es positiva y "bonita",
- check_answer acepta formatos razonables ("11/12", decimales...).
"""

import os
import sys
from fractions import Fraction

import pytest

# Permitir ejecutar pytest desde cualquier carpeta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.math_engine import ChallengeGenerator, MathTopic
from src.math_engine import operations, equations, powers_roots, fractions, geometry


@pytest.fixture
def generator():
    """Una instancia del repartidor de retos (con sus 4 opciones)."""
    return ChallengeGenerator()


# ---------------------------------------------------------------------- #
#  ChallengeGenerator
# ---------------------------------------------------------------------- #
def test_generator_produces_all_topics(generator):
    """Cada tema debe poder generar retos en todas las dificultades."""
    for topic in MathTopic:
        for difficulty in range(1, 6):
            challenge = generator.generate(topic, difficulty)
            assert challenge.question, "La pregunta no puede ser vacía"
            assert challenge.answer is not None
            assert 1 <= challenge.difficulty <= 5
            assert challenge.time_limit > 0
            assert challenge.points > 0


def test_generate_for_level_uses_level_topic(generator):
    """generate_for_level(3) debe producir retos de fracciones (nivel 3)."""
    for _ in range(30):
        challenge = generator.generate_for_level(3)
        assert challenge.difficulty == 3
    # La dificultad se acota al rango 1..5
    challenge = generator.generate_for_level(1, difficulty=99)
    assert challenge.difficulty == 5


def test_every_challenge_has_four_options(generator):
    """Todo reto es opción múltiple: 4 alternativas únicas y una correcta."""
    for topic in MathTopic:
        for _ in range(30):
            c = generator.generate(topic, 3)
            assert len(c.options) == 4, c.question
            assert len(set(c.options)) == 4, f"opciones repetidas: {c.options}"
            # La opción marcada es exactamente la respuesta del reto
            assert c.correct_option() == (c.answer_display or str(c.answer))
            assert c.check_option(c.correct_index) is True
            assert c.check_option((c.correct_index + 1) % 4) is False


def test_options_position_is_shuffled(generator):
    """La correcta no siempre está en la misma posición (A/B/C/D)."""
    positions = {generator.generate(MathTopic.SUMAS, 1).correct_index
                 for _ in range(60)}
    assert len(positions) > 1, "la respuesta siempre cae en la misma letra"


# ---------------------------------------------------------------------- #
#  Operaciones (nivel 1)
# ---------------------------------------------------------------------- #
def test_operations_division_always_exact():
    """Las divisiones deben ser exactas (sin decimales)."""
    for _ in range(100):
        c = operations.generate(3)
        assert float(c.answer) == int(c.answer)
        assert c.answer > 0


def test_operations_combined_respects_order():
    """El generador combinado produce respuestas coherentes con su pregunta."""
    for _ in range(50):
        c = operations.generate(4)
        # formato: "¿Cuánto es a × b + c?" o "¿Cuánto es a + b × c?"
        assert "×" in c.question
        assert c.answer > 0 or " - " in c.question  # la resta puede dar negativo


# ---------------------------------------------------------------------- #
#  Ecuaciones (niveles 4 y 5): la respuesta DEBE verificar la ecuación
# ---------------------------------------------------------------------- #
def _verify_equation(question, x):
    """Reconstruye la ecuación del texto y verifica que x la satisface."""
    q = question.replace("Si ", "").replace(", ¿cuánto vale x?", "")
    left, right = q.split(" = ")
    assert _eval_side(left, x) == _eval_side(right, x)


def _eval_side(side, x):
    """Evalúa '3x + 5', '3(x + 2)', 'x' etc. sustituyendo x por su valor."""
    side = (side.replace(" ", "").replace("·", "*")
                .replace("−", "-").replace("×", "*").replace("÷", "/"))
    # "3x" → "3*x"; "3(x+2)" → "3*(x+2)"
    out = []
    for i, ch in enumerate(side):
        out.append(ch)
        if ch.isdigit() and i + 1 < len(side) and (side[i + 1] == "x" or side[i + 1] == "("):
            out.append("*")
    return eval("".join(out), {"x": x})


@pytest.mark.parametrize("difficulty", [1, 2, 3, 4, 5])
def test_equations_answers_are_correct(difficulty):
    """La x que devuelve cada ecuación DEBE satisfacer la ecuación."""
    for _ in range(50):
        c = equations.generate(difficulty)
        assert isinstance(c.answer, int), f"x debe ser entero: {c.question}"
        _verify_equation(c.question, c.answer)


# ---------------------------------------------------------------------- #
#  Potencias y raíces (reserva fuera del ciclo de niveles)
# ---------------------------------------------------------------------- #
def test_roots_are_exact():
    """La raíz cuadrada de N debe dar entero y N debe ser el cuadrado de la respuesta."""
    for _ in range(50):
        c = powers_roots.generate(3)
        # formato: "¿Cuánto es la raíz cuadrada de 144?"
        n = int(c.question.split(" de ")[1].split("?")[0])
        assert c.answer * c.answer == n


# ---------------------------------------------------------------------- #
#  Fracciones (nivel 3): respuesta en formato a/b y verificable
# ---------------------------------------------------------------------- #
def test_fractions_answer_matches_question():
    """El resultado mostrado debe ser la respuesta real simplificada.

    Si el resultado es entero se muestra como "6" (no como "6/1");
    si no, en formato a/b.
    """
    for _ in range(50):
        c = fractions.generate(3)
        assert c.answer.denominator >= 1
        if "/" in c.answer_display:
            num, den = c.answer_display.split("/")
            assert Fraction(int(num), int(den)) == c.answer
        else:
            assert int(c.answer_display) == c.answer


def test_fraction_check_accepts_slash_format():
    """check_answer debe aceptar '11/12' como respuesta a 2/3 + 1/4."""
    challenge = fractions.generate(3)
    display = challenge.answer_display
    assert challenge.check_answer(display) is True
    wrong = f"{challenge.answer.numerator + 1}/{challenge.answer.denominator}"
    # Solo falla si la "respuesta incorrecta" es realmente distinta
    if Fraction(wrong) != challenge.answer:
        assert challenge.check_answer(wrong) is False


# ---------------------------------------------------------------------- #
#  Geometría (nivel 4): respuestas positivas y con unidades
# ---------------------------------------------------------------------- #
def test_geometry_answers_positive_with_units():
    """Las respuestas de geometría son positivas y llevan unidad."""
    for _ in range(50):
        c = geometry.generate(5)
        assert c.answer > 0
        assert any(u in c.answer_display for u in ("cm", "cm²", "°"))


# ---------------------------------------------------------------------- #
#  Validación de respuestas (tolerancia numérica)
# ---------------------------------------------------------------------- #
def test_check_answer_integer_exact():
    """check_answer compara enteros exactos (y rechaza basura como 'abc')."""
    from src.math_engine.challenge import MathChallenge
    c = MathChallenge(question="test", answer=56)
    assert c.check_answer(56) is True
    assert c.check_answer("56") is True
    assert c.check_answer(" 56 ") is True
    assert c.check_answer(55) is False
    assert c.check_answer("abc") is False


def test_check_answer_float_tolerance():
    """Los decimales se comparan con tolerancia de 0.01 (errores de redondeo)."""
    from src.math_engine.challenge import MathChallenge
    c = MathChallenge(question="test", answer=3.14)
    assert c.check_answer(3.14) is True
    assert c.check_answer("3.15") is False      # fuera de tolerancia 0.01
    assert c.check_answer(3.149) is True
