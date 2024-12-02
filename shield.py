# shield.py

import pygame
import math
from settings import (
    SHIELD_COLOR,
    SHIELD_WIDTH,
    CHARGE_RADIUS,
    COULOMB_CONSTANT,
    POSITIVE_COLOR,
    NEGATIVE_COLOR,
)

def add_shield(start_x, start_y, end_x, end_y, zoom_level, camera_offset_x, camera_offset_y, shields):
    """
    Add a shield as a rectangular conductive region.
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

    # Add the shield as a tuple (x, y, width, height)
    shields.append((rect_x, rect_y, rect_width, rect_height))
    print(f"Shield added at ({rect_x:.2f}, {rect_y:.2f}) with size {rect_width:.2f} x {rect_height:.2f}")

def remove_shield(x, y, zoom_level, camera_offset_x, camera_offset_y, shields):
    """
    Remove the shield near the clicked position.
    """
    world_x = (x - camera_offset_x) / zoom_level
    world_y = (y - camera_offset_y) / zoom_level

    for idx, (rect_x, rect_y, width, height) in enumerate(shields):
        if rect_x <= world_x <= rect_x + width and rect_y <= world_y <= rect_y + height:
            del shields[idx]
            print(f"Shield removed at ({rect_x}, {rect_y})")
            return
    print("No shield found at the clicked position.")

def draw_shields(screen, zoom_level, camera_offset_x, camera_offset_y, shields):
    """
    Draw shields as rectangles on the screen.
    """
    for (world_x, world_y, width, height) in shields:
        # Convert world coordinates to screen coordinates
        screen_x = int(world_x * zoom_level + camera_offset_x)
        screen_y = int(world_y * zoom_level + camera_offset_y)
        screen_width = int(width * zoom_level)
        screen_height = int(height * zoom_level)

        # Draw the shield rectangle
        shield_rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        pygame.draw.rect(screen, SHIELD_COLOR, shield_rect, SHIELD_WIDTH)

        # Optionally, fill the shield with a transparent color to indicate it's conductive
        shield_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        shield_surface.fill((50, 50, 50, 50))  # Semi-transparent gray
        screen.blit(shield_surface, (screen_x, screen_y))
