import pygame
import sys

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
left_team = []
right_team = []
left_characters = [{'pos': [100, 150 + i * 100], 'force': 50, 'selected': False, 'team': 'left'} for i in range(4)]
right_characters = [{'pos': [1100, 150 + i * 100], 'force': 50, 'selected': False, 'team': 'right'} for i in range(4)]
left_sliders = [{'rect': pygame.Rect(50, 130 + i * 100, 100, 10), 'value': 50} for i in range(4)]
right_sliders = [{'rect': pygame.Rect(1050, 130 + i * 100, 100, 10), 'value': 50} for i in range(4)]
left_checkboxes = [{'rect': pygame.Rect(160, 130 + i * 100, 20, 20), 'checked': False} for i in range(4)]
right_checkboxes = [{'rect': pygame.Rect(1020, 130 + i * 100, 20, 20), 'checked': False} for i in range(4)]
friction = 0.1
velocity = 0
rope_pos = WIDTH // 2

# Button positions
start_button = pygame.Rect(550, 700, 100, 50)
restart_button = pygame.Rect(670, 700, 100, 50)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def draw_teams():
    for member in left_team:
        pygame.draw.circle(screen, GREEN, member['pos'], 20)
        draw_text(str(member['force']), font, BLACK, screen, member['pos'][0] - 10, member['pos'][1] - 40)

    for member in right_team:
        pygame.draw.circle(screen, RED, member['pos'], 20)
        draw_text(str(member['force']), font, BLACK, screen, member['pos'][0] - 10, member['pos'][1] - 40)

def draw_characters():
    for i, character in enumerate(left_characters):
        pygame.draw.circle(screen, GRAY, character['pos'], 20)
        draw_text(str(character['force']), font, BLACK, screen, character['pos'][0] - 10, character['pos'][1] - 40)
        pygame.draw.rect(screen, BLACK, left_sliders[i]['rect'], 2)
        pygame.draw.rect(screen, BLUE, (left_sliders[i]['rect'].x, left_sliders[i]['rect'].y, left_sliders[i]['value'], left_sliders[i]['rect'].height))
        pygame.draw.rect(screen, BLACK, left_checkboxes[i]['rect'], 2)
        if left_checkboxes[i]['checked']:
            pygame.draw.line(screen, BLACK, (left_checkboxes[i]['rect'].x, left_checkboxes[i]['rect'].y), 
                             (left_checkboxes[i]['rect'].x + left_checkboxes[i]['rect'].width, left_checkboxes[i]['rect'].y + left_checkboxes[i]['rect'].height), 2)
            pygame.draw.line(screen, BLACK, (left_checkboxes[i]['rect'].x, left_checkboxes[i]['rect'].y + left_checkboxes[i]['rect'].height), 
                             (left_checkboxes[i]['rect'].x + left_checkboxes[i]['rect'].width, left_checkboxes[i]['rect'].y), 2)

    for i, character in enumerate(right_characters):
        pygame.draw.circle(screen, GRAY, character['pos'], 20)
        draw_text(str(character['force']), font, BLACK, screen, character['pos'][0] - 10, character['pos'][1] - 40)
        pygame.draw.rect(screen, BLACK, right_sliders[i]['rect'], 2)
        pygame.draw.rect(screen, BLUE, (right_sliders[i]['rect'].x, right_sliders[i]['rect'].y, right_sliders[i]['value'], right_sliders[i]['rect'].height))
        pygame.draw.rect(screen, BLACK, right_checkboxes[i]['rect'], 2)
        if right_checkboxes[i]['checked']:
            pygame.draw.line(screen, BLACK, (right_checkboxes[i]['rect'].x, right_checkboxes[i]['rect'].y), 
                             (right_checkboxes[i]['rect'].x + right_checkboxes[i]['rect'].width, right_checkboxes[i]['rect'].y + right_checkboxes[i]['rect'].height), 2)
            pygame.draw.line(screen, BLACK, (right_checkboxes[i]['rect'].x, right_checkboxes[i]['rect'].y + right_checkboxes[i]['rect'].height), 
                             (right_checkboxes[i]['rect'].x + right_checkboxes[i]['rect'].width, right_checkboxes[i]['rect'].y), 2)

def main():
    global rope_pos, velocity
    clock = pygame.time.Clock()
    running = True
    simulation_running = False
    selected_character = None

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, character in enumerate(left_characters + right_characters):
                    if (character['team'] == 'left' and left_sliders[i]['rect'].collidepoint(event.pos)) or \
                       (character['team'] == 'right' and right_sliders[i % 4]['rect'].collidepoint(event.pos)):
                        selected_character = character
                        break
                for checkbox in left_checkboxes + right_checkboxes:
                    if checkbox['rect'].collidepoint(event.pos):
                        checkbox['checked'] = not checkbox['checked']
                if start_button.collidepoint(event.pos):
                    simulation_running = True
                    left_team.clear()
                    right_team.clear()
                    for i, checkbox in enumerate(left_checkboxes):
                        if checkbox['checked']:
                            left_team.append({'pos': [200, 200 + len(left_team) * 100], 'force': left_characters[i]['force']})
                    for i, checkbox in enumerate(right_checkboxes):
                        if checkbox['checked']:
                            right_team.append({'pos': [WIDTH - 200, 200 + len(right_team) * 100], 'force': right_characters[i]['force']})
                if restart_button.collidepoint(event.pos):
                    simulation_running = False
                    rope_pos = WIDTH // 2
                    velocity = 0

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_character:
                    selected_character = None

            elif event.type == pygame.MOUSEMOTION:
                if selected_character:
                    for i, slider in enumerate(left_sliders + right_sliders):
                        if slider['rect'].collidepoint(event.pos):
                            slider['value'] = min(max(event.pos[0] - slider['rect'].x, 0), slider['rect'].width)
                            if selected_character['team'] == 'left':
                                left_characters[i]['force'] = slider['value']
                            else:
                                right_characters[i % 4]['force'] = slider['value']

        # Draw teams and characters
        draw_teams()
        draw_characters()

        # Draw rope
        pygame.draw.line(screen, BLACK, (rope_pos, HEIGHT // 2 - 50), (rope_pos, HEIGHT // 2 + 50), 5)

        # Draw buttons
        pygame.draw.rect(screen, GRAY, start_button)
        draw_text('Start', font, BLACK, screen, start_button.x + 20, start_button.y + 10)
        pygame.draw.rect(screen, GRAY, restart_button)
        draw_text('Restart', font, BLACK, screen, restart_button.x + 10, restart_button.y + 10)

        # Sum of forces
        total_force_left = sum(member['force'] for member in left_team)
        total_force_right = sum(member['force'] for member in right_team)
        net_force = total_force_right - total_force_left

        # Display forces
        draw_text(f'Left Team Force: {total_force_left}', font, BLACK, screen, 10, 10)
        draw_text(f'Right Team Force: {total_force_right}', font, BLACK, screen, 10, 50)
        draw_text(f'Net Force: {net_force}', font, BLACK, screen, 10, 90)

        # Update rope position if simulation is running
        if simulation_running:
            acceleration = net_force / 100.0  # Assume mass = 100 units for simplicity
            velocity += acceleration
            velocity *= (1 - friction)
            rope_pos += velocity

            # Keep rope within bounds
            if rope_pos < 100:
                rope_pos = 100
                velocity = 0
            if rope_pos > WIDTH - 100:
                rope_pos = WIDTH - 100
                velocity = 0

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()



