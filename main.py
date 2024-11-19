# main.py

import math
import pygame
import sys
from settings import (
    WIDTH,
    HEIGHT,
    GRID_SIZE,
    TOOLBOX_WIDTH,
    CHARGE_RADIUS,
    POSITIVE_COLOR,
    NEGATIVE_COLOR,
    COULOMB_CONSTANT,
    INITIAL_ZOOM_LEVEL,
    ZOOM_STEP,
    MIN_ZOOM_LEVEL,
    MAX_ZOOM_LEVEL,
    BASE_PAN_SPEED,
    FIELD_LINE_STEP,
    NUM_FIELD_LINES,
    LINE_COLOR,
    LINE_WIDTH,
    WHITE,
    BLACK,
)
from toolbox import draw_toolbox, handle_toolbox_click, get_selected_tool
from electric_field import calculate_field_with_details, draw_field_lines
from dielectric import add_dielectric, draw_dielectrics, remove_dielectric
from ui import draw_probe_info_sidebar, handle_scroll, draw_dielectric_preview

# Initialize Pygame
pygame.init()
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w - TOOLBOX_WIDTH
HEIGHT = screen_info.current_h

# Set windowed fullscreen mode (borderless window)
screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h))
pygame.display.set_caption("Electric Field Simulator")

# Zoom and camera variables
zoom_level = INITIAL_ZOOM_LEVEL
camera_offset_x, camera_offset_y = WIDTH // 2, HEIGHT // 2
charges = []
dielectrics = []  # List to store dielectric regions
is_dragging = False
drag_start_pos = (0, 0)
start_drag_pos = None  # For placing dielectrics
current_tool = "add_positive"  # Default tool

# Variables for field probe
probe_point = None  # Stores the position where the user probed the field
field_at_probe = None  # Stores the electric field at the probe point
math_details = None  # Stores detailed calculations

# Scroll offset for probe field text is now handled in ui.py as a global variable

def draw_grid():
    """
    Draws a grid based on the current zoom level and camera offset.
    """
    scaled_grid_size = int(GRID_SIZE * zoom_level)
    if scaled_grid_size == 0:
        scaled_grid_size = 1  # Prevent division by zero
    start_x = int(-camera_offset_x % scaled_grid_size)
    start_y = int(-camera_offset_y % scaled_grid_size)
    for x in range(start_x, screen_info.current_w, scaled_grid_size):
        pygame.draw.line(screen, (220, 220, 220), (x, 0), (x, screen_info.current_h))
    for y in range(start_y, screen_info.current_h, scaled_grid_size):
        pygame.draw.line(screen, (220, 220, 220), (0, y), (screen_info.current_w, y))

def draw_charges():
    """
    Draws all charges on the screen.
    """
    for (world_x, world_y, charge_magnitude) in charges:
        color = POSITIVE_COLOR if charge_magnitude > 0 else NEGATIVE_COLOR
        screen_x = int(world_x * zoom_level + camera_offset_x)
        screen_y = int(world_y * zoom_level + camera_offset_y)
        radius = max(1, int(CHARGE_RADIUS * zoom_level))  # Scale radius
        pygame.draw.circle(screen, color, (screen_x, screen_y), radius)

def add_charge(x, y, charge_type):
    """
    Adds a charge of specified type at the given screen coordinates.
    """
    world_x = (x - camera_offset_x) / zoom_level
    world_y = (y - camera_offset_y) / zoom_level
    charge_magnitude = 1 if charge_type == "positive" else -1
    charges.append((world_x, world_y, charge_magnitude))
    print(f"Charge added: ({world_x:.2f}, {world_y:.2f}), type: {charge_type}")

def remove_charge(x, y):
    """
    Removes a charge near the specified screen coordinates.
    """
    global charges
    world_x = (x - camera_offset_x) / zoom_level
    world_y = (y - camera_offset_y) / zoom_level
    new_charges = []
    for (cx, cy, q) in charges:
        distance = math.hypot(cx - world_x, cy - world_y)
        if distance > (CHARGE_RADIUS * 2) / zoom_level:
            new_charges.append((cx, cy, q))
    charges = new_charges
    print(f"Charge removed near: ({world_x:.2f}, {world_y:.2f})")

