"""
challenge_generator.py — El "repartidor" de retos
=================================================

ChallengeGenerator es la puerta de entrada del motor matemático.
El resto del juego SOLO habla con esta clase:

    generator = ChallengeGenerator()
    reto = generator.generate(MathTopic.OPERATIONS, difficulty=2)

Ella decide qué módulo especializado genera el reto según el tema
(uno por nivel) y la dificultad.
"""

from .challenge import MathChallenge, MathTopic
from . import operations, equations, powers_roots, fractions, geometry


class ChallengeGenerator:
    """Genera retos matemáticos aleatorios por tema y dificultad."""

    def __init__(self):
        # Tabla de despacho: tema → módulo generador
        self._modules = {
            MathTopic.OPERATIONS: operations,
            MathTopic.EQUATIONS: equations,
            MathTopic.POWERS_ROOTS: powers_roots,
            MathTopic.FRACTIONS: fractions,
            MathTopic.GEOMETRY: geometry,
        }

    def generate(self, topic: MathTopic, difficulty: int = 1) -> MathChallenge:
        """Devuelve un reto aleatorio del tema dado.

        Args:
            topic:      tema matemático (MathTopic, uno por nivel 1-5)
            difficulty: dificultad de 1 (fácil) a 5 (jefe final)
        """
        difficulty = max(1, min(5, int(difficulty)))   # acotar 1..5
        module = self._modules[topic]
        return module.generate(difficulty)

    def generate_for_level(self, level: int, difficulty: int = None) -> MathChallenge:
        """Atajo: genera un reto del tema correspondiente al nivel del juego.

        Si no se indica dificultad, usa la del nivel (los bosses la suben).
        """
        topic = MathTopic(level)          # MathTopic.OPERATIONS == 1, etc.
        if difficulty is None:
            difficulty = level
        return self.generate(topic, difficulty)
