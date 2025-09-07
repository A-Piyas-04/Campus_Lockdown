#!/usr/bin/env python3
"""
Tile system for Campus Lockdown game.

This module contains all tile-related classes and constants including
TileType definitions, colors, and the Tile class.
"""

import pygame

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
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """
        Draw the tile on the screen with camera offset.
        
        Args:
            screen: Pygame screen surface
            camera_x (int): Camera x offset
            camera_y (int): Camera y offset
        """
        # Calculate screen position with camera offset
        screen_x = self.pixel_x - camera_x
        screen_y = self.pixel_y - camera_y
        
        # Draw main tile
        pygame.draw.rect(screen, self.color, (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
        
        # Add accent/border for visual variety
        accent_color = TILE_ACCENT_COLORS.get(self.tile_type, self.color)
        if accent_color != self.color:
            pygame.draw.rect(screen, accent_color, (screen_x + 2, screen_y + 2, TILE_SIZE - 4, TILE_SIZE - 4), 2)
    
    def get_rect(self):
        """
        Get the pygame Rect for this tile.
        
        Returns:
            pygame.Rect: Rectangle representing the tile's position and size
        """
        return pygame.Rect(self.pixel_x, self.pixel_y, TILE_SIZE, TILE_SIZE)
    
    def is_walkable(self):
        """
        Check if this tile is walkable.
        
        Returns:
            bool: True if the tile is walkable, False otherwise
        """
        return self.walkable