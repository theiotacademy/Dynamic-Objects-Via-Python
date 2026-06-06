import pygame
import numpy as np
import math
import sys
import ctypes

from OpenGL.GL import *
from OpenGL.GL import shaders

# ── Constants ────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
PARTICLES = 13000
RADIUS = 300

# ── Shape Generators ─────────────────────────────────────────
def sphere_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(PARTICLES):
        y = 1 - (i / (PARTICLES - 1)) * 2
        r = math.sqrt(max(0, 1 - y * y))
        theta = golden * i
        pos[i] = [math.cos(theta) * r, y, math.sin(theta) * r]
    return pos.flatten()

def cube_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    for i in range(PARTICLES):
        face = i % 6
        u = (np.random.random() - 0.5) * 2
        v = (np.random.random() - 0.5) * 2
        if   face == 0: pos[i] = [ 1,  u,  v]
        elif face == 1: pos[i] = [-1,  u,  v]
        elif face == 2: pos[i] = [ u,  1,  v]
        elif face == 3: pos[i] = [ u, -1,  v]
        elif face == 4: pos[i] = [ u,  v,  1]
        else:           pos[i] = [ u,  v, -1]
    return pos.flatten()

def triangle_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    h = math.sqrt(3) / 2
    verts = np.array([[0, 1, 0], [-h, -0.5, 0], [h, -0.5, 0]], dtype=np.float32)
    for i in range(PARTICLES):
        r = np.random.random(3)
        r /= r.sum()
        side = 1 if np.random.random() > 0.5 else -1
        p = verts[0]*r[0] + verts[1]*r[1] + verts[2]*r[2]
        p = p * (1 + np.random.random() * 0.1)
        p[2] = side * np.random.random() * 0.05
        pos[i] = p
    return pos.flatten()

def pentagon_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    sides = 5
    for i in range(PARTICLES):
        theta = np.random.random() * math.pi * 2
        phi   = math.acos(2 * np.random.random() - 1)
        sector = int((theta / (math.pi * 2)) * sides)
        t0 = sector * (math.pi * 2 / sides)
        t1 = (sector + 1) * (math.pi * 2 / sides)
        t  = t0 + np.random.random() * (t1 - t0)
        r  = math.cos(math.pi / sides) / math.cos(t - (t0 + t1) / 2)
        sinP = math.sin(phi)
        pos[i] = [math.cos(t)*r*sinP, math.cos(phi), math.sin(t)*r*sinP]
    return pos.flatten()

def star_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    for i in range(PARTICLES):
        theta  = np.random.random() * math.pi * 2
        sector = int(theta / (math.pi * 2) * 10)
        r = (1.0 - np.random.random()*0.15) if sector % 2 == 0 else (0.4 + np.random.random()*0.1)
        phi = math.acos(2 * np.random.random() - 1)
        pos[i] = [math.cos(theta)*r*math.sin(phi), math.cos(phi)*r, math.sin(theta)*r*math.sin(phi)]
    return pos.flatten()

def diamond_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    verts = [[0,1,0],[0,-1,0],[1,0,0],[-1,0,0],[0,0,1],[0,0,-1]]
    faces = [[0,2,4],[0,4,3],[0,3,5],[0,5,2],[1,4,2],[1,3,4],[1,5,3],[1,2,5]]
    for i in range(PARTICLES):
        f = faces[i % len(faces)]
        r = np.random.random(3); r /= r.sum()
        v = np.array(verts[f[0]])*r[0] + np.array(verts[f[1]])*r[1] + np.array(verts[f[2]])*r[2]
        pos[i] = v
    return pos.flatten()

def torus_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    R, r = 0.65, 0.28
    for i in range(PARTICLES):
        u = np.random.random() * math.pi * 2
        v = np.random.random() * math.pi * 2
        pos[i] = [(R + r*math.cos(v))*math.cos(u), (R + r*math.cos(v))*math.sin(u), r*math.sin(v)]
    return pos.flatten()

