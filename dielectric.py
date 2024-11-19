# dielectric.py

import pygame
from settings import CHARGE_RADIUS

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

    # Add the dielectric as a rectangle with relative permittivity
    dielectrics.append((rect_x, rect_y, rect_width, rect_height, epsilon_r))
    print(f"Dielectric added at ({rect_x:.2f}, {rect_y:.2f}) with size {rect_width:.2f} x {rect_height:.2f}, epsilon_r = {epsilon_r}")

def draw_dielectrics(screen, zoom_level, camera_offset_x, camera_offset_y, dielectrics):
    """
    Draw dielectrics as rectangles on the screen.
    """
    for (world_x, world_y, width, height, epsilon_r) in dielectrics:
        screen_x = int(world_x * zoom_level + camera_offset_x)
        screen_y = int(world_y * zoom_level + camera_offset_y)
        screen_width = int(width * zoom_level)
        screen_height = int(height * zoom_level)

        # Create a surface for the dielectric with alpha
        dielectric_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        dielectric_color = (0, 255, 255, 100)  # Cyan with transparency
        dielectric_surface.fill(dielectric_color)
        screen.blit(dielectric_surface, (screen_x, screen_y))

        # Draw border around the dielectric
        rect = pygame.Rect(screen_x, screen_y, screen_width, screen_height)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Black border
