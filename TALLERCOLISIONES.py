import pygame
import math
import sys
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Detección de colisiones 2D")
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
class Objeto:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.colisionando = False

    def mover(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > WIDTH:
            self.vx *= -1
        if self.y < 0 or self.y > HEIGHT:
            self.vy *= -1

class Circulo(Objeto):
    def __init__(self, x, y, radio, vx, vy):
        super().__init__(x, y, vx, vy)
        self.radio = radio

    def dibujar(self):
        if self.colisionando:
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radio)
        else:
            pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radio, 3)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radio, 1)

    def aabb(self):
        return pygame.Rect(self.x - self.radio, self.y - self.radio, 2*self.radio, 2*self.radio)

class Rectangulo(Objeto):
    def __init__(self, x, y, w, h, vx, vy):
        super().__init__(x, y, vx, vy)
        self.w = w
        self.h = h

    def dibujar(self):
        rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if self.colisionando:
            pygame.draw.rect(screen, RED, rect)
        else:
            pygame.draw.rect(screen, BLUE, rect, 3)
        pygame.draw.rect(screen, WHITE, rect, 1)

    def aabb(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

# PARAMETROS DE COLISION
def colision_circulos(c1, c2):
    dx = c1.x - c2.x
    dy = c1.y - c2.y
    return math.hypot(dx, dy) < (c1.radio + c2.radio)

def colision_rectangulos(r1, r2):
    return r1.aabb().colliderect(r2.aabb())

def colision_circulo_rectangulo(c, r):
    rect = r.aabb()
    cx = max(rect.left, min(c.x, rect.right))
    cy = max(rect.top, min(c.y, rect.bottom))
    dx = c.x - cx
    dy = c.y - cy
    return dx*dx + dy*dy < c.radio*c.radio

def fuerza_bruta(objetos):
    for i in range(len(objetos)):
        for j in range(i+1, len(objetos)):
            o1, o2 = objetos[i], objetos[j]
            if isinstance(o1, Circulo) and isinstance(o2, Circulo):
                if colision_circulos(o1, o2):
                    o1.colisionando = o2.colisionando = True
            elif isinstance(o1, Rectangulo) and isinstance(o2, Rectangulo):
                if colision_rectangulos(o1, o2):
                    o1.colisionando = o2.colisionando = True
            else:
                if isinstance(o1, Circulo) and isinstance(o2, Rectangulo):
                    if colision_circulo_rectangulo(o1, o2):
                        o1.colisionando = o2.colisionando = True
                elif isinstance(o2, Circulo) and isinstance(o1, Rectangulo):
                    if colision_circulo_rectangulo(o2, o1):
                        o1.colisionando = o2.colisionando = True

def broad_phase_aabb(objetos, cell_size=150):
    grid = {}
    for obj in objetos:
        rect = obj.aabb()
        cx, cy = rect.x // cell_size, rect.y // cell_size
        grid.setdefault((cx, cy), []).append(obj)

    for cell_objs in grid.values():
        if len(cell_objs) > 1:
            fuerza_bruta(cell_objs)

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
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        screen.blit(start, (WIDTH//2 - start.get_width()//2, 320))
        screen.blit(quit_msg, (WIDTH//2 - quit_msg.get_width()//2, 360))
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
        Circulo(200, 200, 40, 3, 2),
        Circulo(500, 400, 30, -4, 2),
        Rectangulo(300, 100, 100, 70, 3, 2),
        Rectangulo(120, 350, 120, 80, -3, -2)
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

        font = pygame.font.SysFont("Arial", 24)
        text = font.render(titulo, True, WHITE)
        info = font.render("P - Regresar al menú | ESC - Salir", True, WHITE)
        screen.blit(text, (20, 20))
        screen.blit(info, (20, 50))

        pygame.display.flip()
        clock.tick(60)

# ------------------ Iniciar ------------------
menu()



