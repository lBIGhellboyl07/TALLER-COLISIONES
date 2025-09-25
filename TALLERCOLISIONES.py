import pygame
import math
import sys
import random
import matplotlib.pyplot as plt
import numpy as np

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Detección de colisiones 2D")

# Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Materiales, colores y propiedades físicas (elasticidad y densidad)
PROPIEDADES_MATERIALES = {
    "hierro": {"color": BLUE, "elasticidad": 0.5, "densidad": 7.87},
    "madera": {"color": (139, 69, 19), "elasticidad": 0.3, "densidad": 0.7},
    "goma": {"color": (100, 100, 100), "elasticidad": 0.8, "densidad": 1.2},
    "vidrio": {"color": CYAN, "elasticidad": 0.2, "densidad": 2.5},
    "oro": {"color": YELLOW, "elasticidad": 0.9, "densidad": 19.3}
}

class Objeto:
    def __init__(self, x, y, vx, vy, material):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.colisionando = False
        self.material = material
        self.color = PROPIEDADES_MATERIALES[material]["color"]
        self.elasticidad = PROPIEDADES_MATERIALES[material]["elasticidad"]
        self.densidad = PROPIEDADES_MATERIALES[material]["densidad"]
        self.activo = True

    def mover(self):
        if self.activo:
            self.x += self.vx
            self.y += self.vy
            if self.x < 0 or self.x > WIDTH:
                self.vx *= -1
            if self.y < 0 or self.y > HEIGHT:
                self.vy *= -1
        
    def reaparecer(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.vx = random.choice([-5, -4, -3, 3, 4, 5])
        self.vy = random.choice([-5, -4, -3, 3, 4, 5])
        self.activo = True

class Circulo(Objeto):
    def __init__(self, x, y, radio, vx, vy, material):
        super().__init__(x, y, vx, vy, material)
        self.radio = radio
        self.masa = math.pi * (self.radio**2) * self.densidad

    def dibujar(self):
        if self.activo:
            if self.colisionando:
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radio)
            else:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radio, 3)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radio, 1)

    def aabb(self):
        if self.activo:
            return pygame.Rect(self.x - self.radio, self.y - self.radio, 2*self.radio, 2*self.radio)
        return pygame.Rect(0, 0, 0, 0)

class Rectangulo(Objeto):
    def __init__(self, x, y, w, h, vx, vy, material):
        super().__init__(x, y, vx, vy, material)
        self.w = w
        self.h = h
        self.masa = self.w * self.h * self.densidad

    def dibujar(self):
        if self.activo:
            rect = pygame.Rect(self.x, self.y, self.w, self.h)
            if self.colisionando:
                pygame.draw.rect(screen, RED, rect)
            else:
                pygame.draw.rect(screen, self.color, rect, 3)
            pygame.draw.rect(screen, WHITE, rect, 1)

    def aabb(self):
        if self.activo:
            return pygame.Rect(self.x, self.y, self.w, self.h)
        return pygame.Rect(0, 0, 0, 0)

# --- Funciones de colisión ---
def colision_circulos(c1, c2):
    if c1.activo and c2.activo:
        dx = c1.x - c2.x
        dy = c1.y - c2.y
        return math.hypot(dx, dy) < (c1.radio + c2.radio)
    return False

def colision_rectangulos(r1, r2):
    if r1.activo and r2.activo:
        return r1.aabb().colliderect(r2.aabb())
    return False

def colision_circulo_rectangulo(c, r):
    if c.activo and r.activo:
        rect = r.aabb()
        cx = max(rect.left, min(c.x, rect.right))
        cy = max(rect.top, min(c.y, rect.bottom))
        dx = c.x - cx
        dy = c.y - cy
        return dx*dx + dy*dy < c.radio*c.radio
    return False

# --- Funciones de colisión con respuesta física ---
def respuesta_colision_circulos(c1, c2):
    # Vector de la distancia entre los centros
    v_normal = pygame.Vector2(c2.x - c1.x, c2.y - c1.y)
    dist = v_normal.length()
    
    # Normalizar el vector y calcular la penetración
    v_normal.normalize_ip()
    penetracion = c1.radio + c2.radio - dist
    
    # Separar los objetos para evitar que se queden atascados
    c1.x -= v_normal.x * penetracion / 2
    c1.y -= v_normal.y * penetracion / 2
    c2.x += v_normal.x * penetracion / 2
    c2.y += v_normal.y * penetracion / 2
    
    # Velocidad relativa en el eje normal
    v_relativa = pygame.Vector2(c2.vx - c1.vx, c2.vy - c1.vy)
    v_rel_normal = v_relativa.dot(v_normal)
    
    if v_rel_normal > 0:
        return # Objetos alejándose, no hay colisión que manejar
    
    # Coeficiente de restitución promedio
    e = min(c1.elasticidad, c2.elasticidad)
    
    # Impulso de colisión
    j = -(1 + e) * v_rel_normal / (1/c1.masa + 1/c2.masa)
    
    # Cambio en las velocidades
    impulse_vector = v_normal * j
    c1.vx -= impulse_vector.x / c1.masa
    c1.vy -= impulse_vector.y / c1.masa
    c2.vx += impulse_vector.x / c2.masa
    c2.vy += impulse_vector.y / c2.masa

