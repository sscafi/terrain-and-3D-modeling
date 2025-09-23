#!/usr/bin/env python3
"""
Real-Time Simulation Engine
Refactored simulation engine for step-by-step execution in real-time.
"""

import numpy as np
import random
import time
from water_simulation import WaterSimulation
from erosion_simulation import ErosionSimulation
from disaster_simulation import DisasterSimulation


class RealtimeSimulation:
    """Real-time simulation engine that runs step-by-step."""
    
    def __init__(self, size=65, roughness=0.5, seed=None):
        """
        Initialize real-time simulation.
        
        Args:
            size (int): Terrain size
            roughness (float): Terrain roughness
            seed (int): Random seed
        """
        self.size = size
        self.roughness = roughness
        self.seed = seed
        
        # Initialize random seed
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Generate initial terrain
        self.terrain = self._generate_terrain()
        
        # Simulation state
        self.current_phase = 1
        self.step_count = 0
        self.last_update_time = time.time()
        
        # Initialize simulation modules
        self.water_sim = None
        self.erosion_sim = None
        self.disaster_sim = None
        
        # Simulation parameters (can be adjusted in real-time)
        self.rainfall_intensity = 1.0
        self.evaporation_rate = 0.1
        self.erosion_rate = 0.01
        self.wind_direction = 0.0
        self.fire_spread_rate = 0.3
        
        # Event tracking
        self.events = []
        self.last_event_time = 0
        
        print(f"Real-time simulation initialized: {size}x{size} terrain")
    
    def _generate_terrain(self):
        """Generate initial terrain using Diamond-Square algorithm."""
        # Initialize terrain with random values
        terrain = np.random.random((self.size, self.size))
        
        # Apply Diamond-Square algorithm
        step_size = self.size - 1
        roughness = self.roughness
        
        while step_size > 1:
            half_step = step_size // 2
            
            # Diamond step
            for x in range(half_step, self.size, step_size):
                for y in range(half_step, self.size, step_size):
                    avg = (terrain[x-half_step][y-half_step] +
                           terrain[x+half_step][y-half_step] +
                           terrain[x-half_step][y+half_step] +
                           terrain[x+half_step][y+half_step]) / 4
                    terrain[x][y] = avg + random.uniform(-1, 1) * roughness
            
            # Square step
            for x in range(0, self.size, half_step):
                for y in range((x + half_step) % step_size, self.size, step_size):
                    avg = 0
                    count = 0
                    if x >= half_step:
                        avg += terrain[x-half_step][y]
                        count += 1
                    if x + half_step < self.size:
                        avg += terrain[x+half_step][y]
                        count += 1
                    if y >= half_step:
                        avg += terrain[x][y-half_step]
                        count += 1
                    if y + half_step < self.size:
                        avg += terrain[x][y+half_step]
                        count += 1
                    terrain[x][y] = avg / count + random.uniform(-1, 1) * roughness
            
            step_size //= 2
            roughness /= 2
        
        return terrain
    
    def step(self):
        """Execute one simulation step."""
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update based on current phase
        if self.current_phase >= 2:
            self._step_water_simulation(dt)
        
        if self.current_phase >= 3:
            self._step_erosion_simulation(dt)
        
        if self.current_phase >= 4:
            self._step_disaster_simulation(dt)
        
        self.step_count += 1
        
        # Check for events
        self._check_events()
    
    def _step_water_simulation(self, dt):
        """Step water flow simulation."""
        if self.water_sim is None:
            self.water_sim = WaterSimulation(
                terrain=self.terrain,
                rainfall_intensity=self.rainfall_intensity,
                evaporation_rate=self.evaporation_rate
            )
        
        # Add rainfall
        if self.step_count % 10 == 0:  # Add rain every 10 steps
            self.water_sim.add_rainfall(self.rainfall_intensity, 0.8)
        
        # Simulate flow
        self.water_sim.simulate_flow_step()
        
        # Update terrain with water effects
        self.terrain = self.water_sim.terrain + self.water_sim.water_surface * 0.1
    
    def _step_erosion_simulation(self, dt):
        """Step erosion simulation."""
        if self.erosion_sim is None:
            self.erosion_sim = ErosionSimulation(
                terrain=self.terrain,
                flow_accumulation=self.water_sim.flow_accumulation if self.water_sim else None,
                water_surface=self.water_sim.water_surface if self.water_sim else None
            )
        
        # Run erosion step
        if self.step_count % 5 == 0:  # Erosion every 5 steps
            self.erosion_sim.thermal_erosion()
            self.erosion_sim.hydraulic_erosion()
            
            # Update terrain
            self.terrain = self.erosion_sim.terrain
    
    def _step_disaster_simulation(self, dt):
        """Step disaster simulation."""
        if self.disaster_sim is None:
            self.disaster_sim = DisasterSimulation(
                terrain=self.terrain,
                flow_accumulation=self.water_sim.flow_accumulation if self.water_sim else None,
                water_surface=self.water_sim.water_surface if self.water_sim else None
            )
        
        # Simulate disasters occasionally
        if self.step_count % 100 == 0:  # Disasters every 100 steps
            if random.random() < 0.1:  # 10% chance
                self.disaster_sim.simulate_wildfire(
                    wind_direction=self.wind_direction,
                    spread_rate=self.fire_spread_rate
                )
                self._add_event("Wildfire started", "fire")
    
    def _check_events(self):
        """Check for significant events."""
        current_time = time.time()
        
        # Check for major water flow
        if self.water_sim and np.max(self.water_sim.flow_accumulation) > 5.0:
            if current_time - self.last_event_time > 5.0:  # Throttle events
                self._add_event("Major water flow detected", "water")
                self.last_event_time = current_time
        
        # Check for significant erosion
        if self.erosion_sim and len(self.erosion_sim.erosion_history) > 0:
            recent_erosion = self.erosion_sim.erosion_history[-1]['total_erosion']
            if recent_erosion > 1.0:
                if current_time - self.last_event_time > 10.0:
                    self._add_event("Significant erosion detected", "erosion")
                    self.last_event_time = current_time
    
    def _add_event(self, message, event_type):
        """Add an event to the event log."""
        event = {
            'time': time.time(),
            'step': self.step_count,
            'message': message,
            'type': event_type
        }
        self.events.append(event)
        
        # Keep only last 50 events
        if len(self.events) > 50:
            self.events = self.events[-50:]
        
        print(f"Event: {message}")
    
    def set_phase(self, phase):
        """Set the current simulation phase."""
        if 1 <= phase <= 6:
            self.current_phase = phase
            print(f"Simulation phase set to: {phase}")
    
    def set_parameter(self, param_name, value):
        """Set a simulation parameter in real-time."""
        if param_name == 'rainfall_intensity':
            self.rainfall_intensity = value
        elif param_name == 'evaporation_rate':
            self.evaporation_rate = value
        elif param_name == 'erosion_rate':
            self.erosion_rate = value
        elif param_name == 'wind_direction':
            self.wind_direction = value
        elif param_name == 'fire_spread_rate':
            self.fire_spread_rate = value
        else:
            print(f"Unknown parameter: {param_name}")
            return
        
        print(f"Parameter {param_name} set to: {value}")
    
    def reset(self):
        """Reset simulation to initial state."""
        self.terrain = self._generate_terrain()
        self.step_count = 0
        self.events = []
        
        # Reset simulation modules
        self.water_sim = None
        self.erosion_sim = None
        self.disaster_sim = None
        
        print("Simulation reset")
    
    def get_terrain(self):
        """Get current terrain data."""
        return self.terrain
    
    def get_water_surface(self):
        """Get current water surface data."""
        if self.water_sim:
            return self.water_sim.water_surface
        return np.zeros_like(self.terrain)
    
    def get_flow_accumulation(self):
        """Get current flow accumulation data."""
        if self.water_sim:
            return self.water_sim.flow_accumulation
        return np.zeros_like(self.terrain)
    
    def get_erosion_data(self):
        """Get current erosion data."""
        if self.erosion_sim:
            return {
                'eroded_terrain': self.erosion_sim.terrain,
                'sediment_map': self.erosion_sim.sediment_map,
                'erosion_history': self.erosion_sim.erosion_history
            }
        return None
    
    def get_disaster_data(self):
        """Get current disaster data."""
        if self.disaster_sim:
            return {
                'flood_map': self.disaster_sim.flood_map,
                'landslide_map': self.disaster_sim.landslide_map,
                'wildfire_map': self.disaster_sim.wildfire_map,
                'vegetation_map': self.disaster_sim.vegetation_map
            }
        return None
    
    def get_statistics(self):
        """Get current simulation statistics."""
        stats = {
            'step_count': self.step_count,
            'current_phase': self.current_phase,
            'terrain_min': np.min(self.terrain),
            'terrain_max': np.max(self.terrain),
            'terrain_mean': np.mean(self.terrain),
            'event_count': len(self.events),
            'recent_events': self.events[-5:] if self.events else []
        }
        
        if self.water_sim:
            stats['water_total'] = np.sum(self.water_sim.water_surface)
            stats['max_flow'] = np.max(self.water_sim.flow_accumulation)
        
        if self.erosion_sim and self.erosion_sim.erosion_history:
            stats['total_erosion'] = sum(h['total_erosion'] for h in self.erosion_sim.erosion_history)
        
        return stats
