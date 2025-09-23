#!/usr/bin/env python3
"""
Terrain 3D Modeling - Main Application
Integrates terrain generation with 3D visualization and export capabilities.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import random
import os
from datetime import datetime
from water_simulation import WaterSimulation


def generate_height_map(size, roughness, seed=None):
    """
    Generate a terrain height map using the diamond-square algorithm.
    
    Args:
        size (int): Size of the height map grid (size x size).
        roughness (float): Roughness factor that determines the variability in height values.
        seed (int, optional): Random seed for reproducible results.
    
    Returns:
        height_map (numpy.ndarray): 2D array representing the terrain height map.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Initialize the height map with random values
    height_map = np.random.random((size, size))
    
    # Generate the terrain by repeatedly applying the diamond-square algorithm
    step_size = size - 1
    while step_size > 1:
        half_step = step_size // 2
        
        # Diamond step
        for x in range(half_step, size, step_size):
            for y in range(half_step, size, step_size):
                avg = (height_map[x-half_step][y-half_step] +
                       height_map[x+half_step][y-half_step] +
                       height_map[x-half_step][y+half_step] +
                       height_map[x+half_step][y+half_step]) / 4
                height_map[x][y] = avg + random.uniform(-1, 1) * roughness
        
        # Square step
        for x in range(0, size, half_step):
            for y in range((x + half_step) % step_size, size, step_size):
                avg = 0
                count = 0
                if x >= half_step:
                    avg += height_map[x-half_step][y]
                    count += 1
                if x + half_step < size:
                    avg += height_map[x+half_step][y]
                    count += 1
                if y >= half_step:
                    avg += height_map[x][y-half_step]
                    count += 1
                if y + half_step < size:
                    avg += height_map[x][y+half_step]
                    count += 1
                height_map[x][y] = avg / count + random.uniform(-1, 1) * roughness
        
        step_size //= 2
        roughness /= 2
    
    return height_map


def visualize_terrain(height_map, title="Generated Terrain"):
    """
    Create 3D visualization of the terrain.
    
    Args:
        height_map (numpy.ndarray): 2D height map data
        title (str): Title for the plot
    """
    size = height_map.shape[0]
    x, y = np.meshgrid(np.arange(size), np.arange(size))
    z = height_map
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create surface plot
    surf = ax.plot_surface(x, y, z, cmap='terrain', alpha=0.8, linewidth=0, antialiased=True)
    
    # Add colorbar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=20, label='Elevation')
    
    # Set labels and title
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Elevation')
    ax.set_title(title)
    
    # Set viewing angle
    ax.view_init(elev=30, azim=45)
    
    plt.tight_layout()
    return fig, ax


def export_terrain(height_map, output_dir="output", prefix="terrain"):
    """
    Export terrain data to NumPy array and PNG image.
    
    Args:
        height_map (numpy.ndarray): 2D height map data
        output_dir (str): Directory to save outputs
        prefix (str): Prefix for output filenames
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export as NumPy array
    np_filename = os.path.join(output_dir, f"{prefix}_{timestamp}.npy")
    np.save(np_filename, height_map)
    print(f"Terrain data saved to: {np_filename}")
    
    # Export as PNG image
    png_filename = os.path.join(output_dir, f"{prefix}_{timestamp}.png")
    plt.figure(figsize=(10, 8))
    plt.imshow(height_map, cmap='terrain', origin='lower')
    plt.colorbar(label='Elevation')
    plt.title(f'Terrain Height Map - {timestamp}')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.savefig(png_filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Terrain image saved to: {png_filename}")
    
    return np_filename, png_filename


def run_water_simulation(height_map, args):
    """
    Run water flow simulation on the generated terrain.
    
    Args:
        height_map (numpy.ndarray): Generated terrain
        args: Command line arguments
    """
    print("\n" + "="*50)
    print("PHASE 2: WATER FLOW SIMULATION")
    print("="*50)
    
    # Initialize water simulation
    water_sim = WaterSimulation(
        terrain=height_map,
        rainfall_intensity=args.rainfall_intensity,
        evaporation_rate=args.evaporation_rate
    )
    
    # Run rainfall simulation
    water_sim.simulate_rainfall_event(
        duration=args.rainfall_duration,
        intensity=args.rainfall_intensity,
        coverage=args.rainfall_coverage
    )
    
    # Identify river network
    water_sim.identify_rivers(threshold=args.river_threshold)
    
    # Calculate watershed statistics
    stats = water_sim.calculate_watershed_stats()
    
    print(f"\nWatershed Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Export water simulation data
    if args.export:
        water_sim.export_water_data(args.output_dir)
    
    # Display water flow visualization
    if not args.no_display:
        fig = water_sim.visualize_water_flow()
        plt.show()
    
    return water_sim


def main():
    """Main application function."""
    parser = argparse.ArgumentParser(description='Generate and visualize 3D terrain with water simulation')
    
    # Terrain generation arguments
    parser.add_argument('--size', type=int, default=65, 
                       help='Size of the terrain grid (default: 65)')
    parser.add_argument('--roughness', type=float, default=0.5,
                       help='Roughness factor for terrain generation (default: 0.5)')
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for reproducible results (default: random)')
    
    # Water simulation arguments
    parser.add_argument('--water-simulation', action='store_true',
                       help='Run water flow simulation (Phase 2)')
    parser.add_argument('--rainfall-intensity', type=float, default=1.0,
                       help='Rainfall intensity for water simulation (default: 1.0)')
    parser.add_argument('--rainfall-duration', type=int, default=50,
                       help='Duration of rainfall simulation in time steps (default: 50)')
    parser.add_argument('--rainfall-coverage', type=float, default=1.0,
                       help='Fraction of terrain covered by rainfall (default: 1.0)')
    parser.add_argument('--evaporation-rate', type=float, default=0.1,
                       help='Water evaporation rate per time step (default: 0.1)')
    parser.add_argument('--river-threshold', type=float, default=None,
                       help='Flow accumulation threshold for river identification (default: 95th percentile)')
    
    # Output arguments
    parser.add_argument('--export', action='store_true',
                       help='Export terrain and water simulation data to files')
    parser.add_argument('--no-display', action='store_true',
                       help='Skip displaying plots')
    parser.add_argument('--output-dir', type=str, default='output',
                       help='Output directory for exported files (default: output)')
    
    args = parser.parse_args()
    
    print(f"Generating terrain with size={args.size}, roughness={args.roughness}, seed={args.seed}")
    
    # Generate terrain
    height_map = generate_height_map(args.size, args.roughness, args.seed)
    
    # Print terrain statistics
    print(f"Terrain statistics:")
    print(f"  Min elevation: {height_map.min():.3f}")
    print(f"  Max elevation: {height_map.max():.3f}")
    print(f"  Mean elevation: {height_map.mean():.3f}")
    print(f"  Std deviation: {height_map.std():.3f}")
    
    # Export if requested
    if args.export:
        export_terrain(height_map, args.output_dir)
    
    # Display 3D visualization
    if not args.no_display:
        title = f"Terrain (Size: {args.size}, Roughness: {args.roughness})"
        if args.seed is not None:
            title += f", Seed: {args.seed}"
        
        fig, ax = visualize_terrain(height_map, title)
        plt.show()


if __name__ == "__main__":
    main()
