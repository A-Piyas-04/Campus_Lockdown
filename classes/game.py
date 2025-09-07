import pygame
import sys
import os
from .tiles import TileType, TILE_SIZE
from .map import Map
from .player import Player
from .camera import Camera
from .items import ItemType, Item, Inventory

# Game constants
WIDTH = 1000
HEIGHT = 800
FPS = 60
PLAYER_SIZE = 40

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Lighting constants
DARKNESS_ALPHA = 200  # Darkness overlay transparency (0-255)
VISIBILITY_RADIUS = 1  # Base visibility radius around player
FLASHLIGHT_RADIUS = 130  # Extended radius when flashlight is on

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
        self.flashlight_radius = FLASHLIGHT_RADIUS
        self.flashlight_intensity = 0.8
        
        # Inventory system
        self.inventory = Inventory()
        
        # Items on the map
        self.items = []
        self._spawn_items()
        
        # Map transition system
        self.current_map_type = "campus"  # Track current map type
        self.campus_map = self.game_map  # Store reference to campus map
        self.interior_maps = {}  # Cache for interior maps
        self.last_building_entered = None  # Track which building player entered from
        
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
                self._transition_to_interior("parking_map")
            elif tile_type == TileType.DOOR and self.current_map_type != "campus":
                # Generic door in interior maps - return to campus
                self._transition_to_campus()
    
    def _transition_to_interior(self, building_type):
        """
        Transition from campus to an interior map.
        """
        if self.current_map_type == "campus":
            # Store current player position for exit positioning
            player_grid_x, player_grid_y = self.player.get_grid_position()
            self.last_building_entered = {
                'type': building_type,
                'campus_exit_pos': (player_grid_x, player_grid_y)
            }
            
            # Load interior map if not cached
            if building_type not in self.interior_maps:
                map_file = os.path.join("maps", f"{building_type}_map.json")
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
                # Update player's grid position to match new pixel position
                self.player.grid_x = entrance_pos[0]
                self.player.grid_y = entrance_pos[1]
                self.player.target_grid_x = entrance_pos[0]
                self.player.target_grid_y = entrance_pos[1]
            
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
                # Update player's grid position to match new pixel position
                self.player.grid_x = exit_pos[0]
                self.player.grid_y = exit_pos[1]
                self.player.target_grid_x = exit_pos[0]
                self.player.target_grid_y = exit_pos[1]
            
            print("Returned to campus")
    
    def _find_entrance_position(self):
        """
        Find a suitable entrance position in interior maps (use spawn point or near door).
        """
        # First, try to use the map's designated spawn point
        if hasattr(self.game_map, 'spawn_point') and self.game_map.spawn_point:
            spawn_x = self.game_map.spawn_point['x']
            spawn_y = self.game_map.spawn_point['y']
            if (0 <= spawn_x < self.game_map.width and 
                0 <= spawn_y < self.game_map.height and
                self.game_map.is_walkable(spawn_x, spawn_y)):
                return (spawn_x, spawn_y)
        
        # Fallback: Find position near a door
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
        
        # Final fallback to any walkable position
        return self._find_valid_start_position()
    
    def _find_campus_exit_position(self):
        """
        Find a position on campus near the building the player just exited.
        """
        # If we have stored the entrance position, use it
        if self.last_building_entered and 'campus_exit_pos' in self.last_building_entered:
            exit_x, exit_y = self.last_building_entered['campus_exit_pos']
            
            # Find a walkable position near the stored exit position
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                test_x, test_y = exit_x + dx, exit_y + dy
                if (0 <= test_x < self.campus_map.width and 
                    0 <= test_y < self.campus_map.height and
                    self.campus_map.is_walkable(test_x, test_y)):
                    return (test_x, test_y)
            
            # If the stored position itself is walkable, use it
            if (0 <= exit_x < self.campus_map.width and 
                0 <= exit_y < self.campus_map.height and
                self.campus_map.is_walkable(exit_x, exit_y)):
                return (exit_x, exit_y)
        
        # Fallback to campus spawn point or any walkable position
        if hasattr(self.campus_map, 'spawn_point') and self.campus_map.spawn_point:
            spawn_x = self.campus_map.spawn_point['x']
            spawn_y = self.campus_map.spawn_point['y']
            if (0 <= spawn_x < self.campus_map.width and 
                0 <= spawn_y < self.campus_map.height and
                self.campus_map.is_walkable(spawn_x, spawn_y)):
                return (spawn_x, spawn_y)
        
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
        self.game_map.draw(self.screen, self.camera)
        
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