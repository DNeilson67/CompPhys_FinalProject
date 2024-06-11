import pygame

class Slider:
    def __init__(self, rect, value):
        self.rect = pygame.Rect(rect)
        self.value = value

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255), self.rect)
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x + self.value, self.rect.y - 5, 10, 20))

    def handle_event(self, pos):
        self.value = max(0, min(100, pos[0] - self.rect.x))
