#!/usr/bin/env python3
"""
Real-Time 3D Terrain Viewer
Main application for interactive 3D terrain simulation.
"""

import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import time
from camera_controller import CameraController
from opengl_renderer import OpenGLRenderer
from realtime_simulation import RealtimeSimulation
from gui_controls import GUIControls


class RealTime3DTerrainApp:
    """Main application class for real-time 3D terrain simulation."""
    
    def __init__(self, width=1200, height=800):
        """
        Initialize the real-time 3D terrain application.
        
        Args:
            width (int): Window width
            height (int): Window height
        """
        self.width = width
        self.height = height
        self.running = False
        self.clock = pygame.time.Clock()
        
        # Initialize pygame and OpenGL
        self._init_pygame()
        
        # Initialize components (after OpenGL context is created)
        self.camera = CameraController()
        self.renderer = OpenGLRenderer()
        self.simulation = RealtimeSimulation()
        self.gui = GUIControls(self)
        
        # Initialize OpenGL after context is ready
        self._init_opengl()
        
        # Simulation state
        self.simulation_running = False
        self.simulation_speed = 1.0
        self.paused = False
        
        # Threading
        self.simulation_thread = None
        
        print("Real-Time 3D Terrain Viewer initialized successfully!")
    
    def _init_pygame(self):
        """Initialize pygame and create OpenGL context."""
        pygame.init()
        
        # Set OpenGL attributes
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, 
                                      pygame.GL_CONTEXT_PROFILE_CORE)
        
        # Create window
        self.screen = pygame.display.set_mode((self.width, self.height), 
                                            pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Real-Time 3D Terrain Simulation")
        
        # Enable mouse capture for FPS camera
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
    
    def _init_opengl(self):
        """Initialize OpenGL settings."""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Enable face culling for performance
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # Set clear color (sky blue)
        glClearColor(0.5, 0.8, 1.0, 1.0)
        
        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Set up light
        light_pos = [10.0, 10.0, 10.0, 1.0]
        light_ambient = [0.3, 0.3, 0.3, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        
        # Set up projection matrix (we'll do this in render loop)
        self.projection_matrix = self._create_projection_matrix()
    
    def _create_projection_matrix(self):
        """Create projection matrix for perspective view."""
        import math
        fov = 45.0
        aspect = self.width / self.height
        near = 0.1
        far = 1000.0
        
        # Create perspective projection matrix
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        matrix = [
            f/aspect, 0, 0, 0,
            0, f, 0, 0,
            0, 0, (far+near)/(near-far), -1,
            0, 0, (2*far*near)/(near-far), 0
        ]
        return matrix
    
    def start_simulation_thread(self):
        """Start the simulation thread."""
        if self.simulation_thread is None or not self.simulation_thread.is_alive():
            self.simulation_thread = threading.Thread(target=self._simulation_loop)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
            self.simulation_running = True
            print("Simulation thread started")
    
    def stop_simulation_thread(self):
        """Stop the simulation thread."""
        self.simulation_running = False
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join()
        print("Simulation thread stopped")
    
    def _simulation_loop(self):
        """Main simulation loop running in separate thread."""
        while self.simulation_running:
            if not self.paused:
                # Run one simulation step
                self.simulation.step()
                
                # Update renderer with new data
                self.renderer.update_terrain(self.simulation.get_terrain())
                self.renderer.update_water_surface(self.simulation.get_water_surface())
                self.renderer.update_flow_accumulation(self.simulation.get_flow_accumulation())
            
            # Control simulation speed
            time.sleep(1.0 / (60.0 * self.simulation_speed))
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event.key)
            
            elif event.type == pygame.MOUSEMOTION:
                self.camera.handle_mouse_motion(event.rel)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.camera.handle_mouse_button(event.button, True)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.camera.handle_mouse_button(event.button, False)
    
    def _handle_keydown(self, key):
        """Handle key press events."""
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_SPACE:
            self.paused = not self.paused
            print(f"Simulation {'paused' if self.paused else 'resumed'}")
        elif key == pygame.K_r:
            self.simulation.reset()
            print("Simulation reset")
        elif key == pygame.K_1:
            self.camera.set_mode('fps')
        elif key == pygame.K_2:
            self.camera.set_mode('orbit')
        elif key == pygame.K_3:
            self.camera.set_mode('bird_eye')
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
            self.simulation_speed = min(10.0, self.simulation_speed * 1.5)
            print(f"Simulation speed: {self.simulation_speed:.1f}x")
        elif key == pygame.K_MINUS:
            self.simulation_speed = max(0.1, self.simulation_speed / 1.5)
            print(f"Simulation speed: {self.simulation_speed:.1f}x")
    
    def _handle_keyup(self, key):
        """Handle key release events."""
        pass
    
    def update(self):
        """Update application state."""
        # Update camera
        self.camera.update()
        
        # Update GUI
        self.gui.update()
        
        # Update renderer
        self.renderer.update()
    
    def render(self):
        """Render the 3D scene."""
        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set up projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width/self.height, 0.1, 1000.0)
        
        # Set up camera view
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.camera.apply_transform()
        
        # Render terrain
        self.renderer.render_terrain()
        
        # Render water effects
        self.renderer.render_water_effects()
        
        # Render particle effects
        self.renderer.render_particle_effects()
        
        # Render GUI overlay
        self.gui.render_overlay()
        
        # Swap buffers
        pygame.display.flip()
    
    def run(self):
        """Main application loop."""
        print("Starting Real-Time 3D Terrain Simulation...")
        print("Controls:")
        print("  WASD - Move camera (FPS mode)")
        print("  Mouse - Look around")
        print("  SPACE - Pause/Resume simulation")
        print("  R - Reset simulation")
        print("  1/2/3 - Camera modes (FPS/Orbit/Bird's Eye)")
        print("  +/- - Speed up/slow down simulation")
        print("  ESC - Exit")
        
        self.running = True
        self.start_simulation_thread()
        
        try:
            while self.running:
                # Handle events
                self.handle_events()
                
                # Update
                self.update()
                
                # Render
                self.render()
                
                # Control frame rate
                self.clock.tick(60)
        
        except KeyboardInterrupt:
            print("Application interrupted by user")
        
        finally:
            # Cleanup
            self.stop_simulation_thread()
            pygame.quit()
            print("Application closed")


def main():
    """Entry point for the real-time 3D terrain application."""
    try:
        app = RealTime3DTerrainApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
