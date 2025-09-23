#!/usr/bin/env python3
"""
Disaster Simulation Module
Implements flooding, landslides, and wildfire spread simulations.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from collections import deque
import random


class DisasterSimulation:
    """Handles disaster simulations on terrain."""
    
    def __init__(self, terrain, flow_accumulation=None, water_surface=None):
        """
        Initialize disaster simulation.
        
        Args:
            terrain (numpy.ndarray): 2D height map
            flow_accumulation (numpy.ndarray): Water flow accumulation data
            water_surface (numpy.ndarray): Current water surface data
        """
        self.terrain = terrain
        self.height, self.width = terrain.shape
        self.flow_accumulation = flow_accumulation if flow_accumulation is not None else np.zeros_like(terrain)
        self.water_surface = water_surface if water_surface is not None else np.zeros_like(terrain)
        
        # Disaster state arrays
        self.flood_map = np.zeros_like(terrain)
        self.landslide_map = np.zeros_like(terrain)
        self.wildfire_map = np.zeros_like(terrain)
        self.vegetation_map = self._generate_vegetation()
        
        # Disaster parameters
        self.sea_level = np.percentile(terrain, 20)  # Assume sea level at 20th percentile
        self.landslide_threshold = 0.8  # Slope threshold for landslides
        self.wildfire_spread_rate = 0.3
        self.wind_direction = 0  # Wind direction in degrees
        
    def _generate_vegetation(self):
        """Generate vegetation map based on terrain characteristics."""
        # Vegetation grows better in valleys and near water
        vegetation = np.zeros_like(self.terrain)
        
        # Higher vegetation in lower elevations
        elevation_factor = 1 - (self.terrain - self.terrain.min()) / (self.terrain.max() - self.terrain.min())
        
        # Higher vegetation near water sources
        water_factor = np.clip(self.flow_accumulation / (np.max(self.flow_accumulation) + 1e-6), 0, 1)
        
        # Combine factors with some randomness
        vegetation = (elevation_factor * 0.6 + water_factor * 0.4) * np.random.random(self.terrain.shape)
        
        return np.clip(vegetation, 0, 1)
    
    def simulate_flooding(self, sea_level_rise=0.1, rainfall_intensity=2.0, duration=20):
        """
        Simulate flooding from sea level rise and rainfall accumulation.
        
        Args:
            sea_level_rise (float): Amount of sea level rise
            rainfall_intensity (float): Intensity of rainfall
            duration (int): Duration of flooding simulation
        """
        print(f"Simulating flooding: sea level rise={sea_level_rise}, rainfall={rainfall_intensity}")
        
        # Update sea level
        new_sea_level = self.sea_level + sea_level_rise
        
        # Initialize flood map
        self.flood_map = np.zeros_like(self.terrain)
        
        # Areas below sea level are flooded
        self.flood_map[self.terrain < new_sea_level] = 1.0
        
        # Simulate rainfall accumulation
        water_accumulation = np.zeros_like(self.terrain)
        
        for step in range(duration):
            # Add rainfall
            rainfall = np.random.random((self.height, self.width)) * rainfall_intensity
            water_accumulation += rainfall
            
            # Water flows downhill and accumulates
            self._simulate_water_flow(water_accumulation)
            
            # Areas with high water accumulation are flooded
            flood_threshold = np.percentile(water_accumulation, 80)
            flooded_areas = water_accumulation > flood_threshold
            self.flood_map[flooded_areas] = np.clip(self.flood_map[flooded_areas] + 0.1, 0, 1)
            
            if step % 5 == 0:
                flood_coverage = np.sum(self.flood_map > 0) / self.flood_map.size * 100
                print(f"  Step {step}: Flood coverage = {flood_coverage:.1f}%")
        
        return self.flood_map
    
    def _simulate_water_flow(self, water_accumulation):
        """Simulate water flow for flooding simulation."""
        # Simple water flow: water moves to lowest neighboring cell
        new_accumulation = water_accumulation.copy()
        
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if water_accumulation[i, j] > 0:
                    # Find lowest neighbor
                    neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
                    lowest_elevation = float('inf')
                    lowest_neighbor = (i, j)
                    
                    for ni, nj in neighbors:
                        if 0 <= ni < self.height and 0 <= nj < self.width:
                            if self.terrain[ni, nj] < lowest_elevation:
                                lowest_elevation = self.terrain[ni, nj]
                                lowest_neighbor = (ni, nj)
                    
                    # Move some water to lowest neighbor
                    if lowest_neighbor != (i, j):
                        flow_amount = water_accumulation[i, j] * 0.1
                        new_accumulation[i, j] -= flow_amount
                        new_accumulation[lowest_neighbor] += flow_amount
        
        water_accumulation[:] = new_accumulation
    
    def simulate_landslides(self, rainfall_trigger=1.5, slope_threshold=None):
        """
        Simulate landslides triggered by rainfall and slope instability.
        
        Args:
            rainfall_trigger (float): Rainfall threshold for landslide trigger
            slope_threshold (float): Slope threshold for landslides
        """
        if slope_threshold is None:
            slope_threshold = self.landslide_threshold
            
        print(f"Simulating landslides: rainfall trigger={rainfall_trigger}, slope threshold={slope_threshold}")
        
        # Calculate slopes
        grad_x = np.gradient(self.terrain, axis=1)
        grad_y = np.gradient(self.terrain, axis=0)
        slopes = np.sqrt(grad_x**2 + grad_y**2)
        
        # Initialize landslide map
        self.landslide_map = np.zeros_like(self.terrain)
        
        # Areas with high slopes and rainfall are prone to landslides
        high_slope = slopes > slope_threshold
        high_rainfall = self.water_surface > rainfall_trigger
        
        # Landslide probability based on slope and rainfall
        landslide_probability = np.zeros_like(self.terrain)
        landslide_probability[high_slope] += 0.3
        landslide_probability[high_rainfall] += 0.2
        landslide_probability[high_slope & high_rainfall] += 0.4
        
        # Add some randomness
        landslide_probability += np.random.random(self.terrain.shape) * 0.1
        
        # Trigger landslides
        landslide_threshold = 0.6
        landslide_cells = landslide_probability > landslide_threshold
        
        # Simulate landslide propagation
        self._propagate_landslides(landslide_cells, slopes)
        
        landslide_coverage = np.sum(self.landslide_map > 0) / self.landslide_map.size * 100
        print(f"Landslide coverage: {landslide_coverage:.1f}%")
        
        return self.landslide_map
    
    def _propagate_landslides(self, initial_cells, slopes):
        """Propagate landslides from initial trigger points."""
        # Use flood fill to propagate landslides
        queue = deque()
        
        # Add initial landslide cells to queue
        for i in range(self.height):
            for j in range(self.width):
                if initial_cells[i, j]:
                    queue.append((i, j))
                    self.landslide_map[i, j] = 1.0
        
        # Propagate landslides
        while queue:
            i, j = queue.popleft()
            
            # Check neighbors
            neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
            for ni, nj in neighbors:
                if (0 <= ni < self.height and 0 <= nj < self.width and 
                    self.landslide_map[ni, nj] == 0):
                    
                    # Probability of propagation based on slope
                    propagation_prob = slopes[ni, nj] * 0.5
                    
                    if np.random.random() < propagation_prob:
                        self.landslide_map[ni, nj] = 0.8  # Slightly less intense
                        queue.append((ni, nj))
    
    def simulate_wildfire(self, ignition_points=None, wind_direction=None, spread_rate=None):
        """
        Simulate wildfire spread based on terrain, vegetation, and wind.
        
        Args:
            ignition_points (list): List of (x, y) ignition points
            wind_direction (float): Wind direction in degrees
            spread_rate (float): Fire spread rate
        """
        if wind_direction is None:
            wind_direction = self.wind_direction
        if spread_rate is None:
            spread_rate = self.wildfire_spread_rate
            
        print(f"Simulating wildfire: wind direction={wind_direction}°, spread rate={spread_rate}")
        
        # Initialize wildfire map
        self.wildfire_map = np.zeros_like(self.terrain)
        
        # Set ignition points
        if ignition_points is None:
            # Random ignition points
            num_ignitions = max(1, self.height * self.width // 1000)
            ignition_points = []
            for _ in range(num_ignitions):
                x = np.random.randint(0, self.width)
                y = np.random.randint(0, self.height)
                ignition_points.append((x, y))
        
        # Start fires at ignition points
        for x, y in ignition_points:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.wildfire_map[y, x] = 1.0
        
        # Simulate fire spread
        self._spread_fire(wind_direction, spread_rate)
        
        fire_coverage = np.sum(self.wildfire_map > 0) / self.wildfire_map.size * 100
        print(f"Fire coverage: {fire_coverage:.1f}%")
        
        return self.wildfire_map
    
    def _spread_fire(self, wind_direction, spread_rate):
        """Simulate fire spread using cellular automata."""
        # Convert wind direction to radians
        wind_rad = np.radians(wind_direction)
        wind_x = np.cos(wind_rad)
        wind_y = np.sin(wind_rad)
        
        # Fire spread simulation
        for iteration in range(50):  # Maximum iterations
            new_fire_map = self.wildfire_map.copy()
            
            for i in range(1, self.height - 1):
                for j in range(1, self.width - 1):
                    if self.wildfire_map[i, j] > 0:  # Cell is on fire
                        # Check neighbors
                        neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1),
                                   (i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)]
                        
                        for ni, nj in neighbors:
                            if (0 <= ni < self.height and 0 <= nj < self.width and 
                                new_fire_map[ni, nj] == 0):  # Neighbor not on fire
                                
                                # Calculate spread probability
                                spread_prob = self._calculate_fire_spread_probability(
                                    i, j, ni, nj, wind_x, wind_y, spread_rate
                                )
                                
                                if np.random.random() < spread_prob:
                                    new_fire_map[ni, nj] = 1.0
            
            # Update fire map
            self.wildfire_map = new_fire_map
            
            # Check if fire has stopped spreading
            if np.sum(self.wildfire_map) == 0:
                break
    
    def _calculate_fire_spread_probability(self, i, j, ni, nj, wind_x, wind_y, spread_rate):
        """Calculate fire spread probability to a neighboring cell."""
        # Base probability from vegetation
        base_prob = self.vegetation_map[ni, nj] * spread_rate
        
        # Wind effect
        dx = nj - j
        dy = ni - i
        wind_effect = (dx * wind_x + dy * wind_y) * 0.3
        
        # Terrain effect (fire spreads faster uphill)
        terrain_effect = (self.terrain[ni, nj] - self.terrain[i, j]) * 0.2
        
        # Combine effects
        spread_prob = base_prob + wind_effect + terrain_effect
        
        return np.clip(spread_prob, 0, 1)
    
    def visualize_disasters(self, figsize=(18, 12)):
        """
        Create comprehensive visualization of disaster simulations.
        """
        fig, axes = plt.subplots(3, 3, figsize=figsize)
        
        # Original terrain
        im1 = axes[0, 0].imshow(self.terrain, cmap='terrain', origin='lower')
        axes[0, 0].set_title('Original Terrain')
        axes[0, 0].set_xlabel('X')
        axes[0, 0].set_ylabel('Y')
        plt.colorbar(im1, ax=axes[0, 0], label='Elevation')
        
        # Vegetation map
        im2 = axes[0, 1].imshow(self.vegetation_map, cmap='Greens', origin='lower')
        axes[0, 1].set_title('Vegetation Map')
        axes[0, 1].set_xlabel('X')
        axes[0, 1].set_ylabel('Y')
        plt.colorbar(im2, ax=axes[0, 1], label='Vegetation Density')
        
        # Flood map
        flood_display = np.ma.masked_where(self.flood_map == 0, self.flood_map)
        im3 = axes[0, 2].imshow(self.terrain, cmap='terrain', origin='lower', alpha=0.7)
        im4 = axes[0, 2].imshow(flood_display, cmap='Blues', origin='lower', alpha=0.8)
        axes[0, 2].set_title('Flood Simulation')
        axes[0, 2].set_xlabel('X')
        axes[0, 2].set_ylabel('Y')
        
        # Landslide map
        landslide_display = np.ma.masked_where(self.landslide_map == 0, self.landslide_map)
        im5 = axes[1, 0].imshow(self.terrain, cmap='terrain', origin='lower', alpha=0.7)
        im6 = axes[1, 0].imshow(landslide_display, cmap='Reds', origin='lower', alpha=0.8)
        axes[1, 0].set_title('Landslide Simulation')
        axes[1, 0].set_xlabel('X')
        axes[1, 0].set_ylabel('Y')
        
        # Wildfire map
        fire_display = np.ma.masked_where(self.wildfire_map == 0, self.wildfire_map)
        im7 = axes[1, 1].imshow(self.terrain, cmap='terrain', origin='lower', alpha=0.7)
        im8 = axes[1, 1].imshow(fire_display, cmap='Oranges', origin='lower', alpha=0.8)
        axes[1, 1].set_title('Wildfire Simulation')
        axes[1, 1].set_xlabel('X')
        axes[1, 1].set_ylabel('Y')
        
        # Combined disaster map
        combined_disasters = np.zeros_like(self.terrain)
        combined_disasters[self.flood_map > 0] = 1
        combined_disasters[self.landslide_map > 0] = 2
        combined_disasters[self.wildfire_map > 0] = 3
        
        im9 = axes[1, 2].imshow(combined_disasters, cmap='viridis', origin='lower')
        axes[1, 2].set_title('Combined Disasters')
        axes[1, 2].set_xlabel('X')
        axes[1, 2].set_ylabel('Y')
        plt.colorbar(im9, ax=axes[1, 2], label='Disaster Type')
        
        # Statistics
        axes[2, 0].axis('off')
        stats_text = f"""Disaster Statistics:
        
