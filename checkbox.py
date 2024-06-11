import pygame

class Checkbox:
    def __init__(self, rect, checked=True):
        self.rect = pygame.Rect(rect)
        self.checked = checked

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, (0, 0, 0), (self.rect.x, self.rect.y),
                             (self.rect.x + 20, self.rect.y + 20), 2)
            pygame.draw.line(screen, (0, 0, 0), (self.rect.x + 20, self.rect.y),
                             (self.rect.x, self.rect.y + 20), 2)

    def handle_event(self):
        self.checked = not self.checked
