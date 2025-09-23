#!/usr/bin/env python3
"""
Topographic Real-Time 3D Terrain Viewer
Realistic topographic terrain with clear elevation and visible GUI controls.
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
import math


class TopographicRealtimeViewer:
    """Topographic real-time 3D terrain viewer with realistic elevation and visible GUI."""
    
    def __init__(self, width=1200, height=800):
        """Initialize the topographic viewer."""
        self.width = width
        self.height = height
        self.running = False
        self.clock = pygame.time.Clock()
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
        pygame.display.set_caption("Topographic Real-Time 3D Terrain with Realistic Elevation")
        
        # Initialize OpenGL
        self._init_opengl()
        
        # Terrain parameters (must be set before generating terrain)
        self.terrain_roughness = 0.6
        self.terrain_height_scale = 15.0
        self.terrain_size = 129
        
        # Generate realistic topographic terrain
        self.terrain = self._generate_topographic_terrain(self.terrain_size)
        
        # Water simulation
        self.water_surface = np.zeros_like(self.terrain)
        self.flow_accumulation = np.zeros_like(self.terrain)
        self.rainfall_active = False
        
        # Rainfall parameters
        self.rainfall_intensity = 0.3
        self.rainfall_coverage = 0.2  # Only 20% of terrain gets rain at once
        self.rainfall_drops = []
        self.max_raindrops = 1500
        
        # GPS-style visualization parameters
        self.show_contour_lines = False  # Disabled by default for performance
        self.contour_interval = 0.1  # Elevation interval for contour lines
        self.show_elevation_shading = True
        self.elevation_shading_strength = 0.3
        
        # Performance optimization
        self.contour_lines_cache = None
        self.last_terrain_hash = None
        self.frame_count = 0
        
        # Camera
        self.camera_pos = [0, 20, 30]
        self.camera_target = [0, 0, 0]
        self.camera_up = [0, 1, 0]
        
        # Mouse control
        self.mouse_sensitivity = 0.1
        self.yaw = -90.0
        self.pitch = -20.0
        
        # Simulation state
        self.simulation_running = True
        self.step_count = 0
        
        # Create GUI controls
        self._create_gui()
        
        print("Topographic Real-Time 3D Terrain Viewer initialized!")
        print("Features: Realistic topographic terrain, clear elevation, visible GUI controls")
        print("🎛️  GUI Control Panel should appear on the right side of your screen!")
    
    def _init_opengl(self):
        """Initialize OpenGL settings."""
        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Set clear color (modern sky)
        glClearColor(0.8, 0.9, 1.0, 1.0)
        
        # Enable face culling
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # Enable blending for particles
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enable lighting for better depth perception
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [10, 20, 10, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1, 1, 1, 1])
        
        # Material properties
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    def _create_gui(self):
        """Create GUI control panel with better visibility."""
        # Create GUI in a separate thread to avoid blocking
        def create_gui_thread():
            self.root = tk.Tk()
            self.root.title("🗻 Topographic Terrain Controls")
            self.root.geometry("450x700")
            self.root.protocol("WM_DELETE_WINDOW", self._on_gui_close)
            
            # Make GUI highly visible
            self.root.attributes('-topmost', True)
            self.root.configure(bg='#e8f4f8')
            
            # Position GUI to the right of the 3D window
            self.root.geometry("450x700+1250+50")
            
            # Make it more prominent
            self.root.attributes('-alpha', 0.95)
            
            # Main frame
            main_frame = ttk.Frame(self.root, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="🗻 Topographic Terrain Controls", 
                                  font=('Arial', 14, 'bold'))
            title_label.pack(pady=(0, 10))
            
            # Terrain Controls
            terrain_frame = ttk.LabelFrame(main_frame, text="🏔️ Terrain Controls", padding="10")
            terrain_frame.pack(fill=tk.X, pady=5)
            
            # Terrain roughness
            ttk.Label(terrain_frame, text="Roughness (Mountain Detail):").pack(anchor=tk.W)
            self.roughness_var = tk.DoubleVar(value=self.terrain_roughness)
            roughness_scale = ttk.Scale(terrain_frame, from_=0.1, to=1.0, 
                                       variable=self.roughness_var, orient=tk.HORIZONTAL,
                                       command=self._on_roughness_change)
            roughness_scale.pack(fill=tk.X, pady=2)
            self.roughness_label = ttk.Label(terrain_frame, text=f"{self.terrain_roughness:.2f}")
            self.roughness_label.pack(anchor=tk.W)
            
            # Terrain height scale
            ttk.Label(terrain_frame, text="Height Scale (Elevation):").pack(anchor=tk.W)
            self.height_var = tk.DoubleVar(value=self.terrain_height_scale)
            height_scale = ttk.Scale(terrain_frame, from_=5.0, to=25.0,
                                    variable=self.height_var, orient=tk.HORIZONTAL,
                                    command=self._on_height_change)
            height_scale.pack(fill=tk.X, pady=2)
            self.height_label = ttk.Label(terrain_frame, text=f"{self.terrain_height_scale:.1f}")
            self.height_label.pack(anchor=tk.W)
            
            # Regenerate terrain button
            ttk.Button(terrain_frame, text="🔄 Generate New Terrain", 
                      command=self._regenerate_terrain).pack(fill=tk.X, pady=5)
            
            # Rainfall Controls
            rain_frame = ttk.LabelFrame(main_frame, text="🌧️ Rainfall Controls", padding="10")
            rain_frame.pack(fill=tk.X, pady=5)
            
            # Rainfall intensity
            ttk.Label(rain_frame, text="Rainfall Intensity:").pack(anchor=tk.W)
            self.rainfall_intensity_var = tk.DoubleVar(value=self.rainfall_intensity)
            intensity_scale = ttk.Scale(rain_frame, from_=0.0, to=1.0,
                                       variable=self.rainfall_intensity_var, orient=tk.HORIZONTAL,
                                       command=self._on_rainfall_intensity_change)
            intensity_scale.pack(fill=tk.X, pady=2)
            self.intensity_label = ttk.Label(rain_frame, text=f"{self.rainfall_intensity:.2f}")
            self.intensity_label.pack(anchor=tk.W)
            
            # Rainfall coverage
            ttk.Label(rain_frame, text="Rainfall Coverage:").pack(anchor=tk.W)
            self.rainfall_coverage_var = tk.DoubleVar(value=self.rainfall_coverage)
            coverage_scale = ttk.Scale(rain_frame, from_=0.1, to=0.5,
                                      variable=self.rainfall_coverage_var, orient=tk.HORIZONTAL,
                                      command=self._on_rainfall_coverage_change)
            coverage_scale.pack(fill=tk.X, pady=2)
            self.coverage_label = ttk.Label(rain_frame, text=f"{self.rainfall_coverage:.2f}")
            self.coverage_label.pack(anchor=tk.W)
            
            # Rainfall toggle
            self.rainfall_toggle_var = tk.BooleanVar()
            ttk.Checkbutton(rain_frame, text="🌧️ Enable Rainfall", 
                           variable=self.rainfall_toggle_var,
                           command=self._on_rainfall_toggle).pack(anchor=tk.W, pady=2)
            
            # Simulation Controls
            sim_frame = ttk.LabelFrame(main_frame, text="⚙️ Simulation Controls", padding="10")
            sim_frame.pack(fill=tk.X, pady=5)
            
            # Pause/Resume
            self.pause_var = tk.BooleanVar()
            ttk.Checkbutton(sim_frame, text="⏸️ Pause Simulation", 
                           variable=self.pause_var,
                           command=self._on_pause_toggle).pack(anchor=tk.W, pady=2)
            
            # Reset button
            ttk.Button(sim_frame, text="🔄 Reset All", 
                      command=self._reset_all).pack(fill=tk.X, pady=5)
            
            # GPS Visualization Controls
            gps_frame = ttk.LabelFrame(main_frame, text="🗺️ GPS Visualization", padding="10")
            gps_frame.pack(fill=tk.X, pady=5)
            
            # Contour lines toggle
            self.contour_lines_var = tk.BooleanVar(value=self.show_contour_lines)
            ttk.Checkbutton(gps_frame, text="📏 Show Contour Lines", 
                           variable=self.contour_lines_var,
                           command=self._on_contour_lines_toggle).pack(anchor=tk.W, pady=2)
            
            # Elevation shading toggle
            self.elevation_shading_var = tk.BooleanVar(value=self.show_elevation_shading)
            ttk.Checkbutton(gps_frame, text="🌅 Show Elevation Shading", 
                           variable=self.elevation_shading_var,
                           command=self._on_elevation_shading_toggle).pack(anchor=tk.W, pady=2)
            
            # Contour interval
            ttk.Label(gps_frame, text="Contour Interval:").pack(anchor=tk.W)
            self.contour_interval_var = tk.DoubleVar(value=self.contour_interval)
            contour_scale = ttk.Scale(gps_frame, from_=0.05, to=0.3,
                                     variable=self.contour_interval_var, orient=tk.HORIZONTAL,
                                     command=self._on_contour_interval_change)
            contour_scale.pack(fill=tk.X, pady=2)
            self.contour_interval_label = ttk.Label(gps_frame, text=f"{self.contour_interval:.2f}")
            self.contour_interval_label.pack(anchor=tk.W)
            
            # Camera Controls
            camera_frame = ttk.LabelFrame(main_frame, text="📷 Camera Controls", padding="10")
            camera_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(camera_frame, text="WASD - Move camera").pack(anchor=tk.W)
            ttk.Label(camera_frame, text="Mouse + Left Click - Look around").pack(anchor=tk.W)
            ttk.Label(camera_frame, text="ESC - Exit").pack(anchor=tk.W)
            
            # Statistics
            stats_frame = ttk.LabelFrame(main_frame, text="📊 Statistics", padding="10")
            stats_frame.pack(fill=tk.X, pady=5)
            
            self.stats_text = tk.Text(stats_frame, height=8, width=50, font=('Courier', 9))
            self.stats_text.pack(fill=tk.BOTH, expand=True)
            
            # Start the GUI
            self.root.mainloop()
        
        # Start GUI in separate thread
        self.gui_thread = threading.Thread(target=create_gui_thread)
        self.gui_thread.daemon = True
        self.gui_thread.start()
        
        # Give GUI time to initialize
        time.sleep(0.5)
    
    def _generate_topographic_terrain(self, size):
        """Generate realistic topographic terrain with clear elevation differences."""
        # Create base terrain with multiple octaves for realistic detail
        terrain = np.zeros((size, size))
        
        # Multiple noise layers for realistic topographic features
        for octave in range(5):
            scale = 2 ** octave
            amplitude = 1.0 / (scale ** 0.8)  # Slightly different falloff
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
        
        # Add realistic topographic features
        x, y = np.meshgrid(np.linspace(-3, 3, size), np.linspace(-3, 3, size))
        
        # Create mountain ranges
        mountain_pattern = (np.sin(x * 1.5) * np.cos(y * 1.2) + 
                           np.sin(x * 0.8) * np.cos(y * 0.6)) * 0.15
        terrain += mountain_pattern
        
        # Create valleys
        valley_pattern = -np.abs(np.sin(x * 2) * np.cos(y * 2)) * 0.1
        terrain += valley_pattern
        
        # Create some plateaus
        plateau_pattern = np.exp(-(x**2 + y**2) / 4) * 0.2
        terrain += plateau_pattern
        
        # Ensure terrain is in valid range and has good contrast
        terrain = np.clip(terrain, 0, 1)
        
        # Enhance contrast for better elevation visibility
        terrain = terrain ** 0.8  # Slightly compress low values, expand high values
        
        return terrain
    
    def _get_modern_topographic_color(self, height, water_depth=0):
        """Get modern GPS-style topographic colors with vibrant, realistic colors."""
        if water_depth > 0.005:
            # Modern water with depth
            depth_factor = min(1.0, water_depth * 20)
            return [0.1, 0.5, 0.9, 0.5 + depth_factor * 0.4]
        
        # Modern elevation color scheme with better contrast
        if height < 0.1:
            return [0.0, 0.3, 0.7]  # Deep water - vibrant blue
        elif height < 0.2:
            return [0.2, 0.6, 0.9]  # Shallow water - bright blue
        elif height < 0.3:
            return [0.9, 0.8, 0.5]  # Beach - warm sand
        elif height < 0.4:
            return [0.5, 0.8, 0.4]  # Lowland - bright green
        elif height < 0.5:
            return [0.3, 0.8, 0.3]  # Grassland - vibrant green
        elif height < 0.6:
            return [0.2, 0.7, 0.2]  # Forest - deep green
        elif height < 0.7:
            return [0.6, 0.6, 0.4]  # Hills - olive
        elif height < 0.8:
            return [0.7, 0.6, 0.5]  # Mountains - warm brown
        elif height < 0.9:
            return [0.6, 0.6, 0.6]  # High mountains - cool gray
        else:
            return [0.95, 0.95, 0.95]  # Peaks - bright white
    
    def _get_contour_line_color(self, height):
        """Get contour line color based on elevation."""
        if height < 0.3:
            return [0.0, 0.0, 0.0, 0.3]  # Black for low elevations
        elif height < 0.6:
            return [0.3, 0.3, 0.3, 0.4]  # Dark gray for mid elevations
        else:
            return [0.1, 0.1, 0.1, 0.5]  # Very dark for high elevations
    
    def _generate_contour_lines_optimized(self):
        """Generate contour lines with caching for better performance."""
        # Create terrain hash for caching
        terrain_hash = hash(self.terrain.tobytes())
        
        # Use cached contour lines if terrain hasn't changed
        if (self.contour_lines_cache is not None and 
            self.last_terrain_hash == terrain_hash):
            return self.contour_lines_cache
        
        # Generate new contour lines (simplified for performance)
        contour_lines = []
        size = self.terrain_size
        step = max(2, size // 32)  # Reduce resolution for performance
        
        min_height = np.min(self.terrain)
        max_height = np.max(self.terrain)
        
        # Generate fewer contour levels for better performance
        levels = np.arange(min_height, max_height, self.contour_interval * 2)
        
        for level in levels:
            for y in range(0, size - 1, step):
                for x in range(0, size - 1, step):
                    # Check only bottom and right edges for performance
                    h1 = self.terrain[y, x]
                    h2 = self.terrain[y, x + step]
                    h3 = self.terrain[y + step, x]
                    
                    # Bottom edge
                    if (h1 <= level < h2) or (h2 <= level < h1):
                        if h2 != h1:
                            t = (level - h1) / (h2 - h1)
                            px = x + t * step
                            py = y
                            contour_lines.append((px, py, level))
                    
                    # Right edge
                    if (h1 <= level < h3) or (h3 <= level < h1):
                        if h3 != h1:
                            t = (level - h1) / (h3 - h1)
                            px = x
                            py = y + t * step
                            contour_lines.append((px, py, level))
        
        # Cache the results
        self.contour_lines_cache = contour_lines
        self.last_terrain_hash = terrain_hash
        
        return contour_lines
    
    def _apply_elevation_shading(self, base_color, height, normal):
        """Apply GPS-style elevation shading based on surface normal."""
        if not self.show_elevation_shading:
            return base_color
        
        # Calculate shading based on surface normal (simulating light from top-left)
        light_dir = np.array([-0.5, 1.0, -0.5])
        light_dir = light_dir / np.linalg.norm(light_dir)
        
        # Calculate dot product for shading
        shading = max(0.1, np.dot(normal, light_dir))
        
        # Apply shading to base color
        shaded_color = [c * (0.3 + 0.7 * shading) for c in base_color[:3]]
        if len(base_color) == 4:
            shaded_color.append(base_color[3])
        
        return shaded_color
    
    def _simulate_realistic_rainfall(self):
        """Simulate realistic rainfall with individual raindrops."""
        if not self.rainfall_active or not self.simulation_running:
            return
        
        # Add new raindrops
        if len(self.rainfall_drops) < self.max_raindrops:
            num_new_drops = int(self.rainfall_intensity * 8)
            for _ in range(num_new_drops):
                if random.random() < self.rainfall_coverage:
                    # Random position above terrain
                    x = random.uniform(-self.terrain_size//2, self.terrain_size//2)
                    z = random.uniform(-self.terrain_size//2, self.terrain_size//2)
                    y = random.uniform(20, 35)  # Start high above terrain
                    
                    self.rainfall_drops.append({
                        'x': x, 'y': y, 'z': z,
                        'velocity': [random.uniform(-0.2, 0.2), -random.uniform(0.8, 2.0), random.uniform(-0.2, 0.2)],
                        'life': 1.0,
                        'size': random.uniform(0.8, 1.5)
                    })
        
        # Update raindrops
        for drop in self.rainfall_drops[:]:
            # Move raindrop
            drop['x'] += drop['velocity'][0]
            drop['y'] += drop['velocity'][1]
            drop['z'] += drop['velocity'][2]
            drop['life'] -= 0.015
            
            # Check if raindrop hits terrain
            terrain_x = int(drop['x'] + self.terrain_size//2)
            terrain_z = int(drop['z'] + self.terrain_size//2)
            
            if (0 <= terrain_x < self.terrain_size and 
                0 <= terrain_z < self.terrain_size):
                terrain_height = self.terrain[terrain_z, terrain_x] * self.terrain_height_scale
                
                if drop['y'] <= terrain_height:
                    # Raindrop hits terrain - add water
                    self.water_surface[terrain_z, terrain_x] += self.rainfall_intensity * 0.008
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
                if self.water_surface[y, x] > 0.003:
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
                        
                        flow_amount = min(self.water_surface[y, x], 0.03)
                        new_water[y, x] -= flow_amount
                        new_water[ny, nx] += flow_amount
                        new_flow[ny, nx] += flow_amount
        
        # Evaporation
        self.water_surface = new_water * 0.992
        self.flow_accumulation = new_flow * 0.995
    
    def render_terrain(self):
        """Render modern GPS-style topographic terrain with optimized performance."""
        size = self.terrain_size
        
        # Render terrain with modern colors and optimized shading
        for y in range(size - 1):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range(size):
                # Current row
                height1 = self.terrain[y, x] * self.terrain_height_scale
                water1 = self.water_surface[y, x]
                base_color1 = self._get_modern_topographic_color(self.terrain[y, x], water1)
                
                # Simplified shading calculation for better performance
                if self.show_elevation_shading and x > 0 and y > 0 and x < size-1 and y < size-1:
                    # Calculate simple gradient for shading
                    dx = self.terrain[y, x+1] - self.terrain[y, x-1]
                    dy = self.terrain[y+1, x] - self.terrain[y-1, x]
                    shading = 0.5 + 0.5 * (dx + dy) * 0.5  # Simplified shading
                    shading = max(0.2, min(1.0, shading))
                    
                    # Apply shading to color
                    color1 = [c * shading for c in base_color1[:3]]
                    if len(base_color1) == 4:
                        color1.append(base_color1[3])
                else:
                    color1 = base_color1
                
                if len(color1) == 4:  # Water with alpha
                    glColor4f(color1[0], color1[1], color1[2], color1[3])
                else:
                    glColor3f(color1[0], color1[1], color1[2])
                
                glVertex3f(x - size//2, height1 + water1 * 0.3, y - size//2)
                
                # Next row
                height2 = self.terrain[y+1, x] * self.terrain_height_scale
                water2 = self.water_surface[y+1, x]
                base_color2 = self._get_modern_topographic_color(self.terrain[y+1, x], water2)
                
                # Simplified shading calculation for better performance
                if self.show_elevation_shading and x > 0 and y+1 > 0 and x < size-1 and y+1 < size-1:
                    dx = self.terrain[y+1, x+1] - self.terrain[y+1, x-1]
                    dy = self.terrain[y+2, x] - self.terrain[y, x]
                    shading = 0.5 + 0.5 * (dx + dy) * 0.5  # Simplified shading
                    shading = max(0.2, min(1.0, shading))
                    
                    # Apply shading to color
                    color2 = [c * shading for c in base_color2[:3]]
                    if len(base_color2) == 4:
                        color2.append(base_color2[3])
                else:
                    color2 = base_color2
                
                if len(color2) == 4:  # Water with alpha
                    glColor4f(color2[0], color2[1], color2[2], color2[3])
                else:
                    glColor3f(color2[0], color2[1], color2[2])
                
                glVertex3f(x - size//2, height2 + water2 * 0.3, (y+1) - size//2)
            glEnd()
    
    def render_contour_lines(self):
        """Render optimized GPS-style contour lines."""
        if not self.show_contour_lines:
            return
        
        # Only generate contour lines every few frames for performance
        if self.frame_count % 10 != 0:
            return
        
        contour_lines = self._generate_contour_lines_optimized()
        if not contour_lines:
            return
        
        # Render contour lines with better performance
        glLineWidth(1.5)
        glDisable(GL_LIGHTING)  # Disable lighting for contour lines
        
        # Render in batches for better performance
        glBegin(GL_LINES)
        for px, py, level in contour_lines:
            height = level * self.terrain_height_scale
            color = self._get_contour_line_color(level)
            
            glColor4f(color[0], color[1], color[2], color[3])
            # Draw contour line segments
            glVertex3f(px - self.terrain_size//2, height + 0.1, py - self.terrain_size//2)
            glVertex3f(px - self.terrain_size//2 + 1.0, height + 0.1, py - self.terrain_size//2)
        glEnd()
        
        glEnable(GL_LIGHTING)  # Re-enable lighting
    
    def render_raindrops(self):
        """Render individual raindrops."""
        if not self.rainfall_drops:
            return
        
        glPointSize(1.5)
        glColor4f(0.7, 0.8, 1.0, 0.9)
        
        glBegin(GL_POINTS)
        for drop in self.rainfall_drops:
            glVertex3f(drop['x'], drop['y'], drop['z'])
        glEnd()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
                glViewport(0, 0, self.width, self.height)
                print(f"Window resized to {self.width}x{self.height}")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Toggle rainfall
                    self.rainfall_active = not self.rainfall_active
                    print(f"🌧️ Rainfall: {'ON' if self.rainfall_active else 'OFF'}")
                elif event.key == pygame.K_r:
                    # Reset all
                    self._reset_all()
                    print("🔄 Reset all - new terrain generated!")
                elif event.key == pygame.K_p:
                    # Pause/Resume
                    self.simulation_running = not self.simulation_running
                    print(f"⏸️ Simulation: {'PAUSED' if not self.simulation_running else 'RUNNING'}")
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    # Increase rainfall intensity
                    self.rainfall_intensity = min(1.0, self.rainfall_intensity + 0.1)
                    print(f"🌧️ Rainfall intensity: {self.rainfall_intensity:.2f}")
                elif event.key == pygame.K_MINUS:
                    # Decrease rainfall intensity
                    self.rainfall_intensity = max(0.0, self.rainfall_intensity - 0.1)
                    print(f"🌧️ Rainfall intensity: {self.rainfall_intensity:.2f}")
                elif event.key == pygame.K_t:
                    # Regenerate terrain
                    self._regenerate_terrain()
                    print("🏔️ New terrain generated!")
                elif event.key == pygame.K_h:
                    # Show help
                    self._show_help()
                elif event.key == pygame.K_F11:
                    # Toggle fullscreen
                    self._toggle_fullscreen()
                elif event.key == pygame.K_1:
                    # Set window size to 800x600
                    self._set_window_size(800, 600)
                elif event.key == pygame.K_2:
                    # Set window size to 1024x768
                    self._set_window_size(1024, 768)
                elif event.key == pygame.K_3:
                    # Set window size to 1280x720
                    self._set_window_size(1280, 720)
                elif event.key == pygame.K_4:
                    # Set window size to 1920x1080
                    self._set_window_size(1920, 1080)
                elif event.key == pygame.K_c:
                    # Toggle contour lines
                    self.show_contour_lines = not self.show_contour_lines
                    if hasattr(self, 'contour_lines_var'):
                        self.contour_lines_var.set(self.show_contour_lines)
                    print(f"📏 Contour lines: {'ON' if self.show_contour_lines else 'OFF'}")
                elif event.key == pygame.K_s:
                    # Toggle elevation shading
                    self.show_elevation_shading = not self.show_elevation_shading
                    if hasattr(self, 'elevation_shading_var'):
                        self.elevation_shading_var.set(self.show_elevation_shading)
                    print(f"🌅 Elevation shading: {'ON' if self.show_elevation_shading else 'OFF'}")
            elif event.type == pygame.MOUSEMOTION:
                # Mouse look
                if pygame.mouse.get_pressed()[0]:  # Left mouse button
                    dx, dy = event.rel
                    self.yaw += dx * self.mouse_sensitivity
                    self.pitch -= dy * self.mouse_sensitivity
                    self.pitch = max(-89, min(89, self.pitch))
    
    def _show_help(self):
        """Show help information."""
        print("\n" + "="*50)
        print("🗻 TOPOGRAPHIC TERRAIN CONTROLS")
        print("="*50)
        print("WASD - Move camera")
        print("Mouse + Left Click - Look around")
        print("SPACE - Toggle rainfall on/off")
        print("R - Reset all (new terrain)")
        print("P - Pause/Resume simulation")
        print("+/- - Increase/Decrease rainfall intensity")
        print("T - Generate new terrain")
        print("H - Show this help")
        print("ESC - Exit")
        print("")
        print("🗺️  GPS VISUALIZATION:")
        print("C - Toggle contour lines")
        print("S - Toggle elevation shading")
        print("")
        print("🖼️  WINDOW CONTROLS:")
        print("F11 - Toggle fullscreen")
        print("1 - Set window to 800x600")
        print("2 - Set window to 1024x768")
        print("3 - Set window to 1280x720")
        print("4 - Set window to 1920x1080")
        print("Drag corners - Resize window manually")
        print("")
        print("🎛️  GUI panel should be visible on the right side!")
        print("="*50)
    
    def update_camera(self):
        """Update camera position based on input."""
        # Calculate forward direction
        forward = [
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        ]
        
        # WASD movement
        speed = 0.4
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
        
        # Render contour lines
        self.render_contour_lines()
        
        # Render raindrops
        self.render_raindrops()
        
        # Increment frame counter for performance optimization
        self.frame_count += 1
        
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
    
    def _on_contour_lines_toggle(self):
        self.show_contour_lines = self.contour_lines_var.get()
    
    def _on_elevation_shading_toggle(self):
        self.show_elevation_shading = self.elevation_shading_var.get()
    
    def _on_contour_interval_change(self, value):
        self.contour_interval = float(value)
        self.contour_interval_label.config(text=f"{self.contour_interval:.2f}")
    
    def _regenerate_terrain(self):
        self.terrain = self._generate_topographic_terrain(self.terrain_size)
        self.water_surface.fill(0)
        self.flow_accumulation.fill(0)
        self.rainfall_drops.clear()
        # Clear contour line cache
        self.contour_lines_cache = None
        self.last_terrain_hash = None
    
    def _reset_all(self):
        self.terrain = self._generate_topographic_terrain(self.terrain_size)
        self.water_surface.fill(0)
        self.flow_accumulation.fill(0)
        self.rainfall_drops.clear()
        self.rainfall_active = False
        # Clear contour line cache
        self.contour_lines_cache = None
        self.last_terrain_hash = None
        if hasattr(self, 'rainfall_toggle_var'):
            self.rainfall_toggle_var.set(False)
    
    def _on_gui_close(self):
        self.running = False
        if hasattr(self, 'root'):
            self.root.quit()
    
    def _toggle_fullscreen(self):
        """Toggle between windowed and fullscreen mode."""
        if self.screen.get_flags() & pygame.FULLSCREEN:
            # Switch to windowed
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
            print("Switched to windowed mode")
        else:
            # Switch to fullscreen
            self.screen = pygame.display.set_mode((0, 0), pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN)
            self.width, self.height = self.screen.get_size()
            glViewport(0, 0, self.width, self.height)
            print(f"Switched to fullscreen mode: {self.width}x{self.height}")
    
    def _set_window_size(self, width, height):
        """Set window to specific size."""
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
        glViewport(0, 0, self.width, self.height)
        print(f"Window size set to {self.width}x{self.height}")
    
    def _update_gui(self):
        """Update GUI statistics."""
        while self.running:
            try:
                if hasattr(self, 'stats_text'):
                    max_height = np.max(self.terrain) * self.terrain_height_scale
                    min_height = np.min(self.terrain) * self.terrain_height_scale
                    elevation_range = max_height - min_height
                    
                    stats = f"""Step: {self.step_count}
Elevation Range: {elevation_range:.1f}m
Max Height: {max_height:.1f}m
Min Height: {min_height:.1f}m
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
        print("Starting Topographic Real-Time 3D Terrain Viewer...")
        self._show_help()
        
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
        viewer = TopographicRealtimeViewer()
        viewer.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
