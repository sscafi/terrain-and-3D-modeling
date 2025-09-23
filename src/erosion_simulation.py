#!/usr/bin/env python3
"""
Erosion Simulation Module
Implements thermal and hydraulic erosion for terrain evolution.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
import random


class ErosionSimulation:
    """Handles erosion simulation on terrain."""
    
    def __init__(self, terrain, flow_accumulation=None, water_surface=None):
        """
        Initialize erosion simulation.
        
        Args:
            terrain (numpy.ndarray): 2D height map
            flow_accumulation (numpy.ndarray): Water flow accumulation data
            water_surface (numpy.ndarray): Current water surface data
        """
        self.original_terrain = terrain.copy()
        self.terrain = terrain.copy()
        self.height, self.width = terrain.shape
        self.flow_accumulation = flow_accumulation if flow_accumulation is not None else np.zeros_like(terrain)
        self.water_surface = water_surface if water_surface is not None else np.zeros_like(terrain)
        
        # Erosion parameters
        self.thermal_erosion_rate = 0.01
        self.hydraulic_erosion_rate = 0.005
        self.sediment_capacity = 0.1
        self.deposition_rate = 0.02
        
        # Erosion tracking
        self.erosion_history = []
        self.sediment_map = np.zeros_like(terrain)
        
    def calculate_slopes(self):
        """Calculate slope angles for each cell."""
        # Calculate gradients
        grad_x = np.gradient(self.terrain, axis=1)
        grad_y = np.gradient(self.terrain, axis=0)
        
        # Calculate slope magnitude
        slope = np.sqrt(grad_x**2 + grad_y**2)
        return slope, grad_x, grad_y
    
    def thermal_erosion(self, talus_angle=0.5):
        """
        Simulate thermal erosion (slope collapse).
        
        Args:
            talus_angle (float): Critical slope angle for collapse
        """
        slope, grad_x, grad_y = self.calculate_slopes()
        
        # Find cells with slopes exceeding talus angle
        unstable_cells = slope > talus_angle
        
        # Calculate erosion amount based on slope excess
        erosion_amount = np.maximum(0, slope - talus_angle) * self.thermal_erosion_rate
        
        # Apply erosion
        self.terrain[unstable_cells] -= erosion_amount[unstable_cells]
        
        # Add sediment to nearby cells (simplified)
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if unstable_cells[i, j]:
                    # Distribute sediment to neighboring cells
                    neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
                    sediment_per_neighbor = erosion_amount[i, j] / 4
                    
                    for ni, nj in neighbors:
                        if 0 <= ni < self.height and 0 <= nj < self.width:
                            self.terrain[ni, nj] += sediment_per_neighbor * 0.3  # 30% deposition
        
        return np.sum(erosion_amount)
    
    def hydraulic_erosion(self):
        """
        Simulate hydraulic erosion (water-carried sediment).
        """
        # Calculate flow strength based on water surface and flow accumulation
        flow_strength = self.water_surface * (1 + self.flow_accumulation)
        
        # Calculate erosion capacity
        slope, _, _ = self.calculate_slopes()
        erosion_capacity = flow_strength * slope * self.hydraulic_erosion_rate
        
        # Calculate actual erosion (limited by sediment capacity)
        actual_erosion = np.minimum(erosion_capacity, self.sediment_capacity)
        
        # Apply erosion
        self.terrain -= actual_erosion
        self.sediment_map += actual_erosion
        
        # Simulate sediment transport and deposition
        self._transport_sediment()
        
        return np.sum(actual_erosion)
    
    def _transport_sediment(self):
        """Simulate sediment transport and deposition."""
        # Simple sediment transport: move sediment downhill
        grad_x = np.gradient(self.terrain, axis=1)
        grad_y = np.gradient(self.terrain, axis=0)
        
        # Normalize gradients for direction
        grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        grad_magnitude[grad_magnitude == 0] = 1  # Avoid division by zero
        
        grad_x_norm = grad_x / grad_magnitude
        grad_y_norm = grad_y / grad_magnitude
        
        # Transport sediment
        new_sediment = np.zeros_like(self.sediment_map)
        
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if self.sediment_map[i, j] > 0:
                    # Calculate transport direction
                    dx = int(np.sign(grad_x_norm[i, j]))
                    dy = int(np.sign(grad_y_norm[i, j]))
                    
                    # Move sediment
                    ni, nj = i + dy, j + dx
                    if 0 <= ni < self.height and 0 <= nj < self.width:
                        transport_amount = self.sediment_map[i, j] * 0.1  # 10% transport rate
                        new_sediment[ni, nj] += transport_amount
                        new_sediment[i, j] -= transport_amount
                    else:
                        # Deposit at boundaries
                        new_sediment[i, j] -= self.sediment_map[i, j] * 0.1
        
        # Update sediment map
        self.sediment_map += new_sediment
        
        # Deposit sediment where flow is low
        low_flow = self.flow_accumulation < np.percentile(self.flow_accumulation, 25)
        deposition = self.sediment_map * self.deposition_rate * low_flow
        
        self.terrain += deposition
        self.sediment_map -= deposition
    
    def run_erosion_cycle(self, thermal_iterations=5, hydraulic_iterations=3):
        """
        Run one complete erosion cycle.
        
        Args:
            thermal_iterations (int): Number of thermal erosion steps
            hydraulic_iterations (int): Number of hydraulic erosion steps
        """
        total_thermal_erosion = 0
        total_hydraulic_erosion = 0
        
        # Thermal erosion
        for _ in range(thermal_iterations):
            erosion = self.thermal_erosion()
            total_thermal_erosion += erosion
        
        # Hydraulic erosion
        for _ in range(hydraulic_iterations):
            erosion = self.hydraulic_erosion()
            total_hydraulic_erosion += erosion
        
        # Record erosion history
        self.erosion_history.append({
            'thermal_erosion': total_thermal_erosion,
            'hydraulic_erosion': total_hydraulic_erosion,
            'total_erosion': total_thermal_erosion + total_hydraulic_erosion
        })
        
        return total_thermal_erosion, total_hydraulic_erosion
    
    def simulate_terrain_aging(self, cycles=10, talus_angle=0.5):
        """
        Simulate terrain aging through multiple erosion cycles.
        
        Args:
            cycles (int): Number of erosion cycles
            talus_angle (float): Critical slope angle for thermal erosion
        """
        print(f"Simulating terrain aging over {cycles} erosion cycles...")
        
        for cycle in range(cycles):
            thermal_erosion, hydraulic_erosion = self.run_erosion_cycle()
            
            if cycle % 2 == 0:  # Print every 2 cycles
                print(f"  Cycle {cycle}: Thermal={thermal_erosion:.3f}, Hydraulic={hydraulic_erosion:.3f}")
        
        print(f"Terrain aging simulation complete!")
        print(f"Total terrain change: {np.sum(self.terrain - self.original_terrain):.3f}")
    
    def visualize_erosion(self, figsize=(15, 12)):
        """
        Create comprehensive visualization of erosion simulation.
        """
        fig, axes = plt.subplots(3, 3, figsize=figsize)
        
        # Original terrain
        im1 = axes[0, 0].imshow(self.original_terrain, cmap='terrain', origin='lower')
        axes[0, 0].set_title('Original Terrain')
        axes[0, 0].set_xlabel('X')
        axes[0, 0].set_ylabel('Y')
        plt.colorbar(im1, ax=axes[0, 0], label='Elevation')
        
        # Eroded terrain
        im2 = axes[0, 1].imshow(self.terrain, cmap='terrain', origin='lower')
        axes[0, 1].set_title('Eroded Terrain')
        axes[0, 1].set_xlabel('X')
        axes[0, 1].set_ylabel('Y')
        plt.colorbar(im2, ax=axes[0, 1], label='Elevation')
        
        # Terrain change
        terrain_change = self.terrain - self.original_terrain
        im3 = axes[0, 2].imshow(terrain_change, cmap='RdBu_r', origin='lower')
        axes[0, 2].set_title('Terrain Change')
        axes[0, 2].set_xlabel('X')
        axes[0, 2].set_ylabel('Y')
        plt.colorbar(im3, ax=axes[0, 2], label='Elevation Change')
        
        # Slope map
        slope, _, _ = self.calculate_slopes()
        im4 = axes[1, 0].imshow(slope, cmap='hot', origin='lower')
        axes[1, 0].set_title('Slope Map')
        axes[1, 0].set_xlabel('X')
        axes[1, 0].set_ylabel('Y')
        plt.colorbar(im4, ax=axes[1, 0], label='Slope')
        
        # Sediment map
        im5 = axes[1, 1].imshow(self.sediment_map, cmap='YlOrBr', origin='lower')
        axes[1, 1].set_title('Sediment Map')
        axes[1, 1].set_xlabel('X')
        axes[1, 1].set_ylabel('Y')
        plt.colorbar(im5, ax=axes[1, 1], label='Sediment')
        
        # Flow accumulation
        im6 = axes[1, 2].imshow(self.flow_accumulation, cmap='viridis', origin='lower')
        axes[1, 2].set_title('Flow Accumulation')
        axes[1, 2].set_xlabel('X')
        axes[1, 2].set_ylabel('Y')
        plt.colorbar(im6, ax=axes[1, 2], label='Flow')
        
        # Erosion history
        if self.erosion_history:
            cycles = range(len(self.erosion_history))
            thermal_erosion = [h['thermal_erosion'] for h in self.erosion_history]
            hydraulic_erosion = [h['hydraulic_erosion'] for h in self.erosion_history]
            
            axes[2, 0].plot(cycles, thermal_erosion, 'r-', label='Thermal', linewidth=2)
            axes[2, 0].plot(cycles, hydraulic_erosion, 'b-', label='Hydraulic', linewidth=2)
            axes[2, 0].set_title('Erosion History')
            axes[2, 0].set_xlabel('Erosion Cycle')
            axes[2, 0].set_ylabel('Erosion Amount')
            axes[2, 0].legend()
            axes[2, 0].grid(True, alpha=0.3)
        
        # Statistics
        axes[2, 1].axis('off')
        stats_text = f"""Erosion Statistics:
        
