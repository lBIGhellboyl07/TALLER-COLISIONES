import pygame
import math
import sys
import random

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

# Materiales y sus colores
MATERIALES = {
    "hierro": BLUE,
    "madera": (139, 69, 19),
    "goma": (100, 100, 100),
    "vidrio": CYAN,
    "oro": YELLOW
}

class Objeto:
    def __init__(self, x, y, vx, vy, material):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.colisionando = False
        self.material = material
        self.color = MATERIALES[material]
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
        return pygame.Rect(0, 0, 0, 0) # Devuelve un rectangulo de tamaño 0 si no esta activo

class Rectangulo(Objeto):
    def __init__(self, x, y, w, h, vx, vy, material):
        super().__init__(x, y, vx, vy, material)
        self.w = w
        self.h = h

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
        return pygame.Rect(0, 0, 0, 0) # Devuelve un rectangulo de tamaño 0 si no esta activo

# PARÁMETROS DE COLISIÓN
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

def fuerza_bruta(objetos):
    for i in range(len(objetos)):
        for j in range(i + 1, len(objetos)):
            o1, o2 = objetos[i], objetos[j]
            colision = False
            if isinstance(o1, Circulo) and isinstance(o2, Circulo):
                if colision_circulos(o1, o2):
                    colision = True
            elif isinstance(o1, Rectangulo) and isinstance(o2, Rectangulo):
                if colision_rectangulos(o1, o2):
                    colision = True
            else:
                if isinstance(o1, Circulo) and isinstance(o2, Rectangulo):
                    if colision_circulo_rectangulo(o1, o2):
                        colision = True
                elif isinstance(o2, Circulo) and isinstance(o1, Rectangulo):
                    if colision_circulo_rectangulo(o2, o1):
                        colision = True
            
            if colision:
                o1.colisionando = o2.colisionando = True
                # Manejar colision de vidrio
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
                            colision = True
                    elif isinstance(o1, Rectangulo) and isinstance(o2, Rectangulo):
                        if colision_rectangulos(o1, o2):
                            colision = True
                    else:
                        if isinstance(o1, Circulo) and isinstance(o2, Rectangulo):
                            if colision_circulo_rectangulo(o1, o2):
                                colision = True
                        elif isinstance(o2, Circulo) and isinstance(o1, Rectangulo):
                            if colision_circulo_rectangulo(o2, o1):
                                colision = True
                    
                    if colision:
                        o1.colisionando = o2.colisionando = True
                        # Manejar colision de vidrio
                        if o1.material == "vidrio":
                            o1.activo = False
                        if o2.material == "vidrio":
                            o2.activo = False

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
        Rectangulo(700, 50, 70, 40, -4, 4, "vidrio") # Nuevo objeto de vidrio
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
                    running = False  # volver al menú

        # Resetear colisiones
        for o in objetos:
            o.colisionando = False
            o.mover()
            if not o.activo:
                o.reaparecer()

        # Algoritmo seleccionado
        if modo == "fuerza_bruta":
            fuerza_bruta(objetos)
            titulo = "Modo: Fuerza Bruta (O(n²)) - C para cambiar"
        else:
            broad_phase_aabb(objetos)
            titulo = "Modo: AABB Broad Phase - C para cambiar"

        # Dibujar objetos
        for o in objetos:
            o.dibujar()

        # Dibujar la leyenda de materiales
        font = pygame.font.SysFont("Arial", 24)
        legend_font = pygame.font.SysFont("Arial", 18)
        text = font.render(titulo, True, WHITE)
        info = font.render("P - Regresar al menú | ESC - Salir", True, WHITE)
        screen.blit(text, (20, 20))
        screen.blit(info, (20, 50))

        # Leyenda
        legend_y_start = 100
        pygame.draw.rect(screen, WHITE, (WIDTH - 150, legend_y_start - 5, 140, len(MATERIALES) * 20 + 10), 2)
        legend_title = legend_font.render("Materiales", True, WHITE)
        screen.blit(legend_title, (WIDTH - 145, legend_y_start))
        
        y_offset = legend_y_start + 25
        for material, color in MATERIALES.items():
            pygame.draw.rect(screen, color, (WIDTH - 140, y_offset, 15, 15))
            mat_text = legend_font.render(material.capitalize(), True, WHITE)
            screen.blit(mat_text, (WIDTH - 120, y_offset))
            y_offset += 20

        pygame.display.flip()
        clock.tick(60)

# ------------------ Iniciar ------------------
menu()




