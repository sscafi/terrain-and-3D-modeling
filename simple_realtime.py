#!/usr/bin/env python3
"""
Simplified Real-Time 3D Terrain Viewer
A basic version that works with modern OpenGL.
"""

import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import time


class SimpleRealtimeViewer:
    """Simplified real-time 3D terrain viewer."""
    
    def __init__(self, width=800, height=600):
        """Initialize the viewer."""
        self.width = width
        self.height = height
        self.running = False
        self.clock = pygame.time.Clock()
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Simple Real-Time 3D Terrain")
        
        # Initialize OpenGL
        self._init_opengl()
        
        # Generate terrain
        self.terrain = self._generate_terrain(65)
        self.terrain_size = 65
        
        # Camera
        self.camera_pos = [0, 5, 10]
        self.camera_target = [0, 0, 0]
        self.camera_up = [0, 1, 0]
        
        # Mouse control
        self.mouse_sensitivity = 0.1
        self.yaw = -90.0
        self.pitch = 0.0
        
        # Keys
        self.keys_pressed = set()
        
        print("Simple Real-Time 3D Terrain Viewer initialized!")
    
    def _init_opengl(self):
        """Initialize OpenGL settings."""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Set clear color (sky blue)
        glClearColor(0.5, 0.8, 1.0, 1.0)
        
        # Enable face culling
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
    
    def _generate_terrain(self, size):
        """Generate simple terrain using Diamond-Square algorithm."""
        terrain = np.random.random((size, size))
        
        # Simple Diamond-Square implementation
        step_size = size - 1
        roughness = 0.5
        
        while step_size > 1:
            half_step = step_size // 2
            
            # Diamond step
            for x in range(half_step, size, step_size):
                for y in range(half_step, size, step_size):
                    avg = (terrain[x-half_step][y-half_step] +
                           terrain[x+half_step][y-half_step] +
                           terrain[x-half_step][y+half_step] +
                           terrain[x+half_step][y+half_step]) / 4
                    terrain[x][y] = avg + np.random.uniform(-1, 1) * roughness
            
            # Square step
            for x in range(0, size, half_step):
                for y in range((x + half_step) % step_size, size, step_size):
                    avg = 0
                    count = 0
                    if x >= half_step:
                        avg += terrain[x-half_step][y]
                        count += 1
                    if x + half_step < size:
                        avg += terrain[x+half_step][y]
                        count += 1
                    if y >= half_step:
                        avg += terrain[x][y-half_step]
                        count += 1
                    if y + half_step < size:
                        avg += terrain[x][y+half_step]
                        count += 1
                    terrain[x][y] = avg / count + np.random.uniform(-1, 1) * roughness
            
            step_size //= 2
            roughness /= 2
        
        return terrain
    
    def _get_terrain_color(self, height):
        """Get color based on terrain height."""
        if height < 0.3:
            return [0.2, 0.4, 0.8]  # Water - blue
        elif height < 0.5:
            return [0.8, 0.7, 0.4]  # Beach - yellow
        elif height < 0.7:
            return [0.3, 0.7, 0.3]  # Grass - green
        elif height < 0.9:
            return [0.5, 0.5, 0.5]  # Rock - gray
        else:
            return [0.9, 0.9, 0.9]  # Snow - white
    
    def render_terrain(self):
        """Render the terrain as triangles."""
        size = self.terrain_size
        
        for y in range(size - 1):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range(size):
                # Current row
                height1 = self.terrain[y, x] * 5  # Scale height
                color1 = self._get_terrain_color(self.terrain[y, x])
                glColor3f(color1[0], color1[1], color1[2])
                glVertex3f(x - size//2, height1, y - size//2)
                
                # Next row
                height2 = self.terrain[y+1, x] * 5
                color2 = self._get_terrain_color(self.terrain[y+1, x])
                glColor3f(color2[0], color2[1], color2[2])
                glVertex3f(x - size//2, height2, (y+1) - size//2)
            glEnd()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.terrain = self._generate_terrain(self.terrain_size)
                    print("Terrain regenerated!")
                elif event.key == pygame.K_SPACE:
                    print("Space pressed - add your pause/resume logic here")
            elif event.type == pygame.KEYUP:
                pass
            elif event.type == pygame.MOUSEMOTION:
                # Simple mouse look
                if pygame.mouse.get_pressed()[0]:  # Left mouse button
                    dx, dy = event.rel
                    self.yaw += dx * self.mouse_sensitivity
                    self.pitch -= dy * self.mouse_sensitivity
                    self.pitch = max(-89, min(89, self.pitch))
    
    def update_camera(self):
        """Update camera position based on input."""
        # Calculate forward direction
        import math
        forward = [
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        ]
        
        # Simple WASD movement
        speed = 0.1
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            self.camera_pos[0] += forward[0] * speed
            self.camera_pos[1] += forward[1] * speed
            self.camera_pos[2] += forward[2] * speed
        if keys[pygame.K_s]:
            self.camera_pos[0] -= forward[0] * speed
            self.camera_pos[1] -= forward[1] * speed
            self.camera_pos[2] -= forward[2] * speed
        if keys[pygame.K_a]:
            # Strafe left
            right = [-forward[2], 0, forward[0]]
            self.camera_pos[0] += right[0] * speed
            self.camera_pos[2] += right[2] * speed
        if keys[pygame.K_d]:
            # Strafe right
            right = [-forward[2], 0, forward[0]]
            self.camera_pos[0] -= right[0] * speed
            self.camera_pos[2] -= right[2] * speed
        
        # Update target
        self.camera_target = [
            self.camera_pos[0] + forward[0],
            self.camera_pos[1] + forward[1],
            self.camera_pos[2] + forward[2]
        ]
    
    def render(self):
        """Render the 3D scene."""
        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width/self.height, 0.1, 1000.0)
        
        # Set up camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(
            self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
            self.camera_target[0], self.camera_target[1], self.camera_target[2],
            self.camera_up[0], self.camera_up[1], self.camera_up[2]
        )
        
        # Render terrain
        self.render_terrain()
        
        # Swap buffers
        pygame.display.flip()
    
    def run(self):
        """Main application loop."""
        print("Starting Simple Real-Time 3D Terrain Viewer...")
        print("Controls:")
        print("  WASD - Move camera")
        print("  Mouse + Left Click - Look around")
        print("  R - Regenerate terrain")
        print("  ESC - Exit")
        
        self.running = True
        
        try:
            while self.running:
                # Handle events
                self.handle_events()
                
                # Update
                self.update_camera()
                
                # Render
                self.render()
                
                # Control frame rate
                self.clock.tick(60)
        
        except KeyboardInterrupt:
            print("Application interrupted by user")
        
        finally:
            pygame.quit()
            print("Application closed")


def main():
    """Entry point."""
    try:
        viewer = SimpleRealtimeViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
