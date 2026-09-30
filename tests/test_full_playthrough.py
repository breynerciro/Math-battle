"""
test_full_playthrough.py — Partida completa simulada
====================================================

Juega un nivel ENTERO automáticamente: abre retos con ATACAR, responde
eligiendo la opción correcta (o una equivocada) dentro de la propia
pantalla de combate y verifica que se llega a la victoria o a GAME OVER.

Es el "playtest automático" del diseño: los 5 niveles completables
respondiendo bien, y las 3 vidas perdidas respondiendo siempre mal.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture(autouse=True)
def isolate_save(tmp_path):
    """Que los tests NO toquen el save_data.json real del jugador."""
    from src import config
    original = config.SAVE_FILE
    config.SAVE_FILE = str(tmp_path / "save.json")
    yield
    config.SAVE_FILE = original


def _step_battle(battle, answer_mode):
    """Un paso de la partida dentro de la pantalla de combate."""
    if battle.question_active:
        wrong = (battle.challenge.correct_index + 1) % 4
        battle._choose_option(battle.challenge.correct_index
                              if answer_mode == "correct" else wrong)
    elif battle.can_attack and not battle.transition.active():
        battle._open_challenge()
    else:
        battle.update(0.2)          # acelerar animaciones/esperas


def _play_level(level: int, answer_mode: str, max_turns=5000):
    """Juega un nivel completo.

    answer_mode: "correct" (siempre bien) o "wrong" (siempre mal).
    Devuelve el estado final (VictoryState o DefeatState).

    Los updates usan dt=0.2s para "quemar" rápido las esperas de animación.
    """
    from src.game import Game
    from src.states.battle_state import BattleState
    from src.states.victory_state import VictoryState
    from src.states.defeat_state import DefeatState

    game = Game()
    game.change_state(BattleState(game, level))

    for turn in range(max_turns):
        state = game.current_state()

        if isinstance(state, (VictoryState, DefeatState)):
            return state

        if isinstance(state, BattleState):
            _step_battle(state, answer_mode)
        else:
            pytest.fail(f"Estado inesperado: {type(state).__name__}")

    pytest.fail(f"El nivel {level} no terminó en {max_turns} turnos")


def test_win_every_level_answering_correctly():
    """Respondiendo bien SE DEBE poder completar cada uno de los 5 niveles."""
    from src.states.victory_state import VictoryState

    for level in range(1, 6):
        final = _play_level(level, "correct")
        assert isinstance(final, VictoryState), \
            f"El nivel {level} no terminó en victoria"
        # El progreso quedó guardado y el nivel quedó desbloqueado
        assert final.save_data["highest_level"] >= min(5, level + 1)


def test_lose_game_answering_wrong():
    """Respondiendo siempre mal se pierden las 3 vidas → GAME OVER."""
    from src.game import Game
    from src.states.battle_state import BattleState
    from src.states.defeat_state import DefeatState

    game = Game()
    game.change_state(BattleState(game, 1))

    state = None
    for turn in range(5000):
        state = game.current_state()
        if isinstance(state, DefeatState):
            break
        if isinstance(state, BattleState):
            _step_battle(state, "wrong")
    else:
        pytest.fail("La partida no terminó en derrota")

    assert isinstance(state, DefeatState)
    assert game.player.lives <= 0


def test_retry_keeps_score_but_heals():
    """Tras perder una vida, el reintento cura al héroe y conserva puntos."""
    from src.game import Game
    from src.states.battle_state import BattleState

    game = Game()
    game.change_state(BattleState(game, 1))

    # Perder una vida a propósito
    for turn in range(5000):
        state = game.current_state()
        if isinstance(state, BattleState) and game.player.lives < 3:
            break        # ya hubo un reintento
        if isinstance(state, BattleState):
            _step_battle(state, "wrong")
    else:
        pytest.fail("No se llegó al reintento")

    battle = game.current_state()
    assert isinstance(battle, BattleState)
    assert game.player.lives == 2
    assert game.player.hp == game.player.max_hp      # curado por completo
