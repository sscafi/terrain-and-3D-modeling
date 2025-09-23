#!/usr/bin/env python3
"""
Data Import Module
Handles importing real-world DEM datasets and running simulations on them.
"""

import numpy as np
import matplotlib.pyplot as plt
import requests
import zipfile
import os
from scipy import ndimage
from scipy.interpolate import griddata
import json


class DataImportSimulation:
    """Handles importing and processing real-world terrain data."""
    
    def __init__(self, data_dir="data"):
        """
        Initialize data import simulation.
        
        Args:
            data_dir (str): Directory to store imported data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Real-world datasets
        self.available_datasets = {
            'srtm_sample': {
                'description': 'Sample SRTM data (simulated)',
                'size': (100, 100),
                'resolution': 30,  # meters
                'format': 'numpy'
            },
            'usgs_sample': {
                'description': 'Sample USGS DEM data (simulated)',
                'size': (150, 150),
                'resolution': 10,  # meters
                'format': 'numpy'
            }
        }
        
        self.loaded_datasets = {}
        
    def generate_sample_srtm_data(self, size=(100, 100), region='mountainous'):
        """
        Generate sample SRTM-like data for demonstration.
        
        Args:
            size (tuple): Size of the dataset
            region (str): Type of terrain to simulate
        
        Returns:
            numpy.ndarray: Sample terrain data
        """
        print(f"Generating sample SRTM data: {size}, region: {region}")
        
        if region == 'mountainous':
            # Create mountainous terrain
            x = np.linspace(-5, 5, size[1])
            y = np.linspace(-5, 5, size[0])
            X, Y = np.meshgrid(x, y)
            
            # Multiple mountain peaks
            terrain = (np.exp(-(X**2 + Y**2)) * 2000 +
                      np.exp(-((X-2)**2 + (Y-1)**2)) * 1500 +
                      np.exp(-((X+1)**2 + (Y+2)**2)) * 1800 +
                      np.random.random(size) * 200)  # Add noise
            
        elif region == 'coastal':
            # Create coastal terrain
            x = np.linspace(-3, 3, size[1])
            y = np.linspace(-3, 3, size[0])
            X, Y = np.meshgrid(x, y)
            
            # Coastal hills with sea level
            terrain = (np.exp(-(X**2 + Y**2)) * 500 +
                      np.exp(-((X-1)**2 + (Y+1)**2)) * 300 +
                      np.random.random(size) * 100)
            
            # Set sea level
            terrain = np.maximum(terrain, 0)
            
        elif region == 'desert':
            # Create desert terrain
            x = np.linspace(-4, 4, size[1])
            y = np.linspace(-4, 4, size[0])
            X, Y = np.meshgrid(x, y)
            
            # Sand dunes
            terrain = (np.sin(X) * np.cos(Y) * 200 +
                      np.sin(X*2) * np.cos(Y*2) * 100 +
                      np.random.random(size) * 50)
            
        else:
            # Default: rolling hills
            x = np.linspace(-2, 2, size[1])
            y = np.linspace(-2, 2, size[0])
            X, Y = np.meshgrid(x, y)
            
            terrain = (np.exp(-(X**2 + Y**2)) * 800 +
                      np.exp(-((X-1)**2 + (Y-1)**2)) * 400 +
                      np.random.random(size) * 100)
        
        # Ensure positive elevation
        terrain = np.maximum(terrain, 0)
        
        return terrain
    
    def load_dataset(self, dataset_name, region='mountainous'):
        """
        Load a dataset (real or simulated).
        
        Args:
            dataset_name (str): Name of the dataset
            region (str): Region type for simulated data
        
        Returns:
            numpy.ndarray: Loaded terrain data
        """
        if dataset_name not in self.available_datasets:
            raise ValueError(f"Dataset {dataset_name} not available")
        
        dataset_info = self.available_datasets[dataset_name]
        
        if dataset_info['format'] == 'numpy':
            # Generate sample data
            terrain = self.generate_sample_srtm_data(dataset_info['size'], region)
        else:
            # For real data, you would implement actual loading here
            terrain = self.generate_sample_srtm_data(dataset_info['size'], region)
        
        # Store metadata
        self.loaded_datasets[dataset_name] = {
            'data': terrain,
            'metadata': dataset_info,
            'region': region
        }
        
        print(f"Loaded dataset {dataset_name}: {terrain.shape}, elevation range: {terrain.min():.1f}-{terrain.max():.1f}m")
        
        return terrain
    
    def preprocess_terrain(self, terrain, dataset_name):
        """
        Preprocess terrain data for simulation.
        
        Args:
            terrain (numpy.ndarray): Raw terrain data
            dataset_name (str): Name of the dataset
        
        Returns:
            numpy.ndarray: Preprocessed terrain data
        """
        print(f"Preprocessing terrain data for {dataset_name}")
        
        # Normalize elevation to 0-1 range for simulation
        terrain_min = terrain.min()
        terrain_max = terrain.max()
        terrain_normalized = (terrain - terrain_min) / (terrain_max - terrain_min)
        
        # Smooth the terrain slightly
        terrain_smoothed = ndimage.gaussian_filter(terrain_normalized, sigma=0.5)
        
        # Store preprocessing info
        if dataset_name in self.loaded_datasets:
            self.loaded_datasets[dataset_name]['preprocessing'] = {
                'original_min': terrain_min,
                'original_max': terrain_max,
                'normalized': terrain_normalized,
                'smoothed': terrain_smoothed
            }
        
        return terrain_smoothed
    
    def run_simulation_on_real_data(self, dataset_name, simulation_type='water', **kwargs):
        """
        Run simulation on real-world terrain data.
        
        Args:
            dataset_name (str): Name of the dataset
            simulation_type (str): Type of simulation to run
            **kwargs: Additional simulation parameters
        
        Returns:
            dict: Simulation results
        """
        if dataset_name not in self.loaded_datasets:
            raise ValueError(f"Dataset {dataset_name} not loaded")
        
        dataset = self.loaded_datasets[dataset_name]
        terrain = dataset['data']  # Use original terrain for simulation
        
        print(f"Running {simulation_type} simulation on {dataset_name}")
        
        results = {
            'dataset': dataset_name,
            'simulation_type': simulation_type,
            'terrain_shape': terrain.shape,
            'parameters': kwargs
        }
        
        if simulation_type == 'water':
            # Import water simulation
            from water_simulation import WaterSimulation
            
            water_sim = WaterSimulation(terrain)
            water_sim.simulate_rainfall_event(duration=kwargs.get('duration', 50))
            water_sim.identify_rivers()
            stats = water_sim.calculate_watershed_stats()
            
            results['water_simulation'] = water_sim
            results['watershed_stats'] = stats
            
        elif simulation_type == 'erosion':
            # Import erosion simulation
            from erosion_simulation import ErosionSimulation
            
            erosion_sim = ErosionSimulation(terrain)
            erosion_sim.simulate_terrain_aging(cycles=kwargs.get('cycles', 10))
            
            results['erosion_simulation'] = erosion_sim
            
        elif simulation_type == 'disasters':
            # Import disaster simulation
            from disaster_simulation import DisasterSimulation
            
            disaster_sim = DisasterSimulation(terrain)
            disaster_sim.simulate_flooding(**kwargs.get('flood_params', {}))
            disaster_sim.simulate_landslides(**kwargs.get('landslide_params', {}))
            disaster_sim.simulate_wildfire(**kwargs.get('fire_params', {}))
            
            results['disaster_simulation'] = disaster_sim
            
        elif simulation_type == 'pathfinding':
            # Import pathfinding simulation
            from pathfinding import PathfindingSimulation
            
            pathfinding_sim = PathfindingSimulation(terrain)
            
            # Generate random start and goal points
            start = (terrain.shape[0]//4, terrain.shape[1]//4)
            goals = [(terrain.shape[0]*3//4, terrain.shape[1]*3//4),
                    (terrain.shape[0]//2, terrain.shape[1]//2)]
            
            paths = pathfinding_sim.find_multiple_paths(start, goals, **kwargs.get('pathfinding_params', {}))
            
            results['pathfinding_simulation'] = pathfinding_sim
            results['paths'] = paths
            
        else:
            raise ValueError(f"Unknown simulation type: {simulation_type}")
        
        return results
    
    def compare_with_known_data(self, dataset_name, simulation_results):
        """
        Compare simulation results with known real-world data.
        
        Args:
            dataset_name (str): Name of the dataset
            simulation_results (dict): Results from simulation
        
        Returns:
            dict: Comparison analysis
        """
        print(f"Comparing simulation results with known data for {dataset_name}")
        
        comparison = {
            'dataset': dataset_name,
            'comparison_metrics': {}
        }
        
        # This is where you would compare with actual real-world data
        # For now, we'll create mock comparison metrics
        
        if 'watershed_stats' in simulation_results:
            stats = simulation_results['watershed_stats']
            
            # Mock comparison with known watershed data
            known_watersheds = 25  # Mock known value
            known_river_length = 120.5  # Mock known value
            
            comparison['comparison_metrics']['watershed_count'] = {
                'simulated': stats.get('num_watersheds', 0),
                'known': known_watersheds,
                'accuracy': 1 - abs(stats.get('num_watersheds', 0) - known_watersheds) / known_watersheds
            }
            
            comparison['comparison_metrics']['river_length'] = {
                'simulated': stats.get('river_length', 0),
                'known': known_river_length,
                'accuracy': 1 - abs(stats.get('river_length', 0) - known_river_length) / known_river_length
            }
        
        return comparison
    
    def visualize_real_data_simulation(self, dataset_name, simulation_results, figsize=(18, 12)):
        """
        Create comprehensive visualization of real data simulation.
        
        Args:
            dataset_name (str): Name of the dataset
            simulation_results (dict): Results from simulation
            figsize (tuple): Figure size
        
        Returns:
            matplotlib.figure.Figure: Visualization figure
        """
        dataset = self.loaded_datasets[dataset_name]
        original_terrain = dataset['data']
        preprocessed_terrain = dataset['preprocessing']['smoothed']
        
        fig, axes = plt.subplots(3, 3, figsize=figsize)
        
        # Original terrain
        im1 = axes[0, 0].imshow(original_terrain, cmap='terrain', origin='lower')
        axes[0, 0].set_title(f'Original {dataset_name.upper()} Data')
        axes[0, 0].set_xlabel('X')
        axes[0, 0].set_ylabel('Y')
        plt.colorbar(im1, ax=axes[0, 0], label='Elevation (m)')
        
        # Preprocessed terrain
        im2 = axes[0, 1].imshow(preprocessed_terrain, cmap='terrain', origin='lower')
        axes[0, 1].set_title('Preprocessed Terrain')
        axes[0, 1].set_xlabel('X')
        axes[0, 1].set_ylabel('Y')
        plt.colorbar(im2, ax=axes[0, 1], label='Normalized Elevation')
        
        # Dataset metadata
        axes[0, 2].axis('off')
        metadata = dataset['metadata']
        metadata_text = f"""Dataset Information:
        
