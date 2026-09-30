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
    """Inicializa (y al final cierra) Pygame una sola vez para el módulo."""
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
    """El héroe tiene sus 4 animaciones con al menos un frame cada una."""
    from src.entities.player import Player
    player = Player()
    for anim in ("idle", "attack", "hurt", "victory"):
        assert anim in player.sprites
        assert len(player.sprites[anim].surfaces) >= 1


def test_backgrounds_generated_for_all_levels(pygame_init):
    """Los 5 fondos se cargan ya escalados al tamaño de la ventana."""
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
    """Flujo completo en UNA pantalla: ATACAR → 4 opciones → daño."""
    from src import config
    from src.game import Game
    from src.states.battle_state import BattleState

    game = Game()
    game.change_state(BattleState(game, 1))
    battle = game.current_state()
    enemy = battle.current_enemy
    hp_before = enemy.hp

    # ATACAR plantea la pregunta DENTRO de la propia batalla
    battle._open_challenge()
    assert game.current_state() is battle       # no se apila ningún estado
    assert battle.question_active is True
    assert len(battle.challenge.options) == 4   # A, B, C, D

    # Responder rápido eligiendo la opción correcta
    battle.combat.challenge_time = 1.0
    battle._choose_option(battle.challenge.correct_index)

    assert battle.question_active is False
    assert battle.feedback == f"CORRECT: MAGIC {config.HERO_DAMAGE} DMG"

    # Tras la animación del turno, el enemigo perdió exactamente 25 HP
    battle.update(2.0)
    assert enemy.hp == hp_before - config.HERO_DAMAGE
    game.quit()


def test_wrong_option_counterattacks(pygame_init):
    """Elegir la opción equivocada hace perder 15 HP al héroe."""
    from src import config
    from src.game import Game
    from src.states.battle_state import BattleState

    game = Game()
    game.change_state(BattleState(game, 1))
    battle = game.current_state()
    player = game.player
    hp_before = player.hp

    battle._open_challenge()
    wrong = (battle.challenge.correct_index + 1) % 4
    battle._choose_option(wrong)

    assert battle.feedback == f"INCORRECT: MAGIC {config.COUNTER_DAMAGE} DMG"
    battle.update(2.0)
    assert player.hp == hp_before - config.COUNTER_DAMAGE
    game.quit()
