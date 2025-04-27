import tkinter as tk
import math
import random

WIDTH = 800
HEIGHT = 600
FPS = 60

camera_pos = [0, 0, -5]
camera_rot = [0, 0, 0]

keys_pressed = set()
button_action = None

def rotate_point(px, py, pz, rx, ry, rz):
    rx = math.radians(rx)
    ry = math.radians(ry)
    rz = math.radians(rz)

    cosa = math.cos(rx)
    sina = math.sin(rx)
    py, pz = py * cosa - pz * sina, py * sina + pz * cosa

    cosb = math.cos(ry)
    sinb = math.sin(ry)
    px, pz = px * cosb + pz * sinb, -px * sinb + pz * cosb

    cosc = math.cos(rz)
    sinc = math.sin(rz)
    px, py = px * cosc - py * sinc, px * sinc + py * cosc

    return px, py, pz

def project_point(ppx, ppy, ppz):
    if ppz <= 0:
        return None
    fov = 500
    px = WIDTH // 2 + int((ppx * fov) / ppz)
    py = HEIGHT // 2 - int((ppy * fov) / ppz)
    return px, py

def create_cuboid(cx, cy, cz, size_cx, size_cy, size_cz):
    sx = size_cx / 2
    sy = size_cy / 2
    sz = size_cz / 2
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
    keys_pressed.add(event.keysym)

def key_up(event):
    keys_pressed.discard(event.keysym)

def move_camera(dx=0, dy=0, dz=0, drotx=0, droty=0, drotz=0):
    camera_pos[0] += dx
    camera_pos[1] += dy
    camera_pos[2] += dz
    camera_rot[0] += drotx
    camera_rot[1] += droty
    camera_rot[2] += drotz

def reset_camera():
    global camera_pos, camera_rot
    camera_pos = [0, 0, -5]
    camera_rot = [0, 0, 0]

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


def update():
    speed = 0.2
    rot_speed = 3

    if 'w' in keys_pressed:
        camera_pos[2] += speed
    if 's' in keys_pressed:
        camera_pos[2] -= speed
    if 'a' in keys_pressed:
        camera_pos[0] -= speed
    if 'd' in keys_pressed:
        camera_pos[0] += speed
    if 'q' in keys_pressed:
        camera_pos[1] += speed
    if 'e' in keys_pressed:
        camera_pos[1] -= speed
    if 'Up' in keys_pressed:
        camera_rot[0] -= rot_speed
    if 'Down' in keys_pressed:
        camera_rot[0] += rot_speed
    if 'Left' in keys_pressed:
        camera_rot[1] -= rot_speed
    if 'Right' in keys_pressed:
        camera_rot[1] += rot_speed

    canvas.delete("all")

    for cuboid, color in zip(cuboids, colors):
        projected_points = []

        for vertex in cuboid:
            vx = vertex[0] - camera_pos[0]
            vy = vertex[1] - camera_pos[1]
            vz = vertex[2] - camera_pos[2]

            vx, vy, vz = rotate_point(vx, vy, vz, camera_rot[0], camera_rot[1], camera_rot[2])

            proj = project_point(vx, vy, vz)
            projected_points.append(proj if proj else None)

        for edge in edges:
            p1 = projected_points[edge[0]]
            p2 = projected_points[edge[1]]
            if p1 and p2:
                canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=color)

    root.after(int(1000/FPS), update)

# Start GUI
root = tk.Tk()
root.title("Wirtualna Kamera 3D")

frame = tk.Frame(root)
frame.pack(side="right", fill="y", padx=10, pady=10)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack(side="left")

# Panel sterowania
tk.Label(frame, text="Ruch kamery", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=5)

# Funkcja pomocnicza do tworzenia przycisków ruchu
def create_move_button(row, col, text, action):
    btn = tk.Button(frame, text=text, font=("Arial", 14))
    btn.grid(row=row, column=col, padx=5, pady=5)
    btn.bind("<ButtonPress-1>", lambda e: start_moving(action))
    btn.bind("<ButtonRelease-1>", lambda e: stop_moving())

# Przyciski ruchu
create_move_button(1, 1, "↑", lambda: move_camera(dz=1))
create_move_button(3, 1, "↓", lambda: move_camera(dz=-1))
create_move_button(2, 0, "←", lambda: move_camera(dx=-1))
create_move_button(2, 2, "→", lambda: move_camera(dx=1))
create_move_button(1, 0, "⤒", lambda: move_camera(dy=1))
create_move_button(1, 2, "⤓", lambda: move_camera(dy=-1))

tk.Label(frame, text="Obrót kamery", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=3, pady=10)

# Przyciski obrotu
create_move_button(5, 0, "↻ w prawo", lambda: move_camera(droty=5))
create_move_button(5, 2, "↺ w lewo", lambda: move_camera(droty=-5))
create_move_button(6, 0, "↥ w górę", lambda: move_camera(drotx=-5))
create_move_button(6, 2, "↧ w dół", lambda: move_camera(drotx=5))

# Reset kamery
btn_reset = tk.Button(frame, text="Reset Kamery", font=("Arial", 14), command=reset_camera)
btn_reset.grid(row=7, column=0, columnspan=3, pady=10)

# Legenda
tk.Label(frame, text="Legenda:", font=("Arial", 12, "bold")).grid(row=8, column=0, columnspan=3, pady=10)
legend_text = """\
W - przód
S - tył
A - w lewo
D - w prawo
Q - w górę
E - w dół

Strzałki:
↑ ↓ → ←
- obrót kamery
"""
tk.Label(frame, text=legend_text, justify="left").grid(row=9, column=0, columnspan=3, pady=5)

# Obsługa klawiatury
root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)

# Start pętli
update()
root.mainloop()
