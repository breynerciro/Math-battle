"""
options.py — Las 4 opciones de respuesta (A, B, C, D)
======================================================

Todo reto del juego se presenta como opción múltiple con 4 alternativas.
Este módulo toma el reto ya generado (que siempre construye PRIMERO la
respuesta correcta) y fabrica 3 distractores creíbles alrededor de ella.

Reglas de los distractores:

- Se parecen a la respuesta (±1, ±2, ±10...), nunca son absurdos:
  en un juego educativo la opción equivocada debe dar que pensar.
- Nunca se repiten y nunca es la correcta.
- Se escriben con el MISMO formato que la respuesta: si la correcta es
  "24 cm²", las otras también llevan " cm²"; si es "11/12", las otras
  también son fracciones.
"""

import random
from fractions import Fraction

#: Desplazamientos usados para fabricar candidatos a distractor
_OFFSETS = (1, -1, 2, -2, 10, -10, 5, -5, 100, -100, 3, -3, 20, -20, 50, -50)


def _format(value, style: str, suffix: str) -> str:
    """Escribe un valor con el mismo formato que la respuesta correcta."""
    if style == "fraction":
        value = Fraction(value)
        return f"{value.numerator}/{value.denominator}{suffix}"
    if style == "int":
        return f"{int(round(value))}{suffix}"
    # float: sin ceros de sobra (78.5 → "78.5", no "78.500000")
    return f"{round(value, 2):g}{suffix}"


def _distractors(answer, style: str, suffix: str, count: int = 3):
    """Genera `count` candidatos distintos de `answer` (y entre sí)."""
    is_fraction = style == "fraction"
    base = Fraction(answer) if is_fraction else answer
    found = []

    def consider(candidate):
        """Acepta un candidato si es válido: distinto de la correcta,
        no repetido y (si el resultado es positivo) también positivo."""
        try:
            if is_fraction:
                candidate = Fraction(candidate)
                if candidate < 0:
                    return
            if candidate == base:
                return
            if not is_fraction and base >= 0 and candidate < 0:
                return
            if isinstance(candidate, float) and candidate != candidate:
                return
            if candidate in found:
                return
            found.append(candidate)
        except (ZeroDivisionError, ValueError, TypeError):
            return

    # 1) Vecinos numéricos: ±1, ±2, ±10... (el error clásico de cálculo)
    for offset in _OFFSETS:
        if len(found) >= count:
            break
        consider(base + offset)

    # 2) Errores típicos: confundir numerador/denominador, olvidar sumar...
    if is_fraction and base.denominator not in (0, 1):
        for candidate in (Fraction(base.denominator, base.numerator or 1),
                          base + Fraction(1, base.denominator),
                          base - Fraction(1, base.denominator),
                          Fraction(base.numerator, base.denominator * 2 or 1)):
            if len(found) >= count:
                break
            consider(candidate)
    elif not is_fraction and base != 0:
        for candidate in (base * 2, base / 2, base + base / 2):
            if len(found) >= count:
                break
            consider(candidate)

    # 3) Red de seguridad: ir sumando 7 hasta completar (nunca falla)
    step, guard = 7, 0
    while len(found) < count and guard < 500:
        consider(base + step)
        step += 7 if step > 0 else -7
        if step < 0:
            step = -step + 7
        guard += 1
    return found[:count]


def build(challenge):
    """Completa el reto con sus 4 opciones.

    Devuelve `(opciones, indice_correcta)`: la lista de textos en el orden
    A, B, C, D y el índice de la correcta. Se baraja para que la respuesta
    no tenga patrón de posición.
    """
    answer = challenge.answer
    display = challenge.answer_display or str(answer)
    style, suffix = _style_of_plain(answer, display)

    correct_text = display
    wrong_values = _distractors(answer, style, suffix, count=3)
    wrong_texts = [_format(v, style, suffix) for v in wrong_values]

    pairs = [(correct_text, True)] + [(t, False) for t in wrong_texts]
    random.shuffle(pairs)
    options = [text for text, _ in pairs]
    correct_index = next(i for i, (_, ok) in enumerate(pairs) if ok)
    return options, correct_index


def _style_of_plain(answer, display: str):
    """(estilo, sufijo) a partir de la respuesta y de su texto bonito."""
    # Fracción propia (2/3) → formato fracción; si es entera (6/1) el
    # juego la muestra como "6", así que usamos el formato entero.
    if isinstance(answer, Fraction) and answer.denominator != 1:
        return "fraction", ""
    plain = str(answer)
    if display.startswith(plain) and len(display) > len(plain):
        suffix = display[len(plain):]
    else:
        suffix = ""
    if isinstance(answer, float):
        return "float", suffix
    return "int", suffix
