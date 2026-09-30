# 🎮 Math Battle

**Math Battle** es un videojuego educativo de combate
estilo RPG retro (pixel art 16-bit) hecho en **Python + Pygame**:
enfrentas a monstruos resolviendo retos de opción múltiple (A, B, C, D).
Responder bien = hechizo de 25 de daño; responder mal = contraataque de
15. ¡Estudiar nunca fue tan peligroso!

> 🎓 Proyecto de ponencia para la **Jornada del Educador Matemático (JEM)**
> — Universidad Pedagógica Nacional. Desarrollado con estudiantes de
> grado noveno.

---

## 🚀 Cómo ejecutar el juego

```bash
# 1. Crear el entorno virtual (solo la primera vez)
python3 -m venv venv

# 2. Instalar las dependencias (solo la primera vez)
./venv/bin/pip install -r requirements.txt

# 3. ¡Jugar!
./venv/bin/python main.py
```

En Windows con Git Bash también funciona `./venv/bin/python main.py`;
con CMD/PowerShell usa `venv\Scripts\python main.py`. El antiguo
`run_game.py` sigue funcionando como alias.

---

## 🕹️ Controles

| Acción | Control |
|--------|---------|
| Moverse por los menús | Mouse (clic) |
| Elegir opción de respuesta | Clic en A/B/C/D o teclas `1` `2` `3` `4` |
| Empezar el turno (ATACAR) | Clic en el botón o `Enter` |
| Abandonar la batalla | `Esc` |

---

## 🧭 El juego

- **5 niveles temáticos**, cada uno con un tema matemático distinto:

| Nivel | Nombre | Tema | Enemigos | Boss (HP) |
|-------|--------|------|----------|-----------|
| 1 | El Bosque de las Sumas | Sumas y restas | Goblin, Esqueleto | Slime Matemático (40) |
| 2 | La Mina de la Multiplicación | ×, ÷ y problemas de lógica | Bruja, Fantasma | Duende Calculador (80) |
| 3 | El Templo de las Fracciones | Fracciones | Demonio Menor, Fénix | Golem de Piedra Rúnica (120) |
| 4 | El Puente Hacia el Caos | Geometría y ecuaciones | Caballero Oscuro, Hidra | Maestro de la Geometría (180) |
| 5 | El Castillo del Caos | Álgebra | Sombra, Dragón Supremo | Archimago del Caos (250) |

- **Combate por turnos de opción múltiple**: cada turno se plantea una
  pregunta con 4 opciones; acertar hace **25 de daño** al enemigo y
  fallar (o agotar el tiempo) recibe **15 de daño**.

- **3 vidas** por partida. Si el héroe cae, se reintenta el nivel.
- **Puntos** por acertar: bonus por **velocidad** y por **combo**
  (racha de respuestas correctas seguidas).
- **El progreso se guarda solo** (archivo `save_data.json`): los niveles
  se desbloquean al completar el anterior, y el récord de puntos queda
  guardado.

---

## 🗂️ Estructura del proyecto

```
Math-battle/
├── main.py                 ← PUNTO DE ENTRADA (ejecuta esto)
├── run_game.py             ← alias histórico de main.py
├── requirements.txt         ← dependencias (pygame)
├── save_data.json           ← tu progreso (se crea solo)
├── src/
│   ├── config.py            ← constantes: dificultad, colores, tiempos
│   ├── game.py              ← loop principal y pila de estados
│   ├── save_system.py       ← guardar/cargar progreso (JSON)
│   ├── states/              ← cada "pantalla" del juego
│   ├── entities/            ← el héroe, los enemigos y sus estadísticas
│   ├── math_engine/         ← 🧠 el corazón educativo: genera los retos
│   ├── combat/              ← lógica de turnos, daño y efectos
│   └── ui/                  ← botones, HUD, sonidos, fondos
├── assets/
│   ├── sprites/             ← pixel art PNG (héroe, enemigos, efectos)
│   ├── backgrounds/         ← fondos de batalla PNG
│   ├── fonts/               ← fuente pixel art
│   └── sounds/              ← sonidos generados (1ª ejecución)
├── tools/
│   ├── pixel.py             ← lienzo de píxel y escalado (Pillow)
│   ├── palettes.py          ← paletas con hue shift y contornos fríos
│   ├── art_hero.py          ← dibujo del héroe (4 animaciones)
│   ├── art_enemies.py       ← dibujo de los 16 enemigos
│   ├── art_backgrounds.py   ← dibujo de los 5 fondos de batalla
│   ├── art_effects.py       ← dibujo de efectos (estrellas)
│   ├── generate_art.py      ← fuente de verdad: escribe y verifica assets/
│   └── generate_sprites.py  ← el comando de siempre (delega en generate_art)
└── tests/                   ← tests automáticos (pytest)
```

---

## 🧪 Ejecutar los tests

```bash
./venv/bin/python -m pytest tests/ -v
```

Los tests verifican que:
- cada generador matemático produce retos con **respuesta correcta**
  (¡incluso resolviendo las ecuaciones!),
