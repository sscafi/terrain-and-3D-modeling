
# Terrain 3D Modelling

A comprehensive Python project for procedural terrain generation, 3D visualization, and environmental simulation. Features both batch processing and real-time interactive 3D applications with professional-grade terrain simulation.

## Features

### 🏔️ **Core Terrain Generation**
- **Procedural Terrain Generation**: Diamond-Square algorithm for realistic height maps
- **Professional Terrain**: Realistic Earth-like terrain with mountain ranges, valleys, and water bodies
- **GPS-Quality Topography**: Contour lines, elevation shading, and topographic visualization
- **Multiple Terrain Styles**: Professional, Satellite, and Topographic views

### 🌊 **Environmental Simulations**
- **Water Flow Simulation**: Rainfall simulation with downhill flow and river network generation
- **Erosion Modeling**: Thermal and hydraulic erosion with terrain aging simulation
- **Disaster Simulations**: Flooding, landslides, and wildfire spread modeling
- **Real-Time Physics**: Live simulation updates with realistic water flow and erosion

### 🎮 **Interactive Applications**
- **Real-Time 3D Viewer**: Professional OpenGL-based 3D terrain viewer
- **Interactive Controls**: GUI panels with sliders for all simulation parameters
- **Camera Systems**: FPS, Orbit, and Bird's Eye camera modes
- **Window Management**: Resizable windows and fullscreen support

### 🗺️ **Data Integration**
- **Free Data Sources**: OpenStreetMap and NASA Worldview integration
- **Real Data Import**: Import and simulate on real-world DEM datasets
- **Pathfinding**: A* and Dijkstra algorithms with terrain-aware cost functions
- **Watershed Analysis**: Automatic watershed identification and statistics

### 💾 **Export & Processing**
- **Export Capabilities**: Save all simulation data as NumPy arrays and PNG images
- **CLI Interface**: Comprehensive command-line arguments for all phases
- **Reproducible Results**: Seed-based random generation
- **Batch Processing**: Run multiple simulations with different parameters

## Project Structure

```
terrain-and-3D-modeling/
├── 📁 src/                    # Core simulation modules
│   ├── water_simulation.py    # Water flow simulation
│   ├── erosion_simulation.py  # Erosion modeling
│   ├── disaster_simulation.py # Disaster simulations
│   ├── pathfinding.py         # Pathfinding algorithms
│   └── data_import.py         # Real data import
├── 📁 docs/                   # Documentation
│   └── PROJECT_SUMMARY.md     # Detailed project summary
├── 📁 examples/               # Example scripts
│   └── quick_start.py         # Quick start example
├── 📁 data/                   # Data files
├── 📁 output/                 # Generated outputs
├── 📁 venv_realtime/          # Virtual environment
├── main.py                    # Batch processing entry point
├── professional_terrain_viewer.py # Real-time 3D viewer
├── requirements.txt           # Batch processing dependencies
├── requirements_realtime.txt  # Real-time viewer dependencies
└── README.md                  # This file
```

## Quick Start

### 🖥️ **Real-Time 3D Viewer (Recommended)**
1. Install real-time dependencies:
```bash
pip install -r requirements_realtime.txt
```

2. Run the professional 3D viewer:
```bash
python professional_terrain_viewer.py
```

3. **Controls:**
   - **WASD** - Move camera
   - **Mouse + Left Click** - Look around
   - **SPACE** - Toggle rainfall
   - **E** - Toggle erosion
   - **F** - Toggle flooding
   - **L** - Toggle landslides
   - **R** - Generate new terrain
   - **C** - Toggle contour lines
   - **S** - Toggle elevation shading
   - **T** - Reset all simulations
   - **ESC** - Exit

### 📊 **Batch Processing**
1. Install batch processing dependencies:
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

### 🚀 **Examples**
Run the quick start example:
```bash
python examples/quick_start.py
```

## Dependencies

### 📊 **Batch Processing** (`requirements.txt`)
- NumPy: Numerical computing and array operations
- Matplotlib: 3D plotting and visualization
- SciPy: Scientific computing and image processing

### 🎮 **Real-Time 3D Viewer** (`requirements_realtime.txt`)
- Pygame: Game development and window management
- PyOpenGL: OpenGL bindings for 3D rendering
- PyOpenGL-accelerate: OpenGL acceleration
- NumPy: Numerical computing and array operations
- SciPy: Scientific computing and image processing
- Pillow: Image processing
- ModernGL: Modern OpenGL wrapper
- Matplotlib: Additional visualization support

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

## 🎮 **Real-Time 3D Applications**

### Professional Terrain Viewer (`professional_terrain_viewer.py`)
- **Real-Time Rendering**: OpenGL-based 3D terrain visualization
- **Interactive Simulations**: Live rainfall, erosion, and disaster effects
- **Professional Visualization**: GPS-quality topographic views with contour lines
- **Free Data Integration**: OpenStreetMap and NASA Worldview imagery
- **GUI Controls**: Tkinter-based control panel for all parameters
- **Multiple Terrain Styles**: Professional, Satellite, and Topographic views
- **Window Management**: Resizable windows and fullscreen support

### Key Features:
- **Real-Time Physics**: Water flow, erosion, and disaster simulations update live
- **Professional Graphics**: Modern OpenGL rendering with realistic lighting
- **Interactive Controls**: GUI sliders for rainfall intensity, erosion rates, disaster parameters
- **Camera Systems**: Multiple camera modes for different viewing angles
- **Performance Optimized**: Cached rendering and efficient update cycles




