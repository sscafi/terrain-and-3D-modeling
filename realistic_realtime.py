#!/usr/bin/env python3
"""
Realistic Real-Time 3D Terrain Viewer
More lifelike terrain and rainfall with GUI controls.
"""

import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
import time
import random
import tkinter as tk
from tkinter import ttk


class RealisticRealtimeViewer:
    """Realistic real-time 3D terrain viewer with lifelike rainfall and GUI controls."""
    
    def __init__(self, width=1200, height=800):
        """Initialize the realistic viewer."""
        self.width = width
        self.height = height
        self.running = False
        self.clock = pygame.time.Clock()
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Realistic Real-Time 3D Terrain with Lifelike Rainfall")
        
        # Initialize OpenGL
        self._init_opengl()
        
        # Terrain parameters (must be set before generating terrain)
        self.terrain_roughness = 0.4
        self.terrain_height_scale = 8.0
        self.terrain_size = 129
        
        # Generate more realistic terrain
        self.terrain = self._generate_realistic_terrain(self.terrain_size)
        
        # Realistic water simulation
        self.water_surface = np.zeros_like(self.terrain)
        self.flow_accumulation = np.zeros_like(self.terrain)
        self.rainfall_active = False
        
        # Realistic rainfall parameters
        self.rainfall_intensity = 0.5
        self.rainfall_coverage = 0.3  # Only 30% of terrain gets rain at once
        self.rainfall_drops = []  # Individual raindrops
        self.max_raindrops = 2000
        
        # Camera
        self.camera_pos = [0, 12, 20]
        self.camera_target = [0, 0, 0]
        self.camera_up = [0, 1, 0]
        
        # Mouse control
        self.mouse_sensitivity = 0.1
        self.yaw = -90.0
        self.pitch = -15.0
        
        # Simulation state
        self.simulation_running = True
        self.step_count = 0
        
        # Create GUI controls
        self._create_gui()
        
        print("Realistic Real-Time 3D Terrain Viewer initialized!")
        print("Features: Lifelike terrain, realistic rainfall, GUI controls")
        print("🎛️  GUI Control Panel should appear on the right side of your screen!")
        print("   If you don't see it, check your taskbar or Alt+Tab to find it.")
    
    def _init_opengl(self):
        """Initialize OpenGL settings."""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Set clear color (realistic sky)
        glClearColor(0.7, 0.8, 0.9, 1.0)
        
        # Enable face culling
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # Enable blending for particles
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def _create_gui(self):
        """Create GUI control panel."""
        self.root = tk.Tk()
        self.root.title("🌧️ Terrain Simulation Controls")
        self.root.geometry("400x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_gui_close)
        
        # Make GUI always on top and more visible
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#f0f0f0')
        
        # Position GUI to the right of the 3D window
        self.root.geometry("400x600+1250+100")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Terrain Controls
        terrain_frame = ttk.LabelFrame(main_frame, text="Terrain Controls", padding="5")
        terrain_frame.pack(fill=tk.X, pady=5)
        
        # Terrain roughness
        ttk.Label(terrain_frame, text="Roughness:").pack(anchor=tk.W)
        self.roughness_var = tk.DoubleVar(value=self.terrain_roughness)
        roughness_scale = ttk.Scale(terrain_frame, from_=0.1, to=1.0, 
                                   variable=self.roughness_var, orient=tk.HORIZONTAL,
                                   command=self._on_roughness_change)
        roughness_scale.pack(fill=tk.X, pady=2)
        self.roughness_label = ttk.Label(terrain_frame, text=f"{self.terrain_roughness:.2f}")
        self.roughness_label.pack(anchor=tk.W)
        
        # Terrain height scale
        ttk.Label(terrain_frame, text="Height Scale:").pack(anchor=tk.W)
        self.height_var = tk.DoubleVar(value=self.terrain_height_scale)
        height_scale = ttk.Scale(terrain_frame, from_=2.0, to=15.0,
                                variable=self.height_var, orient=tk.HORIZONTAL,
                                command=self._on_height_change)
        height_scale.pack(fill=tk.X, pady=2)
        self.height_label = ttk.Label(terrain_frame, text=f"{self.terrain_height_scale:.1f}")
        self.height_label.pack(anchor=tk.W)
        
        # Regenerate terrain button
        ttk.Button(terrain_frame, text="Regenerate Terrain", 
                  command=self._regenerate_terrain).pack(fill=tk.X, pady=5)
        
        # Rainfall Controls
        rain_frame = ttk.LabelFrame(main_frame, text="Rainfall Controls", padding="5")
        rain_frame.pack(fill=tk.X, pady=5)
        
        # Rainfall intensity
        ttk.Label(rain_frame, text="Rainfall Intensity:").pack(anchor=tk.W)
        self.rainfall_intensity_var = tk.DoubleVar(value=self.rainfall_intensity)
        intensity_scale = ttk.Scale(rain_frame, from_=0.0, to=2.0,
                                   variable=self.rainfall_intensity_var, orient=tk.HORIZONTAL,
                                   command=self._on_rainfall_intensity_change)
        intensity_scale.pack(fill=tk.X, pady=2)
        self.intensity_label = ttk.Label(rain_frame, text=f"{self.rainfall_intensity:.2f}")
        self.intensity_label.pack(anchor=tk.W)
        
        # Rainfall coverage
        ttk.Label(rain_frame, text="Rainfall Coverage:").pack(anchor=tk.W)
        self.rainfall_coverage_var = tk.DoubleVar(value=self.rainfall_coverage)
        coverage_scale = ttk.Scale(rain_frame, from_=0.1, to=1.0,
                                  variable=self.rainfall_coverage_var, orient=tk.HORIZONTAL,
                                  command=self._on_rainfall_coverage_change)
        coverage_scale.pack(fill=tk.X, pady=2)
        self.coverage_label = ttk.Label(rain_frame, text=f"{self.rainfall_coverage:.2f}")
        self.coverage_label.pack(anchor=tk.W)
        
        # Rainfall toggle
        self.rainfall_toggle_var = tk.BooleanVar()
        ttk.Checkbutton(rain_frame, text="Enable Rainfall", 
                       variable=self.rainfall_toggle_var,
                       command=self._on_rainfall_toggle).pack(anchor=tk.W, pady=2)
        
        # Simulation Controls
        sim_frame = ttk.LabelFrame(main_frame, text="Simulation Controls", padding="5")
        sim_frame.pack(fill=tk.X, pady=5)
        
        # Pause/Resume
        self.pause_var = tk.BooleanVar()
        ttk.Checkbutton(sim_frame, text="Pause Simulation", 
                       variable=self.pause_var,
                       command=self._on_pause_toggle).pack(anchor=tk.W, pady=2)
        
        # Reset button
        ttk.Button(sim_frame, text="Reset All", 
                  command=self._reset_all).pack(fill=tk.X, pady=5)
        
        # Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=6, width=40)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Start GUI update thread
        self.gui_thread = threading.Thread(target=self._update_gui)
        self.gui_thread.daemon = True
        self.gui_thread.start()
    
    def _generate_realistic_terrain(self, size):
        """Generate more realistic terrain with better detail."""
        # Create base terrain with multiple octaves
        terrain = np.zeros((size, size))
        
        # Multiple noise layers for realistic terrain
        for octave in range(4):
            scale = 2 ** octave
            amplitude = 1.0 / scale
            roughness = self.terrain_roughness * amplitude
            
            # Generate noise at this scale
            octave_terrain = np.random.random((size, size))
            
            # Apply Diamond-Square at this scale
            step_size = size - 1
            while step_size > 1:
                half_step = step_size // 2
                
                # Diamond step
                for x in range(half_step, size, step_size):
                    for y in range(half_step, size, step_size):
                        avg = (octave_terrain[x-half_step][y-half_step] +
                               octave_terrain[x+half_step][y-half_step] +
                               octave_terrain[x-half_step][y+half_step] +
                               octave_terrain[x+half_step][y+half_step]) / 4
                        octave_terrain[x][y] = avg + np.random.uniform(-1, 1) * roughness
                
                # Square step
                for x in range(0, size, half_step):
                    for y in range((x + half_step) % step_size, size, step_size):
                        avg = 0
                        count = 0
                        if x >= half_step:
                            avg += octave_terrain[x-half_step][y]
                            count += 1
                        if x + half_step < size:
                            avg += octave_terrain[x+half_step][y]
                            count += 1
                        if y >= half_step:
                            avg += octave_terrain[x][y-half_step]
                            count += 1
                        if y + half_step < size:
                            avg += octave_terrain[x][y+half_step]
                            count += 1
                        octave_terrain[x][y] = avg / count + np.random.uniform(-1, 1) * roughness
                
                step_size //= 2
                roughness /= 2
            
            # Add this octave to the terrain
            terrain += octave_terrain * amplitude
        
        # Normalize terrain
        terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
        
        # Add some realistic features
        # Create valleys and ridges
        x, y = np.meshgrid(np.linspace(-2, 2, size), np.linspace(-2, 2, size))
        valley_pattern = np.sin(x) * np.cos(y) * 0.1
        terrain += valley_pattern
        
        # Ensure terrain is in valid range
        terrain = np.clip(terrain, 0, 1)
        
        return terrain
    
    def _get_realistic_terrain_color(self, height, water_depth=0):
        """Get realistic terrain colors based on height and water."""
        if water_depth > 0.005:
            # Water with realistic depth
            depth_factor = min(1.0, water_depth * 10)
            return [0.1, 0.4, 0.8, 0.3 + depth_factor * 0.5]
        elif height < 0.2:
            return [0.1, 0.3, 0.7]  # Deep water - dark blue
        elif height < 0.3:
            return [0.8, 0.7, 0.4]  # Beach/sand - light brown
        elif height < 0.4:
            return [0.2, 0.6, 0.2]  # Wet grass - dark green
        elif height < 0.5:
            return [0.3, 0.7, 0.3]  # Grass - green
        elif height < 0.6:
            return [0.4, 0.5, 0.3]  # Forest - dark green
        elif height < 0.7:
            return [0.6, 0.5, 0.4]  # Rocky - brown
        elif height < 0.8:
            return [0.5, 0.5, 0.5]  # Rock - gray
        elif height < 0.9:
            return [0.7, 0.7, 0.7]  # High rock - light gray
        else:
            return [0.9, 0.9, 0.9]  # Snow - white
    
    def _simulate_realistic_rainfall(self):
        """Simulate realistic rainfall with individual raindrops."""
        if not self.rainfall_active or not self.simulation_running:
            return
        
        # Add new raindrops
        if len(self.rainfall_drops) < self.max_raindrops:
            num_new_drops = int(self.rainfall_intensity * 10)
            for _ in range(num_new_drops):
                if random.random() < self.rainfall_coverage:
                    # Random position above terrain
                    x = random.uniform(-self.terrain_size//2, self.terrain_size//2)
                    z = random.uniform(-self.terrain_size//2, self.terrain_size//2)
                    y = random.uniform(15, 25)  # Start high above terrain
                    
                    self.rainfall_drops.append({
                        'x': x, 'y': y, 'z': z,
                        'velocity': [random.uniform(-0.1, 0.1), -random.uniform(0.5, 1.5), random.uniform(-0.1, 0.1)],
                        'life': 1.0,
                        'size': random.uniform(0.5, 1.5)
                    })
        
        # Update raindrops
        for drop in self.rainfall_drops[:]:
            # Move raindrop
            drop['x'] += drop['velocity'][0]
            drop['y'] += drop['velocity'][1]
            drop['z'] += drop['velocity'][2]
            drop['life'] -= 0.02
            
            # Check if raindrop hits terrain
            terrain_x = int(drop['x'] + self.terrain_size//2)
            terrain_z = int(drop['z'] + self.terrain_size//2)
            
            if (0 <= terrain_x < self.terrain_size and 
                0 <= terrain_z < self.terrain_size):
                terrain_height = self.terrain[terrain_z, terrain_x] * self.terrain_height_scale
                
                if drop['y'] <= terrain_height:
                    # Raindrop hits terrain - add water
                    self.water_surface[terrain_z, terrain_x] += self.rainfall_intensity * 0.01
                    self.rainfall_drops.remove(drop)
                    continue
            
            # Remove old raindrops
            if drop['life'] <= 0:
                self.rainfall_drops.remove(drop)
    
    def _simulate_water_flow(self):
        """Simulate realistic water flow."""
        if not self.simulation_running:
            return
        
        # Simulate water flow
        new_water = self.water_surface.copy()
        new_flow = self.flow_accumulation.copy()
        
        for y in range(1, self.terrain_size - 1):
            for x in range(1, self.terrain_size - 1):
                if self.water_surface[y, x] > 0.005:
                    # Find steepest descent direction
                    min_height = float('inf')
                    flow_direction = (0, 0)
                    
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dy == 0 and dx == 0:
                                continue
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.terrain_size and 0 <= nx < self.terrain_size:
                                height = self.terrain[ny, nx] + self.water_surface[ny, nx] * 0.1
                                if height < min_height:
                                    min_height = height
                                    flow_direction = (dy, dx)
                    
                    # Move water downhill
                    if flow_direction != (0, 0):
                        dy, dx = flow_direction
                        ny, nx = y + dy, x + dx
                        
                        flow_amount = min(self.water_surface[y, x], 0.05)
                        new_water[y, x] -= flow_amount
                        new_water[ny, nx] += flow_amount
                        new_flow[ny, nx] += flow_amount
        
        # Evaporation
        self.water_surface = new_water * 0.995
        self.flow_accumulation = new_flow * 0.998
    
    def render_terrain(self):
        """Render realistic terrain with water."""
        size = self.terrain_size
        
        for y in range(size - 1):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range(size):
                # Current row
                height1 = self.terrain[y, x] * self.terrain_height_scale
                water1 = self.water_surface[y, x]
                color1 = self._get_realistic_terrain_color(self.terrain[y, x], water1)
                
                if len(color1) == 4:  # Water with alpha
                    glColor4f(color1[0], color1[1], color1[2], color1[3])
                else:
                    glColor3f(color1[0], color1[1], color1[2])
                
                glVertex3f(x - size//2, height1 + water1 * 0.5, y - size//2)
                
                # Next row
                height2 = self.terrain[y+1, x] * self.terrain_height_scale
                water2 = self.water_surface[y+1, x]
                color2 = self._get_realistic_terrain_color(self.terrain[y+1, x], water2)
                
                if len(color2) == 4:  # Water with alpha
                    glColor4f(color2[0], color2[1], color2[2], color2[3])
                else:
                    glColor3f(color2[0], color2[1], color2[2])
                
                glVertex3f(x - size//2, height2 + water2 * 0.5, (y+1) - size//2)
            glEnd()
    
    def render_raindrops(self):
        """Render individual raindrops."""
        if not self.rainfall_drops:
            return
        
        glPointSize(1.0)
        glColor4f(0.7, 0.8, 1.0, 0.8)
        
        glBegin(GL_POINTS)
        for drop in self.rainfall_drops:
            glVertex3f(drop['x'], drop['y'], drop['z'])
        glEnd()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Toggle rainfall
                    self.rainfall_active = not self.rainfall_active
                    print(f"Rainfall: {'ON' if self.rainfall_active else 'OFF'}")
                elif event.key == pygame.K_r:
                    # Reset all
                    self._reset_all()
                    print("Reset all - new terrain generated!")
                elif event.key == pygame.K_p:
                    # Pause/Resume
                    self.simulation_running = not self.simulation_running
                    print(f"Simulation: {'PAUSED' if not self.simulation_running else 'RUNNING'}")
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    # Increase rainfall intensity
                    self.rainfall_intensity = min(2.0, self.rainfall_intensity + 0.1)
                    print(f"Rainfall intensity: {self.rainfall_intensity:.2f}")
                elif event.key == pygame.K_MINUS:
                    # Decrease rainfall intensity
                    self.rainfall_intensity = max(0.0, self.rainfall_intensity - 0.1)
                    print(f"Rainfall intensity: {self.rainfall_intensity:.2f}")
                elif event.key == pygame.K_t:
                    # Regenerate terrain
                    self._regenerate_terrain()
                    print("New terrain generated!")
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
        speed = 0.3
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
        
        # Render raindrops
        self.render_raindrops()
        
        # Swap buffers
        pygame.display.flip()
    
    # GUI Event Handlers
    def _on_roughness_change(self, value):
        self.terrain_roughness = float(value)
        self.roughness_label.config(text=f"{self.terrain_roughness:.2f}")
    
    def _on_height_change(self, value):
        self.terrain_height_scale = float(value)
        self.height_label.config(text=f"{self.terrain_height_scale:.1f}")
    
    def _on_rainfall_intensity_change(self, value):
        self.rainfall_intensity = float(value)
        self.intensity_label.config(text=f"{self.rainfall_intensity:.2f}")
    
    def _on_rainfall_coverage_change(self, value):
        self.rainfall_coverage = float(value)
        self.coverage_label.config(text=f"{self.rainfall_coverage:.2f}")
    
    def _on_rainfall_toggle(self):
        self.rainfall_active = self.rainfall_toggle_var.get()
    
    def _on_pause_toggle(self):
        self.simulation_running = not self.pause_var.get()
    
    def _regenerate_terrain(self):
        self.terrain = self._generate_realistic_terrain(self.terrain_size)
        self.water_surface.fill(0)
        self.flow_accumulation.fill(0)
        self.rainfall_drops.clear()
    
    def _reset_all(self):
        self.terrain = self._generate_realistic_terrain(self.terrain_size)
        self.water_surface.fill(0)
        self.flow_accumulation.fill(0)
        self.rainfall_drops.clear()
        self.rainfall_active = False
        self.rainfall_toggle_var.set(False)
    
    def _on_gui_close(self):
        self.running = False
        self.root.destroy()
    
    def _update_gui(self):
        """Update GUI statistics."""
        while self.running:
            try:
                if hasattr(self, 'stats_text'):
                    stats = f"""Step: {self.step_count}
Water Total: {np.sum(self.water_surface):.2f}
Max Water: {np.max(self.water_surface):.3f}
Raindrops: {len(self.rainfall_drops)}
Rainfall: {'ON' if self.rainfall_active else 'OFF'}
Simulation: {'RUNNING' if self.simulation_running else 'PAUSED'}
Camera: ({self.camera_pos[0]:.1f}, {self.camera_pos[1]:.1f}, {self.camera_pos[2]:.1f})"""
                    
                    self.stats_text.delete(1.0, tk.END)
                    self.stats_text.insert(1.0, stats)
            except:
                pass
            time.sleep(0.1)
    
    def run(self):
        """Main application loop."""
        print("Starting Realistic Real-Time 3D Terrain Viewer...")
        print("Controls:")
        print("  WASD - Move camera")
        print("  Mouse + Left Click - Look around")
        print("  SPACE - Toggle rainfall on/off")
        print("  R - Reset all (new terrain)")
        print("  P - Pause/Resume simulation")
        print("  +/- - Increase/Decrease rainfall intensity")
        print("  T - Generate new terrain")
        print("  ESC - Exit")
        print("  🎛️  GUI panel should be visible on the right side!")
        
        self.running = True
        
        try:
            while self.running:
                # Handle events
                self.handle_events()
                
                # Update
                self.update_camera()
                self._simulate_realistic_rainfall()
                self._simulate_water_flow()
                
                # Render
                self.render()
                
                # Control frame rate
                self.clock.tick(60)
                
                self.step_count += 1
        
        except KeyboardInterrupt:
            print("Application interrupted by user")
        
        finally:
            pygame.quit()
            if hasattr(self, 'root'):
                self.root.quit()
            print("Application closed")


def main():
    """Entry point."""
    try:
        viewer = RealisticRealtimeViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