def respuesta_colision_rectangulos(r1, r2):
    # Lógica simplificada de rebote para rectángulos
    rect1 = r1.aabb()
    rect2 = r2.aabb()
    
    overlap_x = min(rect1.right, rect2.right) - max(rect1.left, rect2.left)
    overlap_y = min(rect1.bottom, rect2.bottom) - max(rect1.top, rect2.top)
    
    # El eje con menor superposición es el eje de la colisión
    if overlap_x < overlap_y:
        # Colisión en el eje X
        e = min(r1.elasticidad, r2.elasticidad)
        if (r1.vx > 0 and r2.vx < 0) or (r1.vx < 0 and r2.vx > 0):
            v1_new = (r1.vx * (r1.masa - e * r2.masa) + 2 * r2.masa * r2.vx) / (r1.masa + r2.masa)
            v2_new = (r2.vx * (r2.masa - e * r1.masa) + 2 * r1.masa * r1.vx) / (r1.masa + r2.masa)
            r1.vx = v1_new
            r2.vx = v2_new
    else:
        # Colisión en el eje Y
        e = min(r1.elasticidad, r2.elasticidad)
        if (r1.vy > 0 and r2.vy < 0) or (r1.vy < 0 and r2.vy > 0):
            v1_new = (r1.vy * (r1.masa - e * r2.masa) + 2 * r2.masa * r2.vy) / (r1.masa + r2.masa)
            v2_new = (r2.vy * (r2.masa - e * r1.masa) + 2 * r1.masa * r1.vy) / (r1.masa + r2.masa)
            r1.vy = v1_new
            r2.vy = v2_new

def respuesta_colision_circulo_rectangulo(c, r):
    # Lógica de rebote simplificada
    r.vx *= -1 * r.elasticidad
    r.vy *= -1 * r.elasticidad
    c.vx *= -1 * c.elasticidad
    c.vy *= -1 * c.elasticidad

# PARÁMETROS DE COLISIÓN
def fuerza_bruta(objetos):
    for i in range(len(objetos)):
        for j in range(i + 1, len(objetos)):
            o1, o2 = objetos[i], objetos[j]
            colision = False
            if isinstance(o1, Circulo) and isinstance(o2, Circulo):
                if colision_circulos(o1, o2):
                    respuesta_colision_circulos(o1, o2)
                    colision = True
            elif isinstance(o1, Rectangulo) and isinstance(o2, Rectangulo):
                if colision_rectangulos(o1, o2):
                    respuesta_colision_rectangulos(o1, o2)
                    colision = True
            else:
                if isinstance(o1, Circulo) and isinstance(o2, Rectangulo):
                    if colision_circulo_rectangulo(o1, o2):
                        respuesta_colision_circulo_rectangulo(o1, o2)
                        colision = True
                elif isinstance(o2, Circulo) and isinstance(o1, Rectangulo):
                    if colision_circulo_rectangulo(o2, o1):
                        respuesta_colision_circulo_rectangulo(o2, o1)
                        colision = True
            
            if colision:
                o1.colisionando = o2.colisionando = True
                if o1.material == "vidrio":
                    o1.activo = False
                if o2.material == "vidrio":
                    o2.activo = False

def broad_phase_aabb(objetos, cell_size=150):
    grid = {}
    for obj in objetos:
        if obj.activo:
            rect = obj.aabb()
            cx, cy = rect.x // cell_size, rect.y // cell_size
            grid.setdefault((cx, cy), []).append(obj)

    for cell_objs in grid.values():
        if len(cell_objs) > 1:
            for i in range(len(cell_objs)):
                for j in range(i + 1, len(cell_objs)):
                    o1, o2 = cell_objs[i], cell_objs[j]
                    colision = False
                    if isinstance(o1, Circulo) and isinstance(o2, Circulo):
                        if colision_circulos(o1, o2):
                            respuesta_colision_circulos(o1, o2)
                            colision = True
                    elif isinstance(o1, Rectangulo) and isinstance(o2, Rectangulo):
                        if colision_rectangulos(o1, o2):
                            respuesta_colision_rectangulos(o1, o2)
                            colision = True
                    else:
                        if isinstance(o1, Circulo) and isinstance(o2, Rectangulo):
                            if colision_circulo_rectangulo(o1, o2):
                                respuesta_colision_circulo_rectangulo(o1, o2)
                                colision = True
                        elif isinstance(o2, Circulo) and isinstance(o1, Rectangulo):
                            if colision_circulo_rectangulo(o2, o1):
                                respuesta_colision_circulo_rectangulo(o2, o1)
                                colision = True
                    
                    if colision:
                        o1.colisionando = o2.colisionando = True
                        if o1.material == "vidrio":
                            o1.activo = False
                        if o2.material == "vidrio":
                            o2.activo = False

