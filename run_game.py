#!/usr/bin/env python3
"""
run_game.py — Punto de entrada de Math Battle
=============================================

Ejecutar desde la carpeta raíz del proyecto:

    python run_game.py

(o con el entorno virtual:  ./venv/bin/python run_game.py)
"""

import os
import sys

# Asegura que la carpeta raíz esté en el PATH para poder importar `src`
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    try:
        from src.game import Game
    except ImportError as e:
        print("No se pudo importar Pygame. Instala las dependencias con:")
        print("    pip install -r requirements.txt")
        print(f"Detalle técnico: {e}")
        sys.exit(1)

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
