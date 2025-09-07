#!/usr/bin/env python3
"""
Camera class for Campus Lockdown game.

This module contains the Camera class that handles viewport management
and smooth camera following for the game.
"""

class Camera:
    """
    Camera class for handling viewport and scrolling in larger maps.
    """
    
    def __init__(self, width, height):
        """
        Initialize the camera with viewport dimensions.
        
        Args:
            width (int): Viewport width in pixels
            height (int): Viewport height in pixels
        """
        self.width = width
        self.height = height
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.follow_speed = 5.0  # Camera follow smoothness
    
    def follow_target(self, target_x, target_y, map_width, map_height, dt):
        """
        Smoothly follow a target position while keeping camera within map bounds.
        
        Args:
            target_x (float): Target x position in world coordinates
            target_y (float): Target y position in world coordinates
            map_width (int): Total map width in pixels
            map_height (int): Total map height in pixels
            dt (float): Delta time in seconds
        """
        # Center camera on target
        self.target_x = target_x - self.width // 2
        self.target_y = target_y - self.height // 2
        
        # Clamp camera to map bounds (handle small maps that are smaller than viewport)
        if map_width <= self.width:
            # Center small maps horizontally
            self.target_x = -(self.width - map_width) // 2
        else:
            self.target_x = max(0, min(self.target_x, map_width - self.width))
            
        if map_height <= self.height:
            # Center small maps vertically
            self.target_y = -(self.height - map_height) // 2
        else:
            self.target_y = max(0, min(self.target_y, map_height - self.height))
        
        # Smooth camera movement
        self.x += (self.target_x - self.x) * self.follow_speed * dt
        self.y += (self.target_y - self.y) * self.follow_speed * dt
    
    def world_to_screen(self, world_x, world_y):
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_x (float): World x coordinate
            world_y (float): World y coordinate
            
        Returns:
            tuple: (screen_x, screen_y) coordinates
        """
        return (world_x - self.x, world_y - self.y)
    
    def screen_to_world(self, screen_x, screen_y):
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_x (float): Screen x coordinate
            screen_y (float): Screen y coordinate
            
        Returns:
            tuple: (world_x, world_y) coordinates
        """
        return (screen_x + self.x, screen_y + self.y)