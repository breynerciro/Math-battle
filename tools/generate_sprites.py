"""generate_sprites.py — Genera TODOS los recursos visuales del juego.

    ./venv/bin/python tools/generate_sprites.py            # genera
    ./venv/bin/python tools/generate_sprites.py --verify   # solo comprueba

El arte ya no se dibuja aquí: vive en el paquete `tools/art_*.py`, escrito
con Pillow. Este archivo se conserva porque es el comando que todo el mundo
se sabe, pero delega en `tools.generate_art`, que es la única fuente de
verdad.

Antes este módulo pintaba los sprites a mano con `tools/sprite_data.py` y
ESCRIBÍA sobre `assets/`. Eso era un peligro: quien lo ejecutara sin saber
lo que había debajo se llevaría por delante el rediseño. Ahora generar y
dibujar son la misma operación, así que no puede haber dos versiones
distintas del arte.

Los PNG escritos son los mismos archivos que el juego carga:

    assets/sprites/hero/<anim>/frame<N>.png
    assets/sprites/enemies/<slug>/<anim>/frame<N>.png
    assets/sprites/effects/star/frame<N>.png
    assets/backgrounds/level<N>.png
"""

import os
import sys
from pathlib import Path

# SDL "dummy": no hace falta ventana para generar imágenes
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import generate_art  # noqa: E402  (necesita ROOT en sys.path)


def main() -> int:
    return generate_art.main()


if __name__ == "__main__":
    raise SystemExit(main())