Name: {dataset_name}
Size: {metadata['size']}
Resolution: {metadata['resolution']}m
Region: {dataset['region']}
Format: {metadata['format']}

Elevation Range:
Min: {original_terrain.min():.1f}m
Max: {original_terrain.max():.1f}m
Mean: {original_terrain.mean():.1f}m
        """
        axes[0, 2].text(0.1, 0.5, metadata_text, transform=axes[0, 2].transAxes, 
                        fontsize=10, verticalalignment='center',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        # Simulation results
        simulation_type = simulation_results['simulation_type']
        
        if simulation_type == 'water' and 'water_simulation' in simulation_results:
            water_sim = simulation_results['water_simulation']
            
            # Flow accumulation
            im3 = axes[1, 0].imshow(water_sim.flow_accumulation, cmap='viridis', origin='lower')
            axes[1, 0].set_title('Flow Accumulation')
            axes[1, 0].set_xlabel('X')
            axes[1, 0].set_ylabel('Y')
            plt.colorbar(im3, ax=axes[1, 0], label='Flow Volume')
            
            # River network
            river_display = np.ma.masked_where(water_sim.river_network == 0, water_sim.river_network)
            im4 = axes[1, 1].imshow(preprocessed_terrain, cmap='terrain', origin='lower', alpha=0.7)
            im5 = axes[1, 1].imshow(river_display, cmap='Blues', origin='lower', alpha=0.8)
            axes[1, 1].set_title('River Network')
            axes[1, 1].set_xlabel('X')
            axes[1, 1].set_ylabel('Y')
            
            # Watershed statistics
            axes[1, 2].axis('off')
            stats = simulation_results['watershed_stats']
            stats_text = f"""Watershed Statistics:
            
