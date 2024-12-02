# toolbox.py

import pygame
from settings import (
    TOOLBOX_WIDTH,
    BUTTON_HEIGHT,
    BUTTON_COLOR,
    BUTTON_HIGHLIGHT_COLOR,
    TEXT_COLOR,
    FONT_SIZE,
)

# Toolbox button definitions and selected tool
buttons = [
    {"label": "Add Positive", "tool": "add_positive"},
    {"label": "Add Negative", "tool": "add_negative"},
    {"label": "Erase", "tool": "erase"},
    {"label": "Zoom In", "tool": "zoom_in"},
    {"label": "Zoom Out", "tool": "zoom_out"},
    {"label": "Pan", "tool": "pan"},
    {"label": "Add Dielectric", "tool": "add_dielectric"},
    {"label": "Remove Dielectric", "tool": "remove_dielectric"},
    {"label": "Probe Field", "tool": "probe_field"},  
    {"label": "Add Shield", "tool": "add_shield"},  # New Shield Tool
    {"label": "Remove Shield", "tool": "remove_shield"}, 
]
selected_tool = "add_positive"  # Default selected tool


# Function to get the font (after pygame.init())
def get_font():
    return pygame.font.Font(None, FONT_SIZE)


# Draw the toolbox with buttons
def draw_toolbox(screen):
    font = get_font()
    for i, button in enumerate(buttons):
        y = i * BUTTON_HEIGHT
        color = (
            BUTTON_HIGHLIGHT_COLOR
            if button["tool"] == selected_tool
            else BUTTON_COLOR
        )
        pygame.draw.rect(screen, color, (0, y, TOOLBOX_WIDTH, BUTTON_HEIGHT))
        text = font.render(button["label"], True, TEXT_COLOR)
        text_rect = text.get_rect(center=(TOOLBOX_WIDTH // 2, y + BUTTON_HEIGHT // 2))
        screen.blit(text, text_rect)


# Check if a click is within the toolbox and update the selected tool
def handle_toolbox_click(x, y):
    global selected_tool
    if x < TOOLBOX_WIDTH:
        button_index = y // BUTTON_HEIGHT
        if 0 <= button_index < len(buttons):
            selected_tool = buttons[button_index]["tool"]
            print(f"Selected tool: {selected_tool}")  # Debugging output
            return selected_tool
    return None


# Return the currently selected tool
def get_selected_tool():
    return selected_tool