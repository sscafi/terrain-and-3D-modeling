
# Terrain 3D Modelling

A Python project for procedural terrain generation and 3D visualization using the Diamond-Square algorithm. This repository explores realistic terrain mechanics and environmental simulations.

## Features

- **Procedural Terrain Generation**: Diamond-Square algorithm for realistic height maps
- **3D Visualization**: Interactive 3D terrain plots with Matplotlib
- **Water Flow Simulation**: Rainfall simulation with downhill flow and river network generation
- **Watershed Analysis**: Automatic watershed identification and statistics
- **Export Capabilities**: Save terrains and water simulation data as NumPy arrays and PNG images
- **CLI Interface**: Command-line arguments for customization
- **Reproducible Results**: Seed-based random generation

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Generate and visualize terrain:
```bash
python main.py --size 65 --roughness 0.5 --export
```

3. Run water flow simulation:
```bash
python main.py --size 65 --water-simulation --rainfall-duration 50 --export
```

4. View command-line options:
```bash
python main.py --help
```

## Dependencies
- NumPy: Numerical computing and array operations
- Matplotlib: 3D plotting and visualization

## Roadmap

This project follows a simulation-first approach:

- ✅ **Phase 1**: Integration & Cleanup
- ✅ **Phase 2**: Water Flow Simulation  
- 📋 **Phase 3**: Erosion & Terrain Evolution
- 📋 **Phase 4**: Disaster Simulations
- 📋 **Phase 5**: Pathfinding & Accessibility
- 📋 **Phase 6**: Data-Driven Terrain

## Phase 2 Features

- **Rainfall Simulation**: Configurable rainfall intensity, duration, and coverage
- **Flow Accumulation**: Water flows downhill following steepest descent
- **River Network Generation**: Automatic identification of river channels
- **Watershed Analysis**: Statistics on drainage basins and river systems
- **Comprehensive Visualization**: 6-panel visualization showing terrain, water, and rivers




