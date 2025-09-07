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

# Dark environment constants
VISIBILITY_RADIUS = 0  # Player's visibility radius in pixels
FLASHLIGHT_RADIUS = 130   # Flashlight radius when enabled (smaller, focused beam)
DARKNESS_ALPHA = 200     # Alpha value for darkness overlay (0-255, higher = darker)

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
    PATHWAY = 5
    LIBRARY = 6
    CAFETERIA = 7
    DORMITORY = 8
    SPORTS_FIELD = 9
    PARKING_LOT = 10
    DOOR = 11
    BOOKSHELF = 12
    DESK = 13
    CHAIR = 14
    DINING_TABLE = 15
    KITCHEN_COUNTER = 16
    SERVING_COUNTER = 17
    BED = 18
    WARDROBE = 19
    BATHROOM = 20
    PARKING_SPACE = 21
    DRIVING_LANE = 22
    SIDEWALK = 23
    LIBRARY_DOOR = 24
    CAFETERIA_DOOR = 25
    DORMITORY_DOOR = 26
    PARKING_DOOR = 27
    
    # Character to tile type mapping for JSON maps
    CHAR_TO_TYPE = {
        'E': EMPTY,
        'G': GRASS,
        'W': WATER,
        'B': WALL,
        'T': TREE,
        'P': PATHWAY,
        'L': LIBRARY,
        'C': CAFETERIA,
        'D': DORMITORY,
        'S': SPORTS_FIELD,
        'R': PARKING_LOT,
        'O': DOOR,
        'F': BOOKSHELF,
        'K': DESK,
        'H': CHAIR,
        'M': DINING_TABLE,
        'N': KITCHEN_COUNTER,
        'V': SERVING_COUNTER,
        'A': BED,
        'U': WARDROBE,
        'I': BATHROOM,
        'X': PARKING_SPACE,
        'Y': DRIVING_LANE,
        'Z': SIDEWALK,
        'Q': LIBRARY_DOOR,     # DL - Door Library
        'J': CAFETERIA_DOOR,   # DC - Door Cafeteria  
        'M': DORMITORY_DOOR,   # DD - Door Dormitory
        'N': PARKING_DOOR      # DP - Door Parking
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
    TileType.PATHWAY: (169, 169, 169), # Light gray concrete
    TileType.LIBRARY: (139, 69, 19),   # Dark brown library
    TileType.CAFETERIA: (255, 140, 0), # Orange cafeteria
    TileType.DORMITORY: (70, 130, 180), # Steel blue dormitory
    TileType.SPORTS_FIELD: (34, 139, 34), # Forest green sports field
    TileType.PARKING_LOT: (105, 105, 105), # Dim gray parking
    TileType.DOOR: (139, 69, 19),      # Dark brown door (same as library for consistency)
    TileType.BOOKSHELF: (101, 67, 33),  # Dark brown bookshelf
    TileType.DESK: (160, 82, 45),      # Sandy brown desk
    TileType.CHAIR: (139, 69, 19),     # Dark brown chair
    TileType.DINING_TABLE: (139, 69, 19), # Dark brown dining table
    TileType.KITCHEN_COUNTER: (192, 192, 192), # Silver kitchen counter
    TileType.SERVING_COUNTER: (255, 140, 0), # Orange serving counter
    TileType.BED: (255, 192, 203), # Pink bed
    TileType.WARDROBE: (101, 67, 33), # Dark brown wardrobe
    TileType.BATHROOM: (173, 216, 230), # Light blue bathroom
    TileType.PARKING_SPACE: (128, 128, 128), # Gray parking space
    TileType.DRIVING_LANE: (64, 64, 64), # Dark gray driving lane
    TileType.SIDEWALK: (192, 192, 192), # Light gray sidewalk
    TileType.LIBRARY_DOOR: (139, 69, 19), # Dark brown library door
    TileType.CAFETERIA_DOOR: (255, 140, 0), # Orange cafeteria door
    TileType.DORMITORY_DOOR: (70, 130, 180), # Steel blue dormitory door
    TileType.PARKING_DOOR: (105, 105, 105), # Gray parking door
}

