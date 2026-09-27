"""
save_system.py — Guardar y cargar el progreso del jugador
=========================================================

El progreso se guarda en un archivo JSON (save_data.json) en la raíz
del proyecto. JSON es un formato de texto muy simple que se ve así:

    {"highest_level": 3, "high_score": 2450, ...}

Conceptos nuevos para los estudiantes:
- json.load()  → lee el archivo y lo convierte en diccionario de Python
- json.dump()  → hace lo contrario: diccionario → archivo
"""

import json
import os

from . import config

DEFAULT_DATA = {
    "highest_level": 1,     # Nivel más alto desbloqueado (1 a 5)
    "high_score": 0,        # Mejor puntuación histórica
    "last_score": 0,        # Puntuación de la última partida
    "bosses_defeated": 0,   # Cuántos bosses ha vencido en total
    "games_played": 0,      # Partidas iniciadas
}


def load() -> dict:
    """Carga el progreso guardado. Si no existe o está corrupto,
    devuelve los valores por defecto (nunca crashea el juego)."""
    try:
        with open(config.SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Completar con claves que falten (por si la versión cambia)
        merged = DEFAULT_DATA.copy()
        merged.update(data)
        return merged
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return DEFAULT_DATA.copy()


def save(data: dict) -> None:
    """Guarda el progreso. Escritura atómica: primero en un archivo
    temporal y luego renombrar (así un corte de luz no corrompe el save)."""
    tmp_file = config.SAVE_FILE + ".tmp"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, config.SAVE_FILE)   # rename atómico
    except OSError:
        pass  # Si no se puede guardar (disco lleno...), el juego sigue


def reset() -> dict:
    """Borra el progreso y devuelve los datos recién iniciados."""
    try:
        if os.path.exists(config.SAVE_FILE):
            os.remove(config.SAVE_FILE)
    except OSError:
        pass
    return DEFAULT_DATA.copy()


class SaveSystem:
    """Envoltorio orientado a objetos para las funciones de arriba.

    El juego usa esta clase (game.py crea UNA sola: game.save_system).
    """

    def load(self) -> dict:
        return load()

    def save(self, data: dict) -> None:
        save(data)

    def reset(self) -> dict:
        return reset()

    def record_result(self, data: dict, **kwargs) -> dict:
        return record_result(data, **kwargs)


def record_result(data: dict, score: int, level_completed: int,
                  correct: int = 0, wrong: int = 0, max_combo: int = 0,
                  bosses_defeated: int = 0) -> dict:
    """Actualiza los récords al completar un nivel y guarda.

    Args:
        data:            diccionario de guardado actual
        score:           puntuación acumulada del jugador
        level_completed: nivel que acaba de terminar (desbloquea el siguiente)
        correct:         respuestas correctas acumuladas
        wrong:           respuestas incorrectas acumuladas
        max_combo:       combo máximo alcanzado
    """
    data["last_score"] = score
    data["games_played"] = data.get("games_played", 0) + 1
    data["correct_total"] = data.get("correct_total", 0) + correct
    data["wrong_total"] = data.get("wrong_total", 0) + wrong
    data["best_combo"] = max(data.get("best_combo", 0), max_combo)
    data["bosses_defeated"] = data.get("bosses_defeated", 0) + bosses_defeated
    # Completar el nivel L desbloquea L+1 (limitado al último nivel)
    unlocked = min(config.TOTAL_LEVELS, level_completed + 1)
    data["highest_level"] = max(data.get("highest_level", 1), unlocked)
    if score > data.get("high_score", 0):
        data["high_score"] = score
    save(data)
    return data