# --- Gráfica de comportamiento ---
def graficar_comportamiento(objetos):
    colisiones_por_material = {mat: 0 for mat in PROPIEDADES_MATERIALES.keys()}
    activos_por_material = {mat: 0 for mat in PROPIEDADES_MATERIALES.keys()}

    for obj in objetos:
        if obj.activo:
            activos_por_material[obj.material] += 1
        if obj.colisionando:
            colisiones_por_material[obj.material] += 1
    
    materiales = list(PROPIEDADES_MATERIALES.keys())
    
    activos = [activos_por_material[mat] for mat in materiales]
    colisiones = [colisiones_por_material[mat] for mat in materiales]
    
    x = np.arange(len(materiales))
    width = 0.35

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, activos, width, label='Activos', color='blue')
    rects2 = ax.bar(x + width/2, colisiones, width, label='Colisionando', color='red')

    ax.set_ylabel('Cantidad de objetos')
    ax.set_title('Comportamiento de objetos por material')
    ax.set_xticks(x)
    ax.set_xticklabels([mat.capitalize() for mat in materiales])
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    fig.tight_layout()
    plt.show()

# ------------------ Escenas ------------------

def menu():
    font = pygame.font.SysFont("Arial", 48)
    small_font = pygame.font.SysFont("Arial", 28)
    running = True
    while running:
        screen.fill(BLACK)
        title = font.render("Simulación de Colisiones 2D", True, WHITE)
        start = small_font.render("ESPACIO - Iniciar simulación", True, WHITE)
        quit_msg = small_font.render("ESC - Salir", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
        screen.blit(start, (WIDTH // 2 - start.get_width() // 2, 320))
        screen.blit(quit_msg, (WIDTH // 2 - quit_msg.get_width() // 2, 360))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_SPACE:
                    simulacion()

def simulacion():
    objetos = [
        Circulo(200, 200, 40, 3, 2, "hierro"),
        Circulo(500, 400, 30, -4, 2, "goma"),
        Rectangulo(300, 100, 100, 70, 3, 2, "madera"),
        Rectangulo(120, 350, 120, 80, -3, -2, "vidrio"),
        Circulo(650, 150, 25, -2, 4, "oro"),
        Rectangulo(50, 500, 80, 50, 5, -1, "hierro"),
        Circulo(700, 550, 50, -3, -3, "madera"),
        Rectangulo(450, 250, 90, 60, 2, -4, "goma"),
        Rectangulo(700, 50, 70, 40, -4, 4, "vidrio")
    ]

    clock = pygame.time.Clock()
    modo = "fuerza_bruta"
    running = True

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_c:
                    modo = "aabb" if modo == "fuerza_bruta" else "fuerza_bruta"
                elif event.key == pygame.K_p:
                    running = False
                elif event.key == pygame.K_g:
                    graficar_comportamiento(objetos)

        for o in objetos:
            o.colisionando = False
            o.mover()
            if not o.activo:
                o.reaparecer()

        if modo == "fuerza_bruta":
            fuerza_bruta(objetos)
            titulo = "Modo: Fuerza Bruta (O(n²)) - C para cambiar"
        else:
            broad_phase_aabb(objetos)
            titulo = "Modo: AABB Broad Phase - C para cambiar"

        for o in objetos:
            o.dibujar()

        font = pygame.font.SysFont("Arial", 24)
        legend_font = pygame.font.SysFont("Arial", 18)
        text = font.render(titulo, True, WHITE)
        info = font.render("P - Regresar al menú | ESC - Salir | G - Ver Gráfica", True, WHITE)
        screen.blit(text, (20, 20))
        screen.blit(info, (20, 50))

        legend_y_start = 100
        pygame.draw.rect(screen, WHITE, (WIDTH - 150, legend_y_start - 5, 140, len(PROPIEDADES_MATERIALES) * 20 + 10), 2)
        legend_title = legend_font.render("Materiales", True, WHITE)
        screen.blit(legend_title, (WIDTH - 145, legend_y_start))
        
        y_offset = legend_y_start + 25
        for material, props in PROPIEDADES_MATERIALES.items():
            pygame.draw.rect(screen, props["color"], (WIDTH - 140, y_offset, 15, 15))
            mat_text = legend_font.render(f"{material.capitalize()}", True, WHITE)
            screen.blit(mat_text, (WIDTH - 120, y_offset))
            y_offset += 20

        pygame.display.flip()
        clock.tick(60)

# ------------------ Iniciar ------------------
menu()





