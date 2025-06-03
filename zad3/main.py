import pygame as pg
import math
import time
from functools import cache



def aks():
    print("asdasdAsd")

HEIGHT = 600
WIDTH = 600

W2 = WIDTH/2
H2 = HEIGHT/2

# RW = 1/WIDTH
# RH = 1/HEIGHT

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
    def move(self, dx=0.0, dy=0.0, dz=0.0):
        for i in range(3):
            self.pos[i] += self.right[i] * dx
            self.pos[i] += self.up[i] * dy
            self.pos[i] += self.forward[i] * dz
    def setImage(self, path):
        self.img = pg.transform.scale(pg.image.load(path), (30,30))
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

balls = [Ball([WIDTH//4,HEIGHT//4,0], int(min(WIDTH//4, HEIGHT//4)), 200, (1.0, 0, 1.0))]
ball_surfs = []

def ftoc(a:float):
    return min(max(int(a*255), 0.0), 255)

def vlen(vect):
    return math.sqrt(vect[0]**2 + vect[1]**2 + vect[2]**2)

def normalize(vect):
    v = vlen(vect)
    return [vect[0]/v, vect[1]/v, vect[2]/v], v

def update():

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
            return 

        global ball_surfs, balls
        ball_surfs = []
        for ball in balls:
            ball_surf = pg.Surface((2*ball.radius, 2*ball.radius))
            for i in range(-ball.radius, ball.radius,2):
                for j in range(-ball.radius, ball.radius,2):
                    if i**2 + j**2 <= (ball.radius)**2:
                        iB = i + ball.radius
                        jB = j + ball.radius
                        # basics
                        z = math.sqrt((ball.radius)**2 - i**2 - j**2)
                        # to powinno mieć dużo sensu
                        L = [(light_source.pos[0] - ball.start[0]) - iB, (light_source.pos[1] - ball.start[1]) - jB, light_source.pos[2] - z]# - z-ball.start[0]]#-ball.radius]

                        normal, vN = normalize([i, j, z])
                        # normalna zakładając, że środek kuli to (rad,rad,z)
                        light_dir, vL = normalize(L)
                        
                        # diffuse
                        # spójrz tu na normalną
                        tmp = dot(normal, light_dir) # dNL
                        # tmp = max(0.0, dNL)

                        diff = [tmp*light_source.color[0], tmp*light_source.color[1], tmp*light_source.color[2]]

                        # specular
                        cT = tmp / (vN *vL) #dNL
                        R, vR = normalize([light_dir[0] - 2 * normal[0]*cT, light_dir[1]-2*normal[1]*cT,light_dir[2]-2*normal[2]*cT])
                        # cA = max(0.0, (dot(V, [0.0,0.0,1.0]) / vN))**(ball.n)
                        V, vV = normalize([W2 - ball.start[0] - iB, H2 - ball.start[1] - jB , z - 1000])
                        cA = dot(R, V)**(ball.n)
                        spec = [cA*light_source.color[0], cA*light_source.color[1], cA*light_source.color[2]]

                        # suma
                        clr = [ftoc(color*0.2 + df*0.25 + 0.75*sp) for (color, df, sp) in zip(ball.color, diff, spec)]
                        pg.draw.circle(ball_surf, clr, (iB,jB), 2)

            ball_surfs.append((ball_surf, (ball.start[0], ball.start[1])))


keys_pressed = set()


font = pg.font.Font(pg.font.get_default_font(), 20)

def updateText():
    global light_source
    string = "x: " + str(light_source.pos[0]) + " y: " + str(light_source.pos[1]) + " z: " + str(light_source.pos[2]) 
    return font.render(string, True, "#FFFFFF")


#GUI loop
move_speed=10

while running:
    screen.fill((0,0,0))
    screen.blits(ball_surfs)
    if light_source.img is not None:
        screen.blit(light_source.img, (light_source.pos[0] - 15, light_source.pos[1] - 15))
    

    # pg.draw.rect(screen, [255,255,255], (200,100,100,100))
    text = updateText()
    textR = text.get_rect()
    screen.blit(text, textR)

    pg.display.flip()

    update()            

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            # if event.key == pg.K_ESCAPE:
            keys_pressed.add(event.key)
        if event.type == pg.KEYUP:
            keys_pressed.remove(event.key)

    clock.tick(60)

pg.quit()