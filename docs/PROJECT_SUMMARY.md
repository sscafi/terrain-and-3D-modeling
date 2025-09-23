# Terrain 3D Modeling Project - Input/Output Summary

## Project Overview
A comprehensive terrain simulation system featuring both batch processing and real-time interactive 3D applications. Generates procedural terrain and runs multiple environmental simulations including water flow, erosion, disasters, pathfinding, and real-world data analysis with professional-grade visualization.

## Input Parameters

### 🎮 **Real-Time 3D Viewer** (`professional_terrain_viewer.py`)
- **Interactive Controls**: GUI sliders and keyboard shortcuts
- **Terrain Parameters**: Height scale, roughness, terrain style
- **Simulation Parameters**: Rainfall intensity/coverage, erosion rates, disaster settings
- **Visualization**: Contour lines, elevation shading, terrain styles
- **Data Sources**: Free imagery from OpenStreetMap and NASA Worldview

### 📊 **Batch Processing** (`main.py`)

#### Core Terrain Generation
- `--size`: Terrain grid size (default: 65, range: 33-200+)
- `--roughness`: Terrain roughness factor (default: 0.5, range: 0.1-1.0)
- `--seed`: Random seed for reproducible results (default: random)

#### Phase Selection
- `--phases`: Specific phases to run [1,2,3,4,5,6] (default: 1)
- `--all-phases`: Run all 6 phases sequentially

#### Water Simulation (Phase 2)
- `--rainfall-intensity`: Rainfall amount per time step (default: 1.0)
- `--rainfall-duration`: Simulation time steps (default: 50)
- `--rainfall-coverage`: Fraction of terrain covered by rain (default: 1.0)
- `--evaporation-rate`: Water evaporation rate (default: 0.1)
- `--river-threshold`: Flow threshold for river identification (default: 95th percentile)

#### Erosion Simulation (Phase 3)
- `--erosion-cycles`: Number of erosion cycles (default: 10)
- `--talus-angle`: Critical slope angle for thermal erosion (default: 0.5)

#### Disaster Simulation (Phase 4)
- `--sea-level-rise`: Sea level rise amount (default: 0.1)
- `--flood-rainfall-intensity`: Rainfall intensity for flooding (default: 2.0)
- `--flood-duration`: Flooding simulation duration (default: 20)
- `--landslide-rainfall-trigger`: Rainfall threshold for landslides (default: 1.5)
- `--landslide-slope-threshold`: Slope threshold for landslides (default: 0.8)
- `--wind-direction`: Wind direction in degrees (default: 0)
- `--fire-spread-rate`: Fire spread rate (default: 0.3)

