"""
Motor matemático de El Héroe de las Matemáticas
===============================

Uso desde el resto del juego:

    from src.math_engine import ChallengeGenerator
    generator = ChallengeGenerator()
    reto = generator.generate_for_level(2)   # reto del nivel 2 (×, ÷ y lógica)
    reto.options                           # ['8', '6', '7', '9']  (A, B, C, D)
"""

from .challenge import MathChallenge, MathTopic
from .challenge_generator import ChallengeGenerator

__all__ = ["MathChallenge", "MathTopic", "ChallengeGenerator"]
