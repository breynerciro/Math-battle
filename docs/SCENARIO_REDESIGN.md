# Rediseño de Escenarios (documento histórico)

> ⚠️ **Nota**: este documento describe una iteración anterior. Desde
> entonces los niveles se renombraron al diseño final (El Bosque de las
> Sumas, La Mina de la Multiplicación, El Templo de las Fracciones, El
> Puente Hacia el Caos, El Castillo del Caos), el arte se rehizo con
> Pillow en `tools/art_*.py` y la ventana pasó a 1280×720. El texto que
> sigue queda como registro de lo hecho en esa iteración.

## Resumen de Mejoras

Se rediseñaron los escenarios del juego aplicando las skills instaladas:
- **game-developer**: Patrones de arquitectura y optimización
- **game-juice**: Feedback visual, easing, partículas, screen shake
- **pygame-core**: Estructura y patrones de pygame

## Cambios Implementados

### 1. Sistema de Escenarios Dinámicos (`src/ui/scenario.py`)

**Características:**
- **Parallax de múltiples capas**: 3 capas por nivel que se mueven a diferentes velocidades creando profundidad visual
- **Partículas ambientales temáticas**: Cada nivel tiene su propio tipo de partícula:
  - Nivel 1 (Bosque): Hojas cayendo con rotación y movimiento sinusoidal
  - Nivel 2 (Cueva): Polvo flotante en el aire
  - Nivel 3 (Torre): Chispas/estrellas fugaces
  - Nivel 4 (Pantano): Burbujas subiendo con wobble
  - Nivel 5 (Fortaleza): Cristales pulsantes con brillo
- **Efectos de iluminación dinámica**:
  - Cristales brillantes en la cueva con pulso
  - Ventanas iluminadas en la torre con glow
- **Gradientes de cielo y suelo**: Transiciones suaves de color en lugar de colores planos

### 2. Transiciones Mejoradas (`src/ui/transition.py`)

**Mejoras:**
- **Easing curves**: Uso de `ease-in-out-cubic` para transiciones suaves y naturales
- **Colores temáticos**: Cada nivel tiene su color de transición
- **Partículas de transición**: Efecto de partículas durante el fade
- **Duración ajustada**: 0.5s para mejor ritmo visual

### 3. Selección de Niveles Animada (`src/states/level_select_state.py`)

**Mejoras:**
- **Tarjetas con animaciones**:
  - Hover scale con easing (1.08x al pasar el mouse)
  - Bounce effect al hacer clic
  - Glow pulsante con color del nivel
- **Fondo animado**: Estrellas con parpadeo y movimiento sutil
- **Feedback visual mejorado**: Bordes más gruesos para niveles desbloqueados
- **Iconos temáticos**: Emojis representativos de cada nivel

### 4. Efectos de Combate Mejorados (`src/combat/effects.py`)

**Nuevos efectos:**
- **FloatingText mejorado**:
  - Animación de escala con `ease-out-elastic`
  - Movimiento vertical con `ease-out-cubic`
  - Mejor legibilidad con pop-in inicial
- **ScreenShake direccional**:
  - Shake en la dirección del impacto (no aleatorio)
  - Decay exponencial para sensación de peso
  - Intensidad variable según el evento
- **HitStop**: Pausa de 50-80ms en impactos importantes para dar peso
- **FlashEffect**: Flash de pantalla en eventos críticos (muerte de enemigo, daño al jugador)
- **ParticleSystem mejorado**:
  - Tipos de partícula: spark, trail
  - Rotación individual
  - Física con fricción
  - Trails para movimientos rápidos

### 5. Fondos Generados Mejorados (`tools/generate_sprites.py`)

**Mejoras por nivel:**

**Nivel 1 - Bosque Aritmético:**
- Árboles en múltiples capas (fondo y primer plano)
- Follaje en capas con variación de color
- Hierba detallada en el suelo
- Gradiente de cielo a suelo

