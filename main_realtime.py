#!/usr/bin/env python3
"""
Main Entry Point for Real-Time 3D Terrain Simulation
"""

from realtime_3d_viewer import RealTime3DTerrainApp


def main():
    """Entry point for the real-time 3D terrain application."""
    print("="*60)
    print("REAL-TIME 3D TERRAIN SIMULATION")
    print("="*60)
    print("Starting real-time 3D terrain simulation...")
    print("This will open two windows:")
    print("1. 3D Terrain Viewer (Pygame + OpenGL)")
    print("2. Control Panel (Tkinter GUI)")
    print()
    print("Controls:")
    print("  WASD - Move camera (FPS mode)")
    print("  Mouse - Look around")
    print("  SPACE - Pause/Resume simulation")
    print("  R - Reset simulation")
    print("  1/2/3 - Camera modes (FPS/Orbit/Bird's Eye)")
    print("  +/- - Speed up/slow down simulation")
    print("  ESC - Exit")
    print("="*60)
    
    try:
        app = RealTime3DTerrainApp(width=1200, height=800)
        app.run()
    except Exception as e:
        print(f"Error starting real-time application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
