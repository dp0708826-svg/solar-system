import cv2
import mediapipe as mp
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import math
import random

# --- Starfield Setup ---
def generate_stars(num_stars=350):
    stars = []
    for _ in range(num_stars):
        # Generate random spherical coordinates for uniform star distribution
        theta = random.uniform(0, 2 * math.pi)
        phi = math.acos(random.uniform(-1, 1))
        r = random.uniform(25.0, 40.0) # stars outer shell
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        stars.append((x, y, z))
    return stars

# --- Pygame & OpenGL Setup ---
def init_opengl(width, height):
    pygame.init()
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Gesture Controlled 3D Solar System")
    
    glEnable(GL_DEPTH_TEST)
    
    # Enable line smoothing for beautiful orbit lines
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (width / height), 0.1, 100.0) # Extended far plane to 100.0
    glMatrixMode(GL_MODELVIEW)
    
    # Configure lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Ambient, diffuse and specular settings
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 0.9, 1.0])    # Soft golden sunlight
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.15, 0.15, 0.15, 1.0]) # Slight ambient light so back sides aren't pitch black

def draw_stars(stars):
    """Draws background stars."""
    glDisable(GL_LIGHTING)
    glBegin(GL_POINTS)
    glColor3f(0.9, 0.9, 1.0)
    for star in stars:
        glVertex3fv(star)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_cube_wireframe(size=9.0):
    """Draws the bounding holographic box shown in the video."""
    s = size
    vertices = [
        [s, s, s], [s, s, -s], [s, -s, -s], [s, -s, s],
        [-s, s, s], [-s, s, -s], [-s, -s, -s], [-s, -s, s]
    ]
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.3, 0.6, 1.0, 0.2) # Light blue transparent color
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

def draw_orbit_ring(distance):
    """Draws a subtle orbit path circle in the XZ plane."""
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glColor4f(0.4, 0.5, 0.7, 0.25) # Semi-transparent bluish orbit lines
    
    glBegin(GL_LINE_LOOP)
    for i in range(100):
        theta = 2.0 * math.pi * i / 100
        glVertex3f(distance * math.cos(theta), 0.0, distance * math.sin(theta))
    glEnd()
    
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

def draw_sphere(radius, color, slices=24, stacks=24):
    """Draws a generic sphere with lighting material color."""
    glColor3fv(color)
    quadric = gluNewQuadric()
    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)

def draw_sun():
    """Draws the Sun with an glowing outer corona."""
    glDisable(GL_LIGHTING)
    quadric = gluNewQuadric()
    
    # 1. Main Sun core
    glColor3f(1.0, 0.85, 0.1) # Bright Golden
    gluSphere(quadric, 0.65, 32, 32)
    
    # 2. Outer glowing corona (blend)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE) # Addive blend
    glColor4f(1.0, 0.5, 0.0, 0.3)     # Orange corona glow
    gluSphere(quadric, 0.78, 32, 32)
    glDisable(GL_BLEND)
    
    gluDeleteQuadric(quadric)
    glEnable(GL_LIGHTING)

def draw_saturn_rings(inner_radius, outer_radius, color):
    """Draws flat Saturn rings with a separation gap."""
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_CULL_FACE)
    
    glPushMatrix()
    glRotatef(90, 1, 0, 0)  # Make flat in XZ plane
    glRotatef(12, 0, 1, 0)  # Aesthetically tilted rings
    
    quadric = gluNewQuadric()
    # Inner main ring
    glColor4f(color[0], color[1], color[2], 0.6)
    gluDisk(quadric, inner_radius, outer_radius, 40, 2)
    
    # Outer thin ring (Cassini Division representation)
    glColor4f(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8, 0.35)
    gluDisk(quadric, outer_radius + 0.06, outer_radius + 0.16, 40, 1)
    
    gluDeleteQuadric(quadric)
    glPopMatrix()
    
    glEnable(GL_CULL_FACE)
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