# Secondary colors for visual variety
TILE_ACCENT_COLORS = {
    TileType.EMPTY: (55, 55, 60),      # Lighter floor accent
    TileType.GRASS: (139, 195, 74),    # Light grass accent
    TileType.WATER: (100, 181, 246),   # Light water ripples
    TileType.WALL: (141, 110, 99),     # Light brick accent
    TileType.TREE: (102, 187, 106),    # Light leaf accent
    TileType.PATHWAY: (192, 192, 192), # Silver pathway accent
    TileType.LIBRARY: (160, 82, 45),   # Sandy brown library accent
    TileType.CAFETERIA: (255, 165, 0), # Orange cafeteria accent
    TileType.DORMITORY: (100, 149, 237), # Cornflower blue dormitory accent
    TileType.SPORTS_FIELD: (50, 205, 50), # Lime green sports accent
    TileType.PARKING_LOT: (128, 128, 128), # Gray parking accent
    TileType.DOOR: (160, 82, 45),      # Sandy brown door accent
    TileType.BOOKSHELF: (139, 90, 43),  # Light brown bookshelf accent
    TileType.DESK: (205, 133, 63),     # Peru desk accent
    TileType.CHAIR: (160, 82, 45),     # Sandy brown chair accent
    TileType.DINING_TABLE: (160, 82, 45), # Sandy brown dining table accent
    TileType.KITCHEN_COUNTER: (211, 211, 211), # Light gray kitchen counter accent
    TileType.SERVING_COUNTER: (255, 165, 0), # Orange serving counter accent
    TileType.BED: (255, 218, 185), # Peach bed accent
    TileType.WARDROBE: (160, 82, 45), # Light brown wardrobe accent
    TileType.BATHROOM: (135, 206, 235), # Sky blue bathroom accent
    TileType.PARKING_SPACE: (169, 169, 169), # Dark gray parking space accent
    TileType.DRIVING_LANE: (105, 105, 105), # Dim gray driving lane accent
    TileType.SIDEWALK: (211, 211, 211), # Light gray sidewalk accent
    TileType.LIBRARY_DOOR: (160, 82, 45), # Sandy brown library door accent
    TileType.CAFETERIA_DOOR: (255, 165, 0), # Orange cafeteria door accent
    TileType.DORMITORY_DOOR: (100, 149, 237), # Cornflower blue dormitory door accent
    TileType.PARKING_DOOR: (128, 128, 128), # Gray parking door accent
}

