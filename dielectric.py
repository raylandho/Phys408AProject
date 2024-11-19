# dielectric.py

import pygame
import math
from settings import (
    CHARGE_RADIUS,
    COULOMB_CONSTANT,
    POSITIVE_COLOR,
    NEGATIVE_COLOR
)

def add_dielectric(start_x, start_y, end_x, end_y, epsilon_r, zoom_level, camera_offset_x, camera_offset_y, dielectrics):
    """
    Add a dielectric as a rectangular region.
    """
    # Convert screen coordinates to world coordinates
    start_world_x = (start_x - camera_offset_x) / zoom_level
    start_world_y = (start_y - camera_offset_y) / zoom_level
    end_world_x = (end_x - camera_offset_x) / zoom_level
    end_world_y = (end_y - camera_offset_y) / zoom_level

    # Ensure consistent rectangle corners
    rect_x = min(start_world_x, end_world_x)
    rect_y = min(start_world_y, end_world_y)
    rect_width = abs(end_world_x - start_world_x)
    rect_height = abs(end_world_y - start_world_y)

    # Add the dielectric as a tuple with relative permittivity
    dielectrics.append((rect_x, rect_y, rect_width, rect_height, epsilon_r))
    print(f"Dielectric added at ({rect_x:.2f}, {rect_y:.2f}) with size {rect_width:.2f} x {rect_height:.2f}, epsilon_r = {epsilon_r}")

def calculate_field_at_point(charges, world_x, world_y, epsilon_r=1.0):
    """
    Calculate the net electric field at a given world coordinate (world_x, world_y).
    """
    Ex, Ey = 0.0, 0.0
    for (charge_x, charge_y, charge_magnitude) in charges:
        dx = world_x - charge_x
        dy = world_y - charge_y
        r_squared = dx ** 2 + dy ** 2
        if r_squared == 0:
            continue  # Skip charges that are at the same point
        r = math.sqrt(r_squared)
        E = COULOMB_CONSTANT * charge_magnitude / (r_squared * epsilon_r)
        Ex += E * (dx / r)
        Ey += E * (dy / r)
    return Ex, Ey

def draw_dielectrics(screen, zoom_level, camera_offset_x, camera_offset_y, dielectrics, charges):
    """
    Draw dielectrics as rectangles on the screen, including bound charges based on the field direction.
    """
    for (world_x, world_y, width, height, epsilon_r) in dielectrics:
        # Convert world coordinates to screen coordinates
        screen_x = int(world_x * zoom_level + camera_offset_x)
        screen_y = int(world_y * zoom_level + camera_offset_y)
        screen_width = int(width * zoom_level)
        screen_height = int(height * zoom_level)

        # Draw the dielectric rectangle with transparency
        dielectric_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        dielectric_color = (0, 255, 255, 100)  # Cyan with transparency
        dielectric_surface.fill(dielectric_color)
        screen.blit(dielectric_surface, (screen_x, screen_y))

        # Draw the border
        rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Black border

        # Calculate polarization direction based on electric field at the center
        center_world_x = world_x + width / 2
        center_world_y = world_y + height / 2
        Ex, Ey = calculate_field_at_point(charges, center_world_x, center_world_y, epsilon_r)

        # Determine dominant field direction
        abs_Ex = abs(Ex)
        abs_Ey = abs(Ey)

        # Threshold to determine dominance (you can adjust this as needed)
        threshold = 0.1 * max(abs_Ex, abs_Ey)
        
        # Initialize sides to None
        top_side = bottom_side = left_side = right_side = None

        # Decide which sides to place bound charges on based on field direction
        if abs_Ey > threshold:
            if Ey > 0:
                # Field points upward: positive at bottom, negative at top
                top_side = "negative"
                bottom_side = "positive"
            else:
                # Field points downward: positive at top, negative at bottom
                top_side = "positive"
                bottom_side = "negative"

        if abs_Ex > threshold:
            if Ex > 0:
                # Field points to the right: positive on right, negative on left
                right_side = "positive"
                left_side = "negative"
            else:
                # Field points to the left: positive on left, negative on right
                right_side = "negative"
                left_side = "positive"

        # Function to place bound charges along a side
        def place_bound_charges(side):
            num_charges = max(5, (screen_width if side in ["top", "bottom"] else screen_height) // 30)
            for i in range(num_charges):
                if side == "top":
                    x = screen_x + int(i * screen_width / num_charges)
                    y = screen_y
                    color = NEGATIVE_COLOR if top_side == "negative" else POSITIVE_COLOR
                elif side == "bottom":
                    x = screen_x + int(i * screen_width / num_charges)
                    y = screen_y + screen_height
                    color = POSITIVE_COLOR if bottom_side == "positive" else NEGATIVE_COLOR
                elif side == "left":
                    x = screen_x
                    y = screen_y + int(i * screen_height / num_charges)
                    color = NEGATIVE_COLOR if left_side == "negative" else POSITIVE_COLOR
                elif side == "right":
                    x = screen_x + screen_width
                    y = screen_y + int(i * screen_height / num_charges)
                    color = POSITIVE_COLOR if right_side == "positive" else NEGATIVE_COLOR
                pygame.draw.circle(screen, color, (x, y), 5)  # Bound charge marker

        # Place bound charges on relevant sides
        if top_side:
            place_bound_charges("top")
        if bottom_side:
            place_bound_charges("bottom")
        if left_side:
            place_bound_charges("left")
        if right_side:
            place_bound_charges("right")