def draw_jupiter_bands(radius):
    """Draws decorative surface bands around Jupiter's equator."""
    glPushMatrix()
    glRotatef(90, 1, 0, 0) # Align cylinder with equator
    quadric = gluNewQuadric()
    
    # Band 1 (Upper Equator)
    glColor3f(0.5, 0.35, 0.25) # Dark reddish brown band
    glTranslatef(0, 0, -radius * 0.35)
    gluCylinder(quadric, radius * 1.008, radius * 1.008, radius * 0.15, 30, 1)
    
    # Band 2 (Lower Equator)
    glTranslatef(0, 0, radius * 0.55)
    gluCylinder(quadric, radius * 1.008, radius * 1.008, radius * 0.15, 30, 1)
    
    gluDeleteQuadric(quadric)
    glPopMatrix()

# --- Main Application ---
def main():
    width, height = 1024, 768 # Larger window for better visual clarity
    init_opengl(width, height)
    
    stars = generate_stars(350)
    
    # Initialize Webcam and MediaPipe Hand Tracking
    cap = cv2.VideoCapture(0)
    webcam_enabled = cap.isOpened()
    hands = None
    if webcam_enabled:
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    else:
        print("[WARNING] Could not open webcam/camera. Falling back to keyboard and mouse controls.")
        print("Use Left Click + Drag to rotate, Mouse Scroll or Up/Down arrows to Zoom.")
        
    # Planets configuration
    planets = [
        {
            "name": "Earth", 
            "radius": 0.6, 
            "distance": 0.0, 
            "color": (0.2, 0.5, 1.0), 
            "speed": 0.8, 
            "angle": random.uniform(0, 360),
            "moon_radius": 0.15, 
            "moon_distance": 1.6, 
            "moon_color": (0.75, 0.75, 0.75), 
            "moon_speed": 1.5, 
            "moon_angle": 0.0
        }
    ]
    
    # State variables
    rot_x, rot_y = 20.0, 0.0 # start slightly tilted for perspective
    zoom_distance = -5.0
    time_speed = 1.0
    paused = False
    show_box = True
    
    # Mouse drag variables
    mouse_down = False
    last_mouse_pos = (0, 0)
    
    clock = pygame.time.Clock()
    
    # Console Instructions
    print("=" * 60)
    print("        GESTURE CONTROLLED 3D SOLAR SYSTEM SIMULATOR")
    print("=" * 60)
    print("Controls:")
    print("  - Index Finger: Move hand to rotate camera")
    print("  - Mouse Left Click & Drag: Rotate camera (fallback)")
    print("  - Mouse Scroll / Up/Down Arrows: Zoom In / Out")
    print("  - Left/Right Arrows: Rotate camera horizontally")
    print("  - Spacebar: Pause / Resume simulation")
    print("  - [ and ]: Decrease / Increase orbit speed")
    print("  - H: Toggle holographic bounding box")
    print("  - Q or ESC: Exit application")
    print("=" * 60)
    
    while True:
        # 1. Handle Pygame Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if webcam_enabled:
                    cap.release()
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left Click drag start
                    mouse_down = True
                    last_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 4: # Scroll Up (Zoom In)
                    zoom_distance = min(-3.0, zoom_distance + 0.5)
                elif event.button == 5: # Scroll Down (Zoom Out)
                    zoom_distance = max(-30.0, zoom_distance - 0.5)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
                    
            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    x, y = pygame.mouse.get_pos()
                    dx = x - last_mouse_pos[0]
                    dy = y - last_mouse_pos[1]
                    rot_y += dx * 0.5
                    rot_x += dy * 0.5
                    last_mouse_pos = (x, y)
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    if webcam_enabled:
                        cap.release()
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_h:
                    show_box = not show_box
                elif event.key == pygame.K_LEFTBRACKET:
                    time_speed = max(0.0, time_speed - 0.2)
                elif event.key == pygame.K_RIGHTBRACKET:
                    time_speed = min(5.0, time_speed + 0.2)

        # Keyboard Navigation holds
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            zoom_distance = min(-3.0, zoom_distance + 0.15)
        if keys[pygame.K_DOWN]:
            zoom_distance = max(-30.0, zoom_distance - 0.15)
        if keys[pygame.K_LEFT]:
            rot_y -= 1.5
        if keys[pygame.K_RIGHT]:
            rot_y += 1.5

        # Update caption with stats
        status_text = f"3D Solar System | Zoom: {abs(zoom_distance):.1f} | Speed: {time_speed:.1f}x"
        if paused:
            status_text += " [PAUSED]"
        pygame.display.set_caption(status_text)

        # 2. Capture and Process Webcam Frame (if enabled)
        if webcam_enabled:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        index_tip = hand_landmarks.landmark[8]
                        # Interpolate rotation angles smoothly from hand coordinates
                        rot_y = (index_tip.x - 0.5) * 360
                        rot_x = (index_tip.y - 0.5) * 360
                
                cv2.imshow('Hand Gesture Input Feed', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        # Update planetary orbital positions
        if not paused:
            for planet in planets:
                planet["angle"] += planet["speed"] * time_speed
                if "moon_angle" in planet:
                    planet["moon_angle"] += planet["moon_speed"] * time_speed

        # 3. Render 3D Environment (OpenGL)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Position Camera
        glTranslatef(0.0, 0.0, zoom_distance)
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)
        
        # Position the Light Source representing distant sunlight
        glLightfv(GL_LIGHT0, GL_POSITION, [1.5, 0.5, 1.5, 0.0])
        
        # Draw Starfield background
        draw_stars(stars)
        
        # Draw holographic boundary box if active
        if show_box:
            draw_cube_wireframe(9.0)
            
        # Draw Orbits and Planets
        for planet in planets:
            # 1. Draw Moon's Orbit Ring around Earth
            draw_orbit_ring(planet["moon_distance"])
            
            # 2. Draw Planet Sphere
            glPushMatrix()
            angle_rad = math.radians(planet["angle"])
            px = planet["distance"] * math.cos(angle_rad)
            pz = planet["distance"] * math.sin(angle_rad)
            glTranslatef(px, 0.0, pz)
            
            # Local Rotation (self spin)
            self_rot = pygame.time.get_ticks() * 0.05 * planet["speed"] * time_speed
            glRotatef(self_rot, 0, 1, 0)
            
            # Draw sphere
            draw_sphere(planet["radius"], planet["color"])
            
            # Draw Earth's beautiful glowing atmosphere
            glDisable(GL_LIGHTING)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE) # Additive blend
            glColor4f(0.3, 0.6, 1.0, 0.22)   # Blue atmospheric glow
            quadric = gluNewQuadric()
            gluSphere(quadric, planet["radius"] * 1.08, 24, 24)
            gluDeleteQuadric(quadric)
            glDisable(GL_BLEND)
            glEnable(GL_LIGHTING)
            
            # 3. Draw Subcomponents (Moons, Rings, stripes)
            if planet["name"] == "Earth":
                glPushMatrix()
                m_angle_rad = math.radians(planet["moon_angle"])
                mx = planet["moon_distance"] * math.cos(m_angle_rad)
                mz = planet["moon_distance"] * math.sin(m_angle_rad)
                glTranslatef(mx, 0.0, mz)
                draw_sphere(planet["moon_radius"], planet["moon_color"])
                glPopMatrix()
                
            elif planet["name"] == "Jupiter":
                draw_jupiter_bands(planet["radius"])
                
            elif planet["name"] == "Saturn":
                draw_saturn_rings(planet["ring_inner"], planet["ring_outer"], planet["ring_color"])
                
            glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

    if webcam_enabled:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
