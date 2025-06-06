import tkinter as tk
import math
import random
import time


PI_DIV = 20
WIDTH = 800
HEIGHT = 800
FPS = 30 # 60
EDGES = [
    (0,1), (1,2), (2,3), (3,0),
    (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]
N_OBJ = 5

BALL_H = HEIGHT/5
BALL_W = WIDTH/5
BALL_R = BALL_H/2

camera_fov = 500

def normalize(vector):
    length = math.sqrt(sum(c * c for c in vector))
    if length == 0:
        return [0, 0, 0]
    return [c / length for c in vector]

def cross(vec_a, vec_b):
    return [
        vec_a[1]*vec_b[2] - vec_a[2]*vec_b[1],
        vec_a[2]*vec_b[0] - vec_a[0]*vec_b[2],
        vec_a[0]*vec_b[1] - vec_a[1]*vec_b[0]
    ]

def dot(vec_a, vec_b):
    return sum(i * j for i, j in zip(vec_a, vec_b))

def rotate_vector(vector, axis, angle_deg):
    angle_rad = math.radians(angle_deg)
    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)
    ax, ay, az = axis
    vx, vy, vz = vector

    rotated = [
        (cos_theta + (1 - cos_theta) * ax * ax) * vx + ((1 - cos_theta) * ax * ay - sin_theta * az) * vy + ((1 - cos_theta) * ax * az + sin_theta * ay) * vz,
        ((1 - cos_theta) * ay * ax + sin_theta * az) * vx + (cos_theta + (1 - cos_theta) * ay * ay) * vy + ((1 - cos_theta) * ay * az - sin_theta * ax) * vz,
        ((1 - cos_theta) * az * ax - sin_theta * ay) * vx + ((1 - cos_theta) * az * ay + sin_theta * ax) * vy + (cos_theta + (1 - cos_theta) * az * az) * vz
    ]
    return rotated

class Camera:
    def __init__(self, pos):
        self.pos = pos
        self.forward = [0, 0, 1]
        self.right = [1, 0, 0]
        self.up = [0, 1, 0]

    def move(self, dx=0.0, dy=0.0, dz=0.0):
        for i in range(3):
            self.pos[i] += self.right[i] * dx
            self.pos[i] += self.up[i] * dy
            self.pos[i] += self.forward[i] * dz

    def rotate(self, axis, angle_deg):
        self.forward = normalize(rotate_vector(self.forward, axis, angle_deg))
        self.right = normalize(rotate_vector(self.right, axis, angle_deg))
        self.up = normalize(cross(self.forward, self.right))

light_source = Camera([0, 0, 0])
camera = Camera([0,0,-5])


class Triangle:
    def __init__(self, pts:list[3], color):
        self.pts = pts
        self.norm = self.setNormal()
        self.color = color
        
    def setNormal(self):
        w0 = [self.pts[0][0] - self.pts[1][0], self.pts[0][1] - self.pts[1][1], self.pts[0][2] - self.pts[1][2]]
        w1 = [self.pts[2][0] - self.pts[1][0], self.pts[2][1] - self.pts[1][1], self.pts[2][2] - self.pts[1][2]]
        
        return [w0[1]*w1[2] - w0[2]*w1[1], -1*(w0[0]*w1[2] - w0[2]*w1[0]), w0[0]*w1[1] - w0[1]*w1[0]]    
    
    
class Ball:
    def __init__(self, cent, rad, color):
        self.center = cent
        self.radius = rad
        self.color = color
        self.makePoints()
        self.makeFaces()
        
    def makePoints(self):
        self.pts = []
        fi = math.pi
        rad = self.radius
        while(round(fi, 2)<=2*math.pi):
            sF = math.sin(fi); cF = math.cos(fi)
            th = 0
            while(round(th, 2)<math.pi):
                sT = math.sin(th); cT = math.cos(th)
                self.pts.append([rad*cF*sT+ self.center[0], 
                                    rad*cT+ self.center[1],
                                    rad* sF * sT + self.center[2]])
                th += math.pi/PI_DIV
            fi += math.pi/PI_DIV
        return 
    
    def makeFaces(self):
        self.faces = []
        for j in range(PI_DIV+1):
            for i in range(PI_DIV):
                self.faces.extend([Triangle([self.pts[i+j*PI_DIV], self.pts[i+(j+1)*PI_DIV], self.pts[i+1+j*PI_DIV]], self.color),
                                   Triangle([self.pts[i+(j+1)*PI_DIV], self.pts[i+1+(j+1)*PI_DIV], self.pts[i+1+j*PI_DIV]], self.color)])
            