- las fracciones aceptan respuestas tipo `11/12`,
- la lógica de combate (daño, combos, timeout) funciona,
- el arte de `assets/` está sincronizado con su generador
  (rutas, tamaños y frames),
- el juego completo arranca y corre frames sin crashear.

---

## 👩‍🎓 Guía para estudiantes: ¡personaliza el juego!

### 1. Cambia los personajes (¡sin tocar el código del juego!)

Los sprites son imágenes PNG en `assets/sprites/`. Hay dos formas de
personalizarlos:

**Opción A — Dibuja tus propios PNG** (recomendada para arte final):
usa **Piskel** (piskel.web.app) o **Lospec**, exporta cada frame como
`frame0.png`, `frame1.png`... y reemplaza los archivos conservando los
nombres. El juego los carga automáticamente:

```
assets/sprites/enemies/slime/idle/frame0.png    ← reemplázalo por tu slime
assets/sprites/hero/attack/frame1.png           ← tu héroe atacando
assets/backgrounds/level1.png                   ← tu bosque (960×540)
```

**Opción B — Edita el dibujo en código** (sin programa de dibujo):
el arte vive en `tools/art_*.py`, escrito con Pillow. Cada personaje es
una función que pinta sobre un lienzo lógico de 32×32 con los colores de
`tools/palettes.py`:

```python
def slime(phase: int = 0) -> Canvas:
    c = Canvas(32, 32)
    c.fill_rect(6, 16, 20, 10, GREEN)   # cuerpo
    c.put(11, 19, WHITE)                # ojo
    ...
    return c
```

Y regeneras todos los PNG con:

```bash
./venv/bin/python tools/generate_sprites.py      # genera y verifica
./venv/bin/python tools/generate_art.py --verify  # solo comprueba
```

> **Nota:** `tools/generate_art.py` es la única fuente de verdad: escribe
> exactamente las rutas y el número de frames que espera el juego, así
> que **los PNG de `assets/` no se editan a mano**. Si hay que cambiar un
> dibujo, se cambia aquí y se vuelve a generar. `tests/test_assets.py`
> avisa si falta un archivo o si el arte quedó desincronizado.

### 2. Crea un enemigo nuevo

1. Dibuja sus frames en `tools/art_enemies.py` y regístralo en el
   diccionario `ENEMIES` de `tools/generate_art.py` (o coloca a mano
   sus PNG en `assets/sprites/enemies/<nombre>/` con las carpetas
   `idle/` y `hurt/`, frames `frame0.png`, ...).
2. Copia una clase de `src/entities/enemies/`, cambia el nombre y las
   estadísticas (`hp`, `attack`). El nombre de la clase en snake_case
   es el nombre de carpeta del sprite (`DarkKnight` → `dark_knight`;
   también puedes fijar `SPRITE_NAME`).
3. Agrégalo a la lista de su nivel en `src/entities/enemies/__init__.py`.

### 3. Cambia la dificultad del juego

Todo está en `src/config.py`: vidas, daño, tiempos por pregunta,
puntos por respuesta... Un solo archivo para ajustarlo todo.

### 4. Agrega un tipo de reto matemático nuevo

Cada módulo de `src/math_engine/` genera retos de un tema
(`operations.py`, `equations.py`, `fractions.py`...). Cada función
generadora **construye primero la respuesta y después la pregunta**,
para garantizar que el resultado siempre sea bonito. ¡Copia el patrón!

---

## 🎨 Notas técnicas

- **Resolución**: 1280×720 (16:9). Los personajes se dibujan con escala
  entera (32×32 → ×5 = 160×160, vecino más próximo) y los fondos se
  generan a 480×270 → ×2 y se reescalan al cargarlos.
- **Sprites y fondos**: imágenes PNG en `assets/`. Se generan con
  Pillow desde `tools/art_*.py` (`tools/generate_art.py` los escribe y
  verifica) y se pueden reemplazar por pixel art propio sin tocar el
  código del juego. Escala entera con `Image.NEAREST`: los personajes
  32×32 → ×5 (160×160), los fondos 480×270 → ×2 (960×540) y se
  reescalan a 1280×720 al cargarlos.
- **Sonidos y música**: se generan matemáticamente (ondas senoidales) y
  se guardan como `.wav` en `assets/sounds/` la primera vez que se
  ejecuta el juego.
- **Fuente**: [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P)
  (Google Fonts, licencia OFL), incluida en `assets/fonts/`.
- **Progreso**: JSON con escritura atómica (nunca se corrompe el guardado).

---

## 👥 Créditos

- **Estudiantes**: *[ Estudiante 1 ]* y *[ Estudiante 2 ]* — grado noveno
- **Docente orientador**: *[ Nombre del docente ]*
- **Institución**: *[ Nombre de la institución ]*
- **Ponencia**: Jornada del Educador Matemático (JEM) — Universidad Pedagógica Nacional

> ✏️ *Edita esta sección con los nombres reales del equipo. Los mismos
> datos aparecen en la pantalla de CRÉDITOS del juego:
> `src/states/credits_state.py` → lista `LINES`.*
