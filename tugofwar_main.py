import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 800
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

# Load images
background = pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT))
box_image = pygame.transform.scale(pygame.image.load("box.png"), (100, 100))
box_rect = box_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Initial positions and forces
left_team = [{'pos': [100, 150 + i * 100], 'force': 50, 'selected': False, 'team': 'left', 'stamina': 100, 'max_force': 50, 'enabled': True, 'resting': False} for i in range(4)]
right_team = [{'pos': [1100, 150 + i * 100], 'force': 50, 'selected': False, 'team': 'right', 'stamina': 100, 'max_force': 50, 'enabled': True, 'resting': False} for i in range(4)]
left_sliders = [{'rect': pygame.Rect(145, 610 + i * 50, 100, 10), 'value': 50} for i in range(4)]
right_sliders = [{'rect': pygame.Rect(1040, 610 + i * 50, 100, 10), 'value': 50} for i in range(4)]
left_checkboxes = [{'rect': pygame.Rect(260, 605 + i * 50, 20, 20), 'checked': True} for i in range(4)]
right_checkboxes = [{'rect': pygame.Rect(1000, 605 + i * 50, 20, 20), 'checked': True} for i in range(4)]
friction = 0.1
velocity = 0
acceleration = 0
rope_pos = WIDTH // 2

# Button positions
start_button = pygame.Rect(600, 650, 100, 50)
restart_button = pygame.Rect(600, 725, 100, 50)
stamina_button = pygame.Rect(560, 575, 175, 50)

dragging_slider = None

start_time = None
timer_running = False
simulation_running = False
winner = None  # Variable to store the winner
stamina_enabled = True  # Variable to track the stamina state


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


def draw_teams():
    for i, member in enumerate(left_team):
        if member['enabled']:
            pygame.draw.circle(screen, RED, member['pos'], 20)
            draw_text(str(member['force']) + " N", font, BLACK, screen, member['pos'][0] - 20, member['pos'][1] -50)
            draw_text(f'{i+1}', font, BLACK, screen, member['pos'][0] - 7.5, member['pos'][1] - 15)

            # Draw stamina bar
            stamina_bar_rect = pygame.Rect(member['pos'][0] - 50, member['pos'][1] + 25, 100, 10)
            pygame.draw.rect(screen, RED, stamina_bar_rect)
            pygame.draw.rect(screen, GREEN, (stamina_bar_rect.x, stamina_bar_rect.y, stamina_bar_rect.width * (member['stamina'] / 100), stamina_bar_rect.height))
            draw_text(f'{member["stamina"]:.1f}', font, BLACK, screen, member['pos'][0] + 65, member['pos'][1] + 20)

    for i, member in enumerate(right_team):
        if member['enabled']:
            pygame.draw.circle(screen, BLUE, member['pos'], 20)
            draw_text(str(member['force']) + " N", font, BLACK, screen, member['pos'][0] - 20, member['pos'][1] -50)
            draw_text(f'{i+1}', font, BLACK, screen, member['pos'][0] - 7.5, member['pos'][1] - 15)

            # Draw stamina bar
            stamina_bar_rect = pygame.Rect(member['pos'][0] - 50, member['pos'][1] + 25, 100, 10)
            pygame.draw.rect(screen, RED, stamina_bar_rect)
            pygame.draw.rect(screen, GREEN, (stamina_bar_rect.x, stamina_bar_rect.y, stamina_bar_rect.width * (member['stamina'] / 100), stamina_bar_rect.height))
            draw_text(f'{member["stamina"]:.1f}', font, BLACK, screen, member['pos'][0] + 65, member['pos'][1] + 20)

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
            pygame.draw.line(screen, BLACK, (checkbox['rect'].x, checkbox['rect'].y), (checkbox['rect'].x + 20, checkbox['rect'].y + 20), 2)
            pygame.draw.line(screen, BLACK, (checkbox['rect'].x + 20, checkbox['rect'].y), (checkbox['rect'].x, checkbox['rect'].y + 20), 2)

    for checkbox in right_checkboxes:
        pygame.draw.rect(screen, BLACK, checkbox['rect'], 2)
        if checkbox['checked']:
            pygame.draw.line(screen, BLACK, (checkbox['rect'].x, checkbox['rect'].y), (checkbox['rect'].x + 20, checkbox['rect'].y + 20), 2)
            pygame.draw.line(screen, BLACK, (checkbox['rect'].x + 20, checkbox['rect'].y), (checkbox['rect'].x, checkbox['rect'].y + 20), 2)


def calculate_effective_force(team):
    total_force = 0
    for member in team:
        if member['enabled']:
            if stamina_enabled:
                total_force += member['force'] * (member['stamina'] / 100.0)
            else:
                total_force += member['force']
    return total_force


def update_stamina_and_force():
    if stamina_enabled:
        for member in left_team + right_team:
            if member['enabled']:
                if member['stamina'] > 0:
                    if not member['resting']:
                        member['stamina'] -= member['force'] / 1000.0
                        if member['stamina'] < 20 or member['force'] == 0:  # Threshold for resting
                            member['resting'] = True
                    elif member['force'] == 0:
                        if member['stamina'] <= 100:
                            member['stamina'] += 0.25
                            if member['stamina'] > 100:
                                member['stamina'] = 100
                    else: 
                        member['stamina'] += 0.25 # Regain stamina faster when resting
                        if member['stamina'] > 80:  # Threshold to stop resting
                            member['resting'] = False

                else:
                    member['stamina'] = 0

                # Adjust force based on stamina and resting state
                if member['resting'] or member['force'] == 0.0:  # Regenerate stamina if resting or force is zero
                    member['force'] = member['max_force'] / 2
                else:
                    member['force'] = member['max_force']



