"""
sound_manager.py — Sonidos y música (generados por código)
==========================================================

No hay archivos de audio en el proyecto: TODOS los sonidos se generan
matemáticamente (ondas senoidales con envolvente) y se cachean en
assets/sounds/ como archivos .wav la primera vez.

Concepto nuevo: el SONIDO es una onda. Si la onda vibra rápido (más Hz),
suena agudo; si vibra lento, suena grave. ¡Las matemáticas están en todo!
"""

import math
import os
import random
import struct
import wave

import pygame

from .. import config

SAMPLE_RATE = 22050


class SoundManager:
    """Carga (o genera) los efectos y controla la música de fondo."""

    _generated = False       # ¿ya generamos los .wav en esta sesión?

    def __init__(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
            except pygame.error:
                return          # sin audio disponible (ej: servidor sin tarjeta)
        self.sounds = {}
        self.current_music = None
        self._ensure_sounds()

    # ------------------------------------------------------------------ #
    #  Generación de ondas
    # ------------------------------------------------------------------ #
    @staticmethod
    def _synth_tone(freqs, duration, volume=0.5, decay=True, noise=False):
        """Genera una onda (mezcla de senos) como lista de enteros 16-bit.

        Args:
            freqs:   lista de frecuencias (acorde si hay varias)
            duration: duración en segundos
            volume:  volumen 0..1
            decay:   si True, el sonido se apaga suavemente (envolvente)
            noise:   si True, añade ruido blanco (bueno para golpes)
        """
        n_samples = int(SAMPLE_RATE * duration)
        samples = []
        for i in range(n_samples):
            t = i / SAMPLE_RATE
            value = sum(math.sin(2 * math.pi * f * t) for f in freqs)
            value /= len(freqs)
            if noise:
                value += random.uniform(-0.3, 0.3)
            if decay:
                envelope = (1.0 - i / n_samples) ** 2     # caída cuadrática
            else:
                envelope = 1.0
            samples.append(int(max(-1, min(1, value * envelope * volume)) * 32767))
        return samples

    @classmethod
    def _save_wav(cls, path, samples):
        """Guarda la lista de muestras como archivo WAV estéreo."""
        with wave.open(path, "w") as f:
            f.setnchannels(2)
            f.setsampwidth(2)                     # 16 bits
            f.setframerate(SAMPLE_RATE)
            frames = b"".join(struct.pack("<hh", s, s) for s in samples)
            f.writeframes(frames)

    @classmethod
    def _ensure_sounds(cls):
        """Genera los .wav la primera vez (si no existen ya)."""
        if cls._generated:
            return
        cls._generated = True
        sfx_dir = os.path.join(config.SOUNDS_DIR, "sfx")
        music_dir = os.path.join(config.SOUNDS_DIR, "music")
        os.makedirs(sfx_dir, exist_ok=True)
        os.makedirs(music_dir, exist_ok=True)

        recipes = {
            # sonido: (frecuencias, duración, volumen, ruido)
            "attack.wav": ([880, 1320], 0.18, 0.5, False),
            "hit.wav": ([180, 240], 0.22, 0.6, True),
            "correct.wav": ([660, 880, 1320], 0.25, 0.5, False),
            "wrong.wav": ([200, 150], 0.35, 0.55, False),
            "victory.wav": ([523, 659, 784, 1047], 0.8, 0.5, False),
            "defeat.wav": ([330, 262, 196], 0.9, 0.5, False),
            "click.wav": ([1200], 0.06, 0.4, False),
            "timeout.wav": ([150, 100], 0.5, 0.5, False),
        }
        for filename, (freqs, dur, vol, noise) in recipes.items():
            path = os.path.join(sfx_dir, filename)
            if not os.path.exists(path):
                cls._save_wav(path, cls._synth_tone(freqs, dur, vol, noise=noise))

        # Música: bucles cortos de arpegios por "zona" (menú/niveles)
        melodies = {
            "menu.wav":  [523, 659, 784, 659],       # Do Mi Sol Mi
            "battle.wav": [440, 523, 659, 523],       # La Do Mi Do (más tenso)
            "boss.wav":  [392, 415, 392, 415],        # tintineo inquietante
        }
        for filename, notes in melodies.items():
            path = os.path.join(music_dir, filename)
            if not os.path.exists(path):
                samples = []
                for note in notes:
                    samples += cls._synth_tone([note, note * 1.5], 0.45, 0.35)
                cls._save_wav(path, samples)

    # ------------------------------------------------------------------ #
    #  Reproducción
    # ------------------------------------------------------------------ #
    def play(self, name):
        """Reproduce un efecto por nombre: 'click', 'hit', 'correct'..."""
        path = os.path.join(config.SOUNDS_DIR, "sfx", f"{name}.wav")
        try:
            if path not in self.sounds:
                self.sounds[path] = pygame.mixer.Sound(path)
            self.sounds[path].play()
        except (pygame.error, KeyError):
            pass    # sin audio, el juego sigue

    def play_music(self, name, loop=True):
        """Reproduce música de fondo: 'menu', 'battle' o 'boss'."""
        if self.current_music == name:
            return
        path = os.path.join(config.SOUNDS_DIR, "music", f"{name}.wav")
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1 if loop else 0)
            self.current_music = name
        except (pygame.error, FileNotFoundError):
            pass

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
            self.current_music = None
        except pygame.error:
            pass
