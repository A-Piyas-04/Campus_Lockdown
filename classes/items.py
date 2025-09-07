import pygame
from .tiles import TILE_SIZE

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
        
        # Cache the item surface for better performance
        self._surface_cache = None
    
    def update(self, dt):
        """
        Update item animation.
        
        Args:
            dt (float): Delta time in seconds
        """
        if not self.collected:
            # Bobbing animation
            self.bob_offset += self.bob_speed * dt
            
            # Glow animation
            import math
            self.glow_alpha = int(128 + 64 * math.sin(self.bob_offset * 2))
    
    def _create_item_surface(self):
        """
        Create an advanced surface for the item based on its type.
        
        Returns:
            pygame.Surface: The item surface
        """
        surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        center = self.size // 2
        
        if self.item_type == ItemType.POTION:
            # Advanced health potion with glass effect
            # Shadow
            pygame.draw.ellipse(surface, (0, 0, 0, 60), (center-10, center+8, 20, 6))
            
            # Bottle base (glass)
            pygame.draw.rect(surface, (200, 230, 255), (center-8, center-2, 16, 12), border_radius=3)
            pygame.draw.rect(surface, (150, 200, 255), (center-8, center-2, 16, 12), border_radius=3, width=1)
            
            # Health liquid with bubbles
            pygame.draw.rect(surface, (220, 20, 60), (center-6, center, 12, 8), border_radius=2)
            pygame.draw.rect(surface, (255, 50, 100), (center-6, center, 12, 3), border_radius=2)  # liquid surface
            
            # Bubbles in liquid
            pygame.draw.circle(surface, (255, 100, 150), (center-3, center+3), 1)
            pygame.draw.circle(surface, (255, 100, 150), (center+2, center+5), 1)
            pygame.draw.circle(surface, (255, 150, 200), (center+1, center+2), 1)
            
            # Bottle neck
            pygame.draw.rect(surface, (200, 230, 255), (center-3, center-6, 6, 5), border_radius=1)
            pygame.draw.rect(surface, (150, 200, 255), (center-3, center-6, 6, 5), border_radius=1, width=1)
            
            # Cork with texture
            pygame.draw.rect(surface, (139, 69, 19), (center-4, center-9, 8, 4), border_radius=2)
            pygame.draw.rect(surface, (160, 82, 45), (center-4, center-9, 8, 1), border_radius=1)  # cork highlight
            
            # Glass shine effect
            pygame.draw.rect(surface, (255, 255, 255, 120), (center-7, center-1, 3, 8), border_radius=1)
            
            # Label
            pygame.draw.rect(surface, (255, 255, 255, 180), (center-5, center+1, 10, 4), border_radius=1)
            pygame.draw.line(surface, (200, 20, 60), (center-3, center+2), (center+3, center+2), 1)
            pygame.draw.line(surface, (200, 20, 60), (center-3, center+4), (center+3, center+4), 1)
            
        elif self.item_type == ItemType.SCROLL:
            # Advanced mystical scroll with magical effects
            # Shadow
            pygame.draw.ellipse(surface, (0, 0, 0, 60), (center-12, center+8, 24, 6))
            
            # Scroll parchment with aged texture
            pygame.draw.rect(surface, (245, 222, 179), (center-10, center-6, 20, 12), border_radius=2)
            pygame.draw.rect(surface, (210, 180, 140), (center-10, center-6, 20, 12), border_radius=2, width=1)
            
            # Aged spots and texture
            pygame.draw.circle(surface, (200, 170, 130), (center-6, center-3), 1)
            pygame.draw.circle(surface, (200, 170, 130), (center+4, center+2), 1)
            pygame.draw.circle(surface, (220, 190, 150), (center-2, center+3), 1)
            
            # Wooden rods with detail
            pygame.draw.rect(surface, (101, 67, 33), (center-12, center-2, 4, 4), border_radius=2)
            pygame.draw.rect(surface, (139, 69, 19), (center-12, center-2, 4, 1), border_radius=1)  # highlight
            pygame.draw.rect(surface, (101, 67, 33), (center+8, center-2, 4, 4), border_radius=2)
            pygame.draw.rect(surface, (139, 69, 19), (center+8, center-2, 4, 1), border_radius=1)  # highlight
            
            # Mystical text with glow
            # Glowing runes
            pygame.draw.line(surface, (138, 43, 226), (center-8, center-4), (center+8, center-4), 1)
            pygame.draw.line(surface, (75, 0, 130), (center-8, center-1), (center+8, center-1), 1)
            pygame.draw.line(surface, (138, 43, 226), (center-8, center+2), (center+8, center+2), 1)
            
            # Magical symbols
            pygame.draw.circle(surface, (186, 85, 211), (center-6, center-3), 1)
            pygame.draw.circle(surface, (186, 85, 211), (center, center), 1)
            pygame.draw.circle(surface, (186, 85, 211), (center+6, center+3), 1)
            
            # Magical sparkles around scroll
            pygame.draw.circle(surface, (255, 215, 0), (center-12, center-8), 1)
            pygame.draw.circle(surface, (255, 215, 0), (center+12, center-4), 1)
            pygame.draw.circle(surface, (255, 215, 0), (center+8, center+8), 1)
            pygame.draw.circle(surface, (255, 215, 0), (center-8, center+6), 1)
            
        elif self.item_type == ItemType.KEY:
            # Advanced ornate golden key
            # Shadow
            pygame.draw.ellipse(surface, (0, 0, 0, 60), (center-8, center+8, 16, 4))
            
            # Key shaft with engravings
            pygame.draw.rect(surface, (255, 215, 0), (center-2, center-6, 4, 14), border_radius=1)
            pygame.draw.rect(surface, (255, 255, 0), (center-1, center-6, 2, 14), border_radius=1)  # highlight
            
            # Decorative engravings on shaft
            for i in range(3):
                y_pos = center - 4 + i * 3
                pygame.draw.rect(surface, (218, 165, 32), (center-2, y_pos, 4, 1))
            
            # Ornate key head with detailed design
            pygame.draw.circle(surface, (255, 215, 0), (center, center-4), 6)
            pygame.draw.circle(surface, (255, 255, 0), (center, center-4), 4)  # inner circle
            pygame.draw.circle(surface, (218, 165, 32), (center, center-4), 2)  # center detail
            
            # Decorative elements on key head
            pygame.draw.circle(surface, (255, 255, 0), (center-3, center-6), 1)
            pygame.draw.circle(surface, (255, 255, 0), (center+3, center-6), 1)
            pygame.draw.circle(surface, (255, 255, 0), (center-3, center-2), 1)
            pygame.draw.circle(surface, (255, 255, 0), (center+3, center-2), 1)
            
            # Key teeth with intricate design
            pygame.draw.rect(surface, (255, 215, 0), (center, center+4, 8, 2), border_radius=1)
            pygame.draw.rect(surface, (255, 215, 0), (center, center+7, 6, 2), border_radius=1)
            pygame.draw.rect(surface, (255, 215, 0), (center+2, center+6, 2, 1))
            
            # Golden shine effect
            pygame.draw.circle(surface, (255, 255, 255, 150), (center-2, center-6), 2)
            pygame.draw.rect(surface, (255, 255, 255, 120), (center-1, center-2, 1, 6))
            
            # Magical glow around key
            pygame.draw.circle(surface, (255, 215, 0, 50), (center, center), 12)
        
        return surface
    
    def draw(self, screen, camera):
        """
        Draw the item on the screen.
        
        Args:
            screen (pygame.Surface): The screen to draw on
            camera (Camera): Camera object for viewport calculations
        """
        if self.collected:
            return
        
        import math
        
        # Calculate screen position with camera offset
        screen_x = self.pixel_x - camera.x
        screen_y = self.pixel_y - camera.y + math.sin(self.bob_offset) * 3
        
        # Only draw if visible on screen
        if (-self.size <= screen_x <= screen.get_width() + self.size and
            -self.size <= screen_y <= screen.get_height() + self.size):
            
            # Draw glow effect
            glow_surface = pygame.Surface((self.size + 10, self.size + 10), pygame.SRCALPHA)
            glow_color = (*self.color, self.glow_alpha // 3)
            pygame.draw.circle(glow_surface, glow_color, 
                             (self.size // 2 + 5, self.size // 2 + 5), self.size // 2 + 5)
            screen.blit(glow_surface, (screen_x - 5, screen_y - 5))
            
            # Draw detailed item surface
            item_surface = self._create_item_surface()
            screen.blit(item_surface, (int(screen_x), int(screen_y)))
    
    def collect(self):
        """
        Mark the item as collected.
        """
        self.collected = True
    
    def get_rect(self):
        """
        Get the collision rectangle for the item.
        
        Returns:
            pygame.Rect: The item's collision rectangle
        """
        return pygame.Rect(self.pixel_x, self.pixel_y, self.size, self.size)

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