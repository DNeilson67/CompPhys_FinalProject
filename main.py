import pygame
import sys
import time
from settings import Settings
from team import Team
from ui import UIButton, UISlider, UICheckbox

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tug of War Simulation")

# Fonts
font = pygame.font.SysFont(None, 36)

# Load images
background = pygame.transform.scale(pygame.image.load("assets/background.jpg"), (WIDTH, HEIGHT))
box_image = pygame.transform.scale(pygame.image.load("assets/box.png"), (100, 100))
box_rect = box_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Initial positions and forces
left_team = Team('left', [(100, 150 + i * 100) for i in range(4)], font, (255, 0, 0), (0, 255, 0))
right_team = Team('right', [(1100, 150 + i * 100) for i in range(4)], font, (0, 0, 255), (0, 255, 0))

left_sliders = [UISlider(145, 610 + i * 50, 100, 10) for i in range(4)]
right_sliders = [UISlider(1040, 610 + i * 50, 100, 10) for i in range(4)]

left_checkboxes = [UICheckbox(260, 605 + i * 50) for i in range(4)]
right_checkboxes = [UICheckbox(1000, 605 + i * 50) for i in range(4)]

friction = 0.1
velocity = 0
acceleration = 0
mass = 100
rope_pos = WIDTH // 2

# Button positions
start_button = UIButton(600, 650, 100, 50, 'Start', font)
restart_button = UIButton(600, 725, 100, 50, 'Restart', font)
stamina_button = UIButton(560, 575, 175, 50, 'Stamina: On', font)
settings_button = UIButton(750, HEIGHT - 75, 150, 50, 'Settings', font)

settings = Settings(WIDTH, HEIGHT, font)

start_time = None
timer_running = False
simulation_running = False
winner = None  # Variable to store the winner
stamina_enabled = True  # Variable to track the stamina state

dragging_slider = None

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def main():
    global dragging_slider, start_time, timer_running, simulation_running, velocity, acceleration, rope_pos, winner, stamina_enabled, net_force, mass, friction

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.blit(background, (0, 0))

        start_button.draw(screen)
        restart_button.draw(screen)
        stamina_button.draw(screen)
        settings_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for slider in left_sliders + right_sliders:
                        if slider.rect.collidepoint(event.pos):
                            dragging_slider = slider
                            break

                    for i, checkbox in enumerate(left_checkboxes + right_checkboxes):
                        if checkbox.rect.collidepoint(event.pos):
                            checkbox.toggle()
                            if i < len(left_checkboxes):
                                left_team.members[i]['enabled'] = checkbox.checked
                            else:
                                right_team.members[i - len(left_checkboxes)]['enabled'] = checkbox.checked

                    if start_button.rect.collidepoint(event.pos):
                        if not timer_running:
                            start_time = time.time()
                            timer_running = True
                            simulation_running = True
                            winner = None  # Reset the winner when starting a new game
                    if restart_button.rect.collidepoint(event.pos):
                        start_time = None
                        timer_running = False
                        simulation_running = False
                        velocity = 0
                        rope_pos = WIDTH // 2
                        winner = None  # Reset the winner on restart
                        left_team.reset()
                        right_team.reset()
                        for checkbox in left_checkboxes + right_checkboxes:
                            checkbox.checked = True
                    if stamina_button.rect.collidepoint(event.pos):
                        stamina_enabled = not stamina_enabled
                        stamina_button.text = f'Stamina: {"On" if stamina_enabled else "Off"}'
                    if settings_button.rect.collidepoint(event.pos):
                        settings.toggle()
                    if settings.open and settings.mass_slider.rect.collidepoint(event.pos):
                        dragging_slider = 'mass_slider'
                    if settings.open and settings.friction_slider.rect.collidepoint(event.pos):
                        dragging_slider = 'friction_slider'
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_slider = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging_slider:
                    if dragging_slider == 'mass_slider':
                        settings.update_mass_slider(event.pos)
                        mass = settings.mass
                    elif dragging_slider == 'friction_slider':
                        settings.update_friction_slider(event.pos)
                        friction = settings.friction
                    else:
                        dragging_slider.update(event.pos)
                        if dragging_slider in left_sliders:
                            index = left_sliders.index(dragging_slider)
                            left_team.members[index]['force'] = dragging_slider.value
                            left_team.members[index]['max_force'] = dragging_slider.value
                        else:
                            index = right_sliders.index(dragging_slider)
                            right_team.members[index]['force'] = dragging_slider.value
                            right_team.members[index]['max_force'] = dragging_slider.value

        left_team.draw(screen)
        right_team.draw(screen)

        for slider in left_sliders + right_sliders:
            slider.draw(screen)

        for checkbox in left_checkboxes + right_checkboxes:
            checkbox.draw(screen)

        # Draw the box representing the tug of war
        box_rect.centerx = rope_pos
        screen.blit(box_image, box_rect)

        total_force_left = left_team.calculate_effective_force(stamina_enabled)
        total_force_right = right_team.calculate_effective_force(stamina_enabled)
        net_force = total_force_right - total_force_left

        draw_text(f'Left Team Force: {total_force_left:.1f}', font, (255, 0, 0), screen, 10, 10)
        draw_text(f'Right Team Force: {total_force_right:.1f}', font, (0, 0, 255), screen, 10, 50)
        draw_text(f'Net Force: {net_force:.1f}', font, (0, 0, 0), screen, WIDTH//2-75, 10)

        # Draw bottom-left box
        pygame.draw.rect(screen, (200, 200, 200), (10, 570, 300, 210))
        draw_text('Left Team Controls', font, (0, 0, 0), screen, 20, 575)
        for i in range(4):
            draw_text(f'Player {i+1}', font, (0, 0, 0), screen, 25, 600 + i * 50)

        # Draw bottom-right box
        pygame.draw.rect(screen, (200, 200, 200), (950, 570, 300, 210))
        draw_text('Right Team Controls', font, (0, 0, 0), screen, 1000, 575)
        for i in range(4):
            draw_text(f'Player {i+1}', font, (0, 0, 0), screen, 1150, 600 + i * 50)

        if settings.open:
            settings.draw(screen)

        if simulation_running:
            left_team.update_stamina_and_force(stamina_enabled)
            right_team.update_stamina_and_force(stamina_enabled)
            acceleration = net_force / mass  # pixels per second squared
            velocity += acceleration
            velocity *= (1 - friction)
            rope_pos += velocity

            if rope_pos < 100:
                winner = 'Left'
                simulation_running = False
                timer_running = False
            elif rope_pos > WIDTH - 100:
                winner = 'Right'
                simulation_running = False
                timer_running = False

        # Display the winner if there is one
        if winner:
            draw_text(f'{winner} Team Wins!', font, (255, 0, 0) if winner == 'Right' else (0, 255, 0), screen, WIDTH // 2 - 100, HEIGHT // 2)

        draw_text(f'{abs(velocity):.2f} px/s - Speed', font, (0, 0, 0), screen, WIDTH - 275, 10)
        draw_text(f'{acceleration:.2f} px/s - Acceleration ', font, (0, 0, 0), screen, WIDTH - 275, 50)
        if timer_running:
            elapsed_time = time.time() - start_time
            draw_text(f'Time: {elapsed_time:.2f} s', font, (0, 0, 0), screen, WIDTH - 275, 90)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
