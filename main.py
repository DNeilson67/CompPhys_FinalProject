import pygame
import sys
import time

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

# Fonts
font = pygame.font.SysFont(None, 36)

# Initial positions and forces
left_team = [
    {'pos': [100, 150 + i * 100], 'force': 50, 'selected': False, 'team': 'left', 'stamina': 100, 'max_force': 50,
     'enabled': True, 'resting': False} for i in range(4)]
right_team = [
    {'pos': [1100, 150 + i * 100], 'force': 50, 'selected': False, 'team': 'right', 'stamina': 100, 'max_force': 50,
     'enabled': True, 'resting': False} for i in range(4)]
left_sliders = [{'rect': pygame.Rect(50, 130 + i * 100, 100, 10), 'value': 50} for i in range(4)]
right_sliders = [{'rect': pygame.Rect(1050, 130 + i * 100, 100, 10), 'value': 50} for i in range(4)]
left_checkboxes = [{'rect': pygame.Rect(160, 130 + i * 100, 20, 20), 'checked': True} for i in range(4)]
right_checkboxes = [{'rect': pygame.Rect(1020, 130 + i * 100, 20, 20), 'checked': True} for i in range(4)]
friction = 0.1
velocity = 0
acceleration = 0
rope_pos = WIDTH // 2

# Button positions
start_button = pygame.Rect(550, 700, 100, 50)
restart_button = pygame.Rect(670, 700, 100, 50)

dragging_slider = None

start_time = None
timer_running = False
simulation_running = False


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def draw_teams():
    for member in left_team:
        pygame.draw.circle(screen, GREEN, member['pos'], 20)
        draw_text(str(int(member['force'])), font, BLACK, screen, member['pos'][0] - 10, member['pos'][1] - 40)
        draw_text(f'Stamina: {member["stamina"]:.1f}', font, BLACK, screen, member['pos'][0] - 50,
                  member['pos'][1] + 30)

    for member in right_team:
        pygame.draw.circle(screen, RED, member['pos'], 20)
        draw_text(str(int(member['force'])), font, BLACK, screen, member['pos'][0] - 10, member['pos'][1] - 40)
        draw_text(f'Stamina: {member["stamina"]:.1f}', font, BLACK, screen, member['pos'][0] - 50,
                  member['pos'][1] + 30)


def draw_sliders():
    for slider in left_sliders:
        pygame.draw.rect(screen, BLUE, slider['rect'])
        pygame.draw.rect(screen, GREEN, (slider['rect'].x + slider['value'], slider['rect'].y - 5, 10, 20))

    for slider in right_sliders:
        pygame.draw.rect(screen, BLUE, slider['rect'])
        pygame.draw.rect(screen, RED, (slider['rect'].x + slider['value'], slider['rect'].y - 5, 10, 20))


def draw_checkboxes():
    for checkbox in left_checkboxes:
        pygame.draw.rect(screen, BLACK, checkbox['rect'], 2)
        if checkbox['checked']:
            pygame.draw.line(screen, BLACK, (checkbox['rect'].x, checkbox['rect'].y),
                             (checkbox['rect'].x + 20, checkbox['rect'].y + 20), 2)
            pygame.draw.line(screen, BLACK, (checkbox['rect'].x + 20, checkbox['rect'].y),
                             (checkbox['rect'].x, checkbox['rect'].y + 20), 2)

    for checkbox in right_checkboxes:
        pygame.draw.rect(screen, BLACK, checkbox['rect'], 2)
        if checkbox['checked']:
            pygame.draw.line(screen, BLACK, (checkbox['rect'].x, checkbox['rect'].y),
                             (checkbox['rect'].x + 20, checkbox['rect'].y + 20), 2)
            pygame.draw.line(screen, BLACK, (checkbox['rect'].x + 20, checkbox['rect'].y),
                             (checkbox['rect'].x, checkbox['rect'].y + 20), 2)


def calculate_effective_force(team):
    total_force = 0
    for member in team:
        if member['enabled']:
            total_force += member['force'] * (member['stamina'] / 100.0)
    return total_force


