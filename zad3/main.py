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
N_OBJ = 5

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

light_source = Camera([0, 0, -5])

class Ball:
    def __init__(self, cent, rad, color):
        self.center = cent
        self.radius = rad
        self.color = color
    
    # def makePoints(self):


class Triangle:
    def __init__(self, pts:list[3], color):
        self.pts = pts
        self.norm = self.setNormal()
        self.color = color
        
    def setNormal(self):
        w0 = [self.pts[0][0] - self.pts[1][0], self.pts[0][1] - self.pts[1][1], self.pts[0][2] - self.pts[1][2]]
        w1 = [self.pts[2][0] - self.pts[1][0], self.pts[2][1] - self.pts[1][1], self.pts[2][2] - self.pts[1][2]]
        
        return [w0[1]*w1[2] - w0[2]*w1[1], -1*(w0[0]*w1[2] - w0[2]*w1[0]), w0[0]*w1[1] - w0[1]*w1[0]]    
    
    

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


# class BSPNode:
#     def __init__(self):
#         self.left = None    # za  - minus
#         self.right = None   # przed - plus
#         self.val = []
    
#     def makeNode(self, faces):
#         self.val.append(faces.pop(0))
#         l = []; p = []
#         for face in faces:
#             chk = 0
#             lastOnPlane = None
#             lastPos = -1
#             for point in face.pts:
#                 sum = checkPosition(self.val[0], point)
#                 lastPos = face.pts.index(point) if sum == 1.2 else -1
#                 lastOnPlane = point if sum != 0 else None
#                 chk += sum
#             match chk:
#                 case 30:
#                     # wszystkie "przed"
#                     p.append(face)
#                 case 20:
#                     # 2 "przed" i 1 na płaszczyźnie dzielącej 
#                     p.append(face)
#                 case 10:
#                     # 1 "przed" i 2 na dzielącej 
#                     p.append(face)

#                 # jak wyżej tylko "za"
#                 case -3:
#                     l.append(face)
#                 case -2:
#                     l.append(face)
#                 case -1:
#                     l.append(face)


#                 # wszystkie na płaszczyźnie dzielącej
#                 case 0:
#                     self.val.append(face)
                
                
#                 # jeden punkt na płaszczyźne, dwa po róźnych stronach
#                 case 9: 
#                     pts = [x for x in face.pts if x != lastOnPlane]
#                     t = getT(pts[0], pts[1], self.val[0]) 
#                     nPt = [pts[0][0] + t*(pts[1][0] - pts[0][0]), pts[0][1] + t*(pts[1][1] - pts[0][1]), pts[0][2] + t*(pts[1][2] - pts[0][2])]
#                     match lastOnPlane:
#                         case x if x == face.pts[0]:
#                             if lastPos == 1:
#                                 l.append(Triangle([nPt, pts[1], lastOnPlane], face.color))
#                                 p.append(Triangle([pts[0], nPt, lastOnPlane], face.color))
#                             else:
#                                 p.append(Triangle([nPt, pts[1], lastOnPlane], face.color))
#                                 l.append(Triangle([pts[0], nPt, lastOnPlane], face.color))
#                         case x if x == face.pts[1]:
#                             if lastPos == 0:
#                                 p.append(Triangle([pts[0], lastOnPlane, nPt], face.color))
#                                 l.append(Triangle([nPt, lastOnPlane, pts[1]], face.color))
#                             else:
#                                 l.append(Triangle([pts[0], lastOnPlane, nPt], face.color))
#                                 p.append(Triangle([nPt, lastOnPlane, pts[1]], face.color))
#                         case x if x == face.pts[2]:
#                             if lastPos == 0:
#                                 l.append(Triangle([nPt, pts[1], lastOnPlane], face.color))
#                                 p.append(Triangle([pts[0], nPt, lastOnPlane], face.color))
#                             else:
#                                 p.append(Triangle([nPt, pts[1], lastOnPlane], face.color))
#                                 l.append(Triangle([pts[0], nPt, lastOnPlane], face.color))
                

