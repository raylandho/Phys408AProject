import math
import pygame
import sys
from settings import WIDTH, HEIGHT, GRID_SIZE, TOOLBOX_WIDTH, CHARGE_RADIUS, POSITIVE_COLOR, NEGATIVE_COLOR, COULOMB_CONSTANT, INITIAL_ZOOM_LEVEL, ZOOM_STEP, MIN_ZOOM_LEVEL, MAX_ZOOM_LEVEL, BASE_PAN_SPEED
from toolbox import draw_toolbox, handle_toolbox_click, get_selected_tool
from electric_field import calculate_field, draw_field_lines

# Initialize Pygame
pygame.init()
screen_info = pygame.display.Info()
screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h), pygame.NOFRAME)
pygame.display.set_caption("Electric Field Simulator")

# Zoom and camera variables
zoom_level = INITIAL_ZOOM_LEVEL
camera_offset_x, camera_offset_y = 0, 0
charges = []
is_dragging = False
drag_start_pos = (0, 0)

# Draw the grid
def draw_grid():
    scaled_grid_size = int(GRID_SIZE * zoom_level)
    start_x = int(-camera_offset_x % scaled_grid_size)
    start_y = int(-camera_offset_y % scaled_grid_size)
    for x in range(start_x, screen_info.current_w, scaled_grid_size):
        pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, screen_info.current_h))
    for y in range(start_y, screen_info.current_h, scaled_grid_size):
        pygame.draw.line(screen, (200, 200, 200), (0, y), (screen_info.current_w, y))

# Draw charges on the screen
def draw_charges():
    for (world_x, world_y, charge_magnitude) in charges:
        color = POSITIVE_COLOR if charge_magnitude > 0 else NEGATIVE_COLOR
        screen_x = int(world_x * zoom_level + camera_offset_x)
        screen_y = int(world_y * zoom_level + camera_offset_y)
        pygame.draw.circle(screen, color, (screen_x, screen_y), CHARGE_RADIUS)

# Add a charge at the specified grid location
def add_charge(x, y, charge_type):
    world_x = (x - camera_offset_x) / zoom_level
    world_y = (y - camera_offset_y) / zoom_level
    charge_magnitude = 1 if charge_type == "positive" else -1
    charges.append((world_x, world_y, charge_magnitude))

# Remove a charge near a specified location
def remove_charge(x, y):
    global charges
    world_x = (x - camera_offset_x) / zoom_level
    world_y = (y - camera_offset_y) / zoom_level
    charges = [
        (cx, cy, q) for (cx, cy, q) in charges
        if math.sqrt((cx - world_x) ** 2 + (cy - world_y) ** 2) > CHARGE_RADIUS * 2
    ]

# Main game loop
def main():
    global zoom_level, camera_offset_x, camera_offset_y, is_dragging, drag_start_pos
    running = True
    while running:
        screen.fill((255, 255, 255))
        draw_toolbox(screen)
        draw_grid()
        draw_charges()
        draw_field_lines(screen, charges, zoom_level, camera_offset_x, camera_offset_y, screen_info)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x < TOOLBOX_WIDTH:
                    tool = handle_toolbox_click(mouse_x, mouse_y)
                    if tool == "zoom_in":
                        zoom_level = min(zoom_level + ZOOM_STEP, MAX_ZOOM_LEVEL)
                    elif tool == "zoom_out":
                        zoom_level = max(zoom_level - ZOOM_STEP, MIN_ZOOM_LEVEL)
                else:
                    tool = get_selected_tool()
                    if tool == "add_positive":
                        add_charge(mouse_x, mouse_y, "positive")
                    elif tool == "add_negative":
                        add_charge(mouse_x, mouse_y, "negative")
                    elif tool == "erase":
                        remove_charge(mouse_x, mouse_y)
                    elif tool == "pan":
                        is_dragging = True
                        drag_start_pos = (mouse_x, mouse_y)
            elif event.type == pygame.MOUSEBUTTONUP and tool == "pan":
                is_dragging = False
            elif event.type == pygame.MOUSEMOTION and is_dragging:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - drag_start_pos[0]
                dy = mouse_y - drag_start_pos[1]
                camera_offset_x += dx
                camera_offset_y += dy
                drag_start_pos = (mouse_x, mouse_y)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    zoom_level = min(zoom_level + ZOOM_STEP, MAX_ZOOM_LEVEL)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    zoom_level = max(zoom_level - ZOOM_STEP, MIN_ZOOM_LEVEL)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
