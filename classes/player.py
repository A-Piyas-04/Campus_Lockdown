#!/usr/bin/env python3
"""
Player class for Campus Lockdown game.

This module contains the Player class that handles player movement,
animation, and rendering.
"""

import pygame
from .tiles import TILE_SIZE

# Colors
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

# Player constants
PLAYER_SIZE = 50
PLAYER_SPEED = 6

class Player:
    """
    Player class representing a controllable sprite character with smooth grid-based movement.
    """
    
    def __init__(self, x, y, game_map=None):
        """
        Initialize the player with grid position and optional map reference.
        
        Args:
            x (int): Initial x position in pixels (will be converted to grid)
            y (int): Initial y position in pixels (will be converted to grid)
            game_map (Map): Reference to the game map for collision detection
        """
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.color = BLUE
        self.game_map = game_map
        
        # Convert pixel coordinates to grid coordinates
        if game_map:
            self.grid_x, self.grid_y = game_map.pixel_to_grid(x, y)
        else:
            self.grid_x = x // TILE_SIZE
            self.grid_y = y // TILE_SIZE
        
        # Grid position (logical position)
        self.target_grid_x = self.grid_x
        self.target_grid_y = self.grid_y
        
        # Pixel position for rendering (can be between grid positions during animation)
        self.x = float(self.grid_x * TILE_SIZE)
        self.y = float(self.grid_y * TILE_SIZE)
        
        # Animation properties
        self.is_moving = False
        self.move_progress = 0.0
        self.animation_speed = 8.0  # Higher = faster animation
        
        # Load player sprite (fallback to colored rectangle if sprite fails)
        self.sprite = None
        self.use_sprite = False
        try:
            # Try to load the SVG sprite (convert to surface)
            self.sprite = self._create_sprite_surface()
            self.use_sprite = True
        except Exception as e:
            print(f"Could not load sprite, using colored rectangle: {e}")
            self.use_sprite = False
    
    def _create_sprite_surface(self):
        """
        Create an advanced sprite surface with a detailed knight character design.
        
        Returns:
            pygame.Surface: The sprite surface
        """
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Advanced knight character with more detail
        center_x, center_y = self.size // 2, self.size // 2
        
        # Shadow/outline for depth
        shadow_offset = 2
        pygame.draw.ellipse(surface, (0, 0, 0, 80), 
                          (center_x - 18 + shadow_offset, center_y + 15 + shadow_offset, 36, 12))
        
        # Legs with armor plates
        # Left leg
        pygame.draw.rect(surface, (46, 92, 138), (center_x - 12, center_y + 8, 8, 16), border_radius=2)
        pygame.draw.rect(surface, (74, 144, 226), (center_x - 11, center_y + 9, 6, 4), border_radius=1)  # knee guard
        pygame.draw.rect(surface, (74, 144, 226), (center_x - 11, center_y + 18, 6, 4), border_radius=1)  # shin guard
        
        # Right leg
        pygame.draw.rect(surface, (46, 92, 138), (center_x + 4, center_y + 8, 8, 16), border_radius=2)
        pygame.draw.rect(surface, (74, 144, 226), (center_x + 5, center_y + 9, 6, 4), border_radius=1)  # knee guard
        pygame.draw.rect(surface, (74, 144, 226), (center_x + 5, center_y + 18, 6, 4), border_radius=1)  # shin guard
        
        # Boots
        pygame.draw.ellipse(surface, (25, 25, 25), (center_x - 13, center_y + 22, 10, 6))
        pygame.draw.ellipse(surface, (25, 25, 25), (center_x + 3, center_y + 22, 10, 6))
        
        # Main body armor with chest plate details
        pygame.draw.rect(surface, (74, 144, 226), (center_x - 10, center_y - 8, 20, 18), border_radius=4)
        
        # Chest plate decorations
        pygame.draw.rect(surface, (100, 170, 255), (center_x - 8, center_y - 6, 16, 3), border_radius=1)
        pygame.draw.rect(surface, (100, 170, 255), (center_x - 6, center_y - 2, 12, 2), border_radius=1)
        pygame.draw.circle(surface, (255, 215, 0), (center_x, center_y + 2), 3)  # golden emblem
        pygame.draw.circle(surface, (255, 255, 0), (center_x, center_y + 2), 2)  # bright center
        
        # Arms with shoulder guards
        # Left arm
        pygame.draw.rect(surface, (74, 144, 226), (center_x - 18, center_y - 5, 10, 16), border_radius=3)
        pygame.draw.circle(surface, (100, 170, 255), (center_x - 13, center_y - 3), 4)  # shoulder guard
        
        # Right arm (holding sword)
        pygame.draw.rect(surface, (74, 144, 226), (center_x + 8, center_y - 5, 10, 16), border_radius=3)
        pygame.draw.circle(surface, (100, 170, 255), (center_x + 13, center_y - 3), 4)  # shoulder guard
        
        # Advanced sword with detailed hilt
        sword_x = center_x + 20
        # Sword blade (gradient effect)
        for i in range(18):
            color_intensity = 192 + int(63 * (1 - i / 18))
            pygame.draw.rect(surface, (color_intensity, color_intensity, color_intensity), 
                           (sword_x, center_y - 15 + i, 3, 1))
        
        # Sword crossguard
        pygame.draw.rect(surface, (139, 69, 19), (sword_x - 2, center_y + 2, 7, 3), border_radius=1)
        pygame.draw.rect(surface, (255, 215, 0), (sword_x - 1, center_y + 2, 5, 1))  # golden inlay
        
        # Sword grip
        pygame.draw.rect(surface, (101, 67, 33), (sword_x, center_y + 4, 3, 8), border_radius=1)
        
        # Sword pommel
        pygame.draw.circle(surface, (139, 69, 19), (sword_x + 1, center_y + 13), 2)
        
        # Advanced helmet with more detail
        pygame.draw.circle(surface, (192, 192, 192), (center_x, center_y - 15), 12)  # main helmet
        pygame.draw.circle(surface, (220, 220, 220), (center_x, center_y - 15), 10)  # inner helmet
        
        # Helmet crest
        pygame.draw.rect(surface, (255, 215, 0), (center_x - 1, center_y - 25, 2, 8), border_radius=1)
        pygame.draw.circle(surface, (255, 215, 0), (center_x, center_y - 25), 2)
        
        # Enhanced visor with breathing holes
        pygame.draw.rect(surface, (51, 51, 51), (center_x - 8, center_y - 18, 16, 6), border_radius=2)
        
        # Visor breathing holes
        for i in range(3):
            pygame.draw.circle(surface, (25, 25, 25), (center_x - 4 + i * 4, center_y - 15), 1)
        
        # Glowing eyes through visor (more intense)
        pygame.draw.circle(surface, (255, 50, 50), (center_x - 4, center_y - 16), 2)
        pygame.draw.circle(surface, (255, 100, 100), (center_x - 4, center_y - 16), 1)
        pygame.draw.circle(surface, (255, 50, 50), (center_x + 4, center_y - 16), 2)
        pygame.draw.circle(surface, (255, 100, 100), (center_x + 4, center_y - 16), 1)
        
        # Cape/cloak flowing behind
        cape_points = [
            (center_x - 8, center_y - 6),
            (center_x - 15, center_y - 2),
            (center_x - 12, center_y + 12),
            (center_x - 6, center_y + 8)
        ]
        pygame.draw.polygon(surface, (139, 0, 0), cape_points)
        pygame.draw.polygon(surface, (180, 0, 0), cape_points, 2)  # cape outline
        
        return surface
    
    def move(self, dx, dy):
        """
        Attempt to move the player by the specified grid offset.
        
        Args:
            dx (int): Grid x offset (-1, 0, or 1)
            dy (int): Grid y offset (-1, 0, or 1)
            
        Returns:
            bool: True if movement was successful, False if blocked
        """
        # Don't allow movement if already moving
        if self.is_moving:
            return False
        
        # Calculate new target position
        new_grid_x = self.target_grid_x + dx
        new_grid_y = self.target_grid_y + dy
        
        # Check if the new position is walkable
        if self.game_map and not self.game_map.is_walkable(new_grid_x, new_grid_y):
            return False
        
        # Start movement animation
        self.target_grid_x = new_grid_x
        self.target_grid_y = new_grid_y
        self.is_moving = True
        self.move_progress = 0.0
        
        return True
    
    def update(self, dt):
        """
        Update player animation and position.
        
        Args:
            dt (float): Delta time in seconds
        """
        if self.is_moving:
            # Update movement animation
            self.move_progress += self.animation_speed * dt
            
            if self.move_progress >= 1.0:
                # Movement complete
                self.move_progress = 1.0
                self.is_moving = False
                self.grid_x = self.target_grid_x
                self.grid_y = self.target_grid_y
            
            # Interpolate position for smooth movement
            start_x = self.grid_x * TILE_SIZE
            start_y = self.grid_y * TILE_SIZE
            target_x = self.target_grid_x * TILE_SIZE
            target_y = self.target_grid_y * TILE_SIZE
            
            # Use easing for smoother animation
            t = self.move_progress
            eased_t = t * t * (3.0 - 2.0 * t)  # Smoothstep easing
            
            self.x = start_x + (target_x - start_x) * eased_t
            self.y = start_y + (target_y - start_y) * eased_t
    
    def set_map(self, game_map):
        """
        Set the game map reference for collision detection.
        
        Args:
            game_map (Map): The game map instance
        """
        self.game_map = game_map
    
    def get_grid_position(self):
        """
        Get the player's current logical grid position.
        
        Returns:
            tuple: (grid_x, grid_y) coordinates
        """
        return (self.target_grid_x, self.target_grid_y)
    
    def draw(self, screen, camera=None):
        """
        Draw the player sprite or fallback rectangle on the screen.
        
        Args:
            screen: Pygame screen surface to draw on
            camera: Optional camera for coordinate transformation
        """
        # Calculate screen position
        if camera:
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        else:
            screen_x, screen_y = self.x, self.y
        
        if self.use_sprite and self.sprite:
            # Draw the sprite
            screen.blit(self.sprite, (int(screen_x), int(screen_y)))
        else:
            # Fallback to colored rectangle with border for better visibility
            pygame.draw.rect(screen, self.color, (int(screen_x), int(screen_y), self.size, self.size))
            pygame.draw.rect(screen, WHITE, (int(screen_x), int(screen_y), self.size, self.size), 2)