#                 # dwa przed, jeden za
#                 case 19:
#                     oddOne = [x for x in face.pts if checkPosition(self.val[0], x) < 0][0]
#                     if oddOne == face.pts[0]:
#                         t1 = getT(face.pts[0], face.pts[1], self.val[0])
#                         t2 = getT(face.pts[2], face.pts[0], self.val[0])
#                         nPt1 = [face.pts[0][0] + t1*(face.pts[1][0] - face.pts[0][0]), face.pts[0][1] + t1*(face.pts[1][1] - face.pts[0][1]), face.pts[0][2] + t1*(face.pts[1][2] - face.pts[0][2])]
#                         nPt2 = [face.pts[2][0] + t2*(face.pts[0][0] - face.pts[2][0]), face.pts[2][1] + t2*(face.pts[0][1] - face.pts[2][1]), face.pts[2][2] + t2*(face.pts[0][2] - face.pts[2][2])] 
#                         l.append(Triangle([face.pts[0], nPt1, nPt2], face.color))
#                         p.extend([Triangle([face.pts[1], face.pts[2], nPt2], face.color), Triangle([nPt2, nPt1, face.pts[1]], face.color)])
#                     elif oddOne == face.pts[1]:
#                         t1 = getT(face.pts[0], face.pts[1], self.val[0])
#                         t2 = getT(face.pts[1], face.pts[2], self.val[0])
#                         nPt2 = [face.pts[1][0] + t2*(face.pts[2][0] - face.pts[1][0]), face.pts[1][1] + t2*(face.pts[2][1] - face.pts[1][1]), face.pts[1][2] + t2*(face.pts[2][2] - face.pts[1][2])] 
#                         nPt1 = [face.pts[0][0] + t1*(face.pts[1][0] - face.pts[0][0]), face.pts[0][1] + t1*(face.pts[1][1] - face.pts[0][1]), face.pts[0][2] + t1*(face.pts[1][2] - face.pts[0][2])]
#                         l.append(Triangle([nPt2, nPt1, face.pts[1]], face.color))
#                         p.extend([Triangle([face.pts[2], nPt1, nPt2], face.color), Triangle([face.pts[2], face.pts[0], nPt1], face.color)])
#                     else:
#                         t1 = getT(face.pts[1], face.pts[2], self.val[0])
#                         t2 = getT(face.pts[2], face.pts[0], self.val[0])
#                         nPt1 = [face.pts[1][0] + t1*(face.pts[2][0] - face.pts[1][0]), face.pts[1][1] + t1*(face.pts[2][1] - face.pts[1][1]), face.pts[1][2] + t1*(face.pts[2][2] - face.pts[1][2])]
#                         nPt2 = [face.pts[2][0] + t2*(face.pts[0][0] - face.pts[2][0]), face.pts[2][1] + t2*(face.pts[0][1] - face.pts[2][1]), face.pts[2][2] + t2*(face.pts[0][2] - face.pts[2][2])] 
#                         l.append(Triangle([nPt2, nPt1, face.pts[2]], face.color))
#                         p.extend([Triangle([face.pts[1], nPt1, nPt2], face.color), Triangle([face.pts[0], face.pts[1], nPt2], face.color)])


#                 # dwa za, jeden przed
#                 case 8:
#                     oddOne = [x for x in face.pts if checkPosition(self.val[0], x) > 0][0]
#                     if oddOne == face.pts[0]:
#                         t1 = getT(face.pts[0], face.pts[1], self.val[0])
#                         t2 = getT(face.pts[2], face.pts[0], self.val[0])
#                         nPt1 = [face.pts[0][0] + t1*(face.pts[1][0] - face.pts[0][0]), face.pts[0][1] + t1*(face.pts[1][1] - face.pts[0][1]), face.pts[0][2] + t1*(face.pts[1][2] - face.pts[0][2])]
#                         nPt2 = [face.pts[2][0] + t2*(face.pts[0][0] - face.pts[2][0]), face.pts[2][1] + t2*(face.pts[0][1] - face.pts[2][1]), face.pts[2][2] + t2*(face.pts[0][2] - face.pts[2][2])] 
#                         p.append(Triangle([face.pts[0], nPt1, nPt2], face.color))
#                         l.extend([Triangle([face.pts[1], face.pts[2], nPt2], face.color), Triangle([nPt2, nPt1, face.pts[1]], face.color)])
#                     elif oddOne == face.pts[1]:
#                         t1 = getT(face.pts[0], face.pts[1], self.val[0])
#                         t2 = getT(face.pts[1], face.pts[2], self.val[0])
#                         nPt2 = [face.pts[1][0] + t2*(face.pts[2][0] - face.pts[1][0]), face.pts[1][1] + t2*(face.pts[2][1] - face.pts[1][1]), face.pts[1][2] + t2*(face.pts[2][2] - face.pts[1][2])] 
#                         nPt1 = [face.pts[0][0] + t1*(face.pts[1][0] - face.pts[0][0]), face.pts[0][1] + t1*(face.pts[1][1] - face.pts[0][1]), face.pts[0][2] + t1*(face.pts[1][2] - face.pts[0][2])]
#                         p.append(Triangle([nPt2, nPt1, face.pts[1]], face.color))
#                         l.extend([Triangle([face.pts[2], nPt1, nPt2], face.color), Triangle([face.pts[2], face.pts[0], nPt1], face.color)])
#                     else:
#                         t1 = getT(face.pts[1], face.pts[2], self.val[0])
#                         t2 = getT(face.pts[2], face.pts[0], self.val[0])
#                         nPt1 = [face.pts[1][0] + t1*(face.pts[2][0] - face.pts[1][0]), face.pts[1][1] + t1*(face.pts[2][1] - face.pts[1][1]), face.pts[1][2] + t1*(face.pts[2][2] - face.pts[1][2])]
#                         nPt2 = [face.pts[2][0] + t2*(face.pts[0][0] - face.pts[2][0]), face.pts[2][1] + t2*(face.pts[0][1] - face.pts[2][1]), face.pts[2][2] + t2*(face.pts[0][2] - face.pts[2][2])] 
#                         p.append(Triangle([nPt2, nPt1, face.pts[2]], face.color))
#                         l.extend([Triangle([face.pts[1], nPt1, nPt2], face.color), Triangle([face.pts[0], face.pts[1], nPt2], face.color)]) 
        
