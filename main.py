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
# Set windowed mode dimensions
WIDTH = 1200
HEIGHT = 800
FPS = 60

# Colors (RGB values)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Tile constants - Calculate tile size to fit window
# Assuming typical map size of 16x12 tiles with some UI space
TILE_SIZE = min(WIDTH // 16, (HEIGHT - 100) // 12)  # Leave 100px for UI

# Player constants
PLAYER_SIZE = int(TILE_SIZE * 0.8)  # Player is 80% of tile size
PLAYER_SPEED = 6

# Tile types
class TileType:
    EMPTY = 0
    GRASS = 1
    WATER = 2
    WALL = 3
    TREE = 4
    FLOOR = 5
    BUILDING = 6
    PLAYER_SPAWN = 7
    EXIT = 8
    LAKE = 9
    GREEN_FIELD = 10
    LIBRARY = 11
    DORMITORY = 12
    CAFETERIA = 13
    ROCK = 14
    CAVE_WALL = 15
    WATER_POOL = 16

# Tile colors
TILE_COLORS = {
    TileType.EMPTY: (40, 40, 40),      # Dark gray
    TileType.GRASS: (34, 139, 34),     # Forest green
    TileType.WATER: (30, 144, 255),    # Dodger blue
    TileType.WALL: (139, 69, 19),      # Saddle brown
    TileType.TREE: (0, 100, 0),        # Dark green
    TileType.FLOOR: (160, 160, 160),   # Gray
    TileType.BUILDING: (101, 67, 33),  # Brown
    TileType.PLAYER_SPAWN: (255, 255, 0),  # Yellow
    TileType.EXIT: (139, 69, 19),      # Brown (doorway frame)
    TileType.LAKE: (0, 100, 200),      # Deep Blue
    TileType.GREEN_FIELD: (124, 252, 0),  # Lawn Green
    TileType.LIBRARY: (160, 82, 45),   # Saddle Brown
    TileType.DORMITORY: (220, 20, 60), # Crimson
    TileType.CAFETERIA: (255, 165, 0), # Orange
    TileType.ROCK: (128, 128, 128),    # Gray
    TileType.CAVE_WALL: (64, 64, 64),  # Dark Gray
    TileType.WATER_POOL: (72, 61, 139) # Dark Slate Blue
}

# Tile character mapping for JSON maps
TILE_CHARS = {
    'G': TileType.GRASS,
    'W': TileType.WATER,
    'B': TileType.BUILDING,
    'T': TileType.TREE,
    '.': TileType.FLOOR,
    'P': TileType.PLAYER_SPAWN,
    'E': TileType.EXIT,
    ' ': TileType.EMPTY,
    '#': TileType.WALL,
    'L': TileType.LAKE,
    'F': TileType.GREEN_FIELD,
    'I': TileType.LIBRARY,
    'D': TileType.DORMITORY,
    'C': TileType.CAFETERIA,
    'R': TileType.ROCK,
    'V': TileType.CAVE_WALL,
    'O': TileType.WATER_POOL
}

# Walkable tiles (tiles the player can move on)
WALKABLE_TILES = {TileType.EMPTY, TileType.GRASS, TileType.FLOOR, TileType.PLAYER_SPAWN, TileType.EXIT, TileType.GREEN_FIELD}

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
            # Add animated water ripple effects
            import time
            ripple_offset = int(time.time() * 3) % 10
            for i in range(3):
                ripple_radius = (TILE_SIZE//6) + (i * 4) + (ripple_offset % 4)
                if ripple_radius < TILE_SIZE//2:
                    pygame.draw.circle(screen, (100, 180, 255), 
                                     (self.pixel_x + TILE_SIZE//2, self.pixel_y + TILE_SIZE//2), 
                                     ripple_radius, 1)
        elif self.tile_type == TileType.TREE:
            # Enhanced tree with detailed trunk and layered leaves
            trunk_width = max(4, TILE_SIZE//8)
            trunk_rect = pygame.Rect(self.pixel_x + TILE_SIZE//2 - trunk_width//2, 
                                   self.pixel_y + TILE_SIZE//2, trunk_width, TILE_SIZE//2)
            pygame.draw.rect(screen, (101, 67, 33), trunk_rect)  # Brown trunk
            # Add trunk texture
            for i in range(0, TILE_SIZE//2, 4):
                pygame.draw.line(screen, (80, 50, 20), 
                               (trunk_rect.left, trunk_rect.top + i), 
                               (trunk_rect.right, trunk_rect.top + i), 1)
            
            # Layered leaves for depth
            leaf_center_x = self.pixel_x + TILE_SIZE//2
            leaf_center_y = self.pixel_y + TILE_SIZE//3
            pygame.draw.circle(screen, (0, 100, 0), (leaf_center_x, leaf_center_y), TILE_SIZE//3)  # Dark green base
            pygame.draw.circle(screen, (0, 150, 0), (leaf_center_x-2, leaf_center_y-2), TILE_SIZE//4)  # Lighter green highlight
        elif self.tile_type == TileType.WALL:
            # Add brick pattern
            for i in range(0, TILE_SIZE, 10):
                for j in range(0, TILE_SIZE, 10):
                    if (i + j) % 20 == 0:
                        pygame.draw.rect(screen, (160, 82, 45), 
                                       (self.pixel_x + i, self.pixel_y + j, 8, 8))
        elif self.tile_type == TileType.EXIT:
            # Draw doorway design
            # Door frame (darker brown)
            frame_color = (101, 67, 33)
            # Door opening (black)
            opening_color = (40, 40, 40)
            
            # Draw door frame
            frame_width = TILE_SIZE // 8
            pygame.draw.rect(screen, frame_color, 
                           (self.pixel_x, self.pixel_y, TILE_SIZE, frame_width))  # Top
            pygame.draw.rect(screen, frame_color, 
                           (self.pixel_x, self.pixel_y + TILE_SIZE - frame_width, TILE_SIZE, frame_width))  # Bottom
            pygame.draw.rect(screen, frame_color, 
                           (self.pixel_x, self.pixel_y, frame_width, TILE_SIZE))  # Left
            pygame.draw.rect(screen, frame_color, 
                           (self.pixel_x + TILE_SIZE - frame_width, self.pixel_y, frame_width, TILE_SIZE))  # Right
            
            # Draw door opening (center)
            opening_rect = pygame.Rect(self.pixel_x + frame_width, self.pixel_y + frame_width, 
                                     TILE_SIZE - 2*frame_width, TILE_SIZE - 2*frame_width)
            pygame.draw.rect(screen, opening_color, opening_rect)
            
            # Add door handle
            handle_size = max(2, TILE_SIZE // 16)
            handle_x = self.pixel_x + TILE_SIZE - frame_width - handle_size * 2
            handle_y = self.pixel_y + TILE_SIZE // 2
            pygame.draw.circle(screen, (255, 215, 0), (handle_x, handle_y), handle_size)  # Gold handle
        elif self.tile_type == TileType.LIBRARY:
            # Add book shelves pattern
            shelf_color = (120, 60, 30)
            book_colors = [(200, 50, 50), (50, 150, 50), (50, 50, 200), (200, 200, 50)]
            for i in range(0, TILE_SIZE, TILE_SIZE//4):
                pygame.draw.rect(screen, shelf_color, (self.pixel_x, self.pixel_y + i, TILE_SIZE, 3))
                for j in range(0, TILE_SIZE, 8):
                    book_color = book_colors[(i//4 + j//8) % len(book_colors)]
                    pygame.draw.rect(screen, book_color, (self.pixel_x + j, self.pixel_y + i + 3, 6, TILE_SIZE//4 - 6))
        elif self.tile_type == TileType.DORMITORY:
            # Add window pattern
            window_color = (100, 150, 200)
            frame_color = (80, 80, 80)
            window_size = TILE_SIZE // 3
            window_x = self.pixel_x + (TILE_SIZE - window_size) // 2
            window_y = self.pixel_y + (TILE_SIZE - window_size) // 2
            pygame.draw.rect(screen, frame_color, (window_x - 2, window_y - 2, window_size + 4, window_size + 4))
            pygame.draw.rect(screen, window_color, (window_x, window_y, window_size, window_size))
            # Window cross
            pygame.draw.line(screen, frame_color, (window_x + window_size//2, window_y), 
                           (window_x + window_size//2, window_y + window_size), 2)
            pygame.draw.line(screen, frame_color, (window_x, window_y + window_size//2), 
                           (window_x + window_size, window_y + window_size//2), 2)
        elif self.tile_type == TileType.CAFETERIA:
            # Add table and chairs pattern
            table_color = (139, 69, 19)
            chair_color = (101, 67, 33)
            # Table
            table_size = TILE_SIZE // 2
            table_x = self.pixel_x + (TILE_SIZE - table_size) // 2
            table_y = self.pixel_y + (TILE_SIZE - table_size) // 2
            pygame.draw.rect(screen, table_color, (table_x, table_y, table_size, table_size))
            # Chairs (small squares around table)
            chair_size = TILE_SIZE // 8
            positions = [(table_x - chair_size, table_y), (table_x + table_size, table_y),
                        (table_x, table_y - chair_size), (table_x, table_y + table_size)]
            for pos in positions:
                pygame.draw.rect(screen, chair_color, (pos[0], pos[1], chair_size, chair_size))
        elif self.tile_type == TileType.ROCK:
            # Add rock texture with highlights and shadows
            highlight_color = (160, 160, 160)
            shadow_color = (80, 80, 80)
            # Draw random rock-like shapes
            import random
            random.seed(self.grid_x * 1000 + self.grid_y)  # Consistent pattern per tile
            for _ in range(3):
                size = random.randint(TILE_SIZE//6, TILE_SIZE//3)
                x = self.pixel_x + random.randint(0, TILE_SIZE - size)
                y = self.pixel_y + random.randint(0, TILE_SIZE - size)
                pygame.draw.circle(screen, shadow_color, (x + 2, y + 2), size//2)
                pygame.draw.circle(screen, highlight_color, (x, y), size//2)
        elif self.tile_type == TileType.GREEN_FIELD:
            # Add grass texture
            grass_colors = [(100, 200, 100), (120, 220, 120), (80, 180, 80)]
            import random
            random.seed(self.grid_x * 1000 + self.grid_y)
            for _ in range(8):
                grass_color = random.choice(grass_colors)
                x = self.pixel_x + random.randint(0, TILE_SIZE - 2)
                y = self.pixel_y + random.randint(0, TILE_SIZE - 4)
                pygame.draw.line(screen, grass_color, (x, y + 4), (x, y), 1)
        
        # Draw tile border for grid visibility
        pygame.draw.rect(screen, (0, 0, 0), 
                        (self.pixel_x, self.pixel_y, TILE_SIZE, TILE_SIZE), 1)

class MapManager:
    """
    MapManager class that handles loading, switching, and saving map states.
    Supports unlimited maps stored in JSON files with persistent player state.
    """
    
    def __init__(self, maps_directory="maps"):
        """
        Initialize the MapManager.
        
        Args:
            maps_directory (str): Directory containing map JSON files
        """
        self.maps_directory = maps_directory
        self.loaded_maps = {}  # Cache for loaded maps
        self.current_map_id = None
        self.current_map = None
        self.map_metadata = {}  # Store metadata for all maps
        
        # Player persistent state
        self.player_inventory = []
        self.player_stats = {
            "health": 100,
            "level": 1,
            "experience": 0,
            "gold": 0
        }
        
        # Discover available maps
        self._discover_maps()
    
    def _discover_maps(self):
        """
        Discover all available map files in the maps directory.
        """
        if not os.path.exists(self.maps_directory):
            print(f"Maps directory '{self.maps_directory}' not found!")
            return
        
        for filename in os.listdir(self.maps_directory):
            if filename.endswith('.json'):
                map_id = filename[:-5]  # Remove .json extension
                try:
                    with open(os.path.join(self.maps_directory, filename), 'r') as f:
                        map_data = json.load(f)
                        self.map_metadata[map_id] = map_data.get('metadata', {})
                        print(f"Discovered map: {map_id} - {map_data.get('metadata', {}).get('name', 'Unknown')}")
                except Exception as e:
                    print(f"Error reading map {filename}: {e}")
    
    def load_map(self, map_id):
        """
        Load a map from JSON file.
        
        Args:
            map_id (str): The map identifier (filename without .json)
            
        Returns:
            Map: The loaded map instance or None if failed
        """
        # Check if map is already loaded
        if map_id in self.loaded_maps:
            return self.loaded_maps[map_id]
        
        map_file = os.path.join(self.maps_directory, f"{map_id}.json")
        
        if not os.path.exists(map_file):
            print(f"Map file not found: {map_file}")
            return None
        
        try:
            with open(map_file, 'r') as f:
                map_data = json.load(f)
            
            # Convert JSON map to Map instance
            game_map = self._create_map_from_json(map_data)
            
            # Cache the loaded map
            self.loaded_maps[map_id] = {
                'map': game_map,
                'data': map_data,
                'spawn_points': map_data.get('spawn_points', {}),
                'transitions': map_data.get('transitions', [])
            }
            
            print(f"Loaded map: {map_id}")
            return game_map
            
        except Exception as e:
            print(f"Error loading map {map_id}: {e}")
            return None
    
    def _create_map_from_json(self, map_data):
        """
        Create a Map instance from JSON data.
        
        Args:
            map_data (dict): JSON map data
            
        Returns:
            Map: The created map instance
        """
        tiles_str = map_data.get('tiles', [])
        dimensions = map_data.get('dimensions', {})
        width = dimensions.get('width', len(tiles_str[0]) if tiles_str else 0)
        height = dimensions.get('height', len(tiles_str))
        
        # Convert string tiles to numeric array
        map_array = []
        for row_str in tiles_str:
            row = []
            for char in row_str:
                tile_type = TILE_CHARS.get(char, TileType.EMPTY)
                row.append(tile_type)
            map_array.append(row)
        
        return Map(map_array)
    
    def switch_map(self, map_id, spawn_point="default"):
        """
        Switch to a different map.
        
        Args:
            map_id (str): The target map identifier
            spawn_point (str): The spawn point to use on the new map
            
        Returns:
            tuple: (Map instance, spawn_position) or (None, None) if failed
        """
        # Load the target map
        new_map = self.load_map(map_id)
        if not new_map:
            return None, None
        
        # Update current map
        self.current_map_id = map_id
        self.current_map = new_map
        
        # Get spawn position
        map_info = self.loaded_maps[map_id]
        spawn_points = map_info['spawn_points']
        spawn_pos = spawn_points.get(spawn_point, spawn_points.get('default', {'x': 0, 'y': 0}))
        
        print(f"Switched to map: {map_id} at spawn point: {spawn_point}")
        return new_map, (spawn_pos['x'], spawn_pos['y'])
    
    def get_current_map(self):
        """
        Get the currently active map.
        
        Returns:
            Map: The current map instance or None
        """
        return self.current_map
    
    def get_current_map_id(self):
        """
        Get the current map identifier.
        
        Returns:
            str: The current map ID or None
        """
        return self.current_map_id
    
    def check_transitions(self, player_x, player_y):
        """
        Check if the player is at a transition point.
        
        Args:
            player_x (int): Player grid x position
            player_y (int): Player grid y position
            
        Returns:
            dict: Transition data or None if no transition
        """
        if not self.current_map_id or self.current_map_id not in self.loaded_maps:
            return None
        
        map_info = self.loaded_maps[self.current_map_id]
        transitions = map_info['transitions']
        
        for transition in transitions:
            pos = transition['from_position']
            if pos['x'] == player_x and pos['y'] == player_y:
                return transition
        
        return None
    
    def get_player_inventory(self):
        """
        Get the player's persistent inventory.
        
        Returns:
            list: Player inventory items
        """
        return self.player_inventory.copy()
    
    def get_player_stats(self):
        """
        Get the player's persistent stats.
        
        Returns:
            dict: Player stats
        """
        return self.player_stats.copy()
    
    def update_player_stats(self, **kwargs):
        """
        Update player stats.
        
        Args:
            **kwargs: Stat updates (health=100, level=2, etc.)
        """
        for key, value in kwargs.items():
            if key in self.player_stats:
                self.player_stats[key] = value
    
    def add_to_inventory(self, item):
        """
        Add an item to the player's inventory.
        
        Args:
            item: Item to add to inventory
        """
        self.player_inventory.append(item)
    
    def remove_from_inventory(self, item):
        """
        Remove an item from the player's inventory.
        
        Args:
            item: Item to remove from inventory
            
        Returns:
            bool: True if item was removed, False if not found
        """
        try:
            self.player_inventory.remove(item)
            return True
        except ValueError:
            return False

class Map:
    """
    Map class that manages the tile-based game world.
    """
    
    def __init__(self, map_data):
        """
        Initialize the map from a 2D array.
        
        Args:
            map_data (list): 2D list representing the map layout
        """
        self.map_data = map_data
        self.height = len(map_data)
        self.width = len(map_data[0]) if map_data else 0
        self.tiles = []
        
        # Create tile objects from map data
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile_type = map_data[y][x]
                tile = Tile(tile_type, x, y)
                row.append(tile)
            self.tiles.append(row)
    
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
    
    def draw(self, screen):
        """
        Draw the player sprite or fallback rectangle on the screen.
        
        Args:
            screen: Pygame screen surface to draw on
        """
        if self.use_sprite and self.sprite:
            # Draw the sprite
            screen.blit(self.sprite, (int(self.x), int(self.y)))
        else:
            # Fallback to colored rectangle with border for better visibility
            pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), self.size, self.size))
            pygame.draw.rect(screen, WHITE, (int(self.x), int(self.y), self.size, self.size), 2)

class Game:
    """
    Main game class that manages the game state and loop with MapManager system.
    """
    
    def __init__(self):
        """
        Initialize the game with screen, clock, MapManager, and player.
        """
        # Set up the display in windowed mode
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Adventure Quest - JSON Map System")
        
        # Set up the game clock for consistent FPS
        self.clock = pygame.time.Clock()
        
        # Initialize MapManager
        self.map_manager = MapManager()
        
        # Load initial map
        initial_map, spawn_pos = self.map_manager.switch_map("map1")
        if not initial_map:
            # Fallback to sample map if JSON maps fail
            print("Failed to load JSON maps, creating fallback map...")
            initial_map = self._create_fallback_map()
            spawn_pos = self._find_valid_start_position(initial_map)
        
        # Create player at spawn position
        start_x, start_y = spawn_pos if spawn_pos else (0, 0)
        pixel_x, pixel_y = initial_map.grid_to_pixel(start_x, start_y)
        self.player = Player(pixel_x, pixel_y, initial_map)
        
        # Game state
        self.running = True
        
        # Background color for better contrast
        self.bg_color = (20, 30, 40)  # Dark blue-gray background
    
    def _create_fallback_map(self):
        """
        Create a fallback map if JSON maps fail to load.
        
        Returns:
            Map: The created map instance
        """
        # Create a simple 12x8 map to match JSON format
        map_data = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Grass
            [1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1],  # Wall border
            [1, 3, 5, 5, 5, 5, 5, 5, 5, 5, 3, 1],  # Floor area
            [1, 3, 5, 7, 5, 5, 5, 5, 5, 5, 3, 1],  # Player spawn
            [1, 3, 5, 5, 5, 5, 5, 5, 5, 5, 3, 1],  # Floor area
            [1, 3, 5, 5, 5, 5, 5, 5, 5, 5, 3, 1],  # Floor area
            [1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1],  # Wall border
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 8],  # Exit
        ]
        return Map(map_data)
    
    def _find_valid_start_position(self, game_map):
        """
        Find a valid starting position for the player on a walkable tile.
        
        Args:
            game_map (Map): The map to search for valid positions
        
        Returns:
            tuple: (grid_x, grid_y) grid coordinates for player start position
        """
        # Try to find a walkable tile near the center
        for y in range(game_map.height // 2 - 2, game_map.height // 2 + 3):
            for x in range(game_map.width // 2 - 2, game_map.width // 2 + 3):
                if game_map.is_walkable(x, y):
                    return x, y
        
        # Fallback: find any walkable tile
        for y in range(game_map.height):
            for x in range(game_map.width):
                if game_map.is_walkable(x, y):
                    return x, y
        
        # Last resort: return (0, 0)
        return 0, 0
    
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
        Update game state, player animation, and handle map transitions.
        """
        # Calculate delta time in seconds
        dt = self.clock.get_time() / 1000.0
        
        # Update player animation
        self.player.update(dt)
        
        # Handle input
        self.handle_input()
        
        # Check for map transitions
        player_grid_pos = self.player.get_grid_position()
        transition = self.map_manager.check_transitions(player_grid_pos[0], player_grid_pos[1])
        
        if transition:
            # Perform map transition
            target_map = transition['to_map']
            target_spawn = transition['to_spawn']
            
            new_map, spawn_pos = self.map_manager.switch_map(target_map, target_spawn)
            if new_map and spawn_pos:
                # Update player's map reference and position
                self.player.set_map(new_map)
                
                # Move player to new spawn position
                spawn_x, spawn_y = spawn_pos
                pixel_x, pixel_y = new_map.grid_to_pixel(spawn_x, spawn_y)
                self.player.x = float(pixel_x)
                self.player.y = float(pixel_y)
                self.player.grid_x = spawn_x
                self.player.grid_y = spawn_y
                self.player.target_grid_x = spawn_x
                self.player.target_grid_y = spawn_y
                self.player.is_moving = False
                
                print(f"Transitioned to {target_map} at spawn {target_spawn}")
    
    def draw(self):
        """
        Draw all game objects to the screen.
        """
        # Fill the screen with background color
        self.screen.fill(self.bg_color)
        
        # Draw the current map
        current_map = self.map_manager.get_current_map()
        if current_map:
            current_map.draw(self.screen)
        
        # Draw the player
        self.player.draw(self.screen)
        
        # Draw UI elements
        self._draw_ui()
        
        # Update the display
        pygame.display.flip()
    
    def _draw_ui(self):
        """
        Draw UI elements including position, map info, player stats, and controls.
        """
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        
        # Current map information
        current_map_id = self.map_manager.get_current_map_id()
        if current_map_id:
            map_text = f"Current Map: {current_map_id}"
            map_surface = font.render(map_text, True, GREEN)
            self.screen.blit(map_surface, (10, 10))
        
        # Player position indicator (both pixel and grid coordinates)
        pixel_pos = f"Pixel: ({int(self.player.x)}, {int(self.player.y)})"
        grid_pos = self.player.get_grid_position()
        grid_text = f"Grid: ({grid_pos[0]}, {grid_pos[1]})"
        
        pixel_surface = small_font.render(pixel_pos, True, WHITE)
        grid_surface = small_font.render(grid_text, True, WHITE)
        
        self.screen.blit(pixel_surface, (10, 35))
        self.screen.blit(grid_surface, (10, 55))
        
        # Current tile type indicator
        current_map = self.map_manager.get_current_map()
        if current_map:
            current_tile = current_map.get_tile(grid_pos[0], grid_pos[1])
            if current_tile:
                tile_name = {
                    TileType.EMPTY: "Empty",
                    TileType.GRASS: "Grass", 
                    TileType.WATER: "Water",
                    TileType.WALL: "Wall",
                    TileType.TREE: "Tree",
                    TileType.FLOOR: "Floor",
                    TileType.BUILDING: "Building",
                    TileType.PLAYER_SPAWN: "Spawn Point",
                    TileType.EXIT: "Exit",
                    TileType.LAKE: "Lake",
                    TileType.GREEN_FIELD: "Green Field",
                    TileType.LIBRARY: "Library",
                    TileType.DORMITORY: "Dormitory",
                    TileType.CAFETERIA: "Cafeteria",
                    TileType.ROCK: "Rock",
                    TileType.CAVE_WALL: "Cave Wall",
                    TileType.WATER_POOL: "Water Pool"
                }.get(current_tile.tile_type, "Unknown")
                tile_text = f"Current Tile: {tile_name}"
                tile_surface = small_font.render(tile_text, True, YELLOW)
                self.screen.blit(tile_surface, (10, 75))
        
        # Player stats
        stats = self.map_manager.get_player_stats()
        stats_y = 100
        for stat_name, stat_value in stats.items():
            stat_text = f"{stat_name.title()}: {stat_value}"
            stat_surface = small_font.render(stat_text, True, WHITE)
            self.screen.blit(stat_surface, (10, stats_y))
            stats_y += 20
        
        # Inventory count
        inventory = self.map_manager.get_player_inventory()
        inventory_text = f"Inventory: {len(inventory)} items"
        inventory_surface = small_font.render(inventory_text, True, WHITE)
        self.screen.blit(inventory_surface, (10, stats_y))
        
        # Controls reminder
        controls_text = "Use WASD or Arrow Keys to move • Step on Exit tiles to change maps"
        controls_surface = small_font.render(controls_text, True, WHITE)
        self.screen.blit(controls_surface, (10, HEIGHT - 30))
    
    def run(self):
        """
        Main game loop that runs until the game is quit.
        """
        print("Starting Adventure Quest...")
        print("Controls:")
        print("  Arrow Keys or WASD: Move player")
        print("  ESC or Close Window: Quit game")
        
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