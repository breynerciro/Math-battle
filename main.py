#!/usr/bin/env python3
"""
main.py — Math Battle
======================================

Punto de entrada del juego. Ejecuta desde la raíz del proyecto:

    ./venv/bin/python main.py

(o en Windows: venv\\Scripts\\python main.py)
"""

import os
import sys

# La raíz del proyecto en el PATH para poder importar `src`
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Crea el juego y arranca el bucle principal hasta que se cierre."""
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
