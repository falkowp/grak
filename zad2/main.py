import tkinter as tk
import math
import random

WIDTH = 800
HEIGHT = 600
FPS = 60
EDGES = [
    (0,1), (1,2), (2,3), (3,0),
    (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]
N_OBJ = 2

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

camera = Camera([0, 0, -5])

class Triangle:
    def __init__(self, pts:list[3]):
        self.pts = pts
        self.norm = self.setNormal()
        
    def setNormal(self):
        w0 = [self.pts[0][0] - self.pts[1][0], self.pts[0][1] - self.pts[1][1], self.pts[0][2] - self.pts[1][2]]
        w1 = [self.pts[2][0] - self.pts[1][0], self.pts[2][1] - self.pts[1][1], self.pts[2][2] - self.pts[1][2]]
        
        return [w0[1]*w1[2] - w0[2]*w1[1], -1*(w0[0]*w1[2] - w0[2]*w1[0]), w0[0]*w1[1] - w0[1]*w1[0]]    
        # wyjęte z zeszytu z algebry xD
    

class Cuboid:
    pts = []
    tris:list
    # def __init__(self, pts):
    #     self.pts = pts
    #     self.tris = self.makeTris()

    def __init__(self, cX, cY, cZ, w, l, d):
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
    
    # lista trójkątów w bryle - po 2 na ścianę (kolejność istotna). Ważne dla BSP
    def makeTris(self):
        ret = list()
        ret.extend((Triangle((self.pts[0], self.pts[1], self.pts[2])), Triangle((self.pts[0], self.pts[2], self.pts[3])),
                   Triangle((self.pts[2], self.pts[1], self.pts[5])), Triangle((self.pts[2], self.pts[5], self.pts[6])),
                   Triangle((self.pts[5], self.pts[7], self.pts[6])), Triangle((self.pts[5], self.pts[4], self.pts[7])),
                   Triangle((self.pts[7], self.pts[4], self.pts[0])), Triangle((self.pts[7], self.pts[0], self.pts[3])),
                   Triangle((self.pts[1], self.pts[0], self.pts[5])), Triangle((self.pts[0], self.pts[4], self.pts[5])),
                   Triangle((self.pts[2], self.pts[7], self.pts[3])), Triangle((self.pts[2], self.pts[6], self.pts[7]))))
        return ret

def checkPosition(fc:Triangle, pt:list):
    return 1 if dot(fc.norm, [pt[0] - fc.pts[0][0], pt[1]-fc.pts[0][1], pt[2]-fc.pts[0][2]]) >= 0 else -1
# TODO - rozwinąć, przecięcia

class BSPNode:
    def __init__(self):
        self.left = None    # za  - minus
        self.right = None   # przed - plus
        self.val = None
    
    def makeNode(self, faces):
        self.val = faces.pop(0)
        l = []; p = []
        for face in faces:
            chk = 0
            for point in face.pts:
                chk += checkPosition(self.val, point)
            match chk:
                case 3:
                    p.append(face)
                case -3:
                    l.append(face)
        
        if len(l) != 0 and len(p) != 0:
        # dalszy podział
            self.left = BSPNode()
            self.left.makeNode(l)
            self.right = BSPNode()
            self.right.makeNode(p)
        
        # wszystko jest "po jednej stronie", nie trzzeba nic dzielić
        elif len(l) != 0:
            self.left = BSPNode()
            self.left.val = l
        else:
            self.right = BSPNode()
            self.right.val = p
            


def project_point(px, py, pz):
    div = pz if pz > 0 else 1
    # if pz <= 0: 
    #   return None
    screen_x = WIDTH / 2 + int((px * camera_fov) / div) # tu plus
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
    cuboids.append(Cuboid(pos_x, pos_y, pos_z, size_x, size_y, size_z))
    colors.append("#%06x" % random.randint(0, 0xFFFFFF))

def getFaces(cbs:list):
    ret = []
    for cb in cbs:
        ret.extend(cb.tris)
    return ret

BSProot = BSPNode(getFaces(cuboids))
keys_pressed = set()
button_action = None

def getBSPOrder(node:BSPNode):
    if node.left == None and node.right == None:
        return node.val 

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
    global camera
    global camera_fov
    camera = Camera([0, 0, -5])
    camera_fov = 500

def zoom_in():
    global camera_fov
    camera_fov = min(camera_fov + 20, 2000)

def zoom_out():
    global camera_fov
    camera_fov = max(camera_fov - 20, 100)

def update():
    move_speed = 10
    rotate_speed = 2

    if 'w' in keys_pressed:
        camera.move(dz=move_speed)
    if 's' in keys_pressed:
        camera.move(dz=-move_speed)
    if 'a' in keys_pressed:
        camera.move(dx=-move_speed)
    if 'd' in keys_pressed:
        camera.move(dx=move_speed)
    if 'q' in keys_pressed:
        camera.move(dy=move_speed)
    if 'e' in keys_pressed:
        camera.move(dy=-move_speed)

    if 'j' in keys_pressed:
        camera.rotate(camera.up, -rotate_speed)
    if 'l' in keys_pressed:
        camera.rotate(camera.up, rotate_speed)
    if 'i' in keys_pressed:
        camera.rotate(camera.right, -rotate_speed)
    if 'k' in keys_pressed:
        camera.rotate(camera.right, rotate_speed)
    if 'u' in keys_pressed:
        camera.rotate(camera.forward, rotate_speed)
    if 'o' in keys_pressed:
        camera.rotate(camera.forward, -rotate_speed)

    if 'up' in keys_pressed:
        zoom_in()
    if 'down' in keys_pressed:
        zoom_out()

    if 'escape' in keys_pressed:
        root.quit()

    canvas.delete("all")

    for cuboid, color in zip(cuboids, colors):
        projected_points = []

# # rysowanie liniami
#         for vertex in cuboid.pts:
#             rel_x = vertex[0] - camera.pos[0] # tu minusy
#             rel_y = vertex[1] - camera.pos[1]
#             rel_z = vertex[2] - camera.pos[2]
#             x_proj = dot([rel_x, rel_y, rel_z], camera.right)
#             y_proj = dot([rel_x, rel_y, rel_z], camera.up)
#             z_proj = dot([rel_x, rel_y, rel_z], camera.forward)
#             proj_point = project_point(x_proj, y_proj, z_proj) 
#             projected_points.append(proj_point)



#         for edge_start, edge_end in EDGES:
#             point1 = projected_points[edge_start]
#             point2 = projected_points[edge_end]
#             if point1 and point2:
#                 canvas.create_line(point1[0], point1[1], point2[0], point2[1], fill=color)

# # basic rysowanie trójkątami
#         projected_triangles = []
#         for tri in cuboid.tris:
#             projected_points = []
#             for pt in tri.pts:
#                 rel_x = pt[0] - camera.pos[0]
#                 rel_y = pt[1] - camera.pos[1]
#                 rel_z = pt[2] - camera.pos[2]
#                 x_proj = dot([rel_x, rel_y, rel_z], camera.right)
#                 y_proj = dot([rel_x, rel_y, rel_z], camera.up)
#                 z_proj = dot([rel_x, rel_y, rel_z], camera.forward)
#                 proj_point = project_point(x_proj, y_proj, z_proj)
#                 projected_points.append(proj_point if proj_point else None)
#             projected_triangles.append(projected_points)

#         for tri in projected_triangles:
#             canvas.create_polygon(tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1], fill=color)
    
# rysowanie z BSP
        projected_triangles = []
        for tri in cuboid.tris:
            projected_points = []
            for pt in tri.pts:
                rel_x = pt[0] - camera.pos[0]
                rel_y = pt[1] - camera.pos[1]
                rel_z = pt[2] - camera.pos[2]
                x_proj = dot([rel_x, rel_y, rel_z], camera.right)
                y_proj = dot([rel_x, rel_y, rel_z], camera.up)
                z_proj = dot([rel_x, rel_y, rel_z], camera.forward)
                proj_point = project_point(x_proj, y_proj, z_proj)
                projected_points.append(proj_point if proj_point else None)
            projected_triangles.append(projected_points)

        for tri in projected_triangles:
            canvas.create_polygon(tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1], fill=color)
    

    root.after(int(1000 / FPS), update)

