import pygame as pg
import math
from functools import cache



def aks():
    print("asdasdAsd")

HEIGHT = 600
WIDTH = 600

W2 = WIDTH/2
H2 = HEIGHT/2

# GUI begin
pg.init()
screen = pg.display.set_mode((WIDTH,HEIGHT))
clock = pg.time.Clock()
running= True

def dot(vec_a, vec_b):
    return sum(i * j for i, j in zip(vec_a, vec_b))

class LSource:
    def __init__(self, pos, color):
        self.pos = pos 
        self.color = color
        self.forward = [0, 0, 1]
        self.right = [1, 0, 0]
        self.up = [0, 1, 0]
    def setImage(self, path):
        self.baseImg = pg.image.load(path)
    def move(self, dx=0.0, dy=0.0, dz=0.0):
        for i in range(3):
            self.pos[i] += self.right[i] * dx
            self.pos[i] += self.up[i] * dy
            self.pos[i] += self.forward[i] * dz
    
class Ball:
    def __init__(self, cent, rad, n, color):
        self.start = cent
        self.radius = rad
        self.n = n
        self.color = color

light_source = LSource([0, 0, 0], [1.0, 1.0, 1.0])
light_source.setImage("zad3/sun.png")

def resizeImage(z):
    global light_source
    return pg.transform.scale(light_source.baseImg, (30 + z/10, 30 + z/10))

balls = [Ball([WIDTH//4,HEIGHT//4,0], int(min(WIDTH//4, HEIGHT//4)), 64, (1.0, 0, 1.0))]
ball_surfs = []

def ftoc(a:float):
    return min(max(int(a*255), 0.0), 255)

def vlen(vect):
    return math.sqrt(vect[0]**2 + vect[1]**2 + vect[2]**2)

def normalize(vect):
    v = vlen(vect)
    return [vect[0]/v, vect[1]/v, vect[2]/v]

def renderBalls():
    global balls
    ret = []
    for ball in balls:
        ball_surf = pg.Surface((2*ball.radius, 2*ball.radius))
        for i in range(-ball.radius, ball.radius,2):
            for j in range(-ball.radius, ball.radius,2):
                if i**2 + j**2 <= (ball.radius)**2:
                    
                    # basics
                    iB = i + ball.radius
                    jB = j + ball.radius

                    z = math.sqrt((ball.radius)**2 - i**2 - j**2)
                    L = [(light_source.pos[0] - ball.start[0]) - iB, (light_source.pos[1] - ball.start[1]) - jB, light_source.pos[2] - z]

                    normal = normalize([i, j, z])
                    # normalna zakładając, że środek kuli to (rad,rad,z)
                    light_dir = normalize(L)
                    
                    # diffuse
                    tmp = dot(normal, light_dir) # dNL
                    diff = [tmp*light_source.color[0], tmp*light_source.color[1], tmp*light_source.color[2]]

                    spec = [0,0,0]
                    # specular
                    if tmp > 0:
                    # ^ to zajęło trochę myślenia rozwiązało wiele błędów - jeżeli kąt między L a N jest poza zakresem (-90°:90°), 
                    #   to nie odbija się od powierzchni - nie trzeba liczyć specular
                        R= normalize([light_dir[0] - 2 * normal[0]*tmp, light_dir[1]-2*normal[1]*tmp,light_dir[2]-2*normal[2]*tmp])
                        V = normalize([W2 - ball.start[0] - iB, H2 - ball.start[1] - jB , -z])
                        cA = dot(R, V)**(ball.n)
                        spec = [cA*light_source.color[0], cA*light_source.color[1], cA*light_source.color[2]]

                    # suma świateł
                    clr = [ftoc(color*0.2 + df*0.25 + sp*0.75) for (color, df, sp) in zip(ball.color, diff, spec)]
                    pg.draw.circle(ball_surf, clr, (iB,jB), 2)
        ret.append((ball_surf, (ball.start[0], ball.start[1])))
    return ret



def update():
    global ball_surfs
    if len(keys_pressed) != 0:
        if pg.K_w in keys_pressed:
            light_source.move(dz=move_speed)
        if pg.K_s in keys_pressed:
            light_source.move(dz=-move_speed)
        if pg.K_d in keys_pressed:
            light_source.move(dx=move_speed)
        if pg.K_a in keys_pressed:
            light_source.move(dx=-move_speed)
        if pg.K_e in keys_pressed:
            light_source.move(dy=move_speed)
        if pg.K_q in keys_pressed:
            light_source.move(dy=-move_speed)
        if pg.K_ESCAPE in keys_pressed:
            return False
    
    ball_surfs = renderBalls()
    return True


keys_pressed = set()


font = pg.font.Font(pg.font.get_default_font(), 20)

def updateText():
    global light_source
    string = "x: " + str(light_source.pos[0]) + " y: " + str(light_source.pos[1]) + " z: " + str(light_source.pos[2]) 
    return font.render(string, True, "#FFFFFF")


#GUI loop
move_speed=10

ball_surfs = renderBalls()

lastZ = light_source.pos[2]
sunFlag = light_source.baseImg is not None

while running:
    screen.fill((0,0,0))
    screen.blits(ball_surfs)
    if sunFlag:
        if light_source.pos[2] != lastZ:
            lastZ = light_source.pos[2]
        imedz = resizeImage(lastZ)
        screen.blit(imedz, (light_source.pos[0] - 15, light_source.pos[1] - 15))
    

    text = updateText()
    textR = text.get_rect()
    screen.blit(text, textR)

    pg.display.flip()

    running = update()            

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            keys_pressed.add(event.key)
        if event.type == pg.KEYUP:
            keys_pressed.remove(event.key)

    # clock.tick(60)

pg.quit()