# 🎮 Math Battle

**Math Battle** es un videojuego educativo de combate estilo RPG retro
(pixel art 16-bit) hecho en **Python + Pygame**: enfrentas a monstruos
resolviendo retos matemáticos. Responder bien = atacar; responder mal =
recibir un golpe. ¡Estudiar nunca fue tan peligroso!

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
./venv/bin/python run_game.py
```

En Windows con Git Bash también funciona `./venv/bin/python run_game.py`;
con CMD/PowerShell usa `venv\Scripts\python run_game.py`.

---

## 🕹️ Controles

| Acción | Control |
|--------|---------|
| Moverse por los menús | Mouse (clic) |
| Escribir la respuesta | Teclado (números, `-`, `/`, `.`) |
| Enviar respuesta | `Enter` |
| Borrar | `Backspace` |
| Limpiar la respuesta | `Esc` (en el campo de texto) |
| Abandonar la batalla | `Esc` (en la batalla) |

---

## 🧭 El juego

- **5 niveles temáticos**, cada uno con un tema matemático distinto:

| Nivel | Nombre | Tema | Enemigos | Boss |
|-------|--------|------|----------|------|
| 1 | Bosque Aritmético | Operaciones básicas | Slime, Goblin | Dragón Básico |
| 2 | Cueva de Ecuaciones | Ecuaciones lineales | Esqueleto, Bruja | Gólem de Piedra |
| 3 | Torre de Potencias | Potencias y raíces | Fantasma, Demonio | Fénix |
| 4 | Pantano de Fracciones | Fracciones | Caballero Oscuro, Mago | Hidra de 3 Cabezas |
| 5 | Fortaleza Geométrica | Geometría | Sombra, Archimago | Dragón Supremo |

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
├── run_game.py              ← PUNTO DE ENTRADA (ejecuta esto)
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
│   ├── sprite_data.py       ← datos fuente del pixel art (cuadrículas)
│   └── generate_sprites.py  ← regenera los PNG de assets/
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

**Opción B — Edita las cuadrículas de letras** (sin programa de dibujo):
abre `tools/sprite_data.py`. Cada **letra** es un píxel de color de la
paleta y cada punto `.` es transparencia:

```python
SLIME_SPRITES = {
    "idle": [
        [
            "....GGGG....",   # G = verde
            "..GGGGGGGG..",
            ".GGWGGGGWGG.",   # W = blanco (ojos)
            ".GGKGGGGKGG.",   # K = negro (pupila)
            "GGGGGGGGGGGG",
        ],
    ],
}
```

Y regeneras todos los PNG con:

```bash
./venv/bin/python tools/generate_sprites.py
```

### 2. Crea un enemigo nuevo

1. Crea sus sprites en `assets/sprites/enemies/<nombre>/` con las
   carpetas `idle/` y `hurt/` (frames `frame0.png`, ...).
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

- **Resolución**: 960×540 (escala 2× de 480×270 para pixel art nítido).
- **Sprites y fondos**: imágenes PNG en `assets/`. Se generan con
  `tools/generate_sprites.py` (a partir de cuadrículas de letras en
  `tools/sprite_data.py`) y se pueden reemplazar por pixel art propio
  sin tocar el código del juego.
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
