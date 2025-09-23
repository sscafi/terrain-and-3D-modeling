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
from erosion_simulation import ErosionSimulation
from disaster_simulation import DisasterSimulation
from pathfinding import PathfindingSimulation
from data_import import DataImportSimulation


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


def run_erosion_simulation(height_map, water_sim, args):
    """
    Run erosion simulation on the terrain.
    
    Args:
        height_map (numpy.ndarray): Generated terrain
        water_sim (WaterSimulation): Water simulation results
        args: Command line arguments
    """
    print("\n" + "="*50)
    print("PHASE 3: EROSION & TERRAIN EVOLUTION")
    print("="*50)
    
    # Initialize erosion simulation
    erosion_sim = ErosionSimulation(
        terrain=height_map,
        flow_accumulation=water_sim.flow_accumulation if water_sim else None,
        water_surface=water_sim.water_surface if water_sim else None
    )
    
    # Run terrain aging simulation
    erosion_sim.simulate_terrain_aging(
        cycles=args.erosion_cycles,
        talus_angle=args.talus_angle
    )
    
    # Export erosion data
    if args.export:
        erosion_sim.export_erosion_data(args.output_dir)
    
    # Display erosion visualization
    if not args.no_display:
        fig = erosion_sim.visualize_erosion()
        plt.show()
    
    return erosion_sim


def run_disaster_simulation(height_map, water_sim, erosion_sim, args):
    """
    Run disaster simulations on the terrain.
    
    Args:
        height_map (numpy.ndarray): Generated terrain
        water_sim (WaterSimulation): Water simulation results
        erosion_sim (ErosionSimulation): Erosion simulation results
        args: Command line arguments
    """
    print("\n" + "="*50)
    print("PHASE 4: DISASTER SIMULATIONS")
    print("="*50)
    
    # Initialize disaster simulation
    disaster_sim = DisasterSimulation(
        terrain=height_map,
        flow_accumulation=water_sim.flow_accumulation if water_sim else None,
        water_surface=water_sim.water_surface if water_sim else None
    )
    
    # Run disaster simulations
    disaster_sim.simulate_flooding(
        sea_level_rise=args.sea_level_rise,
        rainfall_intensity=args.flood_rainfall_intensity,
        duration=args.flood_duration
    )
    
    disaster_sim.simulate_landslides(
        rainfall_trigger=args.landslide_rainfall_trigger,
        slope_threshold=args.landslide_slope_threshold
    )
    
    disaster_sim.simulate_wildfire(
        ignition_points=args.fire_ignition_points,
        wind_direction=args.wind_direction,
        spread_rate=args.fire_spread_rate
    )
    
    # Export disaster data
    if args.export:
        disaster_sim.export_disaster_data(args.output_dir)
    
    # Display disaster visualization
    if not args.no_display:
        fig = disaster_sim.visualize_disasters()
        plt.show()
    
    return disaster_sim


def run_pathfinding_simulation(height_map, water_sim, disaster_sim, args):
    """
    Run pathfinding simulation on the terrain.
    
    Args:
        height_map (numpy.ndarray): Generated terrain
        water_sim (WaterSimulation): Water simulation results
        disaster_sim (DisasterSimulation): Disaster simulation results
        args: Command line arguments
    """
    print("\n" + "="*50)
    print("PHASE 5: PATHFINDING & ACCESSIBILITY")
    print("="*50)
    
    # Initialize pathfinding simulation
    pathfinding_sim = PathfindingSimulation(
        terrain=height_map,
        flow_accumulation=water_sim.flow_accumulation if water_sim else None,
        water_surface=water_sim.water_surface if water_sim else None,
        flood_map=disaster_sim.flood_map if disaster_sim else None,
        landslide_map=disaster_sim.landslide_map if disaster_sim else None,
        wildfire_map=disaster_sim.wildfire_map if disaster_sim else None
    )
    
    # Generate start and goal points
    start = (args.pathfinding_start_y, args.pathfinding_start_x)
    goals = [(args.pathfinding_goal_y, args.pathfinding_goal_x)]
    
    # Find paths
    paths = pathfinding_sim.find_multiple_paths(
        start, goals,
        algorithm=args.pathfinding_algorithm,
        cost_type=args.pathfinding_cost_type
    )
    
    # Export pathfinding data
    if args.export:
        pathfinding_sim.export_pathfinding_data(args.output_dir)
    
    # Display pathfinding visualization
    if not args.no_display:
        fig = pathfinding_sim.visualize_pathfinding(paths, args.pathfinding_cost_type)
        plt.show()
    
    return pathfinding_sim


