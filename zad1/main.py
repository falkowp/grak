import tkinter as tk
import math
import random

WIDTH = 800
HEIGHT = 600
FPS = 60

camera_fov = 500  # dodane: zmienna globalna FOV

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

keys_pressed = set()
button_action = None

def project_point(px, py, pz):
    if pz <= 0:
        return None
    screen_x = WIDTH // 2 + int((px * camera_fov) / pz)
    screen_y = HEIGHT // 2 - int((py * camera_fov) / pz)
    return screen_x, screen_y

def create_cuboid(center_x, center_y, center_z, size_cx, size_cy, size_cz):
    half_sx = size_cx / 2
    half_sy = size_cy / 2
    half_sz = size_cz / 2
    return [
        [center_x - half_sx, center_y - half_sy, center_z - half_sz],
        [center_x + half_sx, center_y - half_sy, center_z - half_sz],
        [center_x + half_sx, center_y + half_sy, center_z - half_sz],
        [center_x - half_sx, center_y + half_sy, center_z - half_sz],
        [center_x - half_sx, center_y - half_sy, center_z + half_sz],
        [center_x + half_sx, center_y - half_sy, center_z + half_sz],
        [center_x + half_sx, center_y + half_sy, center_z + half_sz],
        [center_x - half_sx, center_y + half_sy, center_z + half_sz],
    ]

edges = [
    (0,1), (1,2), (2,3), (3,0),
    (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]

cuboids = []
colors = []

for _ in range(5):
    pos_x = random.uniform(-5, 5)
    pos_y = random.uniform(-3, 3)
    pos_z = random.uniform(5, 15)
    size_x = random.uniform(0.5, 2)
    size_y = random.uniform(0.5, 2)
    size_z = random.uniform(0.5, 2)
    cuboids.append(create_cuboid(pos_x, pos_y, pos_z, size_x, size_y, size_z))
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
    if button_action is not None and callable(button_action):
        button_action()
        root.after(50, do_move)

def reset_camera():
    global camera
    global camera_fov
    camera = Camera([0, 0, -5])
    camera_fov = 500

def zoom(event):
    global camera_fov
    if event.delta > 0:
        camera_fov = min(camera_fov + 20, 2000)
    else:
        camera_fov = max(camera_fov - 20, 100)

def zoom_in():
    global camera_fov
    camera_fov = min(camera_fov + 20, 2000)

def zoom_out():
    global camera_fov
    camera_fov = max(camera_fov - 20, 100)

def update():
    move_speed = 0.2
    rotate_speed = 3

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

    if 'left' in keys_pressed:
        camera.rotate(camera.up, -rotate_speed)
    if 'right' in keys_pressed:
        camera.rotate(camera.up, rotate_speed)
    if 'up' in keys_pressed:
        camera.rotate(camera.right, -rotate_speed)
    if 'down' in keys_pressed:
        camera.rotate(camera.right, rotate_speed)
    if 'z' in keys_pressed:
        camera.rotate(camera.forward, rotate_speed)
    if 'x' in keys_pressed:
        camera.rotate(camera.forward, -rotate_speed)

    canvas.delete("all")

    for cuboid, color in zip(cuboids, colors):
        projected_points = []

        for vertex in cuboid:
            rel_x = vertex[0] - camera.pos[0]
            rel_y = vertex[1] - camera.pos[1]
            rel_z = vertex[2] - camera.pos[2]
            x_proj = dot([rel_x, rel_y, rel_z], camera.right)
            y_proj = dot([rel_x, rel_y, rel_z], camera.up)
            z_proj = dot([rel_x, rel_y, rel_z], camera.forward)
            proj_point = project_point(x_proj, y_proj, z_proj)
            projected_points.append(proj_point if proj_point else None)

        for edge_start, edge_end in edges:
            point1 = projected_points[edge_start]
            point2 = projected_points[edge_end]
            if point1 and point2:
                canvas.create_line(point1[0], point1[1], point2[0], point2[1], fill=color)

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
Strzałki - obrót 
Z/X - roll kamery
Scroll - zoom
"""
tk.Label(frame, text=legend_text, justify="left").grid(row=13, column=0, columnspan=3, pady=5)

root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)
root.bind("<MouseWheel>", zoom)

update()
root.mainloop()
