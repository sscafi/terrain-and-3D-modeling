#!/usr/bin/env python3
"""
Water Flow Simulation Module
Implements rainfall simulation, flow accumulation, and river network generation.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import random
from collections import defaultdict, deque


class WaterSimulation:
    """Handles water flow simulation on terrain."""
    
    def __init__(self, terrain, rainfall_intensity=1.0, evaporation_rate=0.1):
        """
        Initialize water simulation.
        
        Args:
            terrain (numpy.ndarray): 2D height map
            rainfall_intensity (float): Amount of water per rainfall event
            evaporation_rate (float): Rate of water evaporation per time step
        """
        self.terrain = terrain
        self.height, self.width = terrain.shape
        self.rainfall_intensity = rainfall_intensity
        self.evaporation_rate = evaporation_rate
        
        # Water state arrays
        self.water_surface = np.zeros_like(terrain)  # Water depth at each cell
        self.flow_accumulation = np.zeros_like(terrain)  # Total water that has flowed through
        self.river_network = np.zeros_like(terrain)  # River network mask
        
        # Flow direction map (8-directional)
        self.flow_directions = self._calculate_flow_directions()
        
        # Statistics
        self.watershed_stats = {}
        
    def _calculate_flow_directions(self):
        """
        Calculate flow direction for each cell based on steepest descent.
        Returns array with values 0-7 representing 8 directions.
        """
        directions = np.zeros_like(self.terrain, dtype=int)
        
        # 8-directional flow (N, NE, E, SE, S, SW, W, NW)
        dx = [-1, -1, 0, 1, 1, 1, 0, -1]
        dy = [0, 1, 1, 1, 0, -1, -1, -1]
        
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                max_slope = -float('inf')
                best_direction = 0
                
                for d in range(8):
                    ni, nj = i + dx[d], j + dy[d]
                    if 0 <= ni < self.height and 0 <= nj < self.width:
                        slope = self.terrain[i, j] - self.terrain[ni, nj]
                        if slope > max_slope:
                            max_slope = slope
                            best_direction = d
                
                directions[i, j] = best_direction
        
        return directions
    
    def add_rainfall(self, intensity=None, coverage=1.0):
        """
        Add rainfall to the terrain.
        
        Args:
            intensity (float): Rainfall intensity (if None, uses default)
            coverage (float): Fraction of terrain covered by rain (0.0-1.0)
        """
        if intensity is None:
            intensity = self.rainfall_intensity
            
        # Random rainfall pattern
        rain_mask = np.random.random((self.height, self.width)) < coverage
        rainfall = rain_mask * intensity
        
        # Add rainfall to water surface
        self.water_surface += rainfall
    
    def simulate_flow_step(self):
        """
        Simulate one time step of water flow.
        """
        # Create copy for simultaneous updates
        new_water_surface = self.water_surface.copy()
        
        # Flow directions
        dx = [-1, -1, 0, 1, 1, 1, 0, -1]
        dy = [0, 1, 1, 1, 0, -1, -1, -1]
        
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if self.water_surface[i, j] > 0:
                    # Get flow direction
                    direction = self.flow_directions[i, j]
                    ni, nj = i + dx[direction], j + dy[direction]
                    
                    # Calculate flow amount (proportional to water depth and slope)
                    slope = self.terrain[i, j] - self.terrain[ni, nj]
                    if slope > 0:  # Only flow downhill
                        flow_rate = min(self.water_surface[i, j], slope * 0.1)
                        
                        # Move water
                        new_water_surface[i, j] -= flow_rate
                        new_water_surface[ni, nj] += flow_rate
                        
                        # Update flow accumulation
                        self.flow_accumulation[ni, nj] += flow_rate
        
        # Apply evaporation
        self.water_surface = new_water_surface * (1 - self.evaporation_rate)
    
    def simulate_rainfall_event(self, duration=50, intensity=None, coverage=1.0):
        """
        Simulate a complete rainfall event.
        
        Args:
            duration (int): Number of time steps
            intensity (float): Rainfall intensity
            coverage (float): Fraction of terrain covered by rain
        """
        print(f"Simulating rainfall event: {duration} steps, intensity={intensity or self.rainfall_intensity}")
        
        for step in range(duration):
            # Add rainfall for first half of simulation
            if step < duration // 2:
                self.add_rainfall(intensity, coverage)
            
            # Simulate flow
            self.simulate_flow_step()
            
            if step % 10 == 0:
                total_water = np.sum(self.water_surface)
                print(f"  Step {step}: Total water = {total_water:.2f}")
    
    def identify_rivers(self, threshold=None):
        """
        Identify river network based on flow accumulation.
        
        Args:
            threshold (float): Flow accumulation threshold for rivers
        """
        if threshold is None:
            # Use 95th percentile as default threshold
            threshold = np.percentile(self.flow_accumulation, 95)
        
        self.river_network = (self.flow_accumulation > threshold).astype(int)
        
        print(f"River network identified with threshold {threshold:.2f}")
        print(f"River cells: {np.sum(self.river_network)} ({np.sum(self.river_network) / self.river_network.size * 100:.1f}%)")
    
    def calculate_watershed_stats(self):
        """Calculate watershed statistics."""
        # Find watersheds by following flow directions to outlets
        watersheds = {}
        visited = np.zeros_like(self.terrain, dtype=bool)
        
        dx = [-1, -1, 0, 1, 1, 1, 0, -1]
        dy = [0, 1, 1, 1, 0, -1, -1, -1]
        
        for i in range(self.height):
            for j in range(self.width):
                if not visited[i, j]:
                    # Follow flow path to find watershed
                    path = []
                    current_i, current_j = i, j
                    
                    while (0 <= current_i < self.height and 
                           0 <= current_j < self.width and 
                           not visited[current_i, current_j]):
                        visited[current_i, current_j] = True
                        path.append((current_i, current_j))
                        
                        direction = self.flow_directions[current_i, current_j]
                        current_i += dx[direction]
                        current_j += dy[direction]
                    
                    # Assign watershed ID
                    watershed_id = len(watersheds)
                    for pi, pj in path:
                        if pi not in watersheds:
                            watersheds[pi] = {}
                        watersheds[pi][pj] = watershed_id
        
        # Calculate statistics
        num_watersheds = len(set(watershed_id for ws in watersheds.values() for watershed_id in ws.values()))
        
        # River length calculation
        river_length = np.sum(self.river_network) * np.sqrt(2)  # Approximate length
        
        self.watershed_stats = {
            'num_watersheds': num_watersheds,
            'river_length': river_length,
            'max_flow_accumulation': np.max(self.flow_accumulation),
            'total_flow': np.sum(self.flow_accumulation),
            'river_coverage': np.sum(self.river_network) / self.river_network.size
        }
        
        return self.watershed_stats
    
    def visualize_water_flow(self, figsize=(15, 10)):
        """
        Create comprehensive visualization of water flow simulation.
        """
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        
        # Original terrain
        im1 = axes[0, 0].imshow(self.terrain, cmap='terrain', origin='lower')
        axes[0, 0].set_title('Original Terrain')
        axes[0, 0].set_xlabel('X')
        axes[0, 0].set_ylabel('Y')
        plt.colorbar(im1, ax=axes[0, 0], label='Elevation')
        
        # Water surface
        im2 = axes[0, 1].imshow(self.water_surface, cmap='Blues', origin='lower')
        axes[0, 1].set_title('Water Surface')
        axes[0, 1].set_xlabel('X')
        axes[0, 1].set_ylabel('Y')
        plt.colorbar(im2, ax=axes[0, 1], label='Water Depth')
        
        # Flow accumulation
        im3 = axes[0, 2].imshow(self.flow_accumulation, cmap='viridis', origin='lower')
        axes[0, 2].set_title('Flow Accumulation')
        axes[0, 2].set_xlabel('X')
        axes[0, 2].set_ylabel('Y')
        plt.colorbar(im3, ax=axes[0, 2], label='Flow Volume')
        
        # River network
        river_display = np.ma.masked_where(self.river_network == 0, self.river_network)
        im4 = axes[1, 0].imshow(self.terrain, cmap='terrain', origin='lower', alpha=0.7)
        im5 = axes[1, 0].imshow(river_display, cmap='Blues', origin='lower', alpha=0.8)
        axes[1, 0].set_title('River Network Overlay')
        axes[1, 0].set_xlabel('X')
        axes[1, 0].set_ylabel('Y')
        
        # Combined terrain + water
        combined = self.terrain + self.water_surface * 0.1  # Scale water for visibility
        im6 = axes[1, 1].imshow(combined, cmap='terrain', origin='lower')
        axes[1, 1].set_title('Terrain + Water')
        axes[1, 1].set_xlabel('X')
        axes[1, 1].set_ylabel('Y')
        plt.colorbar(im6, ax=axes[1, 1], label='Combined Height')
        
        # Statistics text
        axes[1, 2].axis('off')
        stats_text = f"""Watershed Statistics:
        
