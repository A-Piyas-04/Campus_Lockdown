#!/usr/bin/env python3
"""
Adventure Quest - A simple Pygame-based game

This is the main game file that sets up the game window, handles events,
and manages the game loop with a movable player square.
"""

import pygame
import sys
import json
import os

# Initialize Pygame
pygame.init()

# Game constants
WIDTH = 1000
HEIGHT = 800
FPS = 60

# Colors (RGB values)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Player constants
PLAYER_SIZE = 50
PLAYER_SPEED = 6

# Tile constants
TILE_SIZE = 50

# Tile types
class TileType:
    EMPTY = 0
    GRASS = 1
    WATER = 2
    WALL = 3
    TREE = 4
    
    # Character to tile type mapping for JSON maps
    CHAR_TO_TYPE = {
        'E': EMPTY,
        'G': GRASS,
        'W': WATER,
        'B': WALL,
        'T': TREE
    }
    
    @classmethod
    def from_char(cls, char):
        """Convert a character to a tile type."""
        return cls.CHAR_TO_TYPE.get(char.upper(), cls.EMPTY)

# Tile colors - Enhanced for better visual variety
TILE_COLORS = {
    TileType.EMPTY: (45, 45, 50),      # Dark blue-gray for indoor floors
    TileType.GRASS: (76, 175, 80),     # Vibrant grass green
    TileType.WATER: (33, 150, 243),    # Clear blue water
    TileType.WALL: (121, 85, 72),      # Warm brown building walls
    TileType.TREE: (56, 142, 60),      # Rich forest green
}

# Secondary colors for visual variety
TILE_ACCENT_COLORS = {
    TileType.EMPTY: (55, 55, 60),      # Lighter floor accent
    TileType.GRASS: (139, 195, 74),    # Light grass accent
    TileType.WATER: (100, 181, 246),   # Light water ripples
    TileType.WALL: (141, 110, 99),     # Light brick accent
    TileType.TREE: (102, 187, 106),    # Light leaf accent
}

# Walkable tiles (tiles the player can move on)
WALKABLE_TILES = {TileType.EMPTY, TileType.GRASS}

