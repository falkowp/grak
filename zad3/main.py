import pygame as pg
import math

def aks():
    print("asdasdAsd")

HEIGHT = 750
WIDTH = 750

def dot(vec_a, vec_b):
    return sum(i * j for i, j in zip(vec_a, vec_b))

class LSource:
    def __init__(self, pos, color):
        self.pos = pos 
        self.color = color
    def move(self, dx=0.0, dy=0.0, dz=0.0):
        for i in range(3):
            self.pos[i] += self.right[i] * dx
            self.pos[i] += self.up[i] * dy
            self.pos[i] += self.forward[i] * dz



class Ball:
    def __init__(self, cent, rad, color):
        self.center = cent
        self.radius = rad
        self.color = color


W5 = WIDTH/5
H5 = HEIGHT/5

light_source = LSource([700, 700, 0], [1.0, 1.0, 1.0])

balls = [Ball([W5,H5,0], min(WIDTH//10,HEIGHT//10), (0.7, 0, 0.7)), Ball([W5,3*H5,0], min(WIDTH//10,HEIGHT//10), (0,0.7,0.7)),
         Ball([3*W5,H5,0], min(WIDTH//10, HEIGHT//10), (0.7,0.7,0)), Ball([3*W5,3*H5,0], min(WIDTH//10,HEIGHT//10), (0,0,0))]
ball_surfs = []

def ftoc(a:float):
    return min(max(int(a*255), 0.0), 255)

for ball in balls:
    ball_surf = pg.Surface((2*ball.radius, 2*ball.radius))
    for i in range(-ball.radius, ball.radius):
        for j in range(-ball.radius, ball.radius):
            if i**2 + j**2 <= (ball.radius)**2:
                z = math.sqrt(ball.radius**2 - i**2 - j**2)
                bigdot = dot([light_source.pos[0]/WIDTH, light_source.pos[1]/HEIGHT, light_source.pos[2]/ball.radius], [(i+ball.radius)/WIDTH, (j+ball.radius)/HEIGHT, z/ball.radius])
                # print(bigdot)
                tmp = max(0.0, bigdot)
                diff = [tmp*light_source.color[0], tmp*light_source.color[1], tmp*light_source.color[2]]
                # print(diff)
                clr = [ftoc(color*0.4 + df*0.6) for (color, df) in zip(ball.color, diff)]
                pg.draw.rect(ball_surf, clr, (i+ball.radius,j+ball.radius,1,1))

    ball_surfs.append((ball_surf, (ball.center[0], ball.center[1])))


#GUI 
pg.init()
screen = pg.display.set_mode((WIDTH,HEIGHT))
clock = pg.time.Clock()
running= True

while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    screen.fill((0,0,0))
    screen.blits(ball_surfs)
    pg.display.flip()

    clock.tick(60)

pg.quit()