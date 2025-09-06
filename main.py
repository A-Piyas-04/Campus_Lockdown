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
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors (RGB values)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Player constants
PLAYER_SIZE = 50
PLAYER_SPEED = 5

class Player:
    """
    Player class representing the controllable square character.
    """
    
    def __init__(self, x, y):
        """
        Initialize the player at the given position.
        
        Args:
            x (int): Initial x position
            y (int): Initial y position
        """
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.color = BLUE
    
    def move(self, dx, dy):
        """
        Move the player by the given delta values.
        Ensures the player stays within screen boundaries.
        
        Args:
            dx (int): Change in x position
            dy (int): Change in y position
        """
        # Update position
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # Keep player within screen boundaries
        self.x = max(0, min(self.x, WIDTH - self.size))
        self.y = max(0, min(self.y, HEIGHT - self.size))
    
    def draw(self, screen):
        """
        Draw the player on the screen.
        
        Args:
            screen: Pygame screen surface to draw on
        """
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

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
        pygame.display.set_caption("Adventure Quest")
        
        # Set up the game clock for consistent FPS
        self.clock = pygame.time.Clock()
        
        # Create player at center of screen
        player_x = (WIDTH - PLAYER_SIZE) // 2
        player_y = (HEIGHT - PLAYER_SIZE) // 2
        self.player = Player(player_x, player_y)
        
        # Game state
        self.running = True
    
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
        # Clear screen with black background
        self.screen.fill(BLACK)
        
        # Draw the player
        self.player.draw(self.screen)
        
        # Update the display
        pygame.display.flip()
    
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