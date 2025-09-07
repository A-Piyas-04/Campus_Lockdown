import json
import os
import pygame
import time
from .tiles import TileType, Tile, TILE_SIZE

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
    
    def get_tile(self, x, y):
        """
        Get the tile at the specified grid coordinates.
        
        Args:
            x (int): Grid x coordinate
            y (int): Grid y coordinate
            
        Returns:
            Tile: The tile at the specified position, or None if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
    
    def is_walkable(self, x, y):
        """
        Check if the tile at the specified grid coordinates is walkable.
        
        Args:
            x (int): Grid x coordinate
            y (int): Grid y coordinate
            
        Returns:
            bool: True if the tile is walkable, False otherwise
        """
        tile = self.get_tile(x, y)
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
    
    def draw(self, screen, camera):
        """
        Draw the visible portion of the map without grid borders for cleaner appearance.
        
        Args:
            screen: Pygame screen surface
            camera: Camera object for viewport calculations
        """
        # Calculate visible tile range
        start_x = max(0, int(camera.x // TILE_SIZE))
        start_y = max(0, int(camera.y // TILE_SIZE))
        end_x = min(self.width, int((camera.x + camera.width) // TILE_SIZE) + 1)
        end_y = min(self.height, int((camera.y + camera.height) // TILE_SIZE) + 1)
        
        # Draw tiles without borders for cleaner look
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                
                # Calculate screen position
                screen_x = x * TILE_SIZE - camera.x
                screen_y = y * TILE_SIZE - camera.y
                
                # Draw tile without border
                pygame.draw.rect(screen, tile.color, 
                               (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                
                # Add enhanced visual details based on tile type
                if tile.tile_type == TileType.WATER:
                    # Animated water effect with multiple ripples
                    wave_offset = int(time.time() * 3) % 20
                    ripple_color = tuple(min(255, c + 20) for c in tile.color)
                    
                    # Draw multiple ripple lines
                    for i in range(0, TILE_SIZE, 8):
                        ripple_y = screen_y + (i + wave_offset) % TILE_SIZE
                        if screen_y <= ripple_y < screen_y + TILE_SIZE:
                            pygame.draw.line(screen, ripple_color, 
                                           (screen_x, ripple_y), 
                                           (screen_x + TILE_SIZE, ripple_y), 1)
                    
                    # Add some sparkle effects
                    sparkle_positions = [(10, 15), (30, 35), (20, 5), (40, 25)]
                    sparkle_color = (200, 230, 255)
                    for sx, sy in sparkle_positions:
                        if (wave_offset + sx + sy) % 40 < 10:
                            pygame.draw.circle(screen, sparkle_color, 
                                             (screen_x + sx, screen_y + sy), 1)
                
                elif tile.tile_type == TileType.TREE:
                    # Enhanced tree with trunk and leaves
                    trunk_color = (101, 67, 33)  # Brown trunk
                    leaf_color = tuple(min(255, c + 30) for c in tile.color)
                    
                    # Draw trunk
                    trunk_width = TILE_SIZE // 4
                    trunk_x = screen_x + (TILE_SIZE - trunk_width) // 2
                    trunk_y = screen_y + TILE_SIZE // 2
                    pygame.draw.rect(screen, trunk_color, 
                                   (trunk_x, trunk_y, trunk_width, TILE_SIZE // 2))
                    
                    # Draw leaves (multiple circles for fuller look)
                    leaf_radius = TILE_SIZE // 3
                    pygame.draw.circle(screen, leaf_color, 
                                     (screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 3), 
                                     leaf_radius)
                    pygame.draw.circle(screen, tile.color, 
                                     (screen_x + TILE_SIZE // 2 - 5, screen_y + TILE_SIZE // 3 - 5), 
                                     leaf_radius // 2)
                    pygame.draw.circle(screen, leaf_color, 
                                     (screen_x + TILE_SIZE // 2 + 5, screen_y + TILE_SIZE // 3 + 5), 
                                     leaf_radius // 2)
                
                elif tile.tile_type == TileType.WALL:
                    # Add subtle texture variation for visual interest without grid lines
                    texture_color = (min(255, tile.color[0] + 10), 
                                   min(255, tile.color[1] + 10), 
                                   min(255, tile.color[2] + 10))
                    
                    # Sparse texture pattern for walls
                    for i in range(2):
                        for j in range(2):
                            if (x + y + i + j) % 3 == 0:
                                texture_x = screen_x + i * (TILE_SIZE // 2) + (TILE_SIZE // 4)
                                texture_y = screen_y + j * (TILE_SIZE // 2) + (TILE_SIZE // 4)
                                darker_color = (max(0, tile.color[0] - 20), 
                                              max(0, tile.color[1] - 20), 
                                              max(0, tile.color[2] - 20))
                                pygame.draw.circle(screen, darker_color, (texture_x, texture_y), 2)
                
                # Add subtle texture variation for floor tiles without borders
                elif tile.tile_type != TileType.WALL:
                    # Add subtle texture dots for floor tiles
                    texture_color = (min(255, tile.color[0] + 10), 
                                   min(255, tile.color[1] + 10), 
                                   min(255, tile.color[2] + 10))
                    
                    # Sparse texture pattern
                    if (x + y) % 4 == 0:
                        pygame.draw.circle(screen, texture_color, 
                                         (screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 2), 1)