class Cuboid:
    pts = []
    tris:list

    def __init__(self, cX, cY, cZ, w, l, d, color):
        self.color = color
        self.pts = self.makePts(cX,cY,cZ,w,l,d)
        self.tris = self.makeTris()
        

    def makePts(self, cX, cY, cZ, w, l, d):
        w2 = w/2; l2 = l/2; d2 = d/2
        return [
            [cX - w2, cY - l2, cZ - d2],
            [cX + w2, cY - l2, cZ - d2],
            [cX + w2, cY + l2, cZ - d2],
            [cX - w2, cY + l2, cZ - d2],
            [cX - w2, cY - l2, cZ + d2],
            [cX + w2, cY - l2, cZ + d2],
            [cX + w2, cY + l2, cZ + d2],
            [cX - w2, cY + l2, cZ + d2],
        ]

    def makeTris(self):
        ret = list()
        ret.extend((Triangle((self.pts[0], self.pts[1], self.pts[2]), self.color), Triangle((self.pts[0], self.pts[2], self.pts[3]), self.color),
                   Triangle((self.pts[2], self.pts[1], self.pts[5]), self.color), Triangle((self.pts[2], self.pts[5], self.pts[6]), self.color),
                   Triangle((self.pts[5], self.pts[4], self.pts[7]), self.color), Triangle((self.pts[5], self.pts[7], self.pts[6]), self.color), 
                   Triangle((self.pts[7], self.pts[4], self.pts[0]), self.color), Triangle((self.pts[7], self.pts[0], self.pts[3]), self.color),
                   Triangle((self.pts[1], self.pts[0], self.pts[5]), self.color), Triangle((self.pts[0], self.pts[4], self.pts[5]), self.color),
                   Triangle((self.pts[2], self.pts[7], self.pts[3]), self.color), Triangle((self.pts[2], self.pts[6], self.pts[7]), self.color)))
        return ret

def checkPosition(fc:Triangle, pt:list):
    ret = dot(fc.norm, [pt[0] - fc.pts[0][0], pt[1]-fc.pts[0][1], pt[2]-fc.pts[0][2]])
    return 10 if ret > 0 else -1 if ret < 0 else 0

def getT(p0:list, p1:list, fc:Triangle):
    return dot(fc.norm, [p0[0] - fc.pts[0][0], p0[1] - fc.pts[0][1], p0[2] - fc.pts[0][2]]) / dot([-1*fc.norm[0], -1*fc.norm[1], -1*fc.norm[2]], [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]])


def project_point(px, py, pz):
    div = pz if pz > 0 else 1
    screen_x = WIDTH / 2 + int((px * camera_fov) / div) 
    screen_y = HEIGHT / 2 - int((py * camera_fov) / div)
    return screen_x, screen_y

cuboids = []
colors = []

for _ in range(N_OBJ):
    pos_x = random.uniform(-200, 200)
    pos_y = random.uniform(-200, 200)
    pos_z = random.uniform(-200, 200)
    size_x = random.uniform(50, 200)
    size_y = random.uniform(50, 200)
    size_z = random.uniform(50, 200)
    color = "#%06x" % random.randint(0, 0xFFFFFF)
    cuboids.append(Cuboid(pos_x, pos_y, pos_z, size_x, size_y, size_z, color))

def getFaces(cbs:list):
    ret = []
    for cb in cbs:
        ret.extend(cb.tris)
    return ret

keys_pressed = set()
button_action = None

def renderFaces(faces:list):
    global camera
    projected_triangles = []; colors = []
    for tri in faces:
        projected_points = []
        for pt in tri.pts: 
            proj_point = project_point(pt[0] - camera.pos[0], pt[1] - camera.pos[1], pt[2] - camera.pos[2])
            projected_points.append(proj_point if proj_point else None)
        projected_triangles.append(projected_points)
        colors.append(tri.color)

    for tri, color in zip(projected_triangles, colors):
        canvas.create_polygon(tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1], fill=color)

# to throw out
def ftoh(a:float):
    if a < 0:
        return "#000000"
    else:
        return "#"+3*str(hex(int(a*255)))[2:]


def renderBall(ball:Ball):
    renderFaces(ball.faces)

    # # to throw out
    # for pt in ball.pts:
    #     ptX, ptY = project_point(pt[0] - camera.pos[0], pt[1] - camera.pos[1], pt[2] - camera.pos[2])
    #     canvas.create_oval(ptX-1, ptY-1, ptX+1, ptY+1, fill="#ffffff")
    return 


def key_down(event):
    keys_pressed.add(event.keysym.lower())

def key_up(event):
    keys_pressed.discard(event.keysym.lower())

def start_moving(action):
    global button_action
    button_action = action
    do_move()

def stop_moving():
    global button_action
    button_action = None