def run_real_data_simulation(args):
    """
    Run simulations on real-world terrain data.
    
    Args:
        args: Command line arguments
    """
    print("\n" + "="*50)
    print("PHASE 6: DATA-DRIVEN TERRAIN")
    print("="*50)
    
    # Initialize data import simulation
    data_sim = DataImportSimulation(args.data_dir)
    
    # Load dataset
    terrain = data_sim.load_dataset(args.real_dataset, args.real_dataset_region)
    
    # Preprocess terrain
    preprocessed_terrain = data_sim.preprocess_terrain(terrain, args.real_dataset)
    
    # Run simulation on real data
    simulation_results = data_sim.run_simulation_on_real_data(
        args.real_dataset,
        simulation_type=args.real_simulation_type,
        duration=args.real_simulation_duration,
        cycles=args.real_simulation_cycles
    )
    
    # Export real data results
    if args.export:
        data_sim.export_real_data_results(args.real_dataset, simulation_results, args.output_dir)
    
    # Display real data visualization
    if not args.no_display:
        fig = data_sim.visualize_real_data_simulation(args.real_dataset, simulation_results)
        plt.show()
    
    return data_sim, simulation_results


def main():
    """Main application function."""
    parser = argparse.ArgumentParser(description='Complete terrain simulation system with all phases')
    
    # Terrain generation arguments
    parser.add_argument('--size', type=int, default=65, 
                       help='Size of the terrain grid (default: 65)')
    parser.add_argument('--roughness', type=float, default=0.5,
                       help='Roughness factor for terrain generation (default: 0.5)')
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for reproducible results (default: random)')
    
    # Phase selection
    parser.add_argument('--phases', nargs='+', default=['1'], 
                       choices=['1', '2', '3', '4', '5', '6'],
                       help='Phases to run (default: 1)')
    parser.add_argument('--all-phases', action='store_true',
                       help='Run all phases sequentially')
    
    # Water simulation arguments (Phase 2)
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
    
    # Erosion simulation arguments (Phase 3)
    parser.add_argument('--erosion-cycles', type=int, default=10,
                       help='Number of erosion cycles (default: 10)')
    parser.add_argument('--talus-angle', type=float, default=0.5,
                       help='Critical slope angle for thermal erosion (default: 0.5)')
    
    # Disaster simulation arguments (Phase 4)
    parser.add_argument('--sea-level-rise', type=float, default=0.1,
                       help='Sea level rise for flooding simulation (default: 0.1)')
    parser.add_argument('--flood-rainfall-intensity', type=float, default=2.0,
                       help='Rainfall intensity for flooding (default: 2.0)')
    parser.add_argument('--flood-duration', type=int, default=20,
                       help='Duration of flooding simulation (default: 20)')
    parser.add_argument('--landslide-rainfall-trigger', type=float, default=1.5,
                       help='Rainfall threshold for landslide trigger (default: 1.5)')
    parser.add_argument('--landslide-slope-threshold', type=float, default=0.8,
                       help='Slope threshold for landslides (default: 0.8)')
    parser.add_argument('--fire-ignition-points', nargs='+', type=int, default=None,
                       help='Fire ignition points as x,y pairs (default: random)')
    parser.add_argument('--wind-direction', type=float, default=0,
                       help='Wind direction in degrees (default: 0)')
    parser.add_argument('--fire-spread-rate', type=float, default=0.3,
                       help='Fire spread rate (default: 0.3)')
    
    # Pathfinding arguments (Phase 5)
    parser.add_argument('--pathfinding-start-x', type=int, default=None,
                       help='Pathfinding start X coordinate (default: size//4)')
    parser.add_argument('--pathfinding-start-y', type=int, default=None,
                       help='Pathfinding start Y coordinate (default: size//4)')
    parser.add_argument('--pathfinding-goal-x', type=int, default=None,
                       help='Pathfinding goal X coordinate (default: 3*size//4)')
    parser.add_argument('--pathfinding-goal-y', type=int, default=None,
                       help='Pathfinding goal Y coordinate (default: 3*size//4)')
    parser.add_argument('--pathfinding-algorithm', type=str, default='astar',
                       choices=['astar', 'dijkstra'],
                       help='Pathfinding algorithm (default: astar)')
    parser.add_argument('--pathfinding-cost-type', type=str, default='comprehensive',
                       choices=['distance', 'slope', 'water', 'disasters', 'comprehensive'],
                       help='Pathfinding cost function (default: comprehensive)')
    
    # Real data arguments (Phase 6)
    parser.add_argument('--real-dataset', type=str, default='srtm_sample',
                       choices=['srtm_sample', 'usgs_sample'],
                       help='Real dataset to use (default: srtm_sample)')
    parser.add_argument('--real-dataset-region', type=str, default='mountainous',
                       choices=['mountainous', 'coastal', 'desert'],
                       help='Region type for real dataset (default: mountainous)')
    parser.add_argument('--real-simulation-type', type=str, default='water',
                       choices=['water', 'erosion', 'disasters', 'pathfinding'],
                       help='Simulation type for real data (default: water)')
    parser.add_argument('--real-simulation-duration', type=int, default=50,
                       help='Duration for real data simulation (default: 50)')
    parser.add_argument('--real-simulation-cycles', type=int, default=10,
                       help='Cycles for real data simulation (default: 10)')
    parser.add_argument('--data-dir', type=str, default='data',
                       help='Directory for real data storage (default: data)')
    
    # Output arguments
    parser.add_argument('--export', action='store_true',
                       help='Export all simulation data to files')
    parser.add_argument('--no-display', action='store_true',
                       help='Skip displaying plots')
    parser.add_argument('--output-dir', type=str, default='output',
                       help='Output directory for exported files (default: output)')
    
    args = parser.parse_args()
    
    # Determine phases to run
    if args.all_phases:
        phases_to_run = ['1', '2', '3', '4', '5', '6']
    else:
        phases_to_run = args.phases
    
    print(f"Running phases: {phases_to_run}")
    print(f"Generating terrain with size={args.size}, roughness={args.roughness}, seed={args.seed}")
    
    # Initialize simulation results
    water_sim = None
    erosion_sim = None
    disaster_sim = None
    pathfinding_sim = None
    data_sim = None
    
    # Phase 1: Terrain Generation
    if '1' in phases_to_run:
        print("\n" + "="*50)
        print("PHASE 1: TERRAIN GENERATION")
        print("="*50)
        
        # Generate terrain
        height_map = generate_height_map(args.size, args.roughness, args.seed)
        
        # Print terrain statistics
        print(f"Terrain statistics:")
        print(f"  Min elevation: {height_map.min():.3f}")
        print(f"  Max elevation: {height_map.max():.3f}")
        print(f"  Mean elevation: {height_map.mean():.3f}")
        print(f"  Std deviation: {height_map.std():.3f}")
        
        # Export terrain if requested
        if args.export:
            export_terrain(height_map, args.output_dir)
        
        # Display 3D terrain visualization
        if not args.no_display and len(phases_to_run) == 1:
            title = f"Terrain (Size: {args.size}, Roughness: {args.roughness})"
            if args.seed is not None:
                title += f", Seed: {args.seed}"
            
            fig, ax = visualize_terrain(height_map, title)
            plt.show()
    else:
        # For phases 2-6, we need to generate terrain first
        height_map = generate_height_map(args.size, args.roughness, args.seed)
    
    # Phase 2: Water Flow Simulation
    if '2' in phases_to_run:
        water_sim = run_water_simulation(height_map, args)
    
    # Phase 3: Erosion & Terrain Evolution
    if '3' in phases_to_run:
        erosion_sim = run_erosion_simulation(height_map, water_sim, args)
    
    # Phase 4: Disaster Simulations
    if '4' in phases_to_run:
        disaster_sim = run_disaster_simulation(height_map, water_sim, erosion_sim, args)
    
    # Phase 5: Pathfinding & Accessibility
    if '5' in phases_to_run:
        # Set default pathfinding coordinates if not provided
        if args.pathfinding_start_x is None:
            args.pathfinding_start_x = args.size // 4
        if args.pathfinding_start_y is None:
            args.pathfinding_start_y = args.size // 4
        if args.pathfinding_goal_x is None:
            args.pathfinding_goal_x = 3 * args.size // 4
        if args.pathfinding_goal_y is None:
            args.pathfinding_goal_y = 3 * args.size // 4
            
        pathfinding_sim = run_pathfinding_simulation(height_map, water_sim, disaster_sim, args)
    
    # Phase 6: Data-Driven Terrain
    if '6' in phases_to_run:
        data_sim, simulation_results = run_real_data_simulation(args)
    
    print("\n" + "="*50)
    print("SIMULATION COMPLETE")
    print("="*50)
    print(f"Phases completed: {phases_to_run}")
    if args.export:
        print(f"All data exported to: {args.output_dir}/")
    print("="*50)


if __name__ == "__main__":
    main()
