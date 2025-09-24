# Simulación de Detección de Colisiones 2D

Este proyecto implementa una **simulación en Python con Pygame** para visualizar colisiones entre objetos en 2D.

## Características
- Objetos geométricos: **círculos y rectángulos**.
- **Bounding volumes** visibles en pantalla.
- Dos métodos de detección de colisiones:
  - **Fuerza Bruta (O(n²))**
  - **Broad Phase con AABB**
- Interfaz gráfica:
  - `ESPACIO` → iniciar simulación
  - `C` → cambiar método de detección
  - `P` → volver al menú
  - `ESC` → salir

## Requisitos
- Python 3.10+
- Librería [Pygame](https://www.pygame.org/):
  ```bash
  pip install pygame