Flood Coverage: {np.sum(self.flood_map > 0) / self.flood_map.size * 100:.1f}%
Landslide Coverage: {np.sum(self.landslide_map > 0) / self.landslide_map.size * 100:.1f}%
Wildfire Coverage: {np.sum(self.wildfire_map > 0) / self.wildfire_map.size * 100:.1f}%
Sea Level: {self.sea_level:.3f}
Avg Vegetation: {np.mean(self.vegetation_map):.3f}
        """
        axes[2, 0].text(0.1, 0.5, stats_text, transform=axes[2, 0].transAxes, 
                        fontsize=10, verticalalignment='center',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        # Risk assessment
        risk_map = self._calculate_risk_assessment()
        im10 = axes[2, 1].imshow(risk_map, cmap='Reds', origin='lower')
        axes[2, 1].set_title('Risk Assessment')
        axes[2, 1].set_xlabel('X')
        axes[2, 1].set_ylabel('Y')
        plt.colorbar(im10, ax=axes[2, 1], label='Risk Level')
        
        # 3D terrain with disasters
        ax_3d = fig.add_subplot(3, 3, 9, projection='3d')
        x, y = np.meshgrid(np.arange(self.width), np.arange(self.height))
        
        # Show terrain
        ax_3d.plot_surface(x, y, self.terrain, alpha=0.7, cmap='terrain')
        
        # Overlay disasters
        flood_points = np.where(self.flood_map > 0)
        if len(flood_points[0]) > 0:
            ax_3d.scatter(flood_points[1], flood_points[0], 
                         self.terrain[flood_points], c='blue', s=1, alpha=0.6)
        
        ax_3d.set_title('3D Terrain with Disasters')
        ax_3d.set_xlabel('X')
        ax_3d.set_ylabel('Y')
        ax_3d.set_zlabel('Elevation')
        
        plt.tight_layout()
        return fig
    
    def _calculate_risk_assessment(self):
        """Calculate overall risk assessment map."""
        # Combine all disaster factors
        risk_map = np.zeros_like(self.terrain)
        
        # Flood risk
        risk_map += self.flood_map * 0.3
        
        # Landslide risk
        risk_map += self.landslide_map * 0.3
        
        # Wildfire risk
        risk_map += self.wildfire_map * 0.2
        
        # Terrain-based risk (steep slopes)
        grad_x = np.gradient(self.terrain, axis=1)
        grad_y = np.gradient(self.terrain, axis=0)
        slopes = np.sqrt(grad_x**2 + grad_y**2)
        risk_map += slopes * 0.2
        
        return np.clip(risk_map, 0, 1)
    
    def export_disaster_data(self, output_dir="output", prefix="disaster_simulation"):
        """
        Export disaster simulation data.
        """
        import os
        from datetime import datetime
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export arrays
        np.save(os.path.join(output_dir, f"{prefix}_flood_map_{timestamp}.npy"), self.flood_map)
        np.save(os.path.join(output_dir, f"{prefix}_landslide_map_{timestamp}.npy"), self.landslide_map)
        np.save(os.path.join(output_dir, f"{prefix}_wildfire_map_{timestamp}.npy"), self.wildfire_map)
        np.save(os.path.join(output_dir, f"{prefix}_vegetation_map_{timestamp}.npy"), self.vegetation_map)
        
        # Export visualization
        fig = self.visualize_disasters()
        fig.savefig(os.path.join(output_dir, f"{prefix}_visualization_{timestamp}.png"), 
                   dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print(f"Disaster simulation data exported to {output_dir}/")
        return timestamp
