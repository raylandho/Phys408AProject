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
)
from toolbox import draw_toolbox, handle_toolbox_click, get_selected_tool
from electric_field import calculate_field, draw_field_lines
from dielectric import add_dielectric, draw_dielectrics

# Initialize Pygame
pygame.init()
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w - TOOLBOX_WIDTH
HEIGHT = screen_info.current_h

# Set windowed fullscreen mode (borderless window)
screen = pygame.display.set_mode(
    (screen_info.current_w, screen_info.current_h)
)
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

# Draw the grid
def draw_grid():
    scaled_grid_size = int(GRID_SIZE * zoom_level)
    if scaled_grid_size == 0:
        scaled_grid_size = 1  # Prevent division by zero
    start_x = int(-camera_offset_x % scaled_grid_size)
    start_y = int(-camera_offset_y % scaled_grid_size)
    for x in range(start_x, WIDTH + TOOLBOX_WIDTH, scaled_grid_size):
        pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, HEIGHT))
    for y in range(start_y, HEIGHT, scaled_grid_size):
        pygame.draw.line(screen, (200, 200, 200), (TOOLBOX_WIDTH, y), (WIDTH + TOOLBOX_WIDTH, y))

# Draw charges on the screen
def draw_charges():
    for (world_x, world_y, charge_magnitude) in charges:
        color = POSITIVE_COLOR if charge_magnitude > 0 else NEGATIVE_COLOR
        screen_x = int(world_x * zoom_level + camera_offset_x)
        screen_y = int(world_y * zoom_level + camera_offset_y)
        radius = max(1, int(CHARGE_RADIUS * zoom_level))  # Scale radius
        pygame.draw.circle(screen, color, (screen_x, screen_y), radius)

# Add a charge at the specified grid location
def add_charge(x, y, charge_type):
    world_x = (x - camera_offset_x) / zoom_level
    world_y = (y - camera_offset_y) / zoom_level
    charge_magnitude = 1 if charge_type == "positive" else -1
    charges.append((world_x, world_y, charge_magnitude))
    print(f"Charge added: ({world_x:.2f}, {world_y:.2f}), type: {charge_type}")

# Remove a charge near a specified location
def remove_charge(x, y):
    global charges
    world_x = (x - camera_offset_x) / zoom_level
    world_y = (y - camera_offset_y) / zoom_level
    new_charges = []
    for (cx, cy, q) in charges:
        distance = math.sqrt((cx - world_x) ** 2 + (cy - world_y) ** 2)
        if distance > (CHARGE_RADIUS * 2) / zoom_level:
            new_charges.append((cx, cy, q))
    charges = new_charges
    print(f"Charge removed near: ({world_x:.2f}, {world_y:.2f})")

# Scale zoom function to adjust camera offsets
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

def draw_probe_info(screen, probe_point, field_at_probe, math_details):
    """
    Draw a marker at the probe point and display the electric field information and calculations.
    """
    mouse_x, mouse_y = probe_point
    # Draw a small circle at the probe point
    pygame.draw.circle(screen, (255, 0, 0), (mouse_x, mouse_y), 5)

    # Prepare the text to display
    font = pygame.font.Font(None, 22)
    lines = []

    # Add the formula
    lines.append("Electric Field at a Point:")
    lines.append("E = Σ Ei")
    lines.append("Ei = (k * qi) / ri^2")
    lines.append("Ei_x = Ei * cos(θi), Ei_y = Ei * sin(θi)")
    lines.append("")

    # Add whether the point is inside a dielectric
    if math_details['epsilon_r'] > 1.0:
        dielectric_info = f"Inside dielectric (εr = {math_details['epsilon_r']:.2f})"
    else:
        dielectric_info = "In free space (εr = 1.00)"
    lines.append(dielectric_info)
    lines.append("")

    # Show contributions from each charge
    lines.append("Contributions from Charges:")
    for idx, charge_info in enumerate(math_details['charges']):
        q = charge_info['q']
        r = math.sqrt(charge_info['r_squared'])
        angle_deg = math.degrees(charge_info['angle'])
        ex = charge_info['ex']
        ey = charge_info['ey']
        lines.append(f"Charge {idx+1}:")
        lines.append(f"  q = {q} C")
        lines.append(f"  r = {r:.2f} m")
        lines.append(f"  θ = {angle_deg:.2f}°")
        lines.append(f"  Ei_x = {ex:.2e} N/C")
        lines.append(f"  Ei_y = {ey:.2e} N/C")
        lines.append("")

    # Total electric field
    Ex = field_at_probe['Ex']
    Ey = field_at_probe['Ey']
    E_magnitude = field_at_probe['E_magnitude']
    E_angle = math.degrees(math.atan2(Ey, Ex))

    # Show the total electric field calculation
    lines.append("Total Electric Field:")
    lines.append(f"Ex_total = Σ Ei_x = {Ex:.2e} N/C")
    lines.append(f"Ey_total = Σ Ei_y = {Ey:.2e} N/C")
    lines.append(f"|E| = sqrt(Ex_total^2 + Ey_total^2) = {E_magnitude:.2e} N/C")
    lines.append(f"Direction θ = atan2(Ey_total, Ex_total) = {E_angle:.2f}°")

    # Display the lines
    text_x = mouse_x + 10
    text_y = mouse_y + 10
    for line in lines:
        text_surface = font.render(line, True, (0, 0, 0))
        screen.blit(text_surface, (text_x, text_y))
        text_y += 22  # Move down for the next line