def scale_zoom(previous_zoom, new_zoom):
    """
    Adjust the camera offsets to maintain the same view when zooming in or out.
    """
    global camera_offset_x, camera_offset_y
    scale_factor = new_zoom / previous_zoom
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Adjust camera offsets to zoom relative to mouse position
    camera_offset_x = mouse_x - (mouse_x - camera_offset_x) * scale_factor
    camera_offset_y = mouse_y - (mouse_y - camera_offset_y) * scale_factor
    print(
        f"Camera offset after zoom: ({camera_offset_x}, {camera_offset_y}), Zoom level: {new_zoom:.2f}"
    )

def main():
    global zoom_level, camera_offset_x, camera_offset_y, is_dragging, drag_start_pos
    global start_drag_pos, current_tool, probe_point, field_at_probe, math_details

    running = True

    while running:
        screen.fill(WHITE)  # Clear screen with white background
        draw_toolbox(screen)
        draw_grid()
        draw_charges()
        draw_field_lines(
            screen,
            charges,
            dielectrics,
            zoom_level,
            camera_offset_x,
            camera_offset_y,
            screen_info
        )
        draw_dielectrics(
            screen, zoom_level, camera_offset_x, camera_offset_y, dielectrics, charges
        ) 

        # Draw dielectric preview if in progress
        if current_tool == "add_dielectric" and start_drag_pos:
            end_drag_pos = pygame.mouse.get_pos()
            draw_dielectric_preview(screen, start_drag_pos, end_drag_pos)

        # Draw the probe point and field info if available
        if probe_point and field_at_probe and math_details:
            draw_probe_info_sidebar(screen, probe_point, field_at_probe, math_details)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.button == 1:  # Left mouse button clicked
                    if mouse_x < TOOLBOX_WIDTH:
                        # Clicked inside toolbox
                        previous_tool = current_tool
                        current_tool = handle_toolbox_click(mouse_x, mouse_y)
                        # Clear probe point if switching from probe tool
                        if previous_tool == "probe_field" and current_tool != "probe_field":
                            probe_point = None
                            field_at_probe = None
                            math_details = None
                            # Reset scroll_offset in ui.py
                            from ui import scroll_offset
                            scroll_offset = 0
                        if current_tool == "zoom_in":
                            previous_zoom = zoom_level
                            zoom_level = min(zoom_level + ZOOM_STEP, MAX_ZOOM_LEVEL)
                            scale_zoom(previous_zoom, zoom_level)
                        elif current_tool == "zoom_out":
                            previous_zoom = zoom_level
                            zoom_level = max(zoom_level - ZOOM_STEP, MIN_ZOOM_LEVEL)
                            scale_zoom(previous_zoom, zoom_level)
                    else:
                        # Clicked outside toolbox
                        tool = current_tool
                        if tool == "add_positive":
                            add_charge(mouse_x, mouse_y, "positive")
                        elif tool == "add_negative":
                            add_charge(mouse_x, mouse_y, "negative")
                        elif tool == "erase":
                            remove_charge(mouse_x, mouse_y)
                        elif tool == "pan":
                            is_dragging = True
                            drag_start_pos = (mouse_x, mouse_y)
                        elif tool == "add_dielectric":
                            start_drag_pos = (mouse_x, mouse_y)  # Start rectangle for dielectric
                        elif tool == "remove_dielectric":
                            # Call remove_dielectric function
                            removed = remove_dielectric(
                                mouse_x, mouse_y, zoom_level, camera_offset_x, camera_offset_y, dielectrics
                            )
                            if removed:
                                print("Dielectric removed.")
                        elif tool == "probe_field":
                            # Set the probe point and calculate the field with details
                            probe_point = (mouse_x, mouse_y)
                            ex, ey, math_details = calculate_field_with_details(
                                mouse_x, mouse_y, charges, dielectrics, zoom_level, camera_offset_x, camera_offset_y)
                            field_magnitude = math.hypot(ex, ey)
                            field_at_probe = {
                                'Ex': ex,
                                'Ey': ey,
                                'E_magnitude': field_magnitude
                            }
                            # Reset scroll_offset in ui.py
                            from ui import scroll_offset
                            scroll_offset = 0
                            print(f"Probed field at ({mouse_x}, {mouse_y}): Ex={ex}, Ey={ey}, |E|={field_magnitude}")

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button released
                    if is_dragging:
                        is_dragging = False
                    elif current_tool == "add_dielectric" and start_drag_pos:
                        end_drag_pos = pygame.mouse.get_pos()
                        add_dielectric(
                            *start_drag_pos,
                            *end_drag_pos,
                            epsilon_r=10.0,  # Adjust as needed
                            zoom_level=zoom_level,
                            camera_offset_x=camera_offset_x,
                            camera_offset_y=camera_offset_y,
                            dielectrics=dielectrics,
                        )
                        print(f"Dielectric drawn from {start_drag_pos} to {end_drag_pos}")
                        start_drag_pos = None

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging:
                    if event.buttons[0]:  # Left mouse button is pressed
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        dx = mouse_x - drag_start_pos[0]
                        dy = mouse_y - drag_start_pos[1]
                        camera_offset_x += dx
                        camera_offset_y += dy
                        drag_start_pos = (mouse_x, mouse_y)
                    else:
                        is_dragging = False  # Left mouse button not pressed anymore

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    previous_zoom = zoom_level
                    zoom_level = min(zoom_level + ZOOM_STEP, MAX_ZOOM_LEVEL)
                    scale_zoom(previous_zoom, zoom_level)
                    print(f"Zooming in via keyboard. New zoom level: {zoom_level:.2f}")
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    previous_zoom = zoom_level
                    zoom_level = max(zoom_level - ZOOM_STEP, MIN_ZOOM_LEVEL)
                    scale_zoom(previous_zoom, zoom_level)
                    print(f"Zooming out via keyboard. New zoom level: {zoom_level:.2f}")

            elif event.type == pygame.MOUSEWHEEL:
                # Handle mouse wheel scrolling when probe field is active and mouse is over sidebar
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if probe_point and field_at_probe and math_details:
                    # Check if mouse is over the sidebar
                    sidebar_width = TOOLBOX_WIDTH
                    sidebar_x_pos = screen.get_width() - sidebar_width
                    if sidebar_x_pos <= mouse_x <= screen.get_width() and 0 <= mouse_y <= screen.get_height():
                        # Adjust scroll_offset using handle_scroll from ui.py
                        handle_scroll(event)
                        print(f"Scroll offset updated: {scroll_offset}")
                else:
                    # Mouse wheel used outside probe info; handle as needed (e.g., zoom)
                    pass

        pygame.display.flip()