Watersheds: {stats.get('num_watersheds', 'N/A')}
River Length: {stats.get('river_length', 0):.1f} units
Max Flow: {stats.get('max_flow_accumulation', 0):.2f}
Total Flow: {stats.get('total_flow', 0):.2f}
River Coverage: {stats.get('river_coverage', 0)*100:.1f}%
            """
            axes[1, 2].text(0.1, 0.5, stats_text, transform=axes[1, 2].transAxes, 
                            fontsize=10, verticalalignment='center',
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        
        elif simulation_type == 'pathfinding' and 'paths' in simulation_results:
            pathfinding_sim = simulation_results['pathfinding_simulation']
            paths = simulation_results['paths']
            
            # Show paths
            axes[1, 0].imshow(preprocessed_terrain, cmap='terrain', origin='lower', alpha=0.7)
            
            colors = ['red', 'blue', 'green', 'orange']
            for i, (goal, path) in enumerate(paths.items()):
                if path:
                    path_y = [pos[0] for pos in path]
                    path_x = [pos[1] for pos in path]
                    color = colors[i % len(colors)]
                    axes[1, 0].plot(path_x, path_y, color=color, linewidth=2, 
                                   label=f'Path to {goal}')
            
            axes[1, 0].set_title('Pathfinding Results')
            axes[1, 0].set_xlabel('X')
            axes[1, 0].set_ylabel('Y')
            axes[1, 0].legend()
        
        # Comparison with known data
        comparison = self.compare_with_known_data(dataset_name, simulation_results)
        
        axes[2, 0].axis('off')
        if 'comparison_metrics' in comparison:
            metrics = comparison['comparison_metrics']
            comparison_text = "Comparison with Known Data:\n\n"
            
            for metric, data in metrics.items():
                comparison_text += f"{metric}:\n"
                comparison_text += f"  Simulated: {data['simulated']:.2f}\n"
                comparison_text += f"  Known: {data['known']:.2f}\n"
                comparison_text += f"  Accuracy: {data['accuracy']*100:.1f}%\n\n"
            
            axes[2, 0].text(0.1, 0.5, comparison_text, transform=axes[2, 0].transAxes, 
                            fontsize=10, verticalalignment='center',
                            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen"))
        
        # 3D visualization
        ax_3d = fig.add_subplot(3, 3, 8, projection='3d')
        x, y = np.meshgrid(np.arange(original_terrain.shape[1]), 
                          np.arange(original_terrain.shape[0]))
        
        # Show original terrain
        ax_3d.plot_surface(x, y, original_terrain, alpha=0.8, cmap='terrain')
        
        ax_3d.set_title('3D Real Data')
        ax_3d.set_xlabel('X')
        ax_3d.set_ylabel('Y')
        ax_3d.set_zlabel('Elevation (m)')
        
        # Summary
        axes[2, 2].axis('off')
        summary_text = f"""Simulation Summary:
        
