#!/usr/bin/env python3
"""
OpenGL Renderer for Real-Time 3D Terrain Viewer
Handles 3D rendering of terrain, water, and particle effects.
"""

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *


class OpenGLRenderer:
    """Handles OpenGL rendering for terrain and effects."""
    
    def __init__(self):
        """Initialize the OpenGL renderer."""
        self.terrain_data = None
        self.water_surface = None
        self.flow_accumulation = None
        self.particles = []
        
        # Terrain rendering
        self.terrain_vertices = None
        self.terrain_normals = None
        self.terrain_colors = None
        self.terrain_size = 0
        
        # Water rendering
        self.water_vertices = None
        self.water_colors = None
        
        # Particle systems
        self.water_particles = []
        self.fire_particles = []
        self.erosion_particles = []
        
        # Rendering settings
        self.wireframe_mode = False
        self.show_water = True
        self.show_particles = True
        
        print("OpenGL Renderer initialized")
    
    def update_terrain(self, terrain_data):
        """Update terrain data and regenerate mesh."""
        if terrain_data is None:
            return
        
        self.terrain_data = terrain_data
        self.terrain_size = terrain_data.shape[0]
        self._generate_terrain_mesh()
    
    def update_water_surface(self, water_surface):
        """Update water surface data."""
        self.water_surface = water_surface
        if water_surface is not None:
            self._generate_water_mesh()
    
    def update_flow_accumulation(self, flow_accumulation):
        """Update flow accumulation data."""
        self.flow_accumulation = flow_accumulation
    
    def _generate_terrain_mesh(self):
        """Generate terrain mesh vertices, normals, and colors."""
        if self.terrain_data is None:
            return
        
        size = self.terrain_size
        vertices = []
        normals = []
        colors = []
        
        # Generate vertices and colors based on height
        for y in range(size):
            for x in range(size):
                # Vertex position
                height = self.terrain_data[y, x]
                vertices.extend([x - size//2, height * 5, y - size//2])  # Scale height
                
                # Color based on height
                if height < 0.3:
                    # Water/low areas - blue
                    colors.extend([0.2, 0.4, 0.8])
                elif height < 0.5:
                    # Beach/sand - yellow
                    colors.extend([0.8, 0.7, 0.4])
                elif height < 0.7:
                    # Grass - green
                    colors.extend([0.3, 0.7, 0.3])
                elif height < 0.9:
                    # Rock - gray
                    colors.extend([0.5, 0.5, 0.5])
                else:
                    # Snow - white
                    colors.extend([0.9, 0.9, 0.9])
        
        # Calculate normals
        for y in range(size):
            for x in range(size):
                # Calculate normal from neighboring heights
                normal = self._calculate_normal(x, y, size)
                normals.extend(normal)
        
        self.terrain_vertices = np.array(vertices, dtype=np.float32)
        self.terrain_normals = np.array(normals, dtype=np.float32)
        self.terrain_colors = np.array(colors, dtype=np.float32)
    
    def _calculate_normal(self, x, y, size):
        """Calculate normal vector for terrain vertex."""
        if x == 0 or x == size-1 or y == 0 or y == size-1:
            return [0, 1, 0]  # Default up normal for edges
        
        # Get neighboring heights
        h_left = self.terrain_data[y, x-1]
        h_right = self.terrain_data[y, x+1]
        h_up = self.terrain_data[y-1, x]
        h_down = self.terrain_data[y+1, x]
        
        # Calculate gradient
        dx = (h_right - h_left) / 2.0
        dy = (h_down - h_up) / 2.0
        
        # Normal vector (pointing up)
        normal = np.array([-dx, 1.0, -dy])
        normal = normal / np.linalg.norm(normal)
        
        return normal.tolist()
    
    def _generate_water_mesh(self):
        """Generate water surface mesh."""
        if self.water_surface is None or self.terrain_data is None:
            return
        
        size = self.terrain_data.shape[0]
        vertices = []
        colors = []
        
        for y in range(size):
            for x in range(size):
                if self.water_surface[y, x] > 0.01:  # Only render where there's water
                    # Water surface height
                    water_height = self.terrain_data[y, x] + self.water_surface[y, x] * 0.5
                    vertices.extend([x - size//2, water_height * 5, y - size//2])
                    
                    # Water color (blue with transparency)
                    alpha = min(1.0, self.water_surface[y, x] * 2.0)
                    colors.extend([0.1, 0.3, 0.8, alpha])
        
        self.water_vertices = np.array(vertices, dtype=np.float32)
        self.water_colors = np.array(colors, dtype=np.float32)
    
    def render_terrain(self):
        """Render the terrain mesh."""
        if self.terrain_vertices is None:
            return
        
        # Set rendering mode
        if self.wireframe_mode:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        # Enable vertex arrays
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        # Set vertex data
        glVertexPointer(3, GL_FLOAT, 0, self.terrain_vertices)
        glNormalPointer(GL_FLOAT, 0, self.terrain_normals)
        glColorPointer(3, GL_FLOAT, 0, self.terrain_colors)
        
        # Render terrain as triangles
        size = self.terrain_size
        for y in range(size - 1):
            glBegin(GL_TRIANGLE_STRIP)
            for x in range(size):
                # Two vertices per column
                glArrayElement(y * size + x)
                glArrayElement((y + 1) * size + x)
            glEnd()
        
        # Disable vertex arrays
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        
        # Reset polygon mode
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    def render_water_effects(self):
        """Render water surface and effects."""
        if not self.show_water or self.water_vertices is None:
            return
        
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Enable vertex arrays
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        
        # Set vertex data
        glVertexPointer(3, GL_FLOAT, 0, self.water_vertices)
        glColorPointer(4, GL_FLOAT, 0, self.water_colors)
        
        # Render water as points (simple for now)
        glPointSize(3.0)
        glDrawArrays(GL_POINTS, 0, len(self.water_vertices) // 3)
        
        # Disable vertex arrays
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        
        # Disable blending
        glDisable(GL_BLEND)
    
    def render_particle_effects(self):
        """Render particle effects (water flow, fire, erosion)."""
        if not self.show_particles:
            return
        
        # Render water flow particles
        self._render_water_particles()
        
        # Render fire particles
        self._render_fire_particles()
        
        # Render erosion particles
        self._render_erosion_particles()
    
    def _render_water_particles(self):
        """Render water flow particles."""
        if not self.water_particles:
            return
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColor4f(0.2, 0.6, 1.0, 0.7)
        glPointSize(2.0)
        
        glBegin(GL_POINTS)
        for particle in self.water_particles:
            glVertex3f(particle['x'], particle['y'], particle['z'])
        glEnd()
        
        glDisable(GL_BLEND)
    
    def _render_fire_particles(self):
        """Render fire particles."""
        if not self.fire_particles:
            return
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        glPointSize(3.0)
        
        glBegin(GL_POINTS)
        for particle in self.fire_particles:
            # Color based on particle life
            life = particle['life']
            glColor4f(1.0, life, 0.0, life)
            glVertex3f(particle['x'], particle['y'], particle['z'])
        glEnd()
        
        glDisable(GL_BLEND)
    
    def _render_erosion_particles(self):
        """Render erosion particles."""
        if not self.erosion_particles:
            return
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glColor4f(0.6, 0.4, 0.2, 0.5)
        glPointSize(1.5)
        
        glBegin(GL_POINTS)
        for particle in self.erosion_particles:
            glVertex3f(particle['x'], particle['y'], particle['z'])
        glEnd()
        
        glDisable(GL_BLEND)
    
    def add_water_particle(self, x, y, z):
        """Add a water flow particle."""
        self.water_particles.append({
            'x': x, 'y': y, 'z': z,
            'life': 1.0,
            'velocity': [0, -0.1, 0]
        })
    
    def add_fire_particle(self, x, y, z):
        """Add a fire particle."""
        self.fire_particles.append({
            'x': x, 'y': y, 'z': z,
            'life': 1.0,
            'velocity': [0, 0.2, 0]
        })
    
    def add_erosion_particle(self, x, y, z):
        """Add an erosion particle."""
        self.erosion_particles.append({
            'x': x, 'y': y, 'z': z,
            'life': 1.0,
            'velocity': [0, -0.05, 0]
        })
    
    def update_particles(self, dt):
        """Update particle systems."""
        # Update water particles
        self.water_particles = [p for p in self.water_particles if p['life'] > 0]
        for particle in self.water_particles:
            particle['x'] += particle['velocity'][0] * dt
            particle['y'] += particle['velocity'][1] * dt
            particle['z'] += particle['velocity'][2] * dt
            particle['life'] -= dt * 0.5
        
        # Update fire particles
        self.fire_particles = [p for p in self.fire_particles if p['life'] > 0]
        for particle in self.fire_particles:
            particle['x'] += particle['velocity'][0] * dt
            particle['y'] += particle['velocity'][1] * dt
            particle['z'] += particle['velocity'][2] * dt
            particle['life'] -= dt * 0.3
        
        # Update erosion particles
        self.erosion_particles = [p for p in self.erosion_particles if p['life'] > 0]
        for particle in self.erosion_particles:
            particle['x'] += particle['velocity'][0] * dt
            particle['y'] += particle['velocity'][1] * dt
            particle['z'] += particle['velocity'][2] * dt
            particle['life'] -= dt * 0.2
    
    def update(self):
        """Update renderer state."""
        # Update particles
        self.update_particles(1.0/60.0)  # Assuming 60 FPS
    
    def toggle_wireframe(self):
        """Toggle wireframe mode."""
        self.wireframe_mode = not self.wireframe_mode
    
    def toggle_water(self):
        """Toggle water rendering."""
        self.show_water = not self.show_water
    
    def toggle_particles(self):
        """Toggle particle effects."""
        self.show_particles = not self.show_particles
