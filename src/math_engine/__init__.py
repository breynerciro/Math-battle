"""
Motor matemático de Math Battle
===============================

Uso desde el resto del juego:

    from src.math_engine import ChallengeGenerator
    generator = ChallengeGenerator()
    reto = generator.generate_for_level(2)   # reto de ecuaciones, dificultad 2
"""

from .challenge import MathChallenge, MathTopic
from .challenge_generator import ChallengeGenerator

__all__ = ["MathChallenge", "MathTopic", "ChallengeGenerator"]