class Tile:
    """
    Tile class representing individual map tiles.
    """
    
    def __init__(self, tile_type, x, y):
        """
        Initialize a tile with its type and position.
        
        Args:
            tile_type (int): The type of tile (from TileType class)
            x (int): Grid x position
            y (int): Grid y position
        """
        self.tile_type = tile_type
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE
        self.pixel_y = y * TILE_SIZE
        self.walkable = tile_type in WALKABLE_TILES
        self.color = TILE_COLORS.get(tile_type, (255, 0, 255))  # Magenta for unknown types
    
    def draw(self, screen):
        """
        Draw the tile on the screen.
        
        Args:
            screen: Pygame screen surface to draw on
        """
        # Draw base tile
        pygame.draw.rect(screen, self.color, 
                        (self.pixel_x, self.pixel_y, TILE_SIZE, TILE_SIZE))
        
        # Add visual details based on tile type
        if self.tile_type == TileType.WATER:
            # Add water ripple effect
            pygame.draw.circle(screen, (100, 180, 255), 
                             (self.pixel_x + TILE_SIZE//2, self.pixel_y + TILE_SIZE//2), 
                             TILE_SIZE//4, 2)
        elif self.tile_type == TileType.TREE:
            # Add tree trunk and leaves
            trunk_rect = pygame.Rect(self.pixel_x + TILE_SIZE//2 - 3, 
                                   self.pixel_y + TILE_SIZE//2, 6, TILE_SIZE//2)
            pygame.draw.rect(screen, (101, 67, 33), trunk_rect)  # Brown trunk
            pygame.draw.circle(screen, (0, 150, 0), 
                             (self.pixel_x + TILE_SIZE//2, self.pixel_y + TILE_SIZE//3), 
                             TILE_SIZE//3)  # Green leaves
        elif self.tile_type == TileType.WALL:
            # Add brick pattern
            for i in range(0, TILE_SIZE, 10):
                for j in range(0, TILE_SIZE, 10):
                    if (i + j) % 20 == 0:
                        pygame.draw.rect(screen, (160, 82, 45), 
                                       (self.pixel_x + i, self.pixel_y + j, 8, 8))
        
        # Draw tile border for grid visibility
        pygame.draw.rect(screen, (0, 0, 0), 
                        (self.pixel_x, self.pixel_y, TILE_SIZE, TILE_SIZE), 1)

class Map:
    """
    Map class that manages the tile-based game world.
    """
    
    def __init__(self, map_data, name="Unnamed Map", spawn_point=None):
        """
        Initialize the map from a 2D array.
        
        Args:
            map_data (list): 2D list representing the map layout
            name (str): Name of the map
            spawn_point (dict): Dictionary with 'x' and 'y' keys for spawn location
        """
        self.map_data = map_data
        self.height = len(map_data) if map_data else 0
        self.width = len(map_data[0]) if map_data and len(map_data) > 0 else 0
        self.name = name
        self.spawn_point = spawn_point or {'x': 0, 'y': 0}
        self.tiles = []
        
        # Create tile objects from map data
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Ensure we don't go out of bounds
                if y < len(map_data) and x < len(map_data[y]):
                    tile_type = map_data[y][x]
                else:
                    tile_type = TileType.EMPTY  # Default fallback
                tile = Tile(tile_type, x, y)
                row.append(tile)
            self.tiles.append(row)
    
    @classmethod
    def from_json(cls, json_file_path):
        """
        Load a map from a JSON file.
        
        Args:
            json_file_path (str): Path to the JSON map file
            
        Returns:
            Map: A new Map instance loaded from the JSON file
            
        Raises:
            FileNotFoundError: If the JSON file doesn't exist
            ValueError: If the JSON file is malformed
        """
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"Map file not found: {json_file_path}")
        
        try:
            with open(json_file_path, 'r') as f:
                map_json = json.load(f)
            
            # Extract map data
            name = map_json.get('name', 'Unnamed Map')
            spawn_point = map_json.get('spawn_point', {'x': 0, 'y': 0})
            map_strings = map_json.get('map_data', [])
            
            # Debug: Check if map_strings is valid
            if not map_strings:
                raise ValueError("No map_data found in JSON file")
            
            # Convert character-based map to tile type array
            map_data = []
            for i, row_string in enumerate(map_strings):
                if not isinstance(row_string, str):
                    raise ValueError(f"Row {i} is not a string: {type(row_string)}")
                row = []
                for char in row_string:
                    tile_type = TileType.from_char(char)
                    row.append(tile_type)
                map_data.append(row)
            
            # Debug: Verify map_data before creating Map
            if not map_data:
                raise ValueError("No valid map data created")
            
            return cls(map_data, name, spawn_point)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in map file {json_file_path}: {e}")
        except Exception as e:
            raise ValueError(f"Error loading map from {json_file_path}: {e}")
    
    def get_tile(self, grid_x, grid_y):
        """
        Get the tile at the specified grid coordinates.
        
        Args:
            grid_x (int): Grid x coordinate
            grid_y (int): Grid y coordinate
            
        Returns:
            Tile: The tile at the specified position, or None if out of bounds
        """
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.tiles[grid_y][grid_x]
        return None
    
    def is_walkable(self, grid_x, grid_y):
        """
        Check if the tile at the specified coordinates is walkable.
        
        Args:
            grid_x (int): Grid x coordinate
            grid_y (int): Grid y coordinate
            
        Returns:
            bool: True if the tile is walkable, False otherwise
        """
        tile = self.get_tile(grid_x, grid_y)
        return tile is not None and tile.walkable
    
    def pixel_to_grid(self, pixel_x, pixel_y):
        """
        Convert pixel coordinates to grid coordinates.
        
        Args:
            pixel_x (float): Pixel x coordinate
            pixel_y (float): Pixel y coordinate
            
        Returns:
            tuple: (grid_x, grid_y) coordinates
        """
        return int(pixel_x // TILE_SIZE), int(pixel_y // TILE_SIZE)
    
    def grid_to_pixel(self, grid_x, grid_y):
        """
        Convert grid coordinates to pixel coordinates.
        
        Args:
            grid_x (int): Grid x coordinate
            grid_y (int): Grid y coordinate
            
        Returns:
            tuple: (pixel_x, pixel_y) coordinates
        """
        return grid_x * TILE_SIZE, grid_y * TILE_SIZE
    
    def draw(self, screen):
        """
        Draw all tiles in the map.
        
        Args:
            screen: Pygame screen surface to draw on
        """
        for row in self.tiles:
            for tile in row:
                tile.draw(screen)
    
    def draw_with_camera(self, screen, camera):
        """
        Draw only the visible tiles based on camera position for performance.
        
        Args:
            screen: Pygame screen surface to draw on
            camera: Camera instance for viewport management
        """
        # Calculate which tiles are visible
        start_x = max(0, int(camera.x // TILE_SIZE))
        end_x = min(self.width, int((camera.x + camera.width) // TILE_SIZE) + 1)
        start_y = max(0, int(camera.y // TILE_SIZE))
        end_y = min(self.height, int((camera.y + camera.height) // TILE_SIZE) + 1)
        
        # Draw only visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                # Adjust tile position based on camera offset
                screen_x = tile.pixel_x - camera.x
                screen_y = tile.pixel_y - camera.y
                
                # Draw base tile with enhanced colors
                pygame.draw.rect(screen, tile.color, 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                
                # Add enhanced visual details based on tile type
                if tile.tile_type == TileType.WATER:
                    # Animated water effect with multiple ripples
                    import time
                    wave_offset = int(time.time() * 3) % 20
                    pygame.draw.circle(screen, TILE_ACCENT_COLORS[TileType.WATER], 
                                     (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2), 
                                     TILE_SIZE//4 + wave_offset//4, 2)
                    pygame.draw.circle(screen, TILE_ACCENT_COLORS[TileType.WATER], 
                                     (screen_x + TILE_SIZE//3, screen_y + TILE_SIZE//3), 
                                     TILE_SIZE//6, 1)
                    
                elif tile.tile_type == TileType.TREE:
                    # Enhanced tree with trunk and detailed canopy
                    trunk_rect = pygame.Rect(screen_x + TILE_SIZE//2 - 4, 
                                           screen_y + TILE_SIZE*2//3, 8, TILE_SIZE//3)
                    pygame.draw.rect(screen, (101, 67, 33), trunk_rect)  # Brown trunk
                    
                    # Multi-layered canopy for depth
                    pygame.draw.circle(screen, TILE_ACCENT_COLORS[TileType.TREE], 
                                     (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//3), 
                                     TILE_SIZE//2 - 2)  # Outer canopy
                    pygame.draw.circle(screen, tile.color, 
                                     (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//3), 
                                     TILE_SIZE//3)  # Inner canopy
                    
                elif tile.tile_type == TileType.WALL:
                    # Enhanced brick pattern with better spacing
                    accent_color = TILE_ACCENT_COLORS[TileType.WALL]
                    for i in range(0, TILE_SIZE, 12):
                        for j in range(0, TILE_SIZE, 8):
                            offset = 6 if (j // 8) % 2 else 0
                            brick_x = screen_x + (i + offset) % TILE_SIZE
                            brick_y = screen_y + j
                            if brick_x + 10 <= screen_x + TILE_SIZE and brick_y + 6 <= screen_y + TILE_SIZE:
                                pygame.draw.rect(screen, accent_color, 
                                               (brick_x, brick_y, 10, 6))
                    
                elif tile.tile_type == TileType.GRASS:
                    # Add grass texture with small accent patches
                    accent_color = TILE_ACCENT_COLORS[TileType.GRASS]
                    for i in range(5, TILE_SIZE-5, 15):
                        for j in range(5, TILE_SIZE-5, 15):
                            pygame.draw.circle(screen, accent_color, 
                                             (screen_x + i, screen_y + j), 3)
                    
                elif tile.tile_type == TileType.EMPTY:
                    # Indoor floor with subtle pattern
                    accent_color = TILE_ACCENT_COLORS[TileType.EMPTY]
                    # Diagonal lines for floor pattern
                    for i in range(0, TILE_SIZE, 16):
                        pygame.draw.line(screen, accent_color, 
                                       (screen_x + i, screen_y), 
                                       (screen_x, screen_y + i), 1)
                        pygame.draw.line(screen, accent_color, 
                                       (screen_x + TILE_SIZE - i, screen_y + TILE_SIZE), 
                                       (screen_x + TILE_SIZE, screen_y + TILE_SIZE - i), 1)
                
                # Draw tile border
                pygame.draw.rect(screen, (0, 0, 0), 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE), 1)

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
        
        # Clamp camera to map bounds
        self.target_x = max(0, min(self.target_x, map_width - self.width))
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
        Create a sprite surface with a knight-like character design.
        
        Returns:
            pygame.Surface: The sprite surface
        """
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Draw a more detailed knight character
        # Body (blue armor)
        pygame.draw.rect(surface, (74, 144, 226), (15, 20, 20, 25), border_radius=3)
        
        # Arms
        pygame.draw.rect(surface, (74, 144, 226), (10, 22, 8, 15), border_radius=2)
        pygame.draw.rect(surface, (74, 144, 226), (32, 22, 8, 15), border_radius=2)
        
        # Legs
        pygame.draw.rect(surface, (46, 92, 138), (18, 40, 6, 8), border_radius=1)
        pygame.draw.rect(surface, (46, 92, 138), (26, 40, 6, 8), border_radius=1)
        
        # Head/Helmet (silver)
        pygame.draw.circle(surface, (192, 192, 192), (25, 15), 8)
        
        # Helmet visor
        pygame.draw.rect(surface, (51, 51, 51), (20, 12, 10, 4), border_radius=1)
        
        # Eyes (red glow through visor)
        pygame.draw.circle(surface, (255, 107, 107), (22, 14), 1)
        pygame.draw.circle(surface, (255, 107, 107), (28, 14), 1)
        
        # Sword
        pygame.draw.rect(surface, (139, 69, 19), (38, 18, 2, 12), border_radius=1)
        pygame.draw.rect(surface, (192, 192, 192), (36, 15, 6, 3), border_radius=1)
        
        return surface
    
    def move(self, dx, dy):
        """
        Initiate smooth movement to adjacent tile with collision detection.
        
        Args:
            dx (int): Direction in x (-1, 0, or 1)
            dy (int): Direction in y (-1, 0, or 1)
        """
        # Don't start new movement if already moving
        if self.is_moving:
            return
        
        # Only allow movement in cardinal directions (no diagonal)
        if dx != 0 and dy != 0:
            return
        
        # Only allow movement of one tile at a time
        if abs(dx) > 1 or abs(dy) > 1:
            return
        
        # Calculate new grid position
        new_grid_x = self.target_grid_x + dx
        new_grid_y = self.target_grid_y + dy
        
        # Check bounds
        if self.game_map:
            if (new_grid_x < 0 or new_grid_x >= self.game_map.width or 
                new_grid_y < 0 or new_grid_y >= self.game_map.height):
                return
            
            # Check if the new position is walkable
            if not self.game_map.is_walkable(new_grid_x, new_grid_y):
                return
        else:
            # Fallback: basic boundary checking without map
            if (new_grid_x < 0 or new_grid_x >= WIDTH // TILE_SIZE or
                new_grid_y < 0 or new_grid_y >= HEIGHT // TILE_SIZE):
                return
        
        # Start smooth movement animation
        self.target_grid_x = new_grid_x
        self.target_grid_y = new_grid_y
        self.is_moving = True
        self.move_progress = 0.0
    
    def update(self, dt):
        """
        Update player animation and position.
        
        Args:
            dt (float): Delta time in seconds
        """
        if self.is_moving:
            # Update animation progress
            self.move_progress += self.animation_speed * dt
            
            if self.move_progress >= 1.0:
                # Animation complete
                self.move_progress = 1.0
                self.is_moving = False
                self.grid_x = self.target_grid_x
                self.grid_y = self.target_grid_y
            
            # Interpolate between current and target positions
            start_x = self.grid_x * TILE_SIZE
            start_y = self.grid_y * TILE_SIZE
            target_x = self.target_grid_x * TILE_SIZE
            target_y = self.target_grid_y * TILE_SIZE
            
            # Smooth interpolation (easing)
            t = self.move_progress
            # Apply easing function for smoother animation
            eased_t = t * t * (3.0 - 2.0 * t)  # Smoothstep function
            
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

class Game:
    """
    Main game class that manages the game state and loop with tile-based map system.
    """
    
    def __init__(self):
        """
        Initialize the game with screen, clock, map, and player.
        """
        # Set up the display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Campus Lockdown - Scrollable Map Edition")
        
        # Set up the game clock for consistent FPS
        self.clock = pygame.time.Clock()
        
        # Try to load map from JSON, fallback to sample map
        try:
            map_path = os.path.join("maps", "campus_map.json")
            self.game_map = Map.from_json(map_path)
            print(f"Loaded map: {self.game_map.name}")
        except Exception as e:
            print(f"Could not load JSON map: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            print("Using fallback sample map")
            self.game_map = self._create_sample_map()
        
        # Create camera system
        self.camera = Camera(WIDTH, HEIGHT)
        
        # Create player at spawn point or valid starting position
        if hasattr(self.game_map, 'spawn_point'):
            spawn_x = self.game_map.spawn_point['x'] * TILE_SIZE
            spawn_y = self.game_map.spawn_point['y'] * TILE_SIZE
        else:
            spawn_x, spawn_y = self._find_valid_start_position()
        
        self.player = Player(spawn_x, spawn_y, self.game_map)
        
        # Game state
        self.running = True
        
        # Background color for better contrast
        self.bg_color = (20, 30, 40)  # Dark blue-gray background
    
    def _create_sample_map(self):
        """
        Create a sample map with different tile types.
        
        Returns:
            Map: The created map instance
        """
        # Create a 20x16 map (1000x800 pixels / 50 tile size)
        map_data = [
            [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],  # Wall border
            [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3],  # Grass area
            [3, 1, 4, 1, 1, 2, 2, 2, 1, 1, 1, 4, 1, 1, 1, 1, 4, 1, 1, 3],  # Trees and water
            [3, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 3],  # Mixed terrain
            [3, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 3, 3, 1, 1, 1, 3],
            [3, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 3],
            [3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 3],
            [3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0, 3, 1, 1, 1, 1, 1, 1, 1, 3],  # Building area
            [3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 3],
            [3, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 3],
            [3, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3],
            [3, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 3],
            [3, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3],
            [3, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 3],
            [3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3],
            [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],  # Wall border
        ]
        return Map(map_data)
    
    def _find_valid_start_position(self):
        """
        Find a valid starting position for the player on a walkable tile.
        
        Returns:
            tuple: (x, y) pixel coordinates for player start position
        """
        # Try to find a grass tile near the center
        for y in range(self.game_map.height // 2 - 2, self.game_map.height // 2 + 3):
            for x in range(self.game_map.width // 2 - 2, self.game_map.width // 2 + 3):
                if self.game_map.is_walkable(x, y):
                    pixel_x, pixel_y = self.game_map.grid_to_pixel(x, y)
                    return pixel_x, pixel_y
        
        # Fallback: find any walkable tile
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                if self.game_map.is_walkable(x, y):
                    pixel_x, pixel_y = self.game_map.grid_to_pixel(x, y)
                    return pixel_x, pixel_y
        
        # Last resort: center of screen
        return (WIDTH - PLAYER_SIZE) // 2, (HEIGHT - PLAYER_SIZE) // 2
    
    def handle_events(self):
        """
        Handle pygame events like window close and key presses.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def handle_input(self):
        """
        Handle continuous key input for smooth tile-based player movement.
        """
        keys = pygame.key.get_pressed()
        
        # Handle movement with arrow keys or WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move(-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move(1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move(0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move(0, 1)
    
    def update(self):
        """
        Update game state, player animation, and camera.
        """
        # Calculate delta time in seconds
        dt = self.clock.get_time() / 1000.0
        
        # Update player animation
        self.player.update(dt)
        
        # Update camera to follow player
        map_width = self.game_map.width * TILE_SIZE
        map_height = self.game_map.height * TILE_SIZE
        player_center_x = self.player.x + self.player.size // 2
        player_center_y = self.player.y + self.player.size // 2
        self.camera.follow_target(player_center_x, player_center_y, map_width, map_height, dt)
        
        self.handle_input()
    
    def draw(self):
        """
        Draw all game objects to the screen with camera system.
        """
        # Fill the screen with background color
        self.screen.fill(self.bg_color)
        
        # Draw the map tiles with camera
        self.game_map.draw_with_camera(self.screen, self.camera)
        
        # Draw the player with camera
        self.player.draw(self.screen, self.camera)
        
        # Draw UI elements
        self._draw_ui()
        
        # Update the display
        pygame.display.flip()
    
    def _draw_ui(self):
        """
        Draw UI elements like position indicator, camera info, and controls.
        """
        font = pygame.font.Font(None, 24)
        
        # Player position indicator (both pixel and grid coordinates)
        pixel_pos = f"Player: ({int(self.player.x)}, {int(self.player.y)})"
        grid_pos = self.player.get_grid_position()
        grid_text = f"Grid: ({grid_pos[0]}, {grid_pos[1]})"
        
        pixel_surface = font.render(pixel_pos, True, WHITE)
        grid_surface = font.render(grid_text, True, WHITE)
        
        self.screen.blit(pixel_surface, (10, 10))
        self.screen.blit(grid_surface, (10, 35))
        
        # Camera position indicator
        camera_text = f"Camera: ({int(self.camera.x)}, {int(self.camera.y)})"
        camera_surface = font.render(camera_text, True, WHITE)
        self.screen.blit(camera_surface, (10, 60))
        
        # Map information
        map_info = f"Map: {self.game_map.name} ({self.game_map.width}x{self.game_map.height})"
        map_surface = font.render(map_info, True, WHITE)
        self.screen.blit(map_surface, (10, 85))
        
        # Current tile type indicator
        current_tile = self.game_map.get_tile(grid_pos[0], grid_pos[1])
        if current_tile:
            tile_name = {
                TileType.EMPTY: "Empty",
                TileType.GRASS: "Grass", 
                TileType.WATER: "Water",
                TileType.WALL: "Wall",
                TileType.TREE: "Tree"
            }.get(current_tile.tile_type, "Unknown")
            tile_text = f"Current Tile: {tile_name}"
            tile_surface = font.render(tile_text, True, YELLOW)
            self.screen.blit(tile_surface, (10, 110))
        
        # Controls reminder
        controls_text = "Use WASD or Arrow Keys to explore the scrollable campus map"
        controls_surface = font.render(controls_text, True, WHITE)
        self.screen.blit(controls_surface, (10, HEIGHT - 30))
    
    def run(self):
        """
        Main game loop that runs until the game is quit.
        """
        print("Starting Campus Lockdown...")
        print("Controls:")
        print("  Arrow Keys or WASD: Move player around campus")
        print("  ESC or Close Window: Quit game")
        print(f"Map loaded: {self.game_map.name} ({self.game_map.width}x{self.game_map.height} tiles)")
        
        while self.running:
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw everything
            self.draw()
            
            # Maintain consistent frame rate
            self.clock.tick(FPS)
        
        # Clean up
        pygame.quit()
        sys.exit()

def main():
    """
    Main function to start the game.
    """
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()