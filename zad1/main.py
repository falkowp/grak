import tkinter as tk
import math
import random

WIDTH = 800
HEIGHT = 600
FPS = 60

def normalize(v):
    length = math.sqrt(sum(c*c for c in v))
    if length == 0:
        return [0,0,0]
    return [c/length for c in v]

def cross(a, b):
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]

def dot(a, b):
    return sum(i*j for i,j in zip(a,b))

def rotate_vector(v, axis, angle_deg):
    angle_rad = math.radians(angle_deg)
    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)
    x, y, z = axis
    vx, vy, vz = v

    rotated = [
        (cos_theta + (1 - cos_theta) * x * x) * vx + ((1 - cos_theta) * x * y - sin_theta * z) * vy + ((1 - cos_theta) * x * z + sin_theta * y) * vz,
        ((1 - cos_theta) * y * x + sin_theta * z) * vx + (cos_theta + (1 - cos_theta) * y * y) * vy + ((1 - cos_theta) * y * z - sin_theta * x) * vz,
        ((1 - cos_theta) * z * x - sin_theta * y) * vx + ((1 - cos_theta) * z * y + sin_theta * x) * vy + (cos_theta + (1 - cos_theta) * z * z) * vz
    ]
    return rotated

class Camera:
    def __init__(self, pos):
        self.pos = pos
        self.forward = [0, 0, 1]
        self.right = [1, 0, 0]
        self.up = [0, 1, 0]

    def move(self, dx=0, dy=0, dz=0):
        for i in range(3):
            self.pos[i] += self.right[i] * dx
            self.pos[i] += self.up[i] * dy
            self.pos[i] += self.forward[i] * dz

    def rotate(self, axis, angle_deg):
        # Obraca wszystkie osie wokół zadanej osi
        self.forward = normalize(rotate_vector(self.forward, axis, angle_deg))
        self.right = normalize(rotate_vector(self.right, axis, angle_deg))
        self.up = normalize(cross(self.right, self.forward))

camera = Camera([0, 0, -5])

keys_pressed = set()
button_action = None

def project_point(x, y, z):
    if z <= 0:
        return None
    fov = 500
    px = WIDTH // 2 + int((x * fov) / z)
    py = HEIGHT // 2 - int((y * fov) / z)
    return (px, py)

def create_cuboid(cx, cy, cz, size_x, size_y, size_z):
    sx = size_x / 2
    sy = size_y / 2
    sz = size_z / 2
    return [
        [cx - sx, cy - sy, cz - sz],
        [cx + sx, cy - sy, cz - sz],
        [cx + sx, cy + sy, cz - sz],
        [cx - sx, cy + sy, cz - sz],
        [cx - sx, cy - sy, cz + sz],
        [cx + sx, cy - sy, cz + sz],
        [cx + sx, cy + sy, cz + sz],
        [cx - sx, cy + sy, cz + sz],
    ]

edges = [
    (0,1), (1,2), (2,3), (3,0),
    (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]

cuboids = []
colors = []

for _ in range(5):
    x = random.uniform(-5, 5)
    y = random.uniform(-3, 3)
    z = random.uniform(5, 15)
    size_x = random.uniform(0.5, 2)
    size_y = random.uniform(0.5, 2)
    size_z = random.uniform(0.5, 2)
    cuboids.append(create_cuboid(x, y, z, size_x, size_y, size_z))
    colors.append("#%06x" % random.randint(0, 0xFFFFFF))

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
    global button_action
    if button_action is not None and callable(button_action):
        button_action()
        root.after(50, do_move)

def reset_camera():
    global camera
    camera = Camera([0, 0, -5])

def update():
    speed = 0.2
    rot_speed = 3

    if 'w' in keys_pressed:
        camera.move(dz=speed)
    if 's' in keys_pressed:
        camera.move(dz=-speed)
    if 'a' in keys_pressed:
        camera.move(dx=-speed)
    if 'd' in keys_pressed:
        camera.move(dx=speed)
    if 'q' in keys_pressed:
        camera.move(dy=speed)
    if 'e' in keys_pressed:
        camera.move(dy=-speed)

    if 'left' in keys_pressed:
        camera.rotate(camera.up, -rot_speed)
    if 'right' in keys_pressed:
        camera.rotate(camera.up, rot_speed)
    if 'up' in keys_pressed:
        camera.rotate(camera.right, -rot_speed)
    if 'down' in keys_pressed:
        camera.rotate(camera.right, rot_speed)
    if 'z' in keys_pressed:
        camera.rotate(camera.forward, rot_speed) # roll
    if 'x' in keys_pressed:
        camera.rotate(camera.forward, -rot_speed) # roll

    canvas.delete("all")

    for cuboid, color in zip(cuboids, colors):
        projected_points = []

        for vertex in cuboid:
            rel = [vertex[i] - camera.pos[i] for i in range(3)]
            x = dot(rel, camera.right)
            y = dot(rel, camera.up)
            z = dot(rel, camera.forward)
            proj = project_point(x, y, z)
            projected_points.append(proj if proj else None)

        for edge in edges:
            p1 = projected_points[edge[0]]
            p2 = projected_points[edge[1]]
            if p1 and p2:
                canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=color)

    root.after(int(1000/FPS), update)

# Start GUI
root = tk.Tk()
root.title("Prawdziwa Kamera 3D")

frame = tk.Frame(root)
frame.pack(side="right", fill="y", padx=10, pady=10)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack(side="left")

# Panel sterowania
tk.Label(frame, text="Ruch kamery", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=5)

def create_move_button(row, col, text, action):
    btn = tk.Button(frame, text=text, font=("Arial", 14))
    btn.grid(row=row, column=col, padx=5, pady=5)
    btn.bind("<ButtonPress-1>", lambda e: start_moving(action))
    btn.bind("<ButtonRelease-1>", lambda e: stop_moving())

# Przyciski ruchu
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

# Legenda
tk.Label(frame, text="Legenda:", font=("Arial", 12, "bold")).grid(row=9, column=0, columnspan=3, pady=10)
legend_text = """\
W/S/A/D - ruch
Q/E - góra/dół
Strzałki - obrót kamery
Z/X - roll kamery
"""
tk.Label(frame, text=legend_text, justify="left").grid(row=10, column=0, columnspan=3, pady=5)

root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)

update()
root.mainloop()