#### Pathfinding (Phase 5)
- `--pathfinding-start-x/y`: Starting coordinates (default: size//4)
- `--pathfinding-goal-x/y`: Goal coordinates (default: 3*size//4)
- `--pathfinding-algorithm`: Algorithm choice [astar, dijkstra] (default: astar)
- `--pathfinding-cost-type`: Cost function [distance, slope, water, disasters, comprehensive] (default: comprehensive)

#### Real Data (Phase 6)
- `--real-dataset`: Dataset choice [srtm_sample, usgs_sample] (default: srtm_sample)
- `--real-dataset-region`: Region type [mountainous, coastal, desert] (default: mountainous)
- `--real-simulation-type`: Simulation type [water, erosion, disasters, pathfinding] (default: water)
- `--real-simulation-duration`: Duration for real data simulation (default: 50)
- `--real-simulation-cycles`: Cycles for real data simulation (default: 10)

#### Output Control
- `--export`: Export all data to files
- `--no-display`: Skip displaying plots
- `--output-dir`: Output directory (default: output)

## Output Files

### 🎮 **Real-Time 3D Viewer Outputs**
- **Live Visualization**: Real-time 3D terrain rendering with OpenGL
- **Interactive Simulations**: Live rainfall, erosion, and disaster effects
- **GUI Controls**: Real-time parameter adjustment via Tkinter interface
- **Free Data Integration**: Live loading of OpenStreetMap and NASA Worldview imagery
- **Professional Visualization**: GPS-quality topographic views with contour lines

### 📊 **Batch Processing Outputs**

#### Raw Data Files (.npy - NumPy Arrays)

##### Phase 1: Terrain Generation
- `terrain_YYYYMMDD_HHMMSS.npy`: Generated terrain height map (2D array)

##### Phase 2: Water Flow Simulation
- `water_simulation_water_surface_YYYYMMDD_HHMMSS.npy`: Water depth at each cell
- `water_simulation_flow_accumulation_YYYYMMDD_HHMMSS.npy`: Total water flow through each cell
- `water_simulation_river_network_YYYYMMDD_HHMMSS.npy`: River network mask (0/1 values)

##### Phase 3: Erosion Simulation
- `erosion_simulation_original_terrain_YYYYMMDD_HHMMSS.npy`: Original terrain before erosion
- `erosion_simulation_eroded_terrain_YYYYMMDD_HHMMSS.npy`: Terrain after erosion cycles
- `erosion_simulation_sediment_map_YYYYMMDD_HHMMSS.npy`: Sediment distribution map
- `erosion_simulation_history_YYYYMMDD_HHMMSS.npy`: Erosion statistics over time

##### Phase 4: Disaster Simulation
- `disaster_simulation_flood_map_YYYYMMDD_HHMMSS.npy`: Flooded areas (0/1 values)
- `disaster_simulation_landslide_map_YYYYMMDD_HHMMSS.npy`: Landslide areas (0/1 values)
- `disaster_simulation_wildfire_map_YYYYMMDD_HHMMSS.npy`: Burned areas (0/1 values)
- `disaster_simulation_vegetation_map_YYYYMMDD_HHMMSS.npy`: Vegetation density map

##### Phase 5: Pathfinding
- `pathfinding_simulation_paths_YYYYMMDD_HHMMSS.json`: Path coordinates and costs
- `pathfinding_simulation_cost_map_YYYYMMDD_HHMMSS.npy`: Movement cost for each cell

##### Phase 6: Real Data
- `real_data_simulation_[dataset]_original_YYYYMMDD_HHMMSS.npy`: Original real terrain data
- `real_data_simulation_[dataset]_preprocessed_YYYYMMDD_HHMMSS.npy`: Processed terrain data

#### Visualization Files (.png - Images)

##### Phase 1: Terrain Generation
- `terrain_YYYYMMDD_HHMMSS.png`: 2D terrain heatmap with elevation colors

##### Phase 2: Water Flow Simulation
- `water_simulation_visualization_YYYYMMDD_HHMMSS.png`: 6-panel visualization showing:
  - Original terrain
  - Water surface depth
  - Flow accumulation
  - River network overlay
  - Combined terrain + water
  - Watershed statistics

##### Phase 3: Erosion Simulation
- `erosion_simulation_visualization_YYYYMMDD_HHMMSS.png`: 9-panel visualization showing:
  - Original terrain
  - Eroded terrain
  - Terrain change (erosion/deposition)
  - Slope map
  - Sediment map
  - Flow accumulation
  - Erosion history graph
  - Statistics panel
  - 3D comparison

##### Phase 4: Disaster Simulation
- `disaster_simulation_visualization_YYYYMMDD_HHMMSS.png`: 9-panel visualization showing:
  - Original terrain
  - Vegetation map
  - Flood simulation overlay
  - Landslide simulation overlay
  - Wildfire simulation overlay
  - Combined disaster map
  - Statistics panel
  - Risk assessment map
  - 3D terrain with disasters

##### Phase 5: Pathfinding
- `pathfinding_simulation_visualization_YYYYMMDD_HHMMSS.png`: 6-panel visualization showing:
  - Original terrain
  - Cost map
  - Disaster overlay
  - Pathfinding results with routes
  - Path cost comparison
  - Accessibility map

##### Phase 6: Real Data
- `real_data_simulation_visualization_YYYYMMDD_HHMMSS.png`: 9-panel visualization showing:
  - Original real terrain
  - Preprocessed terrain
  - Dataset metadata
  - Simulation results (varies by type)
  - Comparison with known data
  - 3D real data visualization
  - Summary panel

## Data Structure Details

### Terrain Data
- **Format**: 2D NumPy arrays
- **Values**: Normalized elevation (0-1) for generated terrain, real elevation (meters) for real data
- **Shape**: (height, width) where height=width=size parameter

### Water Simulation Data
- **Water Surface**: Continuous values representing water depth
- **Flow Accumulation**: Cumulative water flow through each cell
- **River Network**: Binary mask (0=land, 1=river)

### Erosion Data
- **Terrain Change**: Positive values = deposition, negative values = erosion
- **Sediment Map**: Sediment concentration at each cell
- **History**: Array of erosion amounts per cycle

### Disaster Data
- **Flood/Landslide/Fire Maps**: Binary masks (0=safe, 1=affected)
- **Vegetation Map**: Continuous values (0-1) representing vegetation density

### Pathfinding Data
- **Paths**: JSON format with coordinate lists and cost information
- **Cost Maps**: Continuous values representing movement difficulty

## Usage Examples

### 🎮 **Real-Time 3D Viewer**
```bash
# Install dependencies
pip install -r requirements_realtime.txt

# Run professional 3D viewer
python professional_terrain_viewer.py
```

### 📊 **Batch Processing**

#### Single Command - All Phases
```bash
python main.py --all-phases --size 65 --export
```

#### Specific Phases
```bash
python main.py --phases 1 2 3 --size 65 --export
```

#### Custom Parameters
```bash
python main.py --all-phases --size 100 --roughness 0.3 --seed 123 --export
```

#### Real Data Analysis
```bash
python main.py --phases 6 --real-dataset srtm_sample --real-simulation-type water --export
```

## Key Features

### 🎮 **Real-Time 3D Viewer**
- **Interactive Simulations**: Live rainfall, erosion, and disaster effects
- **Professional Visualization**: GPS-quality topographic views with contour lines
- **Free Data Integration**: OpenStreetMap and NASA Worldview imagery
- **GUI Controls**: Real-time parameter adjustment via Tkinter interface
- **Modern Graphics**: OpenGL-based 3D rendering with realistic lighting
- **Performance Optimized**: Cached rendering and efficient update cycles

### 📊 **Batch Processing**
- **Modular Design**: Each phase can run independently or in sequence
- **Reproducible**: Seed-based random generation
- **Comprehensive**: Covers terrain generation, hydrology, geomorphology, disasters, navigation, and real-world validation
- **Export Ready**: All data available in both raw numerical format and visual representations
- **Scalable**: Works with terrain sizes from 33x33 to 200x200+ cells
- **Real-World Integration**: Can import and analyze actual DEM datasets

## Dependencies

### 🎮 **Real-Time 3D Viewer** (`requirements_realtime.txt`)
- Pygame: Game development and window management
- PyOpenGL: OpenGL bindings for 3D rendering
- PyOpenGL-accelerate: OpenGL acceleration
- NumPy: Numerical computing and array operations
- SciPy: Scientific computing and image processing
- Pillow: Image processing
- ModernGL: Modern OpenGL wrapper
- Matplotlib: Additional visualization support

### 📊 **Batch Processing** (`requirements.txt`)
- NumPy: Numerical computing and array operations
- Matplotlib: 3D plotting and visualization
- SciPy: Scientific computing and image processing
