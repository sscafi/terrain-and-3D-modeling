#!/usr/bin/env python3
"""
Camera Controller for Real-Time 3D Terrain Viewer
Handles multiple camera modes and input controls.
"""

import numpy as np
import math
from OpenGL.GL import *


class CameraController:
    """Handles camera movement and control modes."""
    
    def __init__(self):
        """Initialize camera controller."""
        # Camera position and orientation
        self.position = np.array([0.0, 5.0, 10.0])
        self.target = np.array([0.0, 0.0, 0.0])
        self.up = np.array([0.0, 1.0, 0.0])
        
        # Camera modes
        self.mode = 'fps'  # 'fps', 'orbit', 'bird_eye'
        
        # FPS camera settings
        self.yaw = -90.0  # Horizontal rotation
        self.pitch = 0.0  # Vertical rotation
        self.speed = 5.0
        self.mouse_sensitivity = 0.1
        
        # Orbit camera settings
        self.orbit_distance = 15.0
        self.orbit_angle_x = 0.0
        self.orbit_angle_y = 0.0
        self.orbit_speed = 2.0
        
        # Bird's eye settings
        self.bird_height = 20.0
        self.bird_zoom = 1.0
        
        # Input state
        self.keys_pressed = set()
        self.mouse_buttons = set()
        self.mouse_delta = [0, 0]
        
        # Smooth movement
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.damping = 0.8
    
    def set_mode(self, mode):
        """Set camera mode."""
        if mode in ['fps', 'orbit', 'bird_eye']:
            self.mode = mode
            print(f"Camera mode: {mode}")
    
    def handle_key_press(self, key):
        """Handle key press."""
        self.keys_pressed.add(key)
    
    def handle_key_release(self, key):
        """Handle key release."""
        self.keys_pressed.discard(key)
    
    def handle_mouse_motion(self, rel):
        """Handle mouse movement."""
        self.mouse_delta[0] += rel[0]
        self.mouse_delta[1] += rel[1]
    
    def handle_mouse_button(self, button, pressed):
        """Handle mouse button events."""
        if pressed:
            self.mouse_buttons.add(button)
        else:
            self.mouse_buttons.discard(button)
    
    def update(self):
        """Update camera based on current mode and input."""
        if self.mode == 'fps':
            self._update_fps_camera()
        elif self.mode == 'orbit':
            self._update_orbit_camera()
        elif self.mode == 'bird_eye':
            self._update_bird_eye_camera()
        
        # Apply damping to velocity
        self.velocity *= self.damping
    
    def _update_fps_camera(self):
        """Update FPS camera mode."""
        # Handle mouse look
        if self.mouse_delta[0] != 0 or self.mouse_delta[1] != 0:
            self.yaw += self.mouse_delta[0] * self.mouse_sensitivity
            self.pitch -= self.mouse_delta[1] * self.mouse_sensitivity
            
            # Clamp pitch
            self.pitch = max(-89.0, min(89.0, self.pitch))
            
            self.mouse_delta = [0, 0]
        
        # Calculate forward direction
        forward = np.array([
            math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
            math.sin(math.radians(self.pitch)),
            math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        ])
        forward = forward / np.linalg.norm(forward)
        
        # Calculate right direction
        right = np.cross(forward, self.up)
        right = right / np.linalg.norm(right)
        
        # Handle movement
        move_vector = np.array([0.0, 0.0, 0.0])
        
        # Map keys to movement (you'll need to implement key mapping)
        # This is a placeholder - you'll need to integrate with pygame key events
        
        # Apply movement
        self.position += move_vector * self.speed * 0.016  # Assuming 60 FPS
        
        # Update target
        self.target = self.position + forward
    
    def _update_orbit_camera(self):
        """Update orbit camera mode."""
        # Handle mouse rotation
        if self.mouse_delta[0] != 0 or self.mouse_delta[1] != 0:
            self.orbit_angle_y += self.mouse_delta[0] * self.orbit_speed * 0.01
            self.orbit_angle_x += self.mouse_delta[1] * self.orbit_speed * 0.01
            
            # Clamp vertical rotation
            self.orbit_angle_x = max(-89.0, min(89.0, self.orbit_angle_x))
            
            self.mouse_delta = [0, 0]
        
        # Calculate orbit position
        x = self.orbit_distance * math.cos(math.radians(self.orbit_angle_x)) * math.cos(math.radians(self.orbit_angle_y))
        y = self.orbit_distance * math.sin(math.radians(self.orbit_angle_x))
        z = self.orbit_distance * math.cos(math.radians(self.orbit_angle_x)) * math.sin(math.radians(self.orbit_angle_y))
        
        self.position = np.array([x, y, z])
        self.target = np.array([0.0, 0.0, 0.0])
    
    def _update_bird_eye_camera(self):
        """Update bird's eye camera mode."""
        # Handle mouse panning
        if self.mouse_delta[0] != 0 or self.mouse_delta[1] != 0:
            # Pan the camera
            pan_speed = 0.1
            self.position[0] -= self.mouse_delta[0] * pan_speed
            self.position[2] += self.mouse_delta[1] * pan_speed
            
            self.mouse_delta = [0, 0]
        
        # Set bird's eye position
        self.position[1] = self.bird_height
        self.target = np.array([self.position[0], 0.0, self.position[2]])
        self.up = np.array([0.0, 0.0, -1.0])  # Rotated up vector for bird's eye
    
    def apply_transform(self):
        """Apply camera transform to OpenGL."""
        gluLookAt(
            self.position[0], self.position[1], self.position[2],  # Eye position
            self.target[0], self.target[1], self.target[2],        # Target position
            self.up[0], self.up[1], self.up[2]                     # Up vector
        )
    
    def get_position(self):
        """Get current camera position."""
        return self.position.copy()
    
    def get_target(self):
        """Get current camera target."""
        return self.target.copy()
    
    def set_position(self, position):
        """Set camera position."""
        self.position = np.array(position)
    
    def set_target(self, target):
        """Set camera target."""
        self.target = np.array(target)
    
    def zoom_in(self, factor=1.1):
        """Zoom in (for orbit and bird's eye modes)."""
        if self.mode == 'orbit':
            self.orbit_distance = max(1.0, self.orbit_distance / factor)
        elif self.mode == 'bird_eye':
            self.bird_height = max(5.0, self.bird_height / factor)
    
    def zoom_out(self, factor=1.1):
        """Zoom out (for orbit and bird's eye modes)."""
        if self.mode == 'orbit':
            self.orbit_distance = min(100.0, self.orbit_distance * factor)
        elif self.mode == 'bird_eye':
            self.bird_height = min(100.0, self.bird_height * factor)
    
    def reset_view(self):
        """Reset camera to default position."""
        if self.mode == 'fps':
            self.position = np.array([0.0, 5.0, 10.0])
            self.yaw = -90.0
            self.pitch = 0.0
        elif self.mode == 'orbit':
            self.orbit_distance = 15.0
            self.orbit_angle_x = 0.0
            self.orbit_angle_y = 0.0
        elif self.mode == 'bird_eye':
            self.position = np.array([0.0, 20.0, 0.0])
            self.bird_height = 20.0
