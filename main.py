import pygame
import sys
import time
from tug_of_war import TugOfWar
from utils import draw_text

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tug of War Simulation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Load images
background = pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT))
box_image = pygame.transform.scale(pygame.image.load("box.png"), (100, 100))
box_rect = box_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Fonts
font = pygame.font.SysFont(None, 36)

def main():
    global box_rect

    clock = pygame.time.Clock()
    tug_of_war = TugOfWar(screen, font, background, box_image, box_rect, WIDTH, HEIGHT)
    running = True

    while running:
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                tug_of_war.handle_mouse_button_down(event.pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                tug_of_war.handle_mouse_button_up(event.button)
            elif event.type == pygame.MOUSEMOTION:
                tug_of_war.handle_mouse_motion(event.pos)

        tug_of_war.draw()
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