def draw_dielectric_preview(screen, start_pos, end_pos):
    """
    Draw a preview of the dielectric being added as a rectangle while dragging.
    """
    start_x, start_y = start_pos
    end_x, end_y = end_pos

    rect_x = min(start_x, end_x)
    rect_y = min(start_y, end_y)
    rect_width = abs(end_x - start_x)
    rect_height = abs(end_y - start_y)

    rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    pygame.draw.rect(screen, (0, 255, 255), rect, 2)  # Outline

# Main game loop
def main():
    global zoom_level, camera_offset_x, camera_offset_y, is_dragging, drag_start_pos, start_drag_pos, current_tool, probe_point, field_at_probe, math_details
    running = True
    while running:
        screen.fill((255, 255, 255))  # Clear screen with white background
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
            screen_info,
        )
        draw_dielectrics(
            screen, zoom_level, camera_offset_x, camera_offset_y, dielectrics
        )  # Draw dielectric regions

        # Draw dielectric preview if in progress
        if current_tool == "add_dielectric" and start_drag_pos:
            end_drag_pos = pygame.mouse.get_pos()
            draw_dielectric_preview(screen, start_drag_pos, end_drag_pos)

        # Draw the probe point and field info if available
        if probe_point and field_at_probe and math_details:
            draw_probe_info(screen, probe_point, field_at_probe, math_details)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x < TOOLBOX_WIDTH:
                    # Clicked inside toolbox
                    previous_tool = current_tool
                    current_tool = handle_toolbox_click(mouse_x, mouse_y)
                    # Clear probe point if switching from probe tool
                    if previous_tool == "probe_field" and current_tool != "probe_field":
                        probe_point = None
                        field_at_probe = None
                        math_details = None
                    if current_tool == "zoom_in":
                        previous_zoom = zoom_level
                        zoom_level = min(zoom_level + ZOOM_STEP, MAX_ZOOM_LEVEL)
                        scale_zoom(previous_zoom, zoom_level)
                    elif current_tool == "zoom_out":
                        previous_zoom = zoom_level
                        zoom_level = max(zoom_level - ZOOM_STEP, MIN_ZOOM_LEVEL)
                        scale_zoom(previous_zoom, zoom_level)
                else:
                    # Clicked on simulation area
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
                    elif tool == "add_dielectric":
                        start_drag_pos = (mouse_x, mouse_y)  # Start rectangle for dielectric
                    elif tool == "probe_field":
                        # Set the probe point and calculate the field with details
                        probe_point = (mouse_x, mouse_y)
                        ex, ey, math_details = calculate_field_with_details(mouse_x, mouse_y, charges, dielectrics, zoom_level, camera_offset_x, camera_offset_y)
                        field_magnitude = math.hypot(ex, ey)
                        field_at_probe = {
                            'Ex': ex,
                            'Ey': ey,
                            'E_magnitude': field_magnitude
                        }
                        print(f"Probed field at ({mouse_x}, {mouse_y}): Ex={ex}, Ey={ey}, |E|={field_magnitude}")

            elif event.type == pygame.MOUSEBUTTONUP:
                tool = get_selected_tool()
                if tool == "pan":
                    is_dragging = False
                elif tool == "add_dielectric" and start_drag_pos:
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
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    dx = mouse_x - drag_start_pos[0]
                    dy = mouse_y - drag_start_pos[1]
                    camera_offset_x += dx
                    camera_offset_y += dy
                    drag_start_pos = (mouse_x, mouse_y)
                # No action needed for dielectric preview; it's drawn every frame

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

        pygame.display.flip()

    pygame.quit()
    sys.exit()

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
    main()
