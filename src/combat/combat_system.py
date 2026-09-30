"""
combat_system.py — La lógica del combate
========================================

Coordina el flujo de cada turno (ver el diagrama del plan):

1. El jugador elige ATACAR → se pide un reto matemático con 4 opciones.
2. Si elige la opción CORRECTA → lanza su hechizo y hace daño FIJO al
   enemigo (HERO_DAMAGE = 25).
3. Si FALLA o se agota el tiempo → el enemigo contraataca con daño
   FIJO (COUNTER_DAMAGE = 15).
4. Cuando el enemigo muere → el jugador recupera algo de vida y pasa
   al siguiente enemigo del nivel (o al boss).

Esta clase SOLO calcula: no dibuja nada (eso lo hacen los estados).
"""

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
        """Evalúa una respuesta escrita (compatibilidad con tests/herramientas)."""
        timed_out = self.challenge_time >= self.challenge.time_limit
        correct = (not timed_out) and self.challenge.check_answer(user_answer)
        return self._finish(correct, timed_out)

    def submit_option(self, index):
        """Evalúa la OPCIÓN elegida por el jugador (0=A, 1=B, 2=C, 3=D).

        index puede ser None (se agotó el tiempo y no se eligió nada).

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
        timed_out = (index is None or
                     self.challenge_time >= self.challenge.time_limit)
        correct = (not timed_out) and self.challenge.check_option(index)
        return self._finish(correct, timed_out)

    def _finish(self, correct, timed_out):
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
        """El héroe lanza su hechizo: daño FIJO (respuesta correcta)."""
        damage = config.HERO_DAMAGE

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
        """El enemigo contraataca (por error o por tiempo agotado).

        Daño FIJO igual que el del héroe: así las matemáticas, y no la
        suerte, deciden cuánto dura el combate.
        """
        self.player.register_wrong()
        damage = config.COUNTER_DAMAGE
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
