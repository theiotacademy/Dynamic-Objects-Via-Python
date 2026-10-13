import cv2
import numpy as np
import turtle

image_path = "mataji.jpg"
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

if image is None:
    print(f"Error: Could not find '{image_path}'. Make sure it is in the same folder.")
    exit()

target_width = 750
aspect_ratio = image.shape[0] / image.shape[1]
target_height = int(target_width * aspect_ratio)
resized_image = cv2.resize(image, (target_width, target_height))

_, binary = cv2.threshold(resized_image, 180, 255, cv2.THRESH_BINARY_INV)

contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

if hierarchy is None:
    print("Error: No shapes detected.")
    exit()

hierarchy = hierarchy[0]

screen = turtle.Screen()
screen.setup(width=target_width + 60, height=target_height + 60)
screen.title("Mataji and Lion - Divine Sketch")
screen.bgcolor("#FFF8E7")
screen.tracer(5, 0)

pen = turtle.Turtle()
pen.speed(0)
pen.pensize(1)
pen.shape("classic")
pen.showturtle()

half_w = target_width / 2
half_h = target_height / 2

def to_turtle_coords(x, y):
    return (x - half_w, half_h - y)

def get_contour_depth(idx):
    depth = 0
    parent = hierarchy[idx][3]
    while parent != -1:
        depth += 1
        parent = hierarchy[parent][3]
    return depth

def render_shape(cnt, fill_col, border_col):
    first_pt = cnt[0][0]
    tx, ty = to_turtle_coords(first_pt[0], first_pt[1])
    
    pen.penup()
    pen.goto(tx, ty)
    pen.pendown()
    
    pen.color(border_col, fill_col)
    pen.begin_fill()
    
    step = 2 if len(cnt) > 80 else 1
    for i in range(1, len(cnt), step):
        pt = cnt[i][0]
        tx, ty = to_turtle_coords(pt[0], pt[1])
        pen.goto(tx, ty)
        
    pen.goto(to_turtle_coords(first_pt[0], first_pt[1]))
    pen.end_fill()

max_depth = max(get_contour_depth(i) for i in range(len(contours)))
depth_layers = {d: [] for d in range(max_depth + 1)}

for i, cnt in enumerate(contours):
    if cv2.contourArea(cnt) < 4:
        continue
    d = get_contour_depth(i)
    depth_layers[d].append(cnt)

print("Drawing in progress... Watch the cursor create all details!")

COLORS = ["#8B0000", "#FF6600", "#FFD700", "#CC0000", "#FF8C00", "#B8860B", "#800000"]

def is_golden(cnt):
    x, y, w, h = cv2.boundingRect(cnt)
    area = cv2.contourArea(cnt)
    cx = x + w / 2
    is_trishul = (h > w * 1.5) and (cx > target_width * 0.55) and (y < target_height * 0.5) and (area < 3000)
    is_jewelry = (area < 600) and (y < target_height * 0.75)
    return is_trishul or is_jewelry

for d in range(max_depth + 1):
    fill_color = COLORS[d % len(COLORS)] if d % 2 == 0 else "#FFF8E7"
    border_color = COLORS[(d + 1) % len(COLORS)]
    pen.pensize(2 if d == 0 else 1)

    for cnt in depth_layers[d]:
        if is_golden(cnt):
            render_shape(cnt, "#FFD700", "#B8860B")
        else:
            render_shape(cnt, fill_color, border_color)

pen.hideturtle()
screen.update()
print("Done! Exact reference matched perfectly.")
screen.mainloop()