def main():
    global dragging_slider, start_time, timer_running, simulation_running, velocity, acceleration, rope_pos, winner, stamina_enabled

    clock = pygame.time.Clock()
    running = True

    while running:
        screen.blit(background, (0, 0))

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
                            winner = None  # Reset the winner when starting a new game
                    if restart_button.collidepoint(event.pos):
                        start_time = None
                        timer_running = False
                        simulation_running = False
                        velocity = 0
                        rope_pos = WIDTH // 2
                        winner = None  # Reset the winner on restart
                        for member in left_team + right_team:
                            member['stamina'] = 100
                            member['force'] = member['max_force']
                            member['enabled'] = True
                            member['resting'] = False
                            for checkbox in left_checkboxes + right_checkboxes:
                                checkbox['checked'] = True
                    if stamina_button.collidepoint(event.pos):
                        stamina_enabled = not stamina_enabled
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

        # Draw the box representing the tug of war
        box_rect.centerx = rope_pos
        screen.blit(box_image, box_rect)

        pygame.draw.rect(screen, GREEN, start_button)
        draw_text('Start', font, BLACK, screen, start_button.x + 20, start_button.y + 10)
        pygame.draw.rect(screen, RED, restart_button)
        draw_text('Restart', font, BLACK, screen, restart_button.x + 10, restart_button.y + 10)
        pygame.draw.rect(screen, GRAY, stamina_button)
        draw_text(f'Stamina: {"On" if stamina_enabled else "Off"}', font, BLACK, screen, stamina_button.x + 20, stamina_button.y + 10)

        total_force_left = calculate_effective_force(left_team)
        total_force_right = calculate_effective_force(right_team)
        net_force = total_force_right - total_force_left

        draw_text(f'Left Team Force: {total_force_left:.1f}', font, RED, screen, 10, 10)
        draw_text(f'Right Team Force: {total_force_right:.1f}', font, BLUE, screen, 10, 50)
        draw_text(f'Net Force: {net_force:.1f}', font, BLACK, screen, WIDTH//2-75, 10)

        # Draw bottom-left box
        pygame.draw.rect(screen, GRAY, (10, 570, 300, 210))
        draw_text('Left Team Controls', font, BLACK, screen, 20, 575)
        for i in range(4):
            draw_text(f'Player {i+1}', font, BLACK, screen, 25, 600 + i * 50)
            pygame.draw.rect(screen, BLACK, left_sliders[i]['rect'])
            pygame.draw.rect(screen, GREEN, (left_sliders[i]['rect'].x + left_sliders[i]['value'], left_sliders[i]['rect'].y - 5, 10, 20))
            pygame.draw.rect(screen, BLACK, left_checkboxes[i]['rect'], 2)
            if left_checkboxes[i]['checked']:
                pygame.draw.line(screen, BLACK, (left_checkboxes[i]['rect'].x, left_checkboxes[i]['rect'].y), (left_checkboxes[i]['rect'].x + 20, left_checkboxes[i]['rect'].y + 20), 2)
                pygame.draw.line(screen, BLACK, (left_checkboxes[i]['rect'].x + 20, left_checkboxes[i]['rect'].y), (left_checkboxes[i]['rect'].x, left_checkboxes[i]['rect'].y + 20), 2)

        # Draw bottom-right box
        pygame.draw.rect(screen, GRAY, (950, 570, 300, 210))
        draw_text('Right Team Controls', font, BLACK, screen, 1000, 575)
        for i in range(4):
            draw_text(f'Player {i+1}', font, BLACK, screen, 1150, 600 + i * 50)
            pygame.draw.rect(screen, BLACK, right_sliders[i]['rect'])
            pygame.draw.rect(screen, BLUE, (right_sliders[i]['rect'].x + right_sliders[i]['value'], right_sliders[i]['rect'].y - 5, 10, 20))
            pygame.draw.rect(screen, BLACK, right_checkboxes[i]['rect'], 2)
            if right_checkboxes[i]['checked']:
                pygame.draw.line(screen, BLACK, (right_checkboxes[i]['rect'].x, right_checkboxes[i]['rect'].y), (right_checkboxes[i]['rect'].x + 20, right_checkboxes[i]['rect'].y + 20), 2)
                pygame.draw.line(screen, BLACK, (right_checkboxes[i]['rect'].x + 20, right_checkboxes[i]['rect'].y), (right_checkboxes[i]['rect'].x, right_checkboxes[i]['rect'].y + 20), 2)

        if simulation_running:
            update_stamina_and_force()
            acceleration = net_force / 100.0  # pixels per second squared
            velocity += acceleration
            velocity *= (1 - friction)
            rope_pos += velocity

            if rope_pos < 100:
                winner = 'Left'  # Corrected to declare Left as winner when rope is at left edge
                simulation_running = False
                timer_running = False
            elif rope_pos > WIDTH - 100:
                winner = 'Right'  # Corrected to declare Right as winner when rope is at right edge
                simulation_running = False
                timer_running = False

        # Display the winner if there is one
        if winner:
            if winner == 'Right':
                draw_text('Right Team Wins!', font, RED, screen, WIDTH // 2 - 100, HEIGHT // 2)
            else:
                draw_text('Left Team Wins!', font, GREEN, screen, WIDTH // 2 - 100, HEIGHT // 2)

        draw_text(f'{abs(velocity):.2f} px/s - Speed', font, BLACK, screen, WIDTH - 275, 10)
        draw_text(f'{acceleration:.2f} px/s - Acceleration ', font, BLACK, screen, WIDTH - 275, 50)
        if timer_running:
            elapsed_time = time.time() - start_time
            draw_text(f'Time: {elapsed_time:.2f} s', font, BLACK, screen, WIDTH // 2 - 75, 50)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