# GUI
root = tk.Tk()
root.title("Kamera 3D")

frame = tk.Frame(root)
frame.pack(side="right", fill="y", padx=10, pady=10)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack(side="left")

def create_move_button(row, col, text, action):
    btn = tk.Button(frame, text=text, font=("Arial", 14))
    btn.grid(row=row, column=col, padx=5, pady=5)
    btn.bind("<ButtonPress-1>", lambda e: start_moving(action))
    btn.bind("<ButtonRelease-1>", lambda e: stop_moving())

tk.Label(frame, text="Ruch kamery", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=5)

create_move_button(1, 1, "↑", lambda: camera.move(dz=1))
create_move_button(3, 1, "↓", lambda: camera.move(dz=-1))
create_move_button(2, 0, "←", lambda: camera.move(dx=-1))
create_move_button(2, 2, "→", lambda: camera.move(dx=1))
create_move_button(1, 0, "⤒", lambda: camera.move(dy=1))
create_move_button(1, 2, "⤓", lambda: camera.move(dy=-1))

tk.Label(frame, text="Obrót kamery", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=3, pady=10)

create_move_button(5, 0, "↻ w prawo", lambda: camera.rotate(camera.up, 5))
create_move_button(5, 2, "↺ w lewo", lambda: camera.rotate(camera.up, -5))
create_move_button(6, 0, "↥ w górę", lambda: camera.rotate(camera.right, -5))
create_move_button(6, 2, "↧ w dół", lambda: camera.rotate(camera.right, 5))
create_move_button(7, 0, "↻ roll prawo", lambda: camera.rotate(camera.forward, 5))
create_move_button(7, 2, "↺ roll lewo", lambda: camera.rotate(camera.forward, -5))

btn_reset = tk.Button(frame, text="Reset Kamery", font=("Arial", 14), command=reset_camera)
btn_reset.grid(row=8, column=0, columnspan=3, pady=10)

tk.Label(frame, text="Zoom", font=("Arial", 12, "bold")).grid(row=9, column=0, columnspan=3, pady=10)

def create_zoom_button(row, text, action):
    btn = tk.Button(frame, text=text, font=("Arial", 12))
    btn.grid(row=row, column=0, columnspan=3, pady=2)
    btn.bind("<ButtonPress-1>", lambda e: start_moving(action))
    btn.bind("<ButtonRelease-1>", lambda e: stop_moving())

create_zoom_button(10, "➕ Zoom In", zoom_in)
create_zoom_button(11, "➖ Zoom Out", zoom_out)


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
#root.bind("<MouseWheel>", zoom)

update()
root.mainloop()