Total Erosion: {np.sum(terrain_change):.3f}
Max Erosion: {np.max(terrain_change):.3f}
Max Deposition: {np.max(-terrain_change):.3f}
Avg Slope: {np.mean(slope):.3f}
Max Slope: {np.max(slope):.3f}
Sediment Total: {np.sum(self.sediment_map):.3f}
        """
        axes[2, 1].text(0.1, 0.5, stats_text, transform=axes[2, 1].transAxes, 
                        fontsize=10, verticalalignment='center',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        # 3D comparison
        ax_3d = fig.add_subplot(3, 3, 9, projection='3d')
        x, y = np.meshgrid(np.arange(self.width), np.arange(self.height))
        
        # Show original terrain in wireframe
        ax_3d.plot_wireframe(x, y, self.original_terrain, alpha=0.3, color='blue', linewidth=0.5)
        
        # Show eroded terrain as surface
        ax_3d.plot_surface(x, y, self.terrain, alpha=0.7, cmap='terrain')
        
        ax_3d.set_title('3D Comparison')
        ax_3d.set_xlabel('X')
        ax_3d.set_ylabel('Y')
        ax_3d.set_zlabel('Elevation')
        
        plt.tight_layout()
        return fig
    
    def export_erosion_data(self, output_dir="output", prefix="erosion_simulation"):
        """
        Export erosion simulation data.
        """
        import os
        from datetime import datetime
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export arrays
        np.save(os.path.join(output_dir, f"{prefix}_original_terrain_{timestamp}.npy"), self.original_terrain)
        np.save(os.path.join(output_dir, f"{prefix}_eroded_terrain_{timestamp}.npy"), self.terrain)
        np.save(os.path.join(output_dir, f"{prefix}_sediment_map_{timestamp}.npy"), self.sediment_map)
        
        # Export erosion history
        if self.erosion_history:
            erosion_data = np.array([(h['thermal_erosion'], h['hydraulic_erosion'], h['total_erosion']) 
                                   for h in self.erosion_history])
            np.save(os.path.join(output_dir, f"{prefix}_history_{timestamp}.npy"), erosion_data)
        
        # Export visualization
        fig = self.visualize_erosion()
        fig.savefig(os.path.join(output_dir, f"{prefix}_visualization_{timestamp}.png"), 
                   dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print(f"Erosion simulation data exported to {output_dir}/")
        return timestamp