def helix_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    for i in range(PARTICLES):
        strand = i % 2
        t = (i / PARTICLES) * math.pi * 16
        offset = (strand / 2) * math.pi * 2
        pos[i] = [math.cos(t+offset)*0.55, (i/PARTICLES)*2 - 1, math.sin(t+offset)*0.55]
    return pos.flatten()

def galaxy_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    for i in range(PARTICLES):
        arm = i % 3
        t = np.random.random()
        angle = t * math.pi * 4 + (arm / 3) * math.pi * 2
        radius = t * 0.95 + 0.05
        spread = (1 - t) * 0.15
        pos[i] = [
            math.cos(angle)*radius + (np.random.random()-0.5)*spread,
            (np.random.random()-0.5) * 0.08 * (1 - t),
            math.sin(angle)*radius + (np.random.random()-0.5)*spread
        ]
    return pos.flatten()

def cross_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    for i in range(PARTICLES):
        arm = i % 6
        t = np.random.random()
        w = (np.random.random()-0.5)*0.22
        v = (np.random.random()-0.5)*0.22
        if   arm == 0: pos[i] = [ t,  w,  v]
        elif arm == 1: pos[i] = [-t,  w,  v]
        elif arm == 2: pos[i] = [ w,  t,  v]
        elif arm == 3: pos[i] = [ w, -t,  v]
        elif arm == 4: pos[i] = [ w,  v,  t]
        else:          pos[i] = [ w,  v, -t]
    return pos.flatten()

def heart_positions():
    pos = np.zeros((PARTICLES, 3), dtype=np.float32)
    for i in range(PARTICLES):
        t = np.random.random() * math.pi * 2
        r = 0.8 + np.random.random() * 0.04
        x = r * 16 * math.sin(t)**3 / 17
        y = r * (13*math.cos(t) - 5*math.cos(2*t) - 2*math.cos(3*t) - math.cos(4*t)) / 17
        pos[i] = [x, y - 0.15, (np.random.random()-0.5)*0.12]
    return pos.flatten()

SHAPES = [
    sphere_positions, cube_positions, triangle_positions, pentagon_positions,
    star_positions, diamond_positions, torus_positions, helix_positions,
    galaxy_positions, cross_positions, heart_positions
]

# ── Shaders ──────────────────────────────────────────────────
VERTEX_SHADER = """
#version 330 core

uniform float time;
uniform float radius;
uniform float morphFactor;
uniform float beatScale;
uniform mat4 mvp;
uniform mat4 modelView;

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec3 in_target;

out float vWave;
out float vDepth;
out float vColorT;

void main(){
    vec3 p = mix(in_position, in_target, morphFactor) * beatScale;

    float a1 = atan(p.y + 0.3, p.x + 0.2);
    float a2 = atan(p.z - 0.2, p.y - 0.3);
    float a3 = atan(p.x, p.z);

    float vortex1 = sin(a1 * 14.0 - time * 2.0);
    float vortex2 = sin(a2 * 12.0 + time * 3.0);
    float vortex3 = sin(a3 * 10.0 - time * 4.0);
    float ripple  = sin((p.x + p.y + p.z) * 20.0 - time * 5.0);
    float wave    = vortex1*0.03 + vortex2*0.03 + vortex3*0.03 + ripple*0.02;

    p *= radius * (1.0 + wave);

    vWave   = wave + sin(time + p.x*10.0)*0.2 + cos(time + p.y*10.0)*0.2;
    vColorT = 0.5 + 0.5 * sin(time * 0.3 + p.x * 0.002 + p.y * 0.002);

    vec4 mv = modelView * vec4(p, 1.0);
    vDepth  = -mv.z;

    gl_PointSize = 2.0 + 18.0 / (0.01 * length(mv.xyz));
    gl_Position  = mvp * vec4(p, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 330 core

uniform float colorTime;

in float vWave;
in float vDepth;
in float vColorT;

out vec4 fragColor;

vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d){
    return a + b * cos(6.28318*(c*t+d));
}

void main(){
    vec2 uv = gl_PointCoord - 0.5;
    float d = length(uv);
    if(d > 0.5) discard;

    float glow = smoothstep(0.5, 0.0, d);
    float t  = 0.5 + 0.5 * sin(vDepth * 0.015 + vWave * 50.0);
    float ct = colorTime + vColorT;

    vec3 col1 = palette(ct * 0.1,
        vec3(0.5,0.5,0.5), vec3(0.5,0.5,0.5),
        vec3(1.0,1.0,1.0), vec3(0.0,0.33,0.67));
    vec3 col2 = palette(ct * 0.1 + 0.5,
        vec3(0.5,0.5,0.5), vec3(0.5,0.5,0.5),
        vec3(1.0,1.0,0.5), vec3(0.8,0.9,0.3));

    vec3 color = mix(col1, col2, t);
    fragColor = vec4(color * 1.6, glow);
}
"""