# Walkable tile types (tiles the player can move onto)
WALKABLE_TILES = {TileType.EMPTY, TileType.GRASS, TileType.PATHWAY, TileType.LIBRARY, TileType.CAFETERIA, TileType.DORMITORY, TileType.SPORTS_FIELD, TileType.PARKING_LOT, TileType.DOOR, TileType.DESK, TileType.CHAIR, TileType.DINING_TABLE, TileType.SERVING_COUNTER, TileType.BED, TileType.BATHROOM, TileType.PARKING_SPACE, TileType.DRIVING_LANE, TileType.SIDEWALK, TileType.LIBRARY_DOOR, TileType.CAFETERIA_DOOR, TileType.DORMITORY_DOOR, TileType.PARKING_DOOR}

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
        
        # Grid borders removed for cleaner appearance

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
                
                elif tile.tile_type == TileType.PATHWAY:
                    # Concrete pathway with center line
                    accent_color = TILE_ACCENT_COLORS[TileType.PATHWAY]
                    pygame.draw.line(screen, accent_color, 
                                   (screen_x, screen_y + TILE_SIZE//2), 
                                   (screen_x + TILE_SIZE, screen_y + TILE_SIZE//2), 2)
                
                elif tile.tile_type == TileType.LIBRARY:
                    # Library with book shelves pattern
                    accent_color = TILE_ACCENT_COLORS[TileType.LIBRARY]
                    for i in range(5, TILE_SIZE-5, 10):
                        pygame.draw.rect(screen, accent_color, 
                                       (screen_x + i, screen_y + 5, 8, TILE_SIZE-10))
                
                elif tile.tile_type == TileType.CAFETERIA:
                    # Cafeteria with table pattern
                    accent_color = TILE_ACCENT_COLORS[TileType.CAFETERIA]
                    pygame.draw.rect(screen, accent_color, 
                                   (screen_x + 10, screen_y + 10, TILE_SIZE-20, TILE_SIZE-20))
                    pygame.draw.circle(screen, tile.color, 
                                     (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE//2), 8)
                
                elif tile.tile_type == TileType.DORMITORY:
                    # Dormitory with window pattern
                    accent_color = TILE_ACCENT_COLORS[TileType.DORMITORY]
                    for i in range(8, TILE_SIZE-8, 16):
                        for j in range(8, TILE_SIZE-8, 16):
                            pygame.draw.rect(screen, accent_color, 
                                           (screen_x + i, screen_y + j, 12, 12))
                
                elif tile.tile_type == TileType.SPORTS_FIELD:
                    # Sports field with line markings
                    accent_color = TILE_ACCENT_COLORS[TileType.SPORTS_FIELD]
                    pygame.draw.line(screen, accent_color, 
                                   (screen_x + TILE_SIZE//2, screen_y), 
                                   (screen_x + TILE_SIZE//2, screen_y + TILE_SIZE), 2)
                    pygame.draw.line(screen, accent_color, 
                                   (screen_x, screen_y + TILE_SIZE//2), 
                                   (screen_x + TILE_SIZE, screen_y + TILE_SIZE//2), 2)
                
                elif tile.tile_type == TileType.PARKING_LOT:
                    # Parking lot with parking space lines
                    accent_color = TILE_ACCENT_COLORS[TileType.PARKING_LOT]
                    for i in range(0, TILE_SIZE, 12):
                        pygame.draw.line(screen, accent_color, 
                                       (screen_x + i, screen_y), 
                                       (screen_x + i, screen_y + TILE_SIZE), 1)
                
                # Grid borders removed for cleaner appearance

class ItemType:
    """Item type constants for different collectible items."""
    POTION = 0
    SCROLL = 1
    KEY = 2
    
    # Item names for display
    NAMES = {
        POTION: "Health Potion",
        SCROLL: "Magic Scroll",
        KEY: "Golden Key"
    }
    
    # Item colors for visual representation
    COLORS = {
        POTION: (255, 100, 100),  # Red
        SCROLL: (100, 100, 255),  # Blue
        KEY: (255, 215, 0)        # Gold
    }
    
    # Item descriptions
    DESCRIPTIONS = {
        POTION: "Restores health when consumed",
        SCROLL: "Contains ancient magical knowledge",
        KEY: "Opens locked doors and chests"
    }

class Item:
    """
    Item class representing collectible objects scattered around the map.
    """
    
    def __init__(self, item_type, grid_x, grid_y):
        """
        Initialize an item with its type and grid position.
        
        Args:
            item_type (int): The type of item (from ItemType class)
            grid_x (int): Grid x position
            grid_y (int): Grid y position
        """
        self.item_type = item_type
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * TILE_SIZE + TILE_SIZE // 4  # Center in tile
        self.pixel_y = grid_y * TILE_SIZE + TILE_SIZE // 4
        self.size = TILE_SIZE // 2  # Items are smaller than tiles
        self.collected = False
        
        # Visual properties
        self.color = ItemType.COLORS.get(item_type, (255, 255, 255))
        self.name = ItemType.NAMES.get(item_type, "Unknown Item")
        self.description = ItemType.DESCRIPTIONS.get(item_type, "A mysterious item")
        
        # Animation properties for visual appeal
        self.bob_offset = 0.0
        self.bob_speed = 3.0
        self.glow_alpha = 128
        
    def update(self, dt):
        """
        Update item animation (bobbing effect).
        
        Args:
            dt (float): Delta time in seconds
        """
        if not self.collected:
            self.bob_offset += self.bob_speed * dt
    
    def draw(self, screen, camera=None):
        """
        Draw the item on the screen with visual effects.
        
        Args:
            screen: Pygame screen surface to draw on
            camera: Optional camera for coordinate transformation
        """
        if self.collected:
            return
        
        # Calculate screen position
        if camera:
            screen_x, screen_y = camera.world_to_screen(self.pixel_x, self.pixel_y)
        else:
            screen_x, screen_y = self.pixel_x, self.pixel_y
        
        # Add bobbing animation
        import math
        bob_y = screen_y + math.sin(self.bob_offset) * 3
        
        # Draw glow effect
        glow_surface = pygame.Surface((self.size + 10, self.size + 10), pygame.SRCALPHA)
        glow_color = (*self.color, 64)
        pygame.draw.circle(glow_surface, glow_color, 
                         (self.size // 2 + 5, self.size // 2 + 5), 
                         self.size // 2 + 5)
        screen.blit(glow_surface, (int(screen_x - 5), int(bob_y - 5)))
        
        # Draw item based on type
        if self.item_type == ItemType.POTION:
            self._draw_potion(screen, int(screen_x), int(bob_y))
        elif self.item_type == ItemType.SCROLL:
            self._draw_scroll(screen, int(screen_x), int(bob_y))
        elif self.item_type == ItemType.KEY:
            self._draw_key(screen, int(screen_x), int(bob_y))
        else:
            # Fallback: simple colored circle
            pygame.draw.circle(screen, self.color, 
                             (int(screen_x + self.size // 2), int(bob_y + self.size // 2)), 
                             self.size // 2)
    
    def _draw_potion(self, screen, x, y):
        """Draw a health potion."""
        # Bottle body
        bottle_rect = pygame.Rect(x + 6, y + 8, self.size - 12, self.size - 16)
        pygame.draw.rect(screen, (200, 200, 200), bottle_rect, border_radius=3)
        
        # Liquid inside
        liquid_rect = pygame.Rect(x + 8, y + 10, self.size - 16, self.size - 20)
        pygame.draw.rect(screen, self.color, liquid_rect, border_radius=2)
        
        # Cork/cap
        cap_rect = pygame.Rect(x + 8, y + 4, self.size - 16, 6)
        pygame.draw.rect(screen, (139, 69, 19), cap_rect, border_radius=2)
    
    def _draw_scroll(self, screen, x, y):
        """Draw a magic scroll."""
        # Scroll body
        scroll_rect = pygame.Rect(x + 4, y + 6, self.size - 8, self.size - 12)
        pygame.draw.rect(screen, (245, 245, 220), scroll_rect, border_radius=2)
        
        # Scroll ends
        pygame.draw.circle(screen, (139, 69, 19), (x + 4, y + self.size // 2), 3)
        pygame.draw.circle(screen, (139, 69, 19), (x + self.size - 4, y + self.size // 2), 3)
        
        # Magic runes (simple lines)
        pygame.draw.line(screen, self.color, 
                        (x + 8, y + 10), (x + self.size - 8, y + 10), 2)
        pygame.draw.line(screen, self.color, 
                        (x + 8, y + 14), (x + self.size - 12, y + 14), 2)
        pygame.draw.line(screen, self.color, 
                        (x + 8, y + 18), (x + self.size - 8, y + 18), 2)
    
    def _draw_key(self, screen, x, y):
        """Draw a golden key."""
        # Key shaft
        shaft_rect = pygame.Rect(x + 4, y + self.size // 2 - 2, self.size - 12, 4)
        pygame.draw.rect(screen, self.color, shaft_rect, border_radius=1)
        
        # Key head (circular)
        pygame.draw.circle(screen, self.color, 
                         (x + self.size - 8, y + self.size // 2), 6)
        pygame.draw.circle(screen, (0, 0, 0), 
                         (x + self.size - 8, y + self.size // 2), 3)
        
        # Key teeth
        teeth_points = [
            (x + 6, y + self.size // 2 - 2),
            (x + 6, y + self.size // 2 - 6),
            (x + 10, y + self.size // 2 - 6),
            (x + 10, y + self.size // 2 - 4),
            (x + 14, y + self.size // 2 - 4),
            (x + 14, y + self.size // 2 + 2)
        ]
        pygame.draw.polygon(screen, self.color, teeth_points)
    
    def get_bounds(self):
        """
        Get the bounding rectangle for collision detection.
        
        Returns:
            pygame.Rect: The item's bounding rectangle
        """
        return pygame.Rect(self.pixel_x, self.pixel_y, self.size, self.size)
    
    def collect(self):
        """
        Mark the item as collected.
        """
        self.collected = True

class Inventory:
    """
    Inventory class for managing collected items.
    """
    
    def __init__(self, max_slots=20):
        """
        Initialize the inventory with a maximum number of slots.
        
        Args:
            max_slots (int): Maximum number of items the inventory can hold
        """
        self.max_slots = max_slots
        self.items = []  # List of collected items
        self.item_counts = {}  # Dictionary to track item counts by type
        
        # Initialize item counts
        for item_type in [ItemType.POTION, ItemType.SCROLL, ItemType.KEY]:
            self.item_counts[item_type] = 0
    
    def add_item(self, item):
        """
        Add an item to the inventory.
        
        Args:
            item (Item): The item to add
            
        Returns:
            bool: True if item was added successfully, False if inventory is full
        """
        if len(self.items) >= self.max_slots:
            return False
        
        self.items.append(item)
        self.item_counts[item.item_type] += 1
        return True
    
    def remove_item(self, item_type, count=1):
        """
        Remove items of a specific type from the inventory.
        
        Args:
            item_type (int): The type of item to remove
            count (int): Number of items to remove
            
        Returns:
            int: Number of items actually removed
        """
        removed = 0
        items_to_remove = []
        
        for item in self.items:
            if item.item_type == item_type and removed < count:
                items_to_remove.append(item)
                removed += 1
        
        for item in items_to_remove:
            self.items.remove(item)
            self.item_counts[item_type] -= 1
        
        return removed
    
    def get_item_count(self, item_type):
        """
        Get the count of a specific item type in the inventory.
        
        Args:
            item_type (int): The type of item to count
            
        Returns:
            int: Number of items of the specified type
        """
        return self.item_counts.get(item_type, 0)
    
    def get_total_items(self):
        """
        Get the total number of items in the inventory.
        
        Returns:
            int: Total number of items
        """
        return len(self.items)
    
    def is_full(self):
        """
        Check if the inventory is full.
        
        Returns:
            bool: True if inventory is full, False otherwise
        """
        return len(self.items) >= self.max_slots
    
    def get_items_by_type(self, item_type):
        """
        Get all items of a specific type from the inventory.
        
        Args:
            item_type (int): The type of items to retrieve
            
        Returns:
            list: List of items of the specified type
        """
        return [item for item in self.items if item.item_type == item_type]
    
    def clear(self):
        """
        Clear all items from the inventory.
        """
        self.items.clear()
        for item_type in self.item_counts:
            self.item_counts[item_type] = 0
    
    def get_summary(self):
        """
        Get a summary of items in the inventory.
        
        Returns:
            dict: Dictionary with item types as keys and counts as values
        """
        return self.item_counts.copy()

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
        pygame.display.set_caption("Campus Lockdown - Dark Campus Edition")
        
        # Set up the game clock for consistent FPS
        self.clock = pygame.time.Clock()
        
        # Darkness overlay will be created dynamically in _create_flashlight_effect
        self.darkness_overlay = None
        
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
        
        # Flashlight state
        self.flashlight_enabled = False
        
        # Inventory system
        self.inventory = Inventory()
        
        # Items on the map
        self.items = []
        self._spawn_items()
        
        # Map transition system
        self.current_map_type = "campus"  # Track current map type
        self.campus_map = self.game_map  # Store reference to campus map
        self.interior_maps = {}  # Cache for interior maps
        
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
    
    def _spawn_items(self):
        """
        Spawn items randomly across walkable tiles on the map.
        """
        import random
        
        # Number of items to spawn
        num_potions = random.randint(8, 12)
        num_scrolls = random.randint(5, 8)
        num_keys = random.randint(3, 5)
        
        items_to_spawn = [
            (ItemType.POTION, num_potions),
            (ItemType.SCROLL, num_scrolls),
            (ItemType.KEY, num_keys)
        ]
        
        # Get all walkable positions
        walkable_positions = []
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                if self.game_map.is_walkable(x, y):
                    # Don't spawn items too close to player spawn point
                    spawn_x = self.game_map.spawn_point.get('x', 0)
                    spawn_y = self.game_map.spawn_point.get('y', 0)
                    distance = ((x - spawn_x) ** 2 + (y - spawn_y) ** 2) ** 0.5
                    if distance > 3:  # Minimum distance from spawn
                        walkable_positions.append((x, y))
        
        # Spawn items randomly
        for item_type, count in items_to_spawn:
            for _ in range(count):
                if walkable_positions:
                    pos = random.choice(walkable_positions)
                    walkable_positions.remove(pos)  # Don't spawn multiple items on same tile
                    item = Item(item_type, pos[0], pos[1])
                    self.items.append(item)
    
    def _check_item_collection(self):
        """
        Check if the player is colliding with any items and collect them.
        """
        player_grid_x, player_grid_y = self.player.get_grid_position()
        
        for item in self.items[:]:
            if not item.collected:
                # Check if player is on the same tile as the item
                if item.grid_x == player_grid_x and item.grid_y == player_grid_y:
                    # Collect the item
                    if self.inventory.add_item(item):
                        item.collect()
                        print(f"Collected {item.name}! ({self.inventory.get_item_count(item.item_type)} total)")
                    else:
                        print("Inventory is full!")
    
    def _check_door_transition(self):
        """
        Check if the player is on a door tile and handle map transitions.
        """
        player_grid_x, player_grid_y = self.player.get_grid_position()
        current_tile = self.game_map.get_tile(player_grid_x, player_grid_y)
        
        if current_tile:
            tile_type = current_tile.tile_type
            
            # Check for building-specific doors
            if tile_type == TileType.LIBRARY_DOOR:
                self._transition_to_interior("library")
            elif tile_type == TileType.CAFETERIA_DOOR:
                self._transition_to_interior("cafeteria")
            elif tile_type == TileType.DORMITORY_DOOR:
                self._transition_to_interior("dormitory")
            elif tile_type == TileType.PARKING_DOOR:
                self._transition_to_interior("parking")
            elif tile_type == TileType.DOOR and self.current_map_type != "campus":
                # Generic door in interior maps - return to campus
                self._transition_to_campus()
    
    def _transition_to_interior(self, building_type):
        """
        Transition from campus to an interior map.
        """
        if self.current_map_type == "campus":
            # Load interior map if not cached
            if building_type not in self.interior_maps:
                map_file = f"{building_type}_map.json"
                try:
                    self.interior_maps[building_type] = Map.from_json(map_file)
                    print(f"Loaded {building_type} interior map")
                except FileNotFoundError:
                    print(f"Warning: {map_file} not found")
                    return
            
            # Switch to interior map
            self.game_map = self.interior_maps[building_type]
            self.current_map_type = building_type
            self.player.set_map(self.game_map)
            
            # Position player at entrance (near a door)
            entrance_pos = self._find_entrance_position()
            if entrance_pos:
                self.player.x, self.player.y = self.game_map.grid_to_pixel(entrance_pos[0], entrance_pos[1])
            
            print(f"Entered {building_type}")
    
    def _transition_to_campus(self):
        """
        Transition from interior back to campus map.
        """
        if self.current_map_type != "campus":
            self.game_map = self.campus_map
            self.current_map_type = "campus"
            self.player.set_map(self.game_map)
            
            # Position player outside the building they just exited
            exit_pos = self._find_campus_exit_position()
            if exit_pos:
                self.player.x, self.player.y = self.game_map.grid_to_pixel(exit_pos[0], exit_pos[1])
            
            print("Returned to campus")
    
    def _find_entrance_position(self):
        """
        Find a suitable entrance position in interior maps (near a door).
        """
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                tile = self.game_map.get_tile(x, y)
                if tile and tile.tile_type == TileType.DOOR:
                    # Find adjacent walkable tile
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        adj_x, adj_y = x + dx, y + dy
                        if (0 <= adj_x < self.game_map.width and 
                            0 <= adj_y < self.game_map.height and
                            self.game_map.is_walkable(adj_x, adj_y)):
                            return (adj_x, adj_y)
        
        # Fallback to any walkable position
        return self._find_valid_start_position()
    
    def _find_campus_exit_position(self):
        """
        Find a position on campus near the building the player just exited.
        """
        # For now, just return a safe walkable position
        # In a more complex implementation, this could track which door was used
        return self._find_valid_start_position()
    
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
                elif event.key == pygame.K_f:
                    # Toggle flashlight on/off
                    self.flashlight_enabled = not self.flashlight_enabled
                    print(f"Flashlight {'ON' if self.flashlight_enabled else 'OFF'}")
    
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
        
        # Update items (animations)
        for item in self.items:
            item.update(dt)
        
        # Check for item collection
        self._check_item_collection()
        
        # Check for door transitions
        self._check_door_transition()
        
        self.handle_input()
    
    def draw(self):
        """
        Draw all game objects to the screen with camera system and dark environment effect.
        """
        # Fill the screen with background color
        self.screen.fill(self.bg_color)
        
        # Draw the map tiles with camera
        self.game_map.draw_with_camera(self.screen, self.camera)
        
        # Draw the player with camera
        self.player.draw(self.screen, self.camera)
        
        # Draw items with camera
        for item in self.items:
            item.draw(self.screen, self.camera)
        
        # Create and apply the flashlight effect
        self._create_flashlight_effect()
        if self.darkness_overlay:
            self.screen.blit(self.darkness_overlay, (0, 0))
        
        # Draw UI elements on top of darkness
        self._draw_ui()
        
        # Update the display
        pygame.display.flip()
    
    def _create_flashlight_effect(self):
        """
        Create a flashlight effect by clearing a circular area around the player on the darkness overlay.
        Uses different radius based on flashlight state.
        """
        # Calculate player's screen position
        player_screen_x = self.player.x - self.camera.x + TILE_SIZE // 2
        player_screen_y = self.player.y - self.camera.y + TILE_SIZE // 2
        
        # Create a new darkness overlay surface with per-pixel alpha
        self.darkness_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.darkness_overlay.fill((0, 0, 0, DARKNESS_ALPHA))  # Fill with semi-transparent black
        
        # Create the visibility circle by drawing transparent pixels
        center_x = int(player_screen_x)
        center_y = int(player_screen_y)
        
        # Choose radius based on flashlight state
        current_radius = FLASHLIGHT_RADIUS if self.flashlight_enabled else VISIBILITY_RADIUS
        
        # Draw the main visibility circle (fully transparent)
        for x in range(max(0, center_x - current_radius), min(WIDTH, center_x + current_radius + 1)):
            for y in range(max(0, center_y - current_radius), min(HEIGHT, center_y + current_radius + 1)):
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                if distance <= current_radius:
                    # Create gradient effect
                    if distance <= current_radius * 0.7:
                        # Inner circle - fully visible
                        alpha = 0
                    else:
                        # Outer ring - gradient fade
                        fade_factor = (distance - current_radius * 0.7) / (current_radius * 0.3)
                        alpha = int(DARKNESS_ALPHA * fade_factor)
                    
                    self.darkness_overlay.set_at((x, y), (0, 0, 0, alpha))
    
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
        
        # Flashlight status indicator
        flashlight_status = f"Flashlight: {'ON' if self.flashlight_enabled else 'OFF'} (Press F to toggle)"
        flashlight_color = YELLOW if self.flashlight_enabled else WHITE
        flashlight_surface = font.render(flashlight_status, True, flashlight_color)
        self.screen.blit(flashlight_surface, (10, 135))
        
        # Controls reminder
        controls_text = "Use WASD or Arrow Keys to explore | Press F to toggle flashlight"
        controls_surface = font.render(controls_text, True, WHITE)
        self.screen.blit(controls_surface, (10, HEIGHT - 30))
        
        # Draw inventory UI panel
        self._draw_inventory_ui()
    
    def _draw_inventory_ui(self):
        """
        Draw the inventory UI panel showing collected items.
        """
        # Inventory panel dimensions and position
        panel_width = 250
        panel_height = 150
        panel_x = WIDTH - panel_width - 10
        panel_y = 10
        
        # Draw inventory panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        pygame.draw.rect(panel_surface, WHITE, (0, 0, panel_width, panel_height), 2)
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw inventory title
        font = pygame.font.Font(None, 24)
        title_surface = font.render("Inventory", True, WHITE)
        self.screen.blit(title_surface, (panel_x + 10, panel_y + 10))
        
        # Draw inventory stats
        stats_text = f"{self.inventory.get_total_items()}/{self.inventory.max_slots} items"
        stats_surface = font.render(stats_text, True, YELLOW)
        self.screen.blit(stats_surface, (panel_x + panel_width - 80, panel_y + 10))
        
        # Draw item counts with icons
        item_font = pygame.font.Font(None, 20)
        y_offset = 40
        
        for item_type in [ItemType.POTION, ItemType.SCROLL, ItemType.KEY]:
            count = self.inventory.get_item_count(item_type)
            name = ItemType.NAMES[item_type]
            color = ItemType.COLORS[item_type]
            
            # Draw item icon (small version)
            icon_size = 20
            icon_x = panel_x + 15
            icon_y = panel_y + y_offset
            
            if item_type == ItemType.POTION:
                # Small potion icon
                pygame.draw.rect(self.screen, (200, 200, 200), 
                               (icon_x + 3, icon_y + 4, icon_size - 6, icon_size - 8), border_radius=2)
                pygame.draw.rect(self.screen, color, 
                               (icon_x + 4, icon_y + 5, icon_size - 8, icon_size - 10), border_radius=1)
                pygame.draw.rect(self.screen, (139, 69, 19), 
                               (icon_x + 4, icon_y + 2, icon_size - 8, 3), border_radius=1)
            
            elif item_type == ItemType.SCROLL:
                # Small scroll icon
                pygame.draw.rect(self.screen, (245, 245, 220), 
                               (icon_x + 2, icon_y + 3, icon_size - 4, icon_size - 6), border_radius=1)
                pygame.draw.circle(self.screen, (139, 69, 19), (icon_x + 2, icon_y + icon_size // 2), 2)
                pygame.draw.circle(self.screen, (139, 69, 19), (icon_x + icon_size - 2, icon_y + icon_size // 2), 2)
                pygame.draw.line(self.screen, color, 
                               (icon_x + 4, icon_y + 6), (icon_x + icon_size - 4, icon_y + 6), 1)
                pygame.draw.line(self.screen, color, 
                               (icon_x + 4, icon_y + 9), (icon_x + icon_size - 6, icon_y + 9), 1)
            
            elif item_type == ItemType.KEY:
                # Small key icon
                pygame.draw.rect(self.screen, color, 
                               (icon_x + 2, icon_y + icon_size // 2 - 1, icon_size - 6, 2), border_radius=1)
                pygame.draw.circle(self.screen, color, 
                               (icon_x + icon_size - 4, icon_y + icon_size // 2), 3)
                pygame.draw.circle(self.screen, (0, 0, 0), 
                               (icon_x + icon_size - 4, icon_y + icon_size // 2), 1)
                # Key teeth
                pygame.draw.rect(self.screen, color, (icon_x + 3, icon_y + icon_size // 2 - 3, 2, 3))
                pygame.draw.rect(self.screen, color, (icon_x + 6, icon_y + icon_size // 2 - 2, 2, 2))
            
            # Draw item count and name
            count_text = f"{count}x {name}"
            text_color = WHITE if count > 0 else (128, 128, 128)
            count_surface = item_font.render(count_text, True, text_color)
            self.screen.blit(count_surface, (icon_x + icon_size + 10, icon_y + 2))
            
            y_offset += 25
        
        # Draw inventory instructions
        if self.inventory.get_total_items() == 0:
            instruction_text = "Walk over items to collect them"
            instruction_surface = item_font.render(instruction_text, True, (128, 128, 128))
            text_rect = instruction_surface.get_rect()
            text_x = panel_x + (panel_width - text_rect.width) // 2
            self.screen.blit(instruction_surface, (text_x, panel_y + panel_height - 30))
    
    def run(self):
        """
        Main game loop that runs until the game is quit.
        """
        print("Starting Campus Lockdown...")
        print("Controls:")
        print("  Arrow Keys or WASD: Move player around campus")
        print("  F: Toggle flashlight on/off")
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