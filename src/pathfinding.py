#!/usr/bin/env python3
"""
Pathfinding Module
Implements A* and Dijkstra algorithms for terrain navigation with cost functions.
"""

import numpy as np
import matplotlib.pyplot as plt
from heapq import heappush, heappop
import math


class PathfindingSimulation:
    """Handles pathfinding on terrain with various cost functions."""
    
    def __init__(self, terrain, flow_accumulation=None, water_surface=None, 
                 flood_map=None, landslide_map=None, wildfire_map=None):
        """
        Initialize pathfinding simulation.
        
        Args:
            terrain (numpy.ndarray): 2D height map
            flow_accumulation (numpy.ndarray): Water flow accumulation data
            water_surface (numpy.ndarray): Current water surface data
            flood_map (numpy.ndarray): Flood simulation results
            landslide_map (numpy.ndarray): Landslide simulation results
            wildfire_map (numpy.ndarray): Wildfire simulation results
        """
        self.terrain = terrain
        self.height, self.width = terrain.shape
        self.flow_accumulation = flow_accumulation if flow_accumulation is not None else np.zeros_like(terrain)
        self.water_surface = water_surface if water_surface is not None else np.zeros_like(terrain)
        self.flood_map = flood_map if flood_map is not None else np.zeros_like(terrain)
        self.landslide_map = landslide_map if landslide_map is not None else np.zeros_like(terrain)
        self.wildfire_map = wildfire_map if wildfire_map is not None else np.zeros_like(terrain)
        
        # Pathfinding results
        self.paths = {}
        self.cost_maps = {}
        
    def calculate_movement_cost(self, from_pos, to_pos, cost_type='comprehensive'):
        """
        Calculate movement cost between two positions.
        
        Args:
            from_pos (tuple): Starting position (y, x)
            from_pos (tuple): Target position (y, x)
            cost_type (str): Type of cost calculation
        
        Returns:
            float: Movement cost
        """
        fy, fx = from_pos
        ty, tx = to_pos
        
        # Base distance cost
        distance = math.sqrt((tx - fx)**2 + (ty - fy)**2)
        
        if cost_type == 'distance':
            return distance
        
        # Elevation cost (going uphill is more expensive)
        elevation_diff = self.terrain[ty, tx] - self.terrain[fy, fx]
        elevation_cost = max(0, elevation_diff) * 2.0  # Uphill penalty
        
        # Slope cost
        slope = abs(elevation_diff) / distance if distance > 0 else 0
        slope_cost = slope * 1.5
        
        # Water crossing cost
        water_cost = 0
        if self.water_surface[ty, tx] > 0.1:
            water_cost = self.water_surface[ty, tx] * 3.0
        
        # Flood cost
        flood_cost = 0
        if self.flood_map[ty, tx] > 0:
            flood_cost = self.flood_map[ty, tx] * 10.0  # High penalty for flooded areas
        
        # Landslide cost
        landslide_cost = 0
        if self.landslide_map[ty, tx] > 0:
            landslide_cost = self.landslide_map[ty, tx] * 15.0  # Very high penalty
        
        # Wildfire cost
        fire_cost = 0
        if self.wildfire_map[ty, tx] > 0:
            fire_cost = self.wildfire_map[ty, tx] * 20.0  # Extremely high penalty
        
        # Combine costs
        if cost_type == 'slope':
            return distance + elevation_cost + slope_cost
        elif cost_type == 'water':
            return distance + water_cost + flood_cost
        elif cost_type == 'disasters':
            return distance + flood_cost + landslide_cost + fire_cost
        elif cost_type == 'comprehensive':
            return (distance + elevation_cost + slope_cost + 
                   water_cost + flood_cost + landslide_cost + fire_cost)
        else:
            return distance
    
    def dijkstra(self, start, goal, cost_type='comprehensive'):
        """
        Find shortest path using Dijkstra's algorithm.
        
        Args:
            start (tuple): Starting position (y, x)
            goal (tuple): Goal position (y, x)
            cost_type (str): Type of cost calculation
        
        Returns:
            list: Path as list of (y, x) coordinates, or None if no path found
        """
        # Priority queue: (cost, position, path)
        pq = [(0, start, [start])]
        visited = set()
        
        # 8-directional movement
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        while pq:
            cost, current, path = heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == goal:
                return path
            
            # Explore neighbors
            for dy, dx in directions:
                ny, nx = current[0] + dy, current[1] + dx
                
                if (0 <= ny < self.height and 0 <= nx < self.width and 
                    (ny, nx) not in visited):
                    
                    # Calculate movement cost
                    move_cost = self.calculate_movement_cost(current, (ny, nx), cost_type)
                    new_cost = cost + move_cost
                    new_path = path + [(ny, nx)]
                    
                    heappush(pq, (new_cost, (ny, nx), new_path))
        
        return None  # No path found
    
    def astar(self, start, goal, cost_type='comprehensive'):
        """
        Find shortest path using A* algorithm.
        
        Args:
            start (tuple): Starting position (y, x)
            goal (tuple): Goal position (y, x)
            cost_type (str): Type of cost calculation
        
        Returns:
            list: Path as list of (y, x) coordinates, or None if no path found
        """
        def heuristic(pos):
            """Heuristic function (Euclidean distance)."""
            return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)
        
        # Priority queue: (f_cost, g_cost, position, path)
        pq = [(heuristic(start), 0, start, [start])]
        visited = set()
        g_costs = {start: 0}
        
        # 8-directional movement
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        while pq:
            f_cost, g_cost, current, path = heappop(pq)
            
            if current in visited:
                continue
            
            visited.add(current)
            
            if current == goal:
                return path
            
            # Explore neighbors
            for dy, dx in directions:
                ny, nx = current[0] + dy, current[1] + dx
                
                if (0 <= ny < self.height and 0 <= nx < self.width and 
                    (ny, nx) not in visited):
                    
                    # Calculate movement cost
                    move_cost = self.calculate_movement_cost(current, (ny, nx), cost_type)
                    new_g_cost = g_cost + move_cost
                    new_f_cost = new_g_cost + heuristic((ny, nx))
                    new_path = path + [(ny, nx)]
                    
                    # Only add if we found a better path to this position
                    if (ny, nx) not in g_costs or new_g_cost < g_costs[(ny, nx)]:
                        g_costs[(ny, nx)] = new_g_cost
                        heappush(pq, (new_f_cost, new_g_cost, (ny, nx), new_path))
        
        return None  # No path found
    
    def find_multiple_paths(self, start, goals, algorithm='astar', cost_type='comprehensive'):
        """
        Find paths to multiple goals.
        
        Args:
            start (tuple): Starting position (y, x)
            goals (list): List of goal positions [(y, x), ...]
            algorithm (str): 'astar' or 'dijkstra'
            cost_type (str): Type of cost calculation
        
        Returns:
            dict: Dictionary mapping goals to paths
        """
        paths = {}
        
        for goal in goals:
            if algorithm == 'astar':
                path = self.astar(start, goal, cost_type)
            else:
                path = self.dijkstra(start, goal, cost_type)
            
            if path:
                paths[goal] = path
                self.paths[f"{start}_to_{goal}_{cost_type}"] = path
        
        return paths
    
    def calculate_path_cost(self, path, cost_type='comprehensive'):
        """
        Calculate total cost of a path.
        
        Args:
            path (list): Path as list of (y, x) coordinates
            cost_type (str): Type of cost calculation
        
        Returns:
            float: Total path cost
        """
        if not path or len(path) < 2:
            return 0
        
        total_cost = 0
        for i in range(len(path) - 1):
            cost = self.calculate_movement_cost(path[i], path[i + 1], cost_type)
            total_cost += cost
        
        return total_cost
    
    def generate_cost_map(self, cost_type='comprehensive'):
        """
        Generate a cost map for the entire terrain.
        
        Args:
            cost_type (str): Type of cost calculation
        
        Returns:
            numpy.ndarray: Cost map
        """
        cost_map = np.zeros_like(self.terrain)
        
        for y in range(self.height):
            for x in range(self.width):
                # Calculate cost to move to this position from center
                center_y, center_x = self.height // 2, self.width // 2
                cost = self.calculate_movement_cost((center_y, center_x), (y, x), cost_type)
                cost_map[y, x] = cost
        
        self.cost_maps[cost_type] = cost_map
        return cost_map
    
    def visualize_pathfinding(self, paths=None, cost_type='comprehensive', figsize=(15, 10)):
        """
        Create comprehensive visualization of pathfinding results.
        
        Args:
            paths (dict): Dictionary of paths to visualize
            cost_type (str): Type of cost calculation
            figsize (tuple): Figure size
        """
        fig, axes = plt.subplots(2, 3, figsize=figsize)
        
        # Original terrain
        im1 = axes[0, 0].imshow(self.terrain, cmap='terrain', origin='lower')
        axes[0, 0].set_title('Original Terrain')
        axes[0, 0].set_xlabel('X')
        axes[0, 0].set_ylabel('Y')
        plt.colorbar(im1, ax=axes[0, 0], label='Elevation')
        
        # Cost map
        cost_map = self.generate_cost_map(cost_type)
        im2 = axes[0, 1].imshow(cost_map, cmap='hot', origin='lower')
        axes[0, 1].set_title(f'Cost Map ({cost_type})')
        axes[0, 1].set_xlabel('X')
        axes[0, 1].set_ylabel('Y')
        plt.colorbar(im2, ax=axes[0, 1], label='Movement Cost')
        
        # Disaster overlay
        disaster_map = np.zeros_like(self.terrain)
        disaster_map[self.flood_map > 0] = 1
        disaster_map[self.landslide_map > 0] = 2
        disaster_map[self.wildfire_map > 0] = 3
        
        im3 = axes[0, 2].imshow(disaster_map, cmap='viridis', origin='lower')
        axes[0, 2].set_title('Disaster Map')
        axes[0, 2].set_xlabel('X')
        axes[0, 2].set_ylabel('Y')
        plt.colorbar(im3, ax=axes[0, 2], label='Disaster Type')
        
        # Path visualization
        if paths:
            # Show terrain with paths
            axes[1, 0].imshow(self.terrain, cmap='terrain', origin='lower', alpha=0.7)
            
            colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            for i, (goal, path) in enumerate(paths.items()):
                if path:
                    path_y = [pos[0] for pos in path]
                    path_x = [pos[1] for pos in path]
                    color = colors[i % len(colors)]
                    axes[1, 0].plot(path_x, path_y, color=color, linewidth=2, 
                                   label=f'Path to {goal}')
                    
                    # Mark start and goal
                    axes[1, 0].plot(path_x[0], path_y[0], 'go', markersize=8, label='Start' if i == 0 else "")
                    axes[1, 0].plot(path_x[-1], path_y[-1], 'ro', markersize=8, label='Goal' if i == 0 else "")
            
            axes[1, 0].set_title('Pathfinding Results')
            axes[1, 0].set_xlabel('X')
            axes[1, 0].set_ylabel('Y')
            axes[1, 0].legend()
        
        # Path cost comparison
        if paths:
            path_costs = []
            path_names = []
            for goal, path in paths.items():
                if path:
                    cost = self.calculate_path_cost(path, cost_type)
                    path_costs.append(cost)
                    path_names.append(f'To {goal}')
            
            if path_costs:
                axes[1, 1].bar(range(len(path_costs)), path_costs, color='skyblue')
                axes[1, 1].set_title('Path Cost Comparison')
                axes[1, 1].set_xlabel('Destination')
                axes[1, 1].set_ylabel('Total Cost')
                axes[1, 1].set_xticks(range(len(path_names)))
                axes[1, 1].set_xticklabels(path_names, rotation=45)
        
        # Accessibility map
        accessibility_map = 1.0 / (cost_map + 1e-6)  # Inverse of cost
        im4 = axes[1, 2].imshow(accessibility_map, cmap='RdYlGn', origin='lower')
        axes[1, 2].set_title('Accessibility Map')
        axes[1, 2].set_xlabel('X')
        axes[1, 2].set_ylabel('Y')
        plt.colorbar(im4, ax=axes[1, 2], label='Accessibility')
        
        plt.tight_layout()
        return fig
    
    def export_pathfinding_data(self, output_dir="output", prefix="pathfinding_simulation"):
        """
        Export pathfinding simulation data.
        """
        import os
        from datetime import datetime
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export cost maps
        for cost_type, cost_map in self.cost_maps.items():
            np.save(os.path.join(output_dir, f"{prefix}_cost_map_{cost_type}_{timestamp}.npy"), cost_map)
        
        # Export paths
        if self.paths:
            import json
            # Convert paths to serializable format
            serializable_paths = {k: v for k, v in self.paths.items()}
            with open(os.path.join(output_dir, f"{prefix}_paths_{timestamp}.json"), 'w') as f:
                json.dump(serializable_paths, f)
        
        print(f"Pathfinding simulation data exported to {output_dir}/")
        return timestamp
