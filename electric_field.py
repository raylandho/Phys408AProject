import math
import pygame
from settings import (
    COULOMB_CONSTANT,
    NUM_FIELD_LINES,
    FIELD_LINE_STEP,
    LINE_COLOR,
    LINE_WIDTH,
    CHARGE_RADIUS,
)

def calculate_field(px, py, charges, dielectrics, shields, zoom_level, camera_offset_x, camera_offset_y):
    """
    Calculate the electric field at a point (px, py), considering charges, dielectrics, and shields.
    """
    total_ex, total_ey = 0.0, 0.0

    # Convert screen coordinates to world coordinates
    world_px = (px - camera_offset_x) / zoom_level
    world_py = (py - camera_offset_y) / zoom_level

    # Determine the relative permittivity at the probe point
    epsilon_r = 1.0  # Default relative permittivity (vacuum)

    # Check dielectrics
    for dielectric in dielectrics:
        x1, y1, width, height, dielectric_epsilon = dielectric
        if x1 <= world_px <= x1 + width and y1 <= world_py <= y1 + height:
            epsilon_r = dielectric_epsilon
            break

    # Check shields (conductors have infinite epsilon, but we simulate by setting epsilon_r high)
    for shield in shields:
        x1, y1, width, height = shield
        if x1 <= world_px <= x1 + width and y1 <= world_py <= y1 + height:
            epsilon_r = 1e9  # Simulate conductor with very high epsilon
            break

    # Calculate contributions from each charge
    for charge in charges:
        cx, cy, q = charge
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

    return total_ex, total_ey

def calculate_field_with_details(px, py, charges, dielectrics, shields, zoom_level, camera_offset_x, camera_offset_y):
    """
    Calculate the electric field at a point (px, py) and collect detailed calculation steps.
    Returns total_ex, total_ey, and math_details containing contributions from each charge.
    """
    total_ex, total_ey = 0.0, 0.0
    math_details = {'charges': []}

    # Convert screen coordinates to world coordinates
    world_px = (px - camera_offset_x) / zoom_level
    world_py = (py - camera_offset_y) / zoom_level

    # Determine the relative permittivity at the probe point
    epsilon_r = 1.0  # Default relative permittivity (vacuum)

    # Check dielectrics
    for dielectric in dielectrics:
        x1, y1, width, height, dielectric_epsilon = dielectric
        if x1 <= world_px <= x1 + width and y1 <= world_py <= y1 + height:
            epsilon_r = dielectric_epsilon
            break

    # Check shields (conductors have infinite epsilon, but we simulate by setting epsilon_r high)
    for shield in shields:
        x1, y1, width, height = shield
        if x1 <= world_px <= x1 + width and y1 <= world_py <= y1 + height:
            epsilon_r = 1e9  # Simulate conductor with very high epsilon
            break

    math_details['epsilon_r'] = epsilon_r

    # Calculate contributions from each charge
    for charge in charges:
        cx, cy, q = charge
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

def draw_field_lines(screen, charges, dielectrics, shields, zoom_level, camera_offset_x, camera_offset_y, screen_info):
    """
    Draw electric field lines based on charges, dielectrics, and shields.
    """
    arrow_interval = 10  # Interval to place arrows along the line
    arrow_size = 5       # Size of the arrowhead

    def add_arrow(line_points, charge_magnitude):
        """
        Adds an arrowhead at the last segment of the field line.
        """
        if len(line_points) > 1:
            arrow_end = line_points[-1]
            arrow_start = line_points[-2]
            dx = arrow_end[0] - arrow_start[0]
            dy = arrow_end[1] - arrow_start[1]
            angle = math.atan2(dy, dx)
            if charge_magnitude < 0:
                angle += math.pi

            left_arrow = (
                arrow_end[0] - arrow_size * math.cos(angle - math.pi / 6),
                arrow_end[1] - arrow_size * math.sin(angle - math.pi / 6),
            )
            right_arrow = (
                arrow_end[0] - arrow_size * math.cos(angle + math.pi / 6),
                arrow_end[1] - arrow_size * math.sin(angle + math.pi / 6),
            )
            pygame.draw.polygon(screen, LINE_COLOR, [arrow_end, left_arrow, right_arrow])

    for (cx, cy, charge_magnitude) in charges:
        direction = 1 if charge_magnitude > 0 else -1

        for i in range(NUM_FIELD_LINES):
            angle = i * (2 * math.pi / NUM_FIELD_LINES)
            x = cx * zoom_level + camera_offset_x + direction * CHARGE_RADIUS * math.cos(angle) * zoom_level
            y = cy * zoom_level + camera_offset_y + direction * CHARGE_RADIUS * math.sin(angle) * zoom_level

            line_points = [(x, y)]
            steps = 0

            for _ in range(100):  # Max steps to trace the line
                ex, ey = calculate_field(x, y, charges, dielectrics, shields, zoom_level, camera_offset_x, camera_offset_y)
                magnitude = math.sqrt(ex**2 + ey**2)
                if magnitude == 0:
                    break

                step_size = FIELD_LINE_STEP * zoom_level / magnitude
                x += direction * step_size * ex
                y += direction * step_size * ey

                # Check if the new point is inside any shield
                inside_shield = False
                for shield in shields:
                    shield_x1, shield_y1, shield_width, shield_height = shield
                    shield_screen_x = shield_x1 * zoom_level + camera_offset_x
                    shield_screen_y = shield_y1 * zoom_level + camera_offset_y
                    shield_screen_width = shield_width * zoom_level
                    shield_screen_height = shield_height * zoom_level
                    if shield_screen_x <= x <= shield_screen_x + shield_screen_width and \
                       shield_screen_y <= y <= shield_screen_y + shield_screen_height:
                        inside_shield = True
                        break

                if inside_shield:
                    break  # Stop drawing the line if it enters a shield

                line_points.append((x, y))

                # Add arrowheads at intervals
                if steps % arrow_interval == 0:
                    add_arrow(line_points, charge_magnitude)

                steps += 1
                if x < 0 or x > screen_info.current_w or y < 0 or y > screen_info.current_h:
                    break

            # Draw the field line
            if len(line_points) > 1:
                pygame.draw.lines(screen, LINE_COLOR, False, line_points, LINE_WIDTH)