Dataset: {dataset_name}
Simulation: {simulation_type}
Status: Complete
Results: Available
Comparison: Done
        """
        axes[2, 2].text(0.1, 0.5, summary_text, transform=axes[2, 2].transAxes, 
                        fontsize=12, verticalalignment='center',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow"))
        
        plt.tight_layout()
        return fig
    
    def export_real_data_results(self, dataset_name, simulation_results, output_dir="output", prefix="real_data_simulation"):
        """
        Export real data simulation results.
        """
        import os
        from datetime import datetime
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export dataset
        dataset = self.loaded_datasets[dataset_name]
        np.save(os.path.join(output_dir, f"{prefix}_{dataset_name}_original_{timestamp}.npy"), dataset['data'])
        np.save(os.path.join(output_dir, f"{prefix}_{dataset_name}_preprocessed_{timestamp}.npy"), 
                dataset['preprocessing']['smoothed'])
        
        # Export simulation results
        if 'water_simulation' in simulation_results:
            water_sim = simulation_results['water_simulation']
            np.save(os.path.join(output_dir, f"{prefix}_{dataset_name}_flow_accumulation_{timestamp}.npy"), 
                   water_sim.flow_accumulation)
            np.save(os.path.join(output_dir, f"{prefix}_{dataset_name}_river_network_{timestamp}.npy"), 
                   water_sim.river_network)
        
        # Export comparison results
        comparison = self.compare_with_known_data(dataset_name, simulation_results)
        with open(os.path.join(output_dir, f"{prefix}_{dataset_name}_comparison_{timestamp}.json"), 'w') as f:
            json.dump(comparison, f, indent=2)
        
        # Export visualization
        fig = self.visualize_real_data_simulation(dataset_name, simulation_results)
        fig.savefig(os.path.join(output_dir, f"{prefix}_{dataset_name}_visualization_{timestamp}.png"), 
                   dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        print(f"Real data simulation results exported to {output_dir}/")
        return timestamp
