import pygame
import sys
from classes.game import Game

# Initialize Pygame
pygame.init()

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