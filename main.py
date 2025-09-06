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

class Player:
    """
    Player class representing the controllable sprite character.
    """
    
    def __init__(self, x, y):
        """
        Initialize the player at the given position.
        
        Args:
            x (int): Initial x position
            y (int): Initial y position
        """
        self.x = float(x)  # Use float for smoother movement
        self.y = float(y)
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.color = BLUE
        
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
        Move the player by the given delta values with smooth movement.
        Ensures the player stays within screen boundaries.
        
        Args:
            dx (float): Change in x position (-1, 0, or 1)
            dy (float): Change in y position (-1, 0, or 1)
        """
        # Calculate new position with smooth movement
        new_x = self.x + (dx * self.speed)
        new_y = self.y + (dy * self.speed)
        
        # Keep player within screen boundaries
        self.x = max(0, min(new_x, WIDTH - self.size))
        self.y = max(0, min(new_y, HEIGHT - self.size))
    
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
    Main game class that manages the game state and loop.
    """
    
    def __init__(self):
        """
        Initialize the game with screen, clock, and player.
        """
        # Set up the display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Adventure Quest - Enhanced Edition")
        
        # Set up the game clock for consistent FPS
        self.clock = pygame.time.Clock()
        
        # Create player at center of screen (adjusted for new dimensions)
        player_x = (WIDTH - PLAYER_SIZE) // 2
        player_y = (HEIGHT - PLAYER_SIZE) // 2
        self.player = Player(player_x, player_y)
        
        # Game state
        self.running = True
        
        # Background color for better contrast
        self.bg_color = (20, 30, 40)  # Dark blue-gray background
    
    def handle_events(self):
        """
        Handle all pygame events including quit and key presses.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def handle_input(self):
        """
        Handle continuous key input for player movement.
        """
        keys = pygame.key.get_pressed()
        
        # Calculate movement deltas based on pressed keys
        dx = 0
        dy = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        
        # Move the player
        self.player.move(dx, dy)
    
    def update(self):
        """
        Update game state. Currently just handles input.
        This method can be extended for game logic updates.
        """
        self.handle_input()
    
    def draw(self):
        """
        Draw all game objects to the screen.
        """
        # Clear screen with dark background for better contrast
        self.screen.fill(self.bg_color)
        
        # Draw a subtle grid pattern for visual reference
        self._draw_grid()
        
        # Draw the player
        self.player.draw(self.screen)
        
        # Draw UI elements
        self._draw_ui()
        
        # Update the display
        pygame.display.flip()
    
    def _draw_grid(self):
        """
        Draw a subtle grid pattern on the background.
        """
        grid_size = 50
        grid_color = (30, 40, 50)  # Slightly lighter than background
        
        # Draw vertical lines
        for x in range(0, WIDTH, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, HEIGHT), 1)
        
        # Draw horizontal lines
        for y in range(0, HEIGHT, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (WIDTH, y), 1)
    
    def _draw_ui(self):
        """
        Draw UI elements like position indicator.
        """
        # Create font for UI text
        font = pygame.font.Font(None, 24)
        
        # Display player position
        pos_text = f"Position: ({int(self.player.x)}, {int(self.player.y)})"
        text_surface = font.render(pos_text, True, WHITE)
        self.screen.blit(text_surface, (10, 10))
        
        # Display controls reminder
        controls_text = "Arrow Keys/WASD: Move | ESC: Quit"
        controls_surface = font.render(controls_text, True, (200, 200, 200))
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