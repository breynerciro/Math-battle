"""
test_game_smoke.py — Smoke tests: el juego "arranca" sin crashear
=================================================================

No abren ventana (usamos el driver dummy de SDL): verifican que todos
los módulos se importan, que los estados se crean y que sprites,
sonidos y fondos se generan sin errores.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Driver "dummy" de SDL: no necesita pantalla ni ventana real
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture(scope="module")
def pygame_init():
    import pygame
    pygame.init()
    yield pygame
    pygame.quit()


def test_import_all_modules():
    """Todos los módulos del juego deben importarse sin errores."""
    from src import config                                   # noqa: F401
    from src.game import Game                                # noqa: F401
    from src import save_system                              # noqa: F401
    from src.math_engine import ChallengeGenerator            # noqa: F401
    from src.combat.combat_system import CombatSystem         # noqa: F401
    from src.combat.effects import (FloatingText, ParticleSystem,  # noqa: F401
                                    ScreenShake)
    from src.entities.player import Player                   # noqa: F401
    from src.entities.enemy import Enemy                     # noqa: F401
    from src.entities.enemies import get_level_enemies       # noqa: F401
    from src.ui.animated_sprite import AnimatedSprite        # noqa: F401
    from src.ui.background import get_background             # noqa: F401
    from src.ui.hud import HUD                               # noqa: F401
    from src.ui.text_input import TextInput                  # noqa: F401
    from src.ui.button import Button                         # noqa: F401
    from src.ui.transition import Transition                 # noqa: F401


def test_game_creates_and_runs_frames(pygame_init):
    """El Game debe crearse y correr unos frames con eventos sintéticos."""
    from src.game import Game
    game = Game()
    assert game.current_state() is not None

    # Simular unos 30 frames de menú
    import pygame
    for _ in range(30):
        events = pygame.event.get()
        state = game.current_state()
        state.handle_events(events)
        state.update(1 / 60)
        state.render(game.screen)
    game.quit()


def test_all_enemies_created_with_sprites(pygame_init):
    """Los 15 enemigos (10 normales + 5 bosses) se crean con sprites válidos."""
    from src.entities.enemies import get_level_enemies
    for level in range(1, 6):
        enemies = get_level_enemies(level)
        assert len(enemies) == 3
        assert enemies[-1].is_boss is True          # el boss va al final
        assert not any(e.is_boss for e in enemies[:-1])
        for enemy in enemies:
            assert "idle" in enemy.sprites
            assert "hurt" in enemy.sprites
            assert enemy.hp > 0 and enemy.attack > 0


def test_player_animations_exist(pygame_init):
    from src.entities.player import Player
    player = Player()
    for anim in ("idle", "attack", "hurt", "victory"):
        assert anim in player.sprites
        assert len(player.sprites[anim].surfaces) >= 1


def test_backgrounds_generated_for_all_levels(pygame_init):
    from src.ui.background import get_background
    from src import config
    for level in range(1, config.TOTAL_LEVELS + 1):
        bg = get_background(level)
        assert bg.get_size() == (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)


def test_sounds_generated(pygame_init):
    """Los .wav procedurales se generan y cargan."""
    from src.ui.sound_manager import SoundManager
    from src import config
    manager = SoundManager()
    manager.play("click")          # no debe lanzar excepción
    manager.play_music("menu")
    manager.stop_music()
    # Los archivos deben existir en assets/sounds/
    sfx_dir = os.path.join(config.SOUNDS_DIR, "sfx")
    wavs = [f for f in os.listdir(sfx_dir) if f.endswith(".wav")]
    assert len(wavs) >= 8


def test_save_system_roundtrip(tmp_path):
    """Guardar y cargar el progreso debe ser simétrico."""
    from src import save_system, config
    original_file = config.SAVE_FILE
    try:
        config.SAVE_FILE = str(tmp_path / "save.json")
        data = save_system.load()
        assert data["highest_level"] == 1       # valores por defecto
        data["high_score"] = 999
        save_system.save(data)
        reloaded = save_system.load()
        assert reloaded["high_score"] == 999
    finally:
        config.SAVE_FILE = original_file


def test_record_result_unlocks_next_level(tmp_path):
    """Completar el nivel 2 desbloquea el 3 y actualiza el récord."""
    from src import save_system, config
    original_file = config.SAVE_FILE
    try:
        config.SAVE_FILE = str(tmp_path / "save.json")
        data = save_system.load()
        data = save_system.record_result(data, score=500, level_completed=2,
                                         correct=10, wrong=2, max_combo=5)
        assert data["highest_level"] == 3
        assert data["high_score"] == 500
        assert data["correct_total"] == 10
    finally:
        config.SAVE_FILE = original_file


def test_battle_flow_full_turn(pygame_init):
    """Flujo completo: batalla → pregunta → respuesta correcta → daño."""
    from src.game import Game
    from src.states.battle_state import BattleState
    from src.states.math_challenge_state import MathChallengeState

    game = Game()
    game.change_state(BattleState(game, 1))
    battle = game.current_state()
    enemy = battle.current_enemy
    hp_before = enemy.hp

    # Abrir el reto (push) y responder correctamente
    battle._open_challenge()
    challenge_state = game.current_state()
    assert isinstance(challenge_state, MathChallengeState)
    challenge_state.challenge_time = 1.0     # respuesta rápida
    challenge_state._on_submit(str(challenge_state.challenge.answer))

    # El feedback debe mostrarse y luego cerrarse
    assert challenge_state.showing_feedback is True
    challenge_state.update(2.0)              # espera mayor al timer de feedback

    # De vuelta en batalla, el enemigo recibió daño
    assert game.current_state() is battle
    assert enemy.hp < hp_before
    game.quit()