def calculate_field_with_details(px, py, charges, dielectrics, zoom_level, camera_offset_x, camera_offset_y):
    """
    Calculate the electric field at a point (px, py) and collect detailed calculation steps.
    """
    total_ex, total_ey = 0.0, 0.0
    math_details = {'charges': []}

    # Convert screen coordinates to world coordinates
    world_px = (px - camera_offset_x) / zoom_level
    world_py = (py - camera_offset_y) / zoom_level

    # Check if the point is inside any dielectric region
    epsilon_r = 1.0  # Default relative permittivity (vacuum)
    for (x1, y1, width, height, dielectric_epsilon) in dielectrics:
        x2 = x1 + width
        y2 = y1 + height
        if x1 <= world_px <= x2 and y1 <= world_py <= y2:
            epsilon_r = dielectric_epsilon
            break
    math_details['epsilon_r'] = epsilon_r

    # Calculate contributions from each charge
    for (cx, cy, q) in charges:
        dx = world_px - cx
        dy = world_py - cy
        r_squared = dx**2 + dy**2
        if r_squared == 0:
            continue  # Avoid division by zero

        e_magnitude = COULOMB_CONSTANT * q / (r_squared * epsilon_r)
        angle = math.atan2(dy, dx)
        ex = e_magnitude * math.cos(angle)
        ey = e_magnitude * math.sin(angle)

        total_ex += ex
        total_ey += ey

        # Store details for this charge
        math_details['charges'].append({
            'q': q,
            'r_squared': r_squared,
            'angle': angle,
            'ex': ex,
            'ey': ey,
        })

    return total_ex, total_ey, math_details

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit()
