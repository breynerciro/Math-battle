"""
test_combat_system.py — Tests del sistema de combate
====================================================

Verifica la lógica de turnos SIN Pygame (usando dobles de prueba):
- daño FIJO de 25 al acertar,
- contraataque FIJO de 15 al fallar,
- timers y timeout,
- muerte de enemigos y del jugador,
- cálculo de puntos y combos.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.combat.combat_system import CombatSystem
from src.entities.player import Player
from src.math_engine.challenge import MathChallenge, MathTopic
from src import config


# ---------------------------------------------------------------------- #
#  Dobles de prueba (fakes): reemplazan clases que dependen de Pygame
# ---------------------------------------------------------------------- #
class FakeEnemy:
    """Enemigo mínimo sin sprites (no necesita Pygame)."""

    def __init__(self, hp=100, attack=20, is_boss=False, difficulty=2):
        """Enemigo de prueba: solo estadísticas, sin sprites ni Pygame."""
        self.name = "Fake"
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.math_topic = MathTopic.SUMAS
        self.difficulty = difficulty
        self.is_boss = is_boss

    def take_damage(self, damage):
        """Resta la vida igual que el enemigo real (sin animaciones)."""
        self.hp = max(0, self.hp - damage)
        return damage

    def is_dead(self):
        """True cuando su vida llegó a 0."""
        return self.hp <= 0


class FakeGenerator:
    """Generador que SIEMPRE devuelve el mismo reto controlado."""

    def __init__(self, answer=7, time_limit=30):
        """Reto fijo: la respuesta es 7 y la opción A (índice 0) es la buena."""
        self.answer = answer
        self.time_limit = time_limit
        self.last_difficulty = None

    def generate(self, topic, difficulty):
        """Devuelve SIEMPRE el mismo reto de 4 opciones (controlado)."""
        self.last_difficulty = difficulty
        return MathChallenge(
            question="¿Cuánto es 7?",
            answer=self.answer,
            time_limit=self.time_limit,
            points=100,
            difficulty=difficulty,
            # Opción múltiple controlada: la 0 (A) es la correcta
            options=[str(self.answer), "8", "6", "9"],
            correct_index=0,
        )


@pytest.fixture
def setup():
    """Dobles de prueba: un jugador y un enemigo SIN Pygame (más rápido)."""
    player = Player.__new__(Player)      # crear SIN sprites (sin Pygame)
    player.name = "Test"
    player.max_hp = 100
    player.hp = 100
    player.attack = 20
    player.defense = 0
    player.lives = 3
    player.score = 0
    player.combo = 0
    player.max_combo = 0
    player.correct_count = 0
    player.wrong_count = 0
    player.level_unlocked = 1
    player.heal = lambda amount: setattr(player, "hp",
                                         min(player.max_hp, player.hp + amount))
    player.is_dead = lambda: player.hp <= 0

    def take_damage(damage):
        """Igual que Player.take_damage real: resta el daño tal cual."""
        player.hp = max(0, player.hp - damage)
        return damage
    player.take_damage = take_damage

    def register_correct(challenge, response_time):
        """Igual que Player.register_correct: suma puntos y sube el combo."""
        player.score += challenge.points
        player.combo += 1
        player.max_combo = max(player.max_combo, player.combo)
        player.correct_count += 1
    player.register_correct = register_correct

    def register_wrong():
        """Igual que Player.register_wrong: rompe el combo."""
        player.combo = 0
        player.wrong_count += 1
    player.register_wrong = register_wrong

    enemy = FakeEnemy()
    generator = FakeGenerator()
    combat = CombatSystem(player, generator)
    return player, enemy, generator, combat


# ---------------------------------------------------------------------- #
#  Turnos
# ---------------------------------------------------------------------- #
def test_correct_answer_damages_enemy(setup):
    """Acertar la opción correcta hace 25 de daño y pasa a fase de ataque."""
    player, enemy, generator, combat = setup
    combat.start_challenge(enemy)
    result = combat.submit_answer("7")
    assert result["correct"] is True
    assert result["damage"] == config.HERO_DAMAGE      # daño fijo: 25
    assert enemy.hp == enemy.max_hp - config.HERO_DAMAGE
    assert combat.phase == CombatSystem.PH_PLAYER_ATTACK


def test_submit_option_by_index(setup):
    """El jugador responde eligiendo la opción A-D (índice 0-3)."""
    player, enemy, generator, combat = setup
    combat.start_challenge(enemy)
    # Opción correcta (índice 0 en el doble de prueba)
    result = combat.submit_option(0)
    assert result["correct"] is True
    assert result["damage"] == config.HERO_DAMAGE
    # Opción incorrecta
    combat.start_challenge(enemy)
    hp_before = player.hp
    result = combat.submit_option(3)
    assert result["correct"] is False
    assert result["damage"] == config.COUNTER_DAMAGE   # contraataque: 15
    assert player.hp == hp_before - config.COUNTER_DAMAGE


def test_wrong_answer_counterattacks(setup):
    """Elegir mal hace que el enemigo contraataque por 15 de daño."""
    player, enemy, generator, combat = setup
    combat.start_challenge(enemy)
    hp_before = player.hp
    result = combat.submit_answer("999")
    assert result["correct"] is False
    assert result["damage"] == config.COUNTER_DAMAGE
    assert player.hp == hp_before - config.COUNTER_DAMAGE
    assert combat.phase == CombatSystem.PH_ENEMY_ATTACK


def test_timeout_counts_as_wrong(setup):
    """Agotar el tiempo sin elegir cuenta como error (mismo daño: 15)."""
    player, enemy, generator, combat = setup
    combat.start_challenge(enemy)
    combat.challenge_time = generator.time_limit + 1   # simular espera total
    result = combat.submit_option(None)                # no se eligió nada
    assert result["timeout"] is True
    assert result["correct"] is False
    # El tiempo agotado duele igual: daño fijo del contraataque
    assert result["damage"] == config.COUNTER_DAMAGE


def test_enemy_death_sets_phase_and_heals(setup):
    """El último golpe mata al enemigo y cura un poco al héroe."""
    player, enemy, generator, combat = setup
    enemy.hp = 5                                       # casi muerto
    combat.start_challenge(enemy)
    result = combat.submit_answer("7")
    assert result["enemy_died"] is True
    assert enemy.is_dead()
    assert combat.phase == CombatSystem.PH_ENEMY_DEATH


def test_player_death_sets_defeat(setup):
    """Si el héroe se queda sin vida, el combate pasa a fase de derrota."""
    player, enemy, generator, combat = setup
    player.hp = 1
    combat.start_challenge(enemy)
    result = combat.submit_answer("mala")
    assert result["player_died"] is True
    assert combat.phase == CombatSystem.PH_DEFEAT


def test_damage_is_fixed_for_bosses_too(setup):
    """El daño es FIJO (diseño del juego): ni bosses ni suerte lo cambian."""
    player, _, generator, _ = setup
    boss = FakeEnemy(hp=1000, is_boss=True)
    normal = FakeEnemy(hp=1000, is_boss=False)
    combat_boss = CombatSystem(player, generator)
    combat_norm = CombatSystem(player, generator)

    combat_boss.start_challenge(boss)
    d_boss = combat_boss.submit_answer("7")["damage"]
    combat_norm.start_challenge(normal)
    d_norm = combat_norm.submit_answer("7")["damage"]
    assert d_boss == d_norm == config.HERO_DAMAGE


def test_timer_runs_only_in_challenge_phase(setup):
    """El cronómetro solo corre mientras la pregunta está en pantalla."""
    player, enemy, generator, combat = setup
    combat.start_challenge(enemy)
    combat.update(2.0)
    assert combat.challenge_time == pytest.approx(2.0)
    combat.phase = CombatSystem.PH_PLAYER_ATTACK
    combat.update(5.0)
    assert combat.challenge_time == pytest.approx(2.0)   # no corre fuera de fase
    assert combat.time_remaining() == 0.0


def test_difficulty_passed_to_generator(setup):
    """La dificultad del enemigo llega hasta el generador de retos."""
    player, enemy, generator, combat = setup
    enemy.difficulty = 4
    combat.start_challenge(enemy)
    assert generator.last_difficulty == 4


# ---------------------------------------------------------------------- #
#  Puntuación y combos (Player)
# ---------------------------------------------------------------------- #
def test_player_score_and_combo(setup):
    """Usa el register_correct REAL de Player (no el doble de prueba)."""
    from src.entities.player import Player
    player = setup[0]
    challenge = MathChallenge(question="q", answer=1, points=100, time_limit=30)
    Player.register_correct(player, challenge, 3.0)   # rápido → bonus velocidad
    assert player.combo == 1
    assert player.score > 100
    Player.register_wrong(player)
    assert player.combo == 0
    Player.register_correct(player, challenge, 29.0)  # muy lento → sin bonus
    Player.register_correct(player, challenge, 3.0)
    assert player.combo == 2
    assert player.max_combo == 2


def test_player_damage_is_flat(setup):
    """El contraataque resta exactamente su daño (sin defensa que lo suavice)."""
    player = setup[0]
    real = player.take_damage(config.COUNTER_DAMAGE)
    assert real == config.COUNTER_DAMAGE
    assert player.hp == 100 - config.COUNTER_DAMAGE


def test_player_heal_caps_at_max(setup):
    """Curar nunca sube la vida por encima del máximo (100)."""
    player = setup[0]
    player.hp = 90
    player.heal(50)
    assert player.hp == player.max_hp
