"""
combat_system.py — La lógica del combate
========================================

Coordina el flujo de cada turno (ver el diagrama del plan):

1. El jugador elige ATACAR → se pide un reto matemático.
2. Si responde BIEN y a tiempo → hace daño al enemigo.
   - El daño depende de la velocidad: responder rápido pega más fuerte.
3. Si responde MAL o se agota el tiempo → el enemigo contraataca.
   - Si se agotó el tiempo, el golpe duele la mitad (es menos injusto).
4. Cuando el enemigo muere → el jugador recupera algo de vida y pasa
   al siguiente enemigo del nivel (o al boss).

Esta clase SOLO calcula: no dibuja nada (eso lo hacen los estados).
"""

import random

from .. import config


class CombatSystem:
    """Máquina de turnos del combate."""

    PH_PLAYER_TURN = "player_turn"       # esperando que el jugador ataque
    PH_CHALLENGE = "challenge"           # mostrando pregunta
    PH_PLAYER_ATTACK = "player_attack"   # animación del ataque del héroe
    PH_ENEMY_ATTACK = "enemy_attack"     # animación del contraataque
    PH_ENEMY_DEATH = "enemy_death"       # animación de muerte del enemigo
    PH_VICTORY = "victory"               # enemigos del nivel terminados
    PH_DEFEAT = "defeat"                 # el héroe cayó

    def __init__(self, player, generator):
        self.player = player
        self.generator = generator       # ChallengeGenerator
        self.challenge = None
        self.current_enemy = None
        self.phase = self.PH_PLAYER_TURN
        self.challenge_time = 0.0        # segundos desde que se mostró el reto
        self.response_time = 0.0         # lo que tardó el jugador en responder
        self.is_boss_fight = False

    # ------------------------------------------------------------------ #
    #  Flujo de turnos
    # ------------------------------------------------------------------ #
    def start_challenge(self, enemy):
        """Pide un nuevo reto al motor matemático para este enemigo."""
        self.current_enemy = enemy
        self.is_boss_fight = enemy.is_boss
        # La dificultad del reto crece con el nivel; los bosses pegan con
        # retos más difíciles que los enemigos normales.
        difficulty = enemy.difficulty
        self.challenge = self.generator.generate(enemy.math_topic, difficulty)
        self.phase = self.PH_CHALLENGE
        self.challenge_time = 0.0
        return self.challenge

    def submit_answer(self, user_answer):
        """Evalúa la respuesta del jugador.

        Devuelve un diccionario con el resultado del turno para que
        battle_state lo anime:

            {
                "correct":  bool,
                "timeout":  bool,
                "damage":   int (daño hecho o recibido),
                "points":   int (ganados, si acertó),
                "enemy_died": bool,
                "player_died": bool,
            }
        """
        timed_out = self.challenge_time >= self.challenge.time_limit
        correct = (not timed_out) and self.challenge.check_answer(user_answer)
        result = {
            "correct": correct,
            "timeout": timed_out,
            "damage": 0,
            "points": 0,
            "enemy_died": False,
            "player_died": False,
        }

        if correct:
            result.update(self._player_attacks())
        else:
            result.update(self._enemy_attacks(timed_out))
        return result

    # ------------------------------------------------------------------ #
    #  Daños
    # ------------------------------------------------------------------ #
    def _player_attacks(self):
        """El héroe golpea. Más rápido = más daño (entre 50% y 150% de su ataque)."""
        ratio = 1.0 - min(1.0, self.challenge_time / self.challenge.time_limit)
        damage = int(self.player.attack * (0.5 + ratio))
        damage = max(1, damage)
        # Los bosses tienen "piel dura": reducen un poco el daño recibido
        if self.is_boss_fight:
            damage = max(1, int(damage * 0.85))

        real = self.current_enemy.take_damage(damage)
        points = self.player.register_correct(self.challenge, self.challenge_time)

        result = {
            "correct": True, "timeout": False,
            "damage": real, "points": points,
            "enemy_died": self.current_enemy.is_dead(),
            "player_died": False,
        }
        if result["enemy_died"]:
            self.phase = self.PH_ENEMY_DEATH
            # Curación parcial entre enemigos del mismo nivel
            self.player.heal(config.HEAL_BETWEEN_ENEMIES)
        else:
            self.phase = self.PH_PLAYER_ATTACK
        return result

    def _enemy_attacks(self, timed_out):
        """El enemigo contraataca (por error o por tiempo agotado)."""
        self.player.register_wrong()
        lo, hi = ((config.BOSS_ATTACK_MIN, config.BOSS_ATTACK_MAX)
                  if self.is_boss_fight
                  else (config.ENEMY_ATTACK_MIN, config.ENEMY_ATTACK_MAX))
        damage = random.randint(lo, hi)
        if timed_out:
            damage = max(1, int(damage * config.TIMEOUT_DAMAGE_MULTIPLIER))
        real = self.player.take_damage(damage)

        result = {
            "correct": False, "timeout": timed_out,
            "damage": real, "points": 0,
            "enemy_died": False,
            "player_died": self.player.is_dead(),
        }
        if result["player_died"]:
            self.phase = self.PH_DEFEAT
        else:
            self.phase = self.PH_ENEMY_ATTACK
        return result

    # ------------------------------------------------------------------ #
    #  Actualización por frame (para el timer del reto)
    # ------------------------------------------------------------------ #
    def update(self, dt):
        if self.phase == self.PH_CHALLENGE:
            self.challenge_time += dt

    def time_remaining(self):
        """Segundos que le quedan al jugador para responder (o 0)."""
        if self.challenge is None or self.phase != self.PH_CHALLENGE:
            return 0.0
        return max(0.0, self.challenge.time_limit - self.challenge_time)