#         # dalszy podział
#         if len(l) != 0:
#             self.left = BSPNode()
#             self.left.makeNode(l)
        
#         if len(p) != 0:
#             self.right = BSPNode()
#             self.right.makeNode(p)
    
#     def print(self, n:int, c):
#         for _ in range(n):
#             print(c, end="")
#         print(self.val[0].pts)
#         if(self.left != None):
#             self.left.print(n+1, "-")    
#         if(self.right != None):
#             self.right.print(n+1, "+")


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

# BSProot = BSPNode()
# allFaces = getFaces(cuboids)
# BSProot.makeNode(allFaces)
keys_pressed = set()
button_action = None

def renderFaces(faces:list):
    projected_triangles = []; colors = []
    for tri in faces:
        projected_points = []
        for pt in tri.pts:
            rel_x = pt[0] - light_source.pos[0]
            rel_y = pt[1] - light_source.pos[1]
            rel_z = pt[2] - light_source.pos[2]
            x_proj = dot([rel_x, rel_y, rel_z], light_source.right)
            y_proj = dot([rel_x, rel_y, rel_z], light_source.up)
            z_proj = dot([rel_x, rel_y, rel_z], light_source.forward)
            proj_point = project_point(x_proj, y_proj, z_proj)
            projected_points.append(proj_point if proj_point else None)
        projected_triangles.append(projected_points)
        colors.append(tri.color)

    for tri, color in zip(projected_triangles, colors):
        canvas.create_polygon(tri[0][0], tri[0][1], tri[1][0], tri[1][1], tri[2][0], tri[2][1], fill=color)

# def renderBSPOrder(node:BSPNode):
#     if node == None:
#         return
#     if node.left == None and node.right == None:
#         renderFaces(node.val)
#         return
#     pos = dot(node.val[0].norm, [camera.pos[0] - node.val[0].pts[0][0], camera.pos[1] - node.val[0].pts[0][1], camera.pos[2] - node.val[0].pts[0][2]])
#     if pos >= 0:
#         renderBSPOrder(node.left)
#         renderFaces(node.val)
#         renderBSPOrder(node.right)
#     elif pos < 0:
#         renderBSPOrder(node.right)
#         renderFaces(node.val)
#         renderBSPOrder(node.left)
#     return


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
    global camera_fov
    light_source = Camera([0, 0, -5])
    camera_fov = 500

def cords_update():
    # text.config(state="normal")
    # text.insert("end", "X: "+ str(light_source.pos[0]) + " Y: " + str(light_source.pos[1]) + " Z: " + str(light_source.pos[2]) +"\n")
    # text.config(state="disabled")
    text.set("X: "+ str(light_source.pos[0]) + " Y: " + str(light_source.pos[1]) + " Z: " + str(light_source.pos[2]) +"\n")

def update():
    move_speed = 10
    rotate_speed = 2

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

    canvas.delete("all")

    cords_update()

    canvas.create_oval(100,200,102,202,fill="#aaaaaa")

    # renderBSPOrder(BSProot)    

    root.after(int(1000 / FPS), update)

# GUI
root = tk.Tk()
root.title("Oświetlenie")

frame = tk.Frame(root)
frame.pack(side="right", fill="y", padx=10, pady=10)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#121212")
canvas.pack(side="left")

text = tk.StringVar()
cordLabel = tk.Label(canvas, bg="#121212", fg="#fefefe", textvariable=text)
cordLabel.place(x=2,y=2)
cordLabel.config(font=("Comic Sans", 13))


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

tk.Label(frame, text="Obrót kamery", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=3, pady=10)

create_move_button(5, 0, "↻ w prawo", lambda: light_source.rotate(light_source.up, 5))
create_move_button(5, 2, "↺ w lewo", lambda: light_source.rotate(light_source.up, -5))
create_move_button(6, 0, "↥ w górę", lambda: light_source.rotate(light_source.right, -5))
create_move_button(6, 2, "↧ w dół", lambda: light_source.rotate(light_source.right, 5))
create_move_button(7, 0, "↻ roll prawo", lambda: light_source.rotate(light_source.forward, 5))
create_move_button(7, 2, "↺ roll lewo", lambda: light_source.rotate(light_source.forward, -5))

btn_reset = tk.Button(frame, text="Reset Kamery", font=("Arial", 14), command=reset_camera)
btn_reset.grid(row=8, column=0, columnspan=3, pady=10)

tk.Label(frame, text="Zoom", font=("Arial", 12, "bold")).grid(row=9, column=0, columnspan=3, pady=10)

def create_zoom_button(row, text, action):
    btn = tk.Button(frame, text=text, font=("Arial", 12))
    btn.grid(row=row, column=0, columnspan=3, pady=2)
    btn.bind("<ButtonPress-1>", lambda e: start_moving(action))
    btn.bind("<ButtonRelease-1>", lambda e: stop_moving())


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

update()
root.mainloop()