def do_move():
    if button_action is not None and callable(button_action):
        button_action()
        root.after(50, do_move)

def reset_camera():
    global light_source
    light_source = Camera([0, 0, -5])

balls = [Ball([-3,3,5], 1, "#000099"), Ball([-3,-3,5], 1, "#009900"), 
         Ball([3,3,5], 1, "#990000"), Ball([3,-3,5], 1, "#555555")]



def cords_update():
    # text.config(state="normal")
    # text.insert("end", "X: "+ str(light_source.pos[0]) + " Y: " + str(light_source.pos[1]) + " Z: " + str(light_source.pos[2]) +"\n")
    # text.config(state="disabled")
    text.set("X: "+ str(light_source.pos[0]) + " Y: " + str(light_source.pos[1]) + " Z: " + str(light_source.pos[2]) +"\n")

def update():
    move_speed = 10
    rotate_speed = 2

    if len(keys_pressed) == 0:
        root.after(int(1000 / FPS), update)

    else:

        if 'w' in keys_pressed:
            light_source.move(dz=move_speed)
        if 's' in keys_pressed:
            light_source.move(dz=-move_speed)
        if 'a' in keys_pressed:
            light_source.move(dx=-move_speed)
        if 'd' in keys_pressed:
            light_source.move(dx=move_speed)
        if 'q' in keys_pressed:
            light_source.move(dy=move_speed)
        if 'e' in keys_pressed:
            light_source.move(dy=-move_speed)

        if 'escape' in keys_pressed:
            root.quit()

        for i in range(100):
            for j in range(150):
                img.put("#990000", (i,j))
        

        # canvas.delete("all")

        # print(BALL_H, BALL_W)

        # # canvas.create_oval(BALL_W,BALL_H,2*BALL_W,2*BALL_H, fill="#000099")
        # for i in range(int(BALL_W)):
        #     for j in range(int(BALL_H)):
        #         canvas.create_rectangle(BALL_W+i, BALL_H+j, BALL_W+i, BALL_H+j,fill= "#000099")
        # canvas.create_rectangle(BALL_W,3*BALL_H,2*BALL_W,4*BALL_H, fill="#009900")

        # canvas.create_rectangle(3*BALL_W,BALL_H,4*BALL_W,2*BALL_H, fill="#990099")
        # canvas.create_rectangle(3*BALL_W,3*BALL_H,4*BALL_W,4*BALL_H, fill="#990000")

        # cords_update()

        root.after(int(1000 / FPS), update)

# GUI
root = tk.Tk()
root.title("Oświetlenie")

frame = tk.Frame(root)
frame.pack(side="right", fill="y", padx=10, pady=10)

# canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#121212")
# canvas.pack(side="left")

img = tk.PhotoImage(width=WIDTH, height=HEIGHT)
lbl = tk.Label(root, image=img)
lbl.pack()
for i in range(100):
    for j in range(150):
        img.put("#990099", (i,j))

text = tk.StringVar()
# cordLabel = tk.Label(canvas, bg="#121212", fg="#fefefe", textvariable=text)
# cordLabel.place(x=2,y=2)
# cordLabel.config(font=("Comic Sans", 13))


def create_move_button(row, col, text, action):
    btn = tk.Button(frame, text=text, font=("Arial", 14))
    btn.grid(row=row, column=col, padx=5, pady=5)
    btn.bind("<ButtonPress-1>", lambda e: start_moving(action))
    btn.bind("<ButtonRelease-1>", lambda e: stop_moving())

tk.Label(frame, text="Ruch kamery", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=5)

create_move_button(1, 1, "↑", lambda: light_source.move(dz=1))
create_move_button(3, 1, "↓", lambda: light_source.move(dz=-1))
create_move_button(2, 0, "←", lambda: light_source.move(dx=-1))
create_move_button(2, 2, "→", lambda: light_source.move(dx=1))
create_move_button(1, 0, "⤒", lambda: light_source.move(dy=1))
create_move_button(1, 2, "⤓", lambda: light_source.move(dy=-1))

btn_reset = tk.Button(frame, text="Reset Kamery", font=("Arial", 14), command=reset_camera)
btn_reset.grid(row=8, column=0, columnspan=3, pady=10)


# Legenda
tk.Label(frame, text="Legenda:", font=("Arial", 12, "bold")).grid(row=12, column=0, columnspan=3, pady=10)
legend_text = """\
W/S/A/D - ruch
Q/E - góra/dół
I/K/J/L - obrót 
U/O - roll kamery
Scroll - zoom
"""
tk.Label(frame, text=legend_text, justify="left").grid(row=13, column=0, columnspan=3, pady=5)

root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)


# for ball in balls:
#     renderBall(ball)

# cords_update()


update()
root.mainloop()