def update_stamina_and_force():
    for member in left_team + right_team:
        if member['enabled']:
            if member['stamina'] > 0:
                if not member['resting']:
                    member['stamina'] -= member['force'] / 1000.0
                    if member['stamina'] < 20:  # Threshold for resting
                        member['resting'] = True
                else:
                    member['stamina'] += 0.5  # Regain stamina faster when resting
                    if member['stamina'] > 80:  # Threshold to stop resting
                        member['resting'] = False
            else:
                member['stamina'] = 0

            # Adjust force based on stamina and resting state
            if member['resting']:
                member['force'] = member['max_force'] / 2
            else:
                member['force'] = member['max_force']


def main():
    global dragging_slider, start_time, timer_running, simulation_running, velocity, acceleration, rope_pos

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for slider in left_sliders + right_sliders:
                        if slider['rect'].collidepoint(event.pos):
                            dragging_slider = slider
                            break
                    for i, checkbox in enumerate(left_checkboxes + right_checkboxes):
                        if checkbox['rect'].collidepoint(event.pos):
                            checkbox['checked'] = not checkbox['checked']
                            if i < len(left_checkboxes):
                                left_team[i]['enabled'] = checkbox['checked']
                            else:
                                right_team[i - len(left_checkboxes)]['enabled'] = checkbox['checked']
                    if start_button.collidepoint(event.pos):
                        if not timer_running:
                            start_time = time.time()
                            timer_running = True
                            simulation_running = True
                    if restart_button.collidepoint(event.pos):
                        start_time = None
                        timer_running = False
                        simulation_running = False
                        velocity = 0
                        rope_pos = WIDTH // 2
                        for member in left_team + right_team:
                            member['stamina'] = 100
                            member['force'] = member['max_force']
                            member['enabled'] = True
                            member['resting'] = False
                            for checkbox in left_checkboxes + right_checkboxes:
                                checkbox['checked'] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_slider = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging_slider:
                    dragging_slider['value'] = max(0, min(100, event.pos[0] - dragging_slider['rect'].x))
                    if dragging_slider in left_sliders:
                        index = left_sliders.index(dragging_slider)
                        left_team[index]['force'] = dragging_slider['value']
                        left_team[index]['max_force'] = dragging_slider['value']
                    else:
                        index = right_sliders.index(dragging_slider)
                        right_team[index]['force'] = dragging_slider['value']
                        right_team[index]['max_force'] = dragging_slider['value']

        draw_teams()
        draw_sliders()
        draw_checkboxes()

        # Draw rope
        pygame.draw.line(screen, BLACK, (rope_pos - 50, HEIGHT // 2), (rope_pos + 50, HEIGHT // 2), 5)

        pygame.draw.rect(screen, GRAY, start_button)
        draw_text('Start', font, BLACK, screen, start_button.x + 20, start_button.y + 10)
        pygame.draw.rect(screen, GRAY, restart_button)
        draw_text('Restart', font, BLACK, screen, restart_button.x + 10, restart_button.y + 10)

        total_force_left = calculate_effective_force(left_team)
        total_force_right = calculate_effective_force(right_team)
        net_force = total_force_right - total_force_left

        draw_text(f'Left Team Force: {total_force_left:.1f}', font, BLACK, screen, 10, 10)
        draw_text(f'Right Team Force: {total_force_right:.1f}', font, BLACK, screen, 10, 50)
        draw_text(f'Net Force: {net_force:.1f}', font, BLACK, screen, 10, 90)

        if simulation_running:
            update_stamina_and_force()
            acceleration = net_force / 100.0  # pixels per second squared
            velocity += acceleration
            velocity *= (1 - friction)
            rope_pos += velocity

            if rope_pos < 100:
                draw_text('Right Team Wins!', font, RED, screen, WIDTH // 2 - 100, HEIGHT // 2)
                simulation_running = False
                timer_running = False
            elif rope_pos > WIDTH - 100:
                draw_text('Left Team Wins!', font, GREEN, screen, WIDTH // 2 - 100, HEIGHT // 2)
                simulation_running = False
                timer_running = False

        draw_text(f'Speed: {abs(velocity):.2f} px/s', font, BLACK, screen, 10, HEIGHT - 110)
        draw_text(f'Acceleration: {acceleration:.2f} px/s²', font, BLACK, screen, 10, HEIGHT - 80)
        if timer_running:
            elapsed_time = time.time() - start_time
            draw_text(f'Time: {elapsed_time:.2f} s', font, BLACK, screen, 10, HEIGHT - 50)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