Watersheds: {self.watershed_stats.get('num_watersheds', 'N/A')}
River Length: {self.watershed_stats.get('river_length', 0):.1f} units
Max Flow: {self.watershed_stats.get('max_flow_accumulation', 0):.2f}
Total Flow: {self.watershed_stats.get('total_flow', 0):.2f}
River Coverage: {self.watershed_stats.get('river_coverage', 0)*100:.1f}%
        """
        axes[1, 2].text(0.1, 0.5, stats_text, transform=axes[1, 2].transAxes, 
                        fontsize=10, verticalalignment='center',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        plt.tight_layout()
        return fig
    
    def export_water_data(self, output_dir="output", prefix="water_simulation"):
        """
        Export water simulation data.
        """
        import os
        from datetime import datetime
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export arrays
        np.save(os.path.join(output_dir, f"{prefix}_water_surface_{timestamp}.npy"), self.water_surface)
        np.save(os.path.join(output_dir, f"{prefix}_flow_accumulation_{timestamp}.npy"), self.flow_accumulation)
        np.save(os.path.join(output_dir, f"{prefix}_river_network_{timestamp}.npy"), self.river_network)
        
        # Export visualization
        fig = self.visualize_water_flow()
        fig.savefig(os.path.join(output_dir, f"{prefix}_visualization_{timestamp}.png"), 
                   dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print(f"Water simulation data exported to {output_dir}/")
        return timestamp