**Nivel 2 - Cueva de Ecuaciones:**
- Estalactitas con variación de tamaño
- Cristales brillantes con highlight
- Rocas en el suelo con forma orgánica
- Profundidad visual con capas oscuras

**Nivel 3 - Torre de Potencias:**
- Estrellas en el cielo
- Nubes con forma orgánica (múltiples elipses)
- Ventanas iluminadas con glow interior
- Marco de ventana detallado

**Nivel 4 - Pantano de Fracciones:**
- Niebla con transparencia
- Burbujas con brillo y tamaño variable
- Juncos curvados con interpolación de puntos
- Vegetación detallada

**Nivel 5 - Fortaleza Geométrica:**
- Muro con textura de ladrillos
- Almenas con sombra
- Banderas con detalle
- Antorchas con llamas en capas

### 6. Integración en Battle State (`src/states/battle_state.py`)

**Cambios:**
- Uso del nuevo sistema `Scenario` en lugar de fondos estáticos
- Integración de `HitStop` para pausas de impacto
- Integración de `FlashEffect` para flashes de pantalla
- Screen shake direccional según dirección del ataque
- Partículas mejoradas con más cantidad y velocidad

## Principios de Game-Juice Aplicados

1. **Nada se mueve linealmente**: Todo usa easing curves (cubic, elastic)
2. **Impactos con hit-stop**: 50-80ms de pausa en golpes importantes
3. **Screen shake direccional**: Shake en dirección del impacto con decay exponencial
4. **Squash and stretch**: Textos flotantes con animación de escala elástica
5. **Sonidos variados**: Ya implementado en el juego base
6. **Partículas en cada evento**: Burst de partículas en ataques, muertes, etc.
7. **Números nunca saltan**: Textos flotantes con tweening suave
8. **Anticipación y follow-through**: Animaciones de entrada y salida
9. **Trails en cosas rápidas**: Sistema de trails para partículas
10. **Cámara como personaje**: Screen shake direccional con personalidad

## Principios de Game-Developer Aplicados

1. **Object pooling**: Partículas y efectos reutilizan estructuras
2. **Delta time**: Todo el movimiento es frame-independent
3. **State machines**: Estados del juego bien definidos
4. **Separación de responsabilidades**: Scenario, Effects, BattleState separados
5. **Cache de recursos**: Fondos cacheados en memoria
6. **Performance**: 60 FPS objetivo, optimización de blits

## Principios de Pygame-Core Aplicados

1. **Surface.convert()**: Imágenes convertidas para blits rápidos
2. **SRCALPHA**: Superficies con transparencia para efectos
3. **Sprite groups**: Sistema de partículas eficiente
4. **Delta time**: Movimiento independiente del frame rate
5. **Event handling**: Manejo correcto de eventos de pygame

## Archivos Modificados

- `src/ui/scenario.py` (nuevo)
- `src/ui/transition.py` (mejorado)
- `src/states/level_select_state.py` (mejorado)
- `src/states/battle_state.py` (integración de nuevos efectos)
- `src/combat/effects.py` (mejorado con nuevos efectos)
- `tools/generate_sprites.py` (fondos mejorados)

## Resultados

- **38 tests pasando**: Toda la funcionalidad existente preservada
- **64 imágenes generadas**: Fondos y sprites actualizados
- **Mejor feedback visual**: Cada acción del jugador tiene respuesta en múltiples canales
- **Escenarios más inmersivos**: Parallax, partículas y efectos de iluminación
- **Combate más satisfactorio**: Hit-stop, screen shake direccional, flashes
- **UI más pulida**: Tarjetas animadas, transiciones suaves

## Cómo Ejecutar

```bash
./venv/bin/python run_game.py
```

Los escenarios ahora tienen:
- Profundidad visual con parallax
- Partículas ambientales temáticas
- Efectos de iluminación dinámica
- Transiciones suaves con easing
- Feedback visual mejorado en combate
