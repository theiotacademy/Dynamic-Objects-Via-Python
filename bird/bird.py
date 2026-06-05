import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys

pygame.init()
W, H = 900, 700
pygame.display.set_mode((W, H), DOUBLEBUF | OPENGL)
pygame.display.set_caption("3D Bird")
clock = pygame.time.Clock()

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 4.0, 3.0, 0.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 0.95, 0.9, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.3, 0.3,  0.3, 1.0])
    glLightfv(GL_LIGHT1, GL_POSITION, [-2.0, -1.0, -2.0, 0.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE,  [0.25, 0.25, 0.3, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR,  [0.3, 0.3, 0.3, 1.0])
    glMaterialf (GL_FRONT_AND_BACK, GL_SHININESS, 30.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, W/H, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def c(r, g, b):
    glColor3f(r/255, g/255, b/255)

def ellipsoid(rx, ry, rz, sl=20, st=14):
    for i in range(st):
        a0 = math.pi*(-0.5 + i/st)
        a1 = math.pi*(-0.5 + (i+1)/st)
        z0, r0 = math.sin(a0), math.cos(a0)
        z1, r1 = math.sin(a1), math.cos(a1)
        glBegin(GL_QUAD_STRIP)
        for j in range(sl+1):
            lng = 2*math.pi*j/sl
            x, y = math.cos(lng), math.sin(lng)
            glNormal3f(x*r0/rx, y*r0/ry, z0/rz)
            glVertex3f(x*r0*rx,  y*r0*ry,  z0*rz)
            glNormal3f(x*r1/rx, y*r1/ry, z1/rz)
            glVertex3f(x*r1*rx,  y*r1*ry,  z1*rz)
        glEnd()

def cone(r1, r2, length, sl=14):
    glBegin(GL_QUAD_STRIP)
    for i in range(sl+1):
        a = 2*math.pi*i/sl
        cx, cy = math.cos(a), math.sin(a)
        L = math.sqrt(length**2+(r1-r2)**2+0.001)
        glNormal3f(cx*length/L, cy*length/L, (r1-r2)/L)
        glVertex3f(cx*r1, cy*r1, 0)
        glVertex3f(cx*r2, cy*r2, length)
    glEnd()

# ── Single wing (flat, extends along +X from origin) ─────────────────────────
def draw_one_wing():
    # Primary feathers - 6 individual quads from root to tip
    prim_colors = [
        (85,55,25),(80,52,22),(75,48,20),(70,44,18),(65,40,16),(60,36,14)
    ]
    for i in range(6):
        t0 = i/6;     t1 = (i+1)/6
        x0 = 0.22 + t0*1.1;  x1 = 0.22 + t1*1.1
        z0 = -t0*0.35;        z1 = -t1*0.35   # sweep back
        chord0 = 0.22*(1-0.6*t0)
        chord1 = 0.22*(1-0.6*t1)
        co = prim_colors[i]
        c(co[0], co[1], co[2])
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(x0,  chord0*0.25, z0)   # front top
        glVertex3f(x1,  chord1*0.25, z1)
        glVertex3f(x1, -chord1*0.75, z1)   # back bottom
        glVertex3f(x0, -chord0*0.75, z0)
        glEnd()
        # feather gap line
        glDisable(GL_LIGHTING)
        glColor3f(0.2, 0.12, 0.05)
        glBegin(GL_LINES)
        glVertex3f(x1, chord1*0.25, z1)
        glVertex3f(x1,-chord1*0.75, z1)
        glEnd()
        glEnable(GL_LIGHTING)

    # Secondary feathers
    for i in range(5):
        t0 = i/5;     t1 = (i+1)/5
        x0 = 0.22 + t0*0.7;  x1 = 0.22 + t1*0.7
        z0 = -t0*0.20;        z1 = -t1*0.20
        chord0 = 0.18*(1-0.4*t0)
        chord1 = 0.18*(1-0.4*t1)
        c(105, 72, 35)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0.1)
        glVertex3f(x0,  chord0*0.2+0.01, z0)
        glVertex3f(x1,  chord1*0.2+0.01, z1)
        glVertex3f(x1, -chord1*0.8+0.01, z1)
        glVertex3f(x0, -chord0*0.8+0.01, z0)
        glEnd()

    # Covert feathers (on top)
    for i in range(4):
        t0 = i/4;     t1 = (i+1)/4
        x0 = 0.22 + t0*0.45; x1 = 0.22 + t1*0.45
        chord0 = 0.13*(1-0.3*t0)
        chord1 = 0.13*(1-0.3*t1)
        c(128, 90, 45)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(x0,  chord0*0.15+0.02, -t0*0.10)
        glVertex3f(x1,  chord1*0.15+0.02, -t1*0.10)
        glVertex3f(x1, -chord1*0.85+0.02, -t1*0.10)
        glVertex3f(x0, -chord0*0.85+0.02, -t0*0.10)
        glEnd()

def draw_bird(fly_angle, flap_angle):
    glLoadIdentity()
    glTranslatef(0, 0, -4.5)
    glRotatef(30, 1, 0, 0)

    # Match CSS fly keyframe: rotateX(-120deg) rotateZ(fly) rotateX(10deg)
    glRotatef(-120, 1, 0, 0)                              # tilt orbital plane
    glRotatef(-math.degrees(fly_angle), 0, 0, 1)          # orbit on tilted plane (corrected direction)
    glRotatef(10, 1, 0, 0)                                # slight forward pitch

    # Move bird to orbit radius, face pointing along tangent (+Z = forward)
    glTranslatef(0, 1.2, 0)                               # orbit radius
    glRotatef(90, 0, 0, 1)                                # face tangent direction
    glRotatef(90, 1, 0, 0)                                # bird upright (head up)

    # Body bob with flap
    glTranslatef(0, math.sin(flap_angle*2)*0.015, 0)

    # ── BODY ──────────────────────────────────────────────────────────────────
    glPushMatrix()
    c(108, 78, 48)
    ellipsoid(0.20, 0.15, 0.28)
    # belly
    glTranslatef(0, -0.06, 0.03)
    c(205, 180, 138)
    ellipsoid(0.13, 0.10, 0.17)
    glPopMatrix()

    # ── NECK ──────────────────────────────────────────────────────────────────
    glPushMatrix()
    glTranslatef(0, 0.06, 0.20)
    glRotatef(-35, 1, 0, 0)
    c(98, 70, 42)
    cone(0.075, 0.062, 0.15)
    glPopMatrix()

    # ── HEAD ──────────────────────────────────────────────────────────────────
    glPushMatrix()
    glTranslatef(0, 0.12, 0.37)
    glRotatef(-10, 1, 0, 0)
    c(62, 42, 25)
    ellipsoid(0.11, 0.10, 0.11)
    # crown
    glPushMatrix()
    glTranslatef(0, 0.04, 0.01)
    c(135, 100, 60)
    ellipsoid(0.065, 0.050, 0.065)
    glPopMatrix()
    # cheek
    glPushMatrix()
    glTranslatef(0.065, -0.01, 0.025)
    c(180, 155, 115)
    ellipsoid(0.044, 0.038, 0.044)
    glPopMatrix()

    # ── EYES ──────────────────────────────────────────────────────────────────
    for side in [1, -1]:
        glPushMatrix()
        glTranslatef(side*0.085, 0.062, 0.095)
        c(12, 8, 4);     ellipsoid(0.032, 0.028, 0.028)  # ring
        c(238, 230, 215);ellipsoid(0.026, 0.023, 0.023)  # sclera
        glTranslatef(0, 0, 0.012)
        c(175, 115, 25); ellipsoid(0.019, 0.019, 0.010)  # amber iris
        glTranslatef(0, 0, 0.006)
        c(6, 4, 2);      ellipsoid(0.012, 0.012, 0.007)  # pupil
        glTranslatef(side*-0.005, 0.005, 0.003)
        c(255,255,255);  ellipsoid(0.004, 0.004, 0.003)  # shine
        glPopMatrix()

    # ── BEAK ──────────────────────────────────────────────────────────────────
    glPushMatrix()
    glTranslatef(0, -0.012, 0.108)
    glRotatef(20, 1, 0, 0)
    c(205, 178, 72)
    cone(0.028, 0.003, 0.14)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, -0.038, 0.105)
    glRotatef(10, 1, 0, 0)
    c(185, 155, 52)
    cone(0.020, 0.003, 0.09)
    glPopMatrix()
    glPopMatrix()  # end head

    # ── LEFT WING - pivot at left shoulder, rotate around Z ──────────────────
    glPushMatrix()
    glTranslatef(0.22, 0, 0)           # move to left shoulder
    glRotatef(-flap_angle, 0, 0, 1)    # flap up/down around Z axis
    glTranslatef(-0.22, 0, 0)          # move back
    draw_one_wing()
    glPopMatrix()

    # ── RIGHT WING - mirror of left ───────────────────────────────────────────
    glPushMatrix()
    glTranslatef(-0.22, 0, 0)          # move to right shoulder
    glRotatef(flap_angle, 0, 0, 1)     # flap opposite direction
    glTranslatef(0.22, 0, 0)
    glScalef(-1, 1, 1)                 # mirror along X
    draw_one_wing()
    glPopMatrix()

    # ── TAIL ──────────────────────────────────────────────────────────────────
    glPushMatrix()
    glTranslatef(0, 0.02, -0.24)
    glRotatef(18, 1, 0, 0)
    tail_cols = [(68,46,24),(85,60,30),(102,72,36),(115,82,40),(102,72,36),(85,60,30),(68,46,24)]
    for fi in range(7):
        t = (fi-3)/3.5
        sp = t*0.26
        co = tail_cols[fi]
        c(co[0], co[1], co[2])
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(0, 0.2, -1)
        glVertex3f(sp*0.25, 0, 0)
        steps = 12
        for si in range(steps+1):
            s = si/steps
            glVertex3f(sp*s, -0.03*math.sin(math.pi*s), -s*0.42)
        glEnd()
    glPopMatrix()

    # ── LEGS TUCKED ───────────────────────────────────────────────────────────
    for side in [1, -1]:
        glPushMatrix()
        glTranslatef(side*0.06, -0.14, 0.02)
        glRotatef(92, 1, 0, 0)
        c(150, 120, 50)
        cone(0.012, 0.008, 0.10)
        glTranslatef(0, 0, 0.10)
        for ta in [0, 90, 180, 270]:
            glPushMatrix()
            glRotatef(ta, 0, 0, 1)
            glTranslatef(0.012, 0, 0)
            glRotatef(-50, 1, 0, 0)
            c(95, 72, 30)
            cone(0.006, 0.001, 0.06)
            glPopMatrix()
        glPopMatrix()

def draw_wind(now, fly_angle):
    WINDS = [
        (0.0,  0.3, (100,200,180), 1800, 2500),
        (0.3, -0.2, (100,200,220), 2200, 1200),
        (0.5,  0.1, (100,200,100), 1500, 3800),
        (0.2,  0.4, (100,200,240), 2800, 2000),
        (0.6,  0.0, (100,200,150), 1200, 4500),
        (0.1, -0.4, (100,200,200), 2500, 1800),
        (0.4, -0.1, (100,200, 80), 1900, 3200),
        (0.2,  0.5, (100,200,255), 2100, 2700),
        (0.5,  0.2, (100,200,130), 1600, 1500),
        (0.3,  0.6, (100,200,170), 2300, 4000),
    ]
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glLineWidth(2.0)

    # Wind lines rotate with the bird's orbital plane
    glPushMatrix()
    glRotatef(30, 1, 0, 0)           # match camera tilt
    glRotatef(-120, 1, 0, 0)         # match orbital plane tilt
    glRotatef(-math.degrees(fly_angle), 0, 0, 1)  # rotate with bird

    for (ox, oz, rgb, dur, delay) in WINDS:
        t = (now + delay) % dur
        progress = t / dur
        # Wind trails move along the orbit tangent (X axis in local space)
        tx = -2.0 + progress * 5.0
        glBegin(GL_LINES)
        glColor4f(rgb[0]/255, rgb[1]/255, rgb[2]/255, 0.0)
        glVertex3f(tx,       ox, oz)
        glColor4f(rgb[0]/255, rgb[1]/255, rgb[2]/255, 0.45)
        glVertex3f(tx - 1.2, ox, oz)
        glEnd()

    glPopMatrix()
    glLineWidth(1.0)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

def draw_bg():
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(-1,1,-1,1,-1,1)
    glMatrixMode(GL_MODELVIEW);  glPushMatrix(); glLoadIdentity()
    glBegin(GL_QUADS)
    glColor3f(0.78,0.84,1.00); glVertex2f(-1, 1); glVertex2f(1, 1)
    glColor3f(0.92,0.95,1.00); glVertex2f( 1,-1); glVertex2f(-1,-1)
    glEnd()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()
    glEnable(GL_LIGHTING)

def main():
    init()
    fly_period  = 10000
    wing_period = 800   # faster flap = more realistic

    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit(); sys.exit()

        now = pygame.time.get_ticks()
        fly_angle = (now % fly_period) / fly_period * 2 * math.pi

        # Smooth sine wave flap -40 to +40 degrees
        flap_angle = math.sin((now % wing_period) / wing_period * 2 * math.pi) * 40

        draw_bg()
        glClear(GL_DEPTH_BUFFER_BIT)
        draw_wind(now, fly_angle)
        draw_bird(fly_angle, flap_angle)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
