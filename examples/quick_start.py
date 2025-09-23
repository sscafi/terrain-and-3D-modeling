#!/usr/bin/env python3
"""
Quick Start Example - Terrain 3D Modeling
Simple example showing how to use the terrain simulation system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.water_simulation import WaterSimulation
from src.erosion_simulation import ErosionSimulation
import numpy as np
import matplotlib.pyplot as plt

def main():
    """Run a simple terrain simulation example."""
    print("🏔️ Terrain 3D Modeling - Quick Start Example")
    print("=" * 50)
    
    # Generate a simple terrain
    size = 65
    terrain = np.random.random((size, size)) * 0.5
    
    print(f"📊 Generated terrain: {size}x{size}")
    
    # Run water simulation
    print("🌧️ Running water simulation...")
    water_sim = WaterSimulation(terrain)
    water_sim.simulate_rainfall_event(intensity=1.0, duration=20, coverage=0.8)
    
    # Run erosion simulation
    print("⛰️ Running erosion simulation...")
    erosion_sim = ErosionSimulation(terrain)
    for i in range(5):
        erosion_sim.run_erosion_cycle()
    
    print("✅ Simulation complete!")
    print("\nTo run the full interactive 3D viewer:")
    print("python professional_terrain_viewer.py")

if __name__ == "__main__":
    main()
