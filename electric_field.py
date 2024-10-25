# electric_field.py

import pygame
import math
from settings import CHARGE_RADIUS, FIELD_LINE_STEP, LINE_COLOR, LINE_WIDTH, NUM_FIELD_LINES, COULOMB_CONSTANT

def calculate_field(px, py, charges, zoom_level, camera_offset_x, camera_offset_y):
    total_ex, total_ey = 0, 0
    for (cx, cy, q) in charges:
        dx = (px - (cx * zoom_level + camera_offset_x))
        dy = (py - (cy * zoom_level + camera_offset_y))
        r_squared = (dx ** 2 + dy ** 2) / (zoom_level ** 2)
        if r_squared == 0:
            continue
        e_magnitude = COULOMB_CONSTANT * q / r_squared
        angle = math.atan2(dy, dx)
        total_ex += e_magnitude * math.cos(angle)
        total_ey += e_magnitude * math.sin(angle)
    return total_ex, total_ey

def draw_field_lines(screen, charges, zoom_level, camera_offset_x, camera_offset_y, screen_info):
    arrow_interval = 10  # Interval to place arrows along the line
    arrow_size = 5       # Size of the arrowhead

    for (cx, cy, charge_magnitude) in charges:
        # Determine the line direction for positive or negative charges
        direction = 1 if charge_magnitude > 0 else -1

        for i in range(NUM_FIELD_LINES):
            angle = i * (2 * math.pi / NUM_FIELD_LINES)
            x = cx * zoom_level + camera_offset_x + direction * CHARGE_RADIUS * math.cos(angle) * zoom_level
            y = cy * zoom_level + camera_offset_y + direction * CHARGE_RADIUS * math.sin(angle) * zoom_level

            line_points = [(x, y)]
            steps = 0  # Counter for placing arrows

            for _ in range(100):
                ex, ey = calculate_field(x, y, charges, zoom_level, camera_offset_x, camera_offset_y)
                magnitude = math.sqrt(ex ** 2 + ey ** 2)
                if magnitude == 0:
                    break

                # Normalize and adjust step size
                step_size = FIELD_LINE_STEP * zoom_level / magnitude
                x += direction * step_size * ex
                y += direction * step_size * ey
                line_points.append((x, y))

                # Add arrowheads at intervals
                if steps % arrow_interval == 0 and len(line_points) > 1:
                    arrow_end = line_points[-1]
                    arrow_start = line_points[-2]
                    dx = arrow_end[0] - arrow_start[0]
                    dy = arrow_end[1] - arrow_start[1]
                    angle = math.atan2(dy, dx)
                    angle += math.pi if charge_magnitude < 0 else 0

                    left_arrow = (
                        arrow_end[0] - arrow_size * math.cos(angle - math.pi / 6),
                        arrow_end[1] - arrow_size * math.sin(angle - math.pi / 6),
                    )
                    right_arrow = (
                        arrow_end[0] - arrow_size * math.cos(angle + math.pi / 6),
                        arrow_end[1] - arrow_size * math.sin(angle + math.pi / 6),
                    )
                    pygame.draw.polygon(screen, LINE_COLOR, [arrow_end, left_arrow, right_arrow])

                steps += 1
                if x < 0 or x > screen_info.current_w or y < 0 or y > screen_info.current_h:
                    break

            if len(line_points) > 1:
                pygame.draw.lines(screen, LINE_COLOR, False, line_points, LINE_WIDTH)
