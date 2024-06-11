import pygame
import time
from team_member import TeamMember
from slider import Slider
from checkbox import Checkbox
from utils import draw_text

class TugOfWar:
    def __init__(self, screen, font, background, box_image, box_rect, width, height):
        self.screen = screen
        self.font = font
        self.background = background
        self.box_image = box_image
        self.box_rect = box_rect
        self.width = width
        self.height = height

        self.left_team = [TeamMember([100, 150 + i * 100], 50, 'left') for i in range(4)]
        self.right_team = [TeamMember([1100, 150 + i * 100], 50, 'right') for i in range(4)]
        self.left_sliders = [Slider((50, 130 + i * 100, 100, 10), 50) for i in range(4)]
        self.right_sliders = [Slider((1050, 130 + i * 100, 100, 10), 50) for i in range(4)]
        self.left_checkboxes = [Checkbox((160, 130 + i * 100, 20, 20)) for i in range(4)]
        self.right_checkboxes = [Checkbox((1020, 130 + i * 100, 20, 20)) for i in range(4)]
        self.friction = 0.1
        self.velocity = 0
        self.acceleration = 0
        self.rope_pos = width // 2

        self.start_button = pygame.Rect(550, 700, 100, 50)
        self.restart_button = pygame.Rect(670, 700, 100, 50)
        self.stamina_button = pygame.Rect(900, 700, 200, 50)

        self.dragging_slider = None
        self.start_time = None
        self.timer_running = False
        self.simulation_running = False
        self.winner = None
        self.stamina_enabled = True

    def draw(self):
        for member in self.left_team + self.right_team:
            member.draw(self.screen, self.font)
        for slider in self.left_sliders + self.right_sliders:
            slider.draw(self.screen)
        for checkbox in self.left_checkboxes + self.right_checkboxes:
            checkbox.draw(self.screen)

        self.box_rect.centerx = self.rope_pos
        self.screen.blit(self.box_image, self.box_rect)

        pygame.draw.rect(self.screen, (200, 200, 200), self.start_button)
        draw_text(self.screen, self.font, 'Start', (0, 0, 0), self.start_button.x + 20, self.start_button.y + 10)
        pygame.draw.rect(self.screen, (200, 200, 200), self.restart_button)
        draw_text(self.screen, self.font, 'Restart', (0, 0, 0), self.restart_button.x + 10, self.restart_button.y + 10)
        pygame.draw.rect(self.screen, (200, 200, 200), self.stamina_button)
        draw_text(self.screen, self.font, f'Stamina: {"On" if self.stamina_enabled else "Off"}', (0, 0, 0),
                  self.stamina_button.x + 20, self.stamina_button.y + 10)

        total_force_left = self.calculate_effective_force(self.left_team)
        total_force_right = self.calculate_effective_force(self.right_team)
        net_force = total_force_right - total_force_left

        draw_text(self.screen, self.font, f'Left Team Force: {total_force_left:.1f}', (0, 0, 0), 10, 10)
        draw_text(self.screen, self.font, f'Right Team Force: {total_force_right:.1f}', (0, 0, 0), 10, 50)
        draw_text(self.screen, self.font, f'Net Force: {net_force:.1f}', (0, 0, 0), 10, 90)

        if self.simulation_running:
            self.update_stamina_and_force()
            self.acceleration = net_force / 100.0
            self.velocity += self.acceleration
            self.velocity *= (1 - self.friction)
            self.rope_pos += self.velocity

            if self.rope_pos < 100:
                self.winner = 'Left'
                self.simulation_running = False
                self.timer_running = False
            elif self.rope_pos > self.width - 100:
                self.winner = 'Right'
                self.simulation_running = False
                self.timer_running = False

        if self.winner:
            color = (0, 255, 0) if self.winner == 'Left' else (255, 0, 0)
            draw_text(self.screen, self.font, f'{self.winner} Team Wins!', color, self.width // 2 - 100, self.height // 2)

        draw_text(self.screen, self.font, f'Speed: {abs(self.velocity):.2f} px/s', (0, 0, 0), 10, self.height - 110)
        draw_text(self.screen, self.font, f'Acceleration: {self.acceleration:.2f} px/s²', (0, 0, 0), 10, self.height - 80)
        if self.timer_running:
            elapsed_time = time.time() - self.start_time
            draw_text(self.screen, self.font, f'Time: {elapsed_time:.2f} s', (0, 0, 0), 10, self.height - 50)

    def handle_mouse_button_down(self, pos, button):
        if button == 1:
            for slider in self.left_sliders + self.right_sliders:
                if slider.rect.collidepoint(pos):
                    self.dragging_slider = slider
                    break
            for i, checkbox in enumerate(self.left_checkboxes + self.right_checkboxes):
                if checkbox.rect.collidepoint(pos):
                    checkbox.handle_event()
                    if i < len(self.left_checkboxes):
                        self.left_team[i].enabled = checkbox.checked
                    else:
                        self.right_team[i - len(self.left_checkboxes)].enabled = checkbox.checked
            if self.start_button.collidepoint(pos):
                if not self.timer_running:
                    self.start_time = time.time()
                    self.timer_running = True
                    self.simulation_running = True
                    self.winner = None
            if self.restart_button.collidepoint(pos):
                self.reset()
            if self.stamina_button.collidepoint(pos):
                self.stamina_enabled = not self.stamina_enabled

    def handle_mouse_button_up(self, button):
        if button == 1:
            self.dragging_slider = None

    def handle_mouse_motion(self, pos):
        if self.dragging_slider:
            self.dragging_slider.handle_event(pos)
            if self.dragging_slider in self.left_sliders:
                index = self.left_sliders.index(self.dragging_slider)
                self.left_team[index].force = self.dragging_slider.value
                self.left_team[index].max_force = self.dragging_slider.value
            else:
                index = self.right_sliders.index(self.dragging_slider)
                self.right_team[index].force = self.dragging_slider.value
                self.right_team[index].max_force = self.dragging_slider.value

    def calculate_effective_force(self, team):
        total_force = 0
        for member in team:
            if member.enabled:
                if self.stamina_enabled:
                    total_force += member.force * (member.stamina / 100.0)
                else:
                    total_force += member.force
        return total_force

    def update_stamina_and_force(self):
        if self.stamina_enabled:
            for member in self.left_team + self.right_team:
                if member.enabled:
                    if member.stamina > 0:
                        if not member.resting:
                            member.stamina -= member.force / 1000.0
                            if member.stamina < 20:
                                member.resting = True
                        else:
                            member.stamina += 0.5
                            if member.stamina > 80:
                                member.resting = False
                    else:
                        member.stamina = 0

                    if member.resting:
                        member.force = member.max_force / 2
                    else:
                        member.force = member.max_force

    def reset(self):
        self.start_time = None
        self.timer_running = False
        self.simulation_running = False
        self.velocity = 0
        self.rope_pos = self.width // 2
        self.winner = None
        for member in self.left_team + self.right_team:
            member.stamina = 100
            member.force = member.max_force
            member.enabled = True
            member.resting = False
        for checkbox in self.left_checkboxes + self.right_checkboxes:
            checkbox.checked = True
