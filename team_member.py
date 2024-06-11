import pygame
from utils import draw_text

class TeamMember:
    def __init__(self, pos, force, team):
        self.pos = pos
        self.force = force
        self.selected = False
        self.team = team
        self.stamina = 100
        self.max_force = force
        self.enabled = True
        self.resting = False

    def draw(self, screen, font):
        color = (0, 255, 0) if self.team == 'left' else (255, 0, 0)
        pygame.draw.circle(screen, color, self.pos, 20)
        text_color = (0, 0, 0)
        draw_text(screen, font, str(int(self.force)), text_color, self.pos[0] - 10, self.pos[1] - 40)
        draw_text(screen, font, f'Stamina: {self.stamina:.1f}', text_color, self.pos[0] - 50, self.pos[1] + 30)
