#!/usr/bin/env python3
"""
Adventure Quest - A simple Pygame-based game

This is the main game file that sets up the game window, handles events,
and manages the game loop with a movable player square.
"""

import pygame
import sys

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

# Tile colors
TILE_COLORS = {
    TileType.EMPTY: (40, 40, 40),      # Dark gray
    TileType.GRASS: (34, 139, 34),     # Forest green
    TileType.WATER: (30, 144, 255),    # Dodger blue
    TileType.WALL: (139, 69, 19),      # Saddle brown
    TileType.TREE: (0, 100, 0),        # Dark green
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
    Main game class that manages the game state and loop with tile-based map system.
    """
    
    def __init__(self):
        """
        Initialize the game with screen, clock, map, and player.
        """
        # Set up the display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Adventure Quest - Tile-Based Edition")
        
        # Set up the game clock for consistent FPS
        self.clock = pygame.time.Clock()
        
        # Create sample map (20x16 tiles to fit 1000x800 screen)
        self.game_map = self._create_sample_map()
        
        # Create player at a valid starting position
        start_x, start_y = self._find_valid_start_position()
        self.player = Player(start_x, start_y, self.game_map)
        
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
        Update game state and player animation.
        """
        # Calculate delta time in seconds
        dt = self.clock.get_time() / 1000.0
        
        # Update player animation
        self.player.update(dt)
        
        self.handle_input()
    
    def draw(self):
        """
        Draw all game objects to the screen.
        """
        # Fill the screen with background color
        self.screen.fill(self.bg_color)
        
        # Draw the map tiles
        self.game_map.draw(self.screen)
        
        # Draw the player
        self.player.draw(self.screen)
        
        # Draw UI elements
        self._draw_ui()
        
        # Update the display
        pygame.display.flip()
    
    def _draw_ui(self):
        """
        Draw UI elements like position indicator and controls.
        """
        font = pygame.font.Font(None, 24)
        
        # Player position indicator (both pixel and grid coordinates)
        pixel_pos = f"Pixel: ({int(self.player.x)}, {int(self.player.y)})"
        grid_pos = self.player.get_grid_position()
        grid_text = f"Grid: ({grid_pos[0]}, {grid_pos[1]})"
        
        pixel_surface = font.render(pixel_pos, True, WHITE)
        grid_surface = font.render(grid_text, True, WHITE)
        
        self.screen.blit(pixel_surface, (10, 10))
        self.screen.blit(grid_surface, (10, 35))
        
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
            self.screen.blit(tile_surface, (10, 60))
        
        # Controls reminder
        controls_text = "Use WASD or Arrow Keys to move (only on walkable tiles)"
        controls_surface = font.render(controls_text, True, WHITE)
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