# ── Math helpers ─────────────────────────────────────────────
def perspective(fov_deg, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov_deg) / 2)
    nf = 1.0 / (near - far)
    return np.array([
        [f/aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far+near)*nf, 2*far*near*nf],
        [0, 0, -1, 0]
    ], dtype=np.float32)

def translate(x, y, z):
    m = np.eye(4, dtype=np.float32)
    m[0,3], m[1,3], m[2,3] = x, y, z
    return m

def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4, dtype=np.float32)
    m[1,1]=c; m[1,2]=-s; m[2,1]=s; m[2,2]=c
    return m

def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4, dtype=np.float32)
    m[0,0]=c; m[0,2]=s; m[2,0]=-s; m[2,2]=c
    return m

def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4, dtype=np.float32)
    m[0,0]=c; m[0,1]=-s; m[1,0]=s; m[1,1]=c
    return m

# ── Particle Object ───────────────────────────────────────────
class ParticleObject:
    def __init__(self, prog, base_positions, scale=1.0, rot_y_offset=0.0):
        self.prog  = prog
        self.scale = scale
        self.rx = 0.0
        self.ry = rot_y_offset
        self.rz = 0.0
        self.py = 0.0

        n = len(base_positions) // 3
        pos = base_positions.copy() * scale

        # interleaved: [x,y,z, tx,ty,tz]
        data = np.zeros(n * 6, dtype=np.float32)
        data[0::6] = pos[0::3]
        data[1::6] = pos[1::3]
        data[2::6] = pos[2::3]
        data[3::6] = pos[0::3]
        data[4::6] = pos[1::3]
        data[5::6] = pos[2::3]
        self._data = data
        self.n = n

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_DYNAMIC_DRAW)

        stride = 6 * 4  # 6 floats * 4 bytes
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

        glBindVertexArray(0)

    def update_target(self, new_positions):
        new_scaled = new_positions * self.scale
        self._data[3::6] = new_scaled[0::3]
        self._data[4::6] = new_scaled[1::3]
        self._data[5::6] = new_scaled[2::3]
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, self._data.nbytes, self._data)

    def swap_to_target(self):
        self._data[0::6] = self._data[3::6]
        self._data[1::6] = self._data[4::6]
        self._data[2::6] = self._data[5::6]
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, self._data.nbytes, self._data)

    def render(self, view, proj, t, morph, beat, color_t):
        model = rot_y(self.ry) @ rot_x(self.rx) @ rot_z(self.rz) @ translate(0, self.py, 0)
        mv    = view @ model
        mvp   = proj @ mv

        glUniformMatrix4fv(glGetUniformLocation(self.prog, "mvp"),       1, GL_FALSE, mvp.T)
        glUniformMatrix4fv(glGetUniformLocation(self.prog, "modelView"), 1, GL_FALSE, mv.T)
        glUniform1f(glGetUniformLocation(self.prog, "time"),        t)
        glUniform1f(glGetUniformLocation(self.prog, "radius"),      float(RADIUS))
        glUniform1f(glGetUniformLocation(self.prog, "morphFactor"), morph)
        glUniform1f(glGetUniformLocation(self.prog, "beatScale"),   beat)
        glUniform1f(glGetUniformLocation(self.prog, "colorTime"),   color_t)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, self.n)
        glBindVertexArray(0)

# ── Main ─────────────────────────────────────────────────────
def main():
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
    pygame.display.set_caption("3D Particle Sphere")

    print("OpenGL version:", glGetString(GL_VERSION).decode())

    # Compile shaders
    try:
        vert = shaders.compileShader(VERTEX_SHADER,   GL_VERTEX_SHADER)
        frag = shaders.compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
        prog = shaders.compileProgram(vert, frag)
        print("Shaders compiled OK")
    except Exception as e:
        print("Shader error:", e)
        pygame.quit()
        sys.exit(1)

    glEnable(GL_PROGRAM_POINT_SIZE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # additive blending
    glDisable(GL_DEPTH_TEST)

    w, h = WIDTH, HEIGHT
    glViewport(0, 0, w, h)

    base = sphere_positions()
    obj1 = ParticleObject(prog, base, scale=1.0,  rot_y_offset=0.0)
    obj2 = ParticleObject(prog, base, scale=0.93, rot_y_offset=math.pi/4)

    proj = perspective(60, w/h, 0.1, 3000)
    view = translate(0, 0, -900)

    current_shape_idx = 0
    morph_factor = 0.0
    is_morphing  = False
    mouse_x = mouse_y = 0.0
    rot1 = [0.0, 0.0, 0.0]
    rot2 = [0.0, 0.0, 0.0]

    def do_morph(idx):
        nonlocal is_morphing, morph_factor, current_shape_idx
        if is_morphing:
            return
        is_morphing = True
        current_shape_idx = idx
        obj1.update_target(SHAPES[idx]())
        obj2.update_target(SHAPES[idx]())
        morph_factor = 0.0

    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                do_morph((current_shape_idx + 1) % len(SHAPES))
            elif event.type == pygame.MOUSEMOTION:
                mouse_x = event.pos[0] / w - 0.5
                mouse_y = event.pos[1] / h - 0.5
            elif event.type == pygame.VIDEORESIZE:
                w, h = event.w, event.h
                glViewport(0, 0, w, h)
                proj = perspective(60, w/h, 0.1, 3000)

        t = (pygame.time.get_ticks() - start) / 1000.0

        # Heartbeat
        beat = t % 5
        if   beat < 0.15: beat_scale = 1.0 + beat / 0.15 * 0.08
        elif beat < 0.30: beat_scale = 1.08 - (beat-0.15) / 0.15 * 0.1
        elif beat < 0.45: beat_scale = 0.98 + (beat-0.30) / 0.15 * 0.06
        elif beat < 0.60: beat_scale = 1.04 - (beat-0.45) / 0.15 * 0.04
        else:             beat_scale = 1.0

        # Morph
        if is_morphing:
            morph_factor = min(morph_factor + 0.018, 1.0)
            if morph_factor >= 1.0:
                is_morphing  = False
                morph_factor = 0.0
                obj1.swap_to_target()
                obj2.swap_to_target()

        # Rotations
        rot1[1] += 0.0015;  rot1[0] += 0.0007;  rot1[2] += 0.0004
        rot2[1] -= 0.0012;  rot2[0] += 0.0008;  rot2[2] -= 0.0005
        rot1[1] += mouse_x * 0.0003
        rot1[0] += mouse_y * 0.0003

        float_y = math.sin(t * 0.6) * 15

        obj1.rx, obj1.ry, obj1.rz, obj1.py = rot1[0], rot1[1], rot1[2], float_y
        obj2.rx, obj2.ry, obj2.rz, obj2.py = rot2[0], rot2[1], rot2[2], float_y

        # Render
        glClearColor(18/255, 0, 58/255, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(prog)

        obj1.render(view, proj, t,       morph_factor, beat_scale, t)
        obj2.render(view, proj, t + 2.0, morph_factor, beat_scale, t)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
