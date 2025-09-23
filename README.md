
# Terrain 3D Modelling

A Python project for procedural terrain generation and 3D visualization using the Diamond-Square algorithm. This repository explores realistic terrain mechanics and environmental simulations.

## Features

- **Procedural Terrain Generation**: Diamond-Square algorithm for realistic height maps
- **3D Visualization**: Interactive 3D terrain plots with Matplotlib
- **Water Flow Simulation**: Rainfall simulation with downhill flow and river network generation
- **Erosion Modeling**: Thermal and hydraulic erosion with terrain aging simulation
- **Disaster Simulations**: Flooding, landslides, and wildfire spread modeling
- **Pathfinding**: A* and Dijkstra algorithms with terrain-aware cost functions
- **Real Data Integration**: Import and simulate on real-world DEM datasets
- **Watershed Analysis**: Automatic watershed identification and statistics
- **Export Capabilities**: Save all simulation data as NumPy arrays and PNG images
- **CLI Interface**: Comprehensive command-line arguments for all phases
- **Reproducible Results**: Seed-based random generation

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run all phases:
```bash
python main.py --all-phases --size 65 --export
```

3. Run specific phases:
```bash
python main.py --phases 1 2 3 --size 65 --export
```

4. Run water flow simulation only:
```bash
python main.py --phases 2 --size 65 --rainfall-duration 50 --export
```

5. Run pathfinding on real data:
```bash
python main.py --phases 6 --real-dataset srtm_sample --real-simulation-type pathfinding --export
```

6. View all command-line options:
```bash
python main.py --help
```

## Dependencies
- NumPy: Numerical computing and array operations
- Matplotlib: 3D plotting and visualization
- SciPy: Scientific computing and image processing

## Roadmap

This project follows a simulation-first approach:

- ✅ **Phase 1**: Integration & Cleanup
- ✅ **Phase 2**: Water Flow Simulation  
- ✅ **Phase 3**: Erosion & Terrain Evolution
- ✅ **Phase 4**: Disaster Simulations
- ✅ **Phase 5**: Pathfinding & Accessibility
- ✅ **Phase 6**: Data-Driven Terrain

## Phase Features

### Phase 1: Integration & Cleanup
- **Unified CLI**: Single command-line interface for all operations
- **Export System**: NumPy arrays and PNG images with timestamps
- **Modular Design**: Clean separation of concerns

### Phase 2: Water Flow Simulation
- **Rainfall Simulation**: Configurable intensity, duration, and coverage
- **Flow Accumulation**: Water flows downhill following steepest descent
- **River Network Generation**: Automatic identification of river channels
- **Watershed Analysis**: Statistics on drainage basins and river systems

### Phase 3: Erosion & Terrain Evolution
- **Thermal Erosion**: Slope collapse simulation with talus angle thresholds
- **Hydraulic Erosion**: Water-carried sediment transport and deposition
- **Terrain Aging**: Iterative erosion cycles for realistic terrain evolution
- **Sediment Tracking**: Complete sediment transport modeling

### Phase 4: Disaster Simulations
- **Flooding Model**: Sea level rise and rainfall accumulation simulation
- **Landslide Simulation**: Slope and rainfall-triggered mass movements
- **Wildfire Spread**: Terrain, vegetation, and wind-based fire propagation
- **Risk Assessment**: Combined disaster risk mapping

### Phase 5: Pathfinding & Accessibility
- **A* Algorithm**: Heuristic-based optimal pathfinding
- **Dijkstra Algorithm**: Guaranteed shortest path finding
- **Cost Functions**: Slope, water, disaster, and comprehensive cost models
- **Accessibility Mapping**: Terrain navigation difficulty visualization

### Phase 6: Data-Driven Terrain
- **Real Data Import**: SRTM and USGS DEM dataset integration
- **Data Preprocessing**: Normalization and smoothing for simulation
- **Validation**: Comparison with known real-world data
- **Multi-Region Support**: Mountainous, coastal, and desert terrain types




