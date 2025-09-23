#!/usr/bin/env python3
"""
GUI Controls for Real-Time 3D Terrain Viewer
Provides tkinter control panels for real-time parameter adjustment.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time


class GUIControls:
    """GUI controls for real-time parameter adjustment."""
    
    def __init__(self, app):
        """
        Initialize GUI controls.
        
        Args:
            app: Reference to the main application
        """
        self.app = app
        self.root = None
        self.control_frame = None
        
        # Parameter variables (will be created after root window)
        self.rainfall_var = None
        self.evaporation_var = None
        self.erosion_var = None
        self.wind_var = None
        self.fire_var = None
        self.phase_var = None
        self.speed_var = None
        
        # Statistics variables
        self.stats_vars = {}
        
        # Create GUI in separate thread
        self.gui_thread = threading.Thread(target=self._create_gui)
        self.gui_thread.daemon = True
        self.gui_thread.start()
        
        print("GUI Controls initialized")
    
    def _create_gui(self):
        """Create the GUI controls."""
        self.root = tk.Tk()
        self.root.title("Terrain Simulation Controls")
        self.root.geometry("400x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Initialize parameter variables after root window is created
        self.rainfall_var = tk.DoubleVar(value=1.0)
        self.evaporation_var = tk.DoubleVar(value=0.1)
        self.erosion_var = tk.DoubleVar(value=0.01)
        self.wind_var = tk.DoubleVar(value=0.0)
        self.fire_var = tk.DoubleVar(value=0.3)
        self.phase_var = tk.IntVar(value=1)
        self.speed_var = tk.DoubleVar(value=1.0)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Simulation Control Section
        self._create_simulation_controls(main_frame, 0)
        
        # Parameter Control Section
        self._create_parameter_controls(main_frame, 1)
        
        # Statistics Section
        self._create_statistics_display(main_frame, 2)
        
        # Start GUI update loop
        self._update_gui()
        
        # Start GUI main loop
        self.root.mainloop()
    
    def _create_simulation_controls(self, parent, row):
        """Create simulation control section."""
        # Simulation Control Frame
        sim_frame = ttk.LabelFrame(parent, text="Simulation Control", padding="5")
        sim_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        sim_frame.columnconfigure(1, weight=1)
        
        # Phase Selection
        ttk.Label(sim_frame, text="Phase:").grid(row=0, column=0, sticky=tk.W, pady=2)
        phase_combo = ttk.Combobox(sim_frame, textvariable=self.phase_var, 
                                 values=[1, 2, 3, 4, 5, 6], state="readonly")
        phase_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        phase_combo.bind('<<ComboboxSelected>>', self._on_phase_change)
        
        # Speed Control
        ttk.Label(sim_frame, text="Speed:").grid(row=1, column=0, sticky=tk.W, pady=2)
        speed_scale = ttk.Scale(sim_frame, from_=0.1, to=10.0, variable=self.speed_var,
                              orient=tk.HORIZONTAL, command=self._on_speed_change)
        speed_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Speed Label
        self.speed_label = ttk.Label(sim_frame, text="1.0x")
        self.speed_label.grid(row=1, column=2, padx=5)
        
        # Control Buttons
        button_frame = ttk.Frame(sim_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        ttk.Button(button_frame, text="Pause/Resume", 
                  command=self._toggle_pause).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Reset", 
                  command=self._reset_simulation).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Reset View", 
                  command=self._reset_view).pack(side=tk.LEFT, padx=2)
    
    def _create_parameter_controls(self, parent, row):
        """Create parameter control section."""
        # Parameter Control Frame
        param_frame = ttk.LabelFrame(parent, text="Simulation Parameters", padding="5")
        param_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        param_frame.columnconfigure(1, weight=1)
        
        # Rainfall Intensity
        ttk.Label(param_frame, text="Rainfall:").grid(row=0, column=0, sticky=tk.W, pady=2)
        rainfall_scale = ttk.Scale(param_frame, from_=0.0, to=5.0, variable=self.rainfall_var,
                                 orient=tk.HORIZONTAL, command=self._on_rainfall_change)
        rainfall_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        self.rainfall_label = ttk.Label(param_frame, text="1.0")
        self.rainfall_label.grid(row=0, column=2, padx=5)
        
        # Evaporation Rate
        ttk.Label(param_frame, text="Evaporation:").grid(row=1, column=0, sticky=tk.W, pady=2)
        evap_scale = ttk.Scale(param_frame, from_=0.0, to=0.5, variable=self.evaporation_var,
                             orient=tk.HORIZONTAL, command=self._on_evaporation_change)
        evap_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        self.evap_label = ttk.Label(param_frame, text="0.1")
        self.evap_label.grid(row=1, column=2, padx=5)
        
        # Erosion Rate
        ttk.Label(param_frame, text="Erosion:").grid(row=2, column=0, sticky=tk.W, pady=2)
        erosion_scale = ttk.Scale(param_frame, from_=0.0, to=0.1, variable=self.erosion_var,
                                orient=tk.HORIZONTAL, command=self._on_erosion_change)
        erosion_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        self.erosion_label = ttk.Label(param_frame, text="0.01")
        self.erosion_label.grid(row=2, column=2, padx=5)
        
        # Wind Direction
        ttk.Label(param_frame, text="Wind Dir:").grid(row=3, column=0, sticky=tk.W, pady=2)
        wind_scale = ttk.Scale(param_frame, from_=0, to=360, variable=self.wind_var,
                             orient=tk.HORIZONTAL, command=self._on_wind_change)
        wind_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        self.wind_label = ttk.Label(param_frame, text="0°")
        self.wind_label.grid(row=3, column=2, padx=5)
        
        # Fire Spread Rate
        ttk.Label(param_frame, text="Fire Spread:").grid(row=4, column=0, sticky=tk.W, pady=2)
        fire_scale = ttk.Scale(param_frame, from_=0.0, to=1.0, variable=self.fire_var,
                             orient=tk.HORIZONTAL, command=self._on_fire_change)
        fire_scale.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)
        self.fire_label = ttk.Label(param_frame, text="0.3")
        self.fire_label.grid(row=4, column=2, padx=5)
    
    def _create_statistics_display(self, parent, row):
        """Create statistics display section."""
        # Statistics Frame
        stats_frame = ttk.LabelFrame(parent, text="Simulation Statistics", padding="5")
        stats_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        stats_frame.columnconfigure(1, weight=1)
        
        # Statistics labels
        self.stats_vars = {
            'step_count': tk.StringVar(value="0"),
            'terrain_min': tk.StringVar(value="0.000"),
            'terrain_max': tk.StringVar(value="0.000"),
            'terrain_mean': tk.StringVar(value="0.000"),
            'water_total': tk.StringVar(value="0.000"),
            'max_flow': tk.StringVar(value="0.000"),
            'total_erosion': tk.StringVar(value="0.000"),
            'event_count': tk.StringVar(value="0")
        }
        
        row_idx = 0
        for key, var in self.stats_vars.items():
            label_text = key.replace('_', ' ').title()
            ttk.Label(stats_frame, text=f"{label_text}:").grid(row=row_idx, column=0, sticky=tk.W, pady=1)
            ttk.Label(stats_frame, textvariable=var).grid(row=row_idx, column=1, sticky=tk.W, padx=10)
            row_idx += 1
        
        # Recent Events
        ttk.Label(stats_frame, text="Recent Events:").grid(row=row_idx, column=0, sticky=tk.W, pady=2)
        self.events_text = tk.Text(stats_frame, height=4, width=40)
        self.events_text.grid(row=row_idx+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
    
    def _update_gui(self):
        """Update GUI with current simulation statistics."""
        if self.root and self.app.simulation:
            try:
                stats = self.app.simulation.get_statistics()
                
                # Update statistics
                self.stats_vars['step_count'].set(str(stats['step_count']))
                self.stats_vars['terrain_min'].set(f"{stats['terrain_min']:.3f}")
                self.stats_vars['terrain_max'].set(f"{stats['terrain_max']:.3f}")
                self.stats_vars['terrain_mean'].set(f"{stats['terrain_mean']:.3f}")
                self.stats_vars['event_count'].set(str(stats['event_count']))
                
                if 'water_total' in stats:
                    self.stats_vars['water_total'].set(f"{stats['water_total']:.3f}")
                if 'max_flow' in stats:
                    self.stats_vars['max_flow'].set(f"{stats['max_flow']:.3f}")
                if 'total_erosion' in stats:
                    self.stats_vars['total_erosion'].set(f"{stats['total_erosion']:.3f}")
                
                # Update events
                self.events_text.delete(1.0, tk.END)
                for event in stats['recent_events']:
                    self.events_text.insert(tk.END, f"Step {event['step']}: {event['message']}\n")
                
            except Exception as e:
                print(f"Error updating GUI: {e}")
        
        # Schedule next update
        if self.root:
            self.root.after(100, self._update_gui)  # Update every 100ms
    
    def _on_phase_change(self, event=None):
        """Handle phase change."""
        phase = self.phase_var.get()
        if self.app.simulation:
            self.app.simulation.set_phase(phase)
    
    def _on_speed_change(self, value):
        """Handle speed change."""
        speed = float(value)
        self.app.simulation_speed = speed
        self.speed_label.config(text=f"{speed:.1f}x")
    
    def _on_rainfall_change(self, value):
        """Handle rainfall intensity change."""
        rainfall = float(value)
        if self.app.simulation:
            self.app.simulation.set_parameter('rainfall_intensity', rainfall)
        self.rainfall_label.config(text=f"{rainfall:.1f}")
    
    def _on_evaporation_change(self, value):
        """Handle evaporation rate change."""
        evap = float(value)
        if self.app.simulation:
            self.app.simulation.set_parameter('evaporation_rate', evap)
        self.evap_label.config(text=f"{evap:.2f}")
    
    def _on_erosion_change(self, value):
        """Handle erosion rate change."""
        erosion = float(value)
        if self.app.simulation:
            self.app.simulation.set_parameter('erosion_rate', erosion)
        self.erosion_label.config(text=f"{erosion:.3f}")
    
    def _on_wind_change(self, value):
        """Handle wind direction change."""
        wind = float(value)
        if self.app.simulation:
            self.app.simulation.set_parameter('wind_direction', wind)
        self.wind_label.config(text=f"{wind:.0f}°")
    
    def _on_fire_change(self, value):
        """Handle fire spread rate change."""
        fire = float(value)
        if self.app.simulation:
            self.app.simulation.set_parameter('fire_spread_rate', fire)
        self.fire_label.config(text=f"{fire:.1f}")
    
    def _toggle_pause(self):
        """Toggle simulation pause."""
        self.app.paused = not self.app.paused
    
    def _reset_simulation(self):
        """Reset simulation."""
        if self.app.simulation:
            self.app.simulation.reset()
    
    def _reset_view(self):
        """Reset camera view."""
        if self.app.camera:
            self.app.camera.reset_view()
    
    def _on_closing(self):
        """Handle GUI window closing."""
        self.root.destroy()
    
    def update(self):
        """Update GUI state."""
        pass  # GUI updates are handled in the GUI thread
    
    def render_overlay(self):
        """Render GUI overlay on 3D scene."""
        # This would render GUI elements directly on the 3D scene
        # For now, we use separate tkinter window
        pass
