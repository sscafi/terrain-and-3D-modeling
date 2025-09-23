#!/usr/bin/env python3
"""
Enhanced Real-Time 3D Terrain Viewer
Adds water simulation and particle effects to the basic viewer.
"""

import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import time
import random


class EnhancedRealtimeViewer:
    """Enhanced real-time 3D terrain viewer with water simulation."""
    
    def __init__(self, width=1000, height=700):
        """Initialize the enhanced viewer."""
        self.width = width
        self.height = height
        self.running = False
        self.clock = pygame.time.Clock()
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Enhanced Real-Time 3D Terrain with Water Simulation")
        
        # Initialize OpenGL
        self._init_opengl()
        
        # Generate terrain
        self.terrain = self._generate_terrain(65)
        self.terrain_size = 65
        
        # Water simulation
        self.water_surface = np.zeros_like(self.terrain)
        self.flow_accumulation = np.zeros_like(self.terrain)
        self.rainfall_active = False
        self.rainfall_intensity = 1.0
        
        # Particles
        self.water_particles = []
        self.max_particles = 1000
        
        # Camera
        self.camera_pos = [0, 8, 15]
        self.camera_target = [0, 0, 0]
        self.camera_up = [0, 1, 0]
        
        # Mouse control
        self.mouse_sensitivity = 0.1
        self.yaw = -90.0
        self.pitch = -20.0
        
        # Simulation state
        self.simulation_running = True
        self.step_count = 0
        
        print("Enhanced Real-Time 3D Terrain Viewer initialized!")
        print("Features: Water simulation, particle effects, real-time terrain generation")
    
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
        
        # Enable blending for particles
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def _generate_terrain(self, size):
        """Generate terrain using Diamond-Square algorithm."""
        terrain = np.random.random((size, size))
        
        # Diamond-Square implementation
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
    
    def _get_terrain_color(self, height, water_depth=0):
        """Get color based on terrain height and water depth."""
        if water_depth > 0.01:
            # Water color with depth
            alpha = min(0.8, water_depth * 2)
            return [0.1, 0.3, 0.8, alpha]
        elif height < 0.3:
            return [0.2, 0.4, 0.8]  # Water - blue
        elif height < 0.5:
            return [0.8, 0.7, 0.4]  # Beach - yellow
        elif height < 0.7:
            return [0.3, 0.7, 0.3]  # Grass - green
        elif height < 0.9:
            return [0.5, 0.5, 0.5]  # Rock - gray
        else:
            return [0.9, 0.9, 0.9]  # Snow - white
    
    def simulate_water_flow(self):
        """Simulate water flow and accumulation."""
        if not self.simulation_running:
            return
        
        # Add rainfall
        if self.rainfall_active:
            rain_mask = np.random.random((self.terrain_size, self.terrain_size)) < 0.3
            self.water_surface += rain_mask * self.rainfall_intensity * 0.1
        
        # Simulate water flow
        new_water = self.water_surface.copy()
        new_flow = self.flow_accumulation.copy()
        
        for y in range(1, self.terrain_size - 1):
            for x in range(1, self.terrain_size - 1):
                if self.water_surface[y, x] > 0.01:
                    # Find steepest descent direction
                    min_height = float('inf')
                    flow_direction = (0, 0)
                    
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dy == 0 and dx == 0:
                                continue
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.terrain_size and 0 <= nx < self.terrain_size:
                                height = self.terrain[ny, nx] + self.water_surface[ny, nx]
                                if height < min_height:
                                    min_height = height
                                    flow_direction = (dy, dx)
                    
                    # Move water downhill
                    if flow_direction != (0, 0):
                        dy, dx = flow_direction
                        ny, nx = y + dy, x + dx
                        
                        flow_amount = min(self.water_surface[y, x], 0.1)
                        new_water[y, x] -= flow_amount
                        new_water[ny, nx] += flow_amount
                        new_flow[ny, nx] += flow_amount
                        
                        # Add water particle
                        if len(self.water_particles) < self.max_particles:
                            self.water_particles.append({
                                'x': x - self.terrain_size//2,
                                'y': self.terrain[y, x] * 5 + self.water_surface[y, x] * 2,
                                'z': y - self.terrain_size//2,
                                'life': 1.0,
                                'velocity': [dx * 0.1, -0.05, dy * 0.1]
                            })
        
        # Evaporation
        self.water_surface = new_water * 0.98
        self.flow_accumulation = new_flow * 0.99
        
        # Update particles
        self._update_particles()
    
    def _update_particles(self):
        """Update particle systems."""
        # Update water particles
        self.water_particles = [p for p in self.water_particles if p['life'] > 0]
        for particle in self.water_particles:
            particle['x'] += particle['velocity'][0]
            particle['y'] += particle['velocity'][1]
            particle['z'] += particle['velocity'][2]
            particle['life'] -= 0.01
    
    def render_terrain(self):
        """Render the terrain with water."""
        size = self.terrain_size
        
        for y in range(size - 1):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range(size):
                # Current row
                height1 = self.terrain[y, x] * 5
                water1 = self.water_surface[y, x]
                color1 = self._get_terrain_color(self.terrain[y, x], water1)
                
                if len(color1) == 4:  # Water with alpha
                    glColor4f(color1[0], color1[1], color1[2], color1[3])
                else:
                    glColor3f(color1[0], color1[1], color1[2])
                
                glVertex3f(x - size//2, height1 + water1 * 2, y - size//2)
                
                # Next row
                height2 = self.terrain[y+1, x] * 5
                water2 = self.water_surface[y+1, x]
                color2 = self._get_terrain_color(self.terrain[y+1, x], water2)
                
                if len(color2) == 4:  # Water with alpha
                    glColor4f(color2[0], color2[1], color2[2], color2[3])
                else:
                    glColor3f(color2[0], color2[1], color2[2])
                
                glVertex3f(x - size//2, height2 + water2 * 2, (y+1) - size//2)
            glEnd()
    
    def render_particles(self):
        """Render water particles."""
        if not self.water_particles:
            return
        
        glPointSize(2.0)
        glColor4f(0.2, 0.6, 1.0, 0.7)
        
        glBegin(GL_POINTS)
        for particle in self.water_particles:
            glVertex3f(particle['x'], particle['y'], particle['z'])
        glEnd()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.terrain = self._generate_terrain(self.terrain_size)
                        self.water_surface.fill(0)
                        self.flow_accumulation.fill(0)
                        self.water_particles.clear()
                        print("Terrain and water reset!")
                    elif event.key == pygame.K_SPACE:
                        self.rainfall_active = not self.rainfall_active
                        print(f"Rainfall {'started' if self.rainfall_active else 'stopped'}")
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.rainfall_intensity = min(5.0, self.rainfall_intensity + 0.5)
                        print(f"Rainfall intensity: {self.rainfall_intensity}")
                    elif event.key == pygame.K_MINUS:
                        self.rainfall_intensity = max(0.1, self.rainfall_intensity - 0.5)
                        print(f"Rainfall intensity: {self.rainfall_intensity}")
                    elif event.key == pygame.K_p:
                        self.simulation_running = not self.simulation_running
                        print(f"Simulation {'paused' if not self.simulation_running else 'resumed'}")
            elif event.type == pygame.MOUSEMOTION:
                # Mouse look
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
        
        # WASD movement
        speed = 0.2
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
        
        # Render terrain with water
        self.render_terrain()
        
        # Render particles
        self.render_particles()
        
        # Swap buffers
        pygame.display.flip()
    
    def run(self):
        """Main application loop."""
        print("Starting Enhanced Real-Time 3D Terrain Viewer...")
        print("Controls:")
        print("  WASD - Move camera")
        print("  Mouse + Left Click - Look around")
        print("  R - Reset terrain and water")
        print("  SPACE - Toggle rainfall")
        print("  +/- - Increase/decrease rainfall intensity")
        print("  P - Pause/resume simulation")
        print("  ESC - Exit")
        
        self.running = True
        
        try:
            while self.running:
                # Handle events
                self.handle_events()
                
                # Update
                self.update_camera()
                self.simulate_water_flow()
                
                # Render
                self.render()
                
                # Control frame rate
                self.clock.tick(60)
                
                # Print stats occasionally
                if self.step_count % 300 == 0:  # Every 5 seconds at 60fps
                    water_total = np.sum(self.water_surface)
                    particles = len(self.water_particles)
                    print(f"Step {self.step_count}: Water={water_total:.2f}, Particles={particles}")
                
                self.step_count += 1
        
        except KeyboardInterrupt:
            print("Application interrupted by user")
        
        finally:
            pygame.quit()
            print("Application closed")


def main():
    """Entry point."""
    try:
        viewer = EnhancedRealtimeViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
