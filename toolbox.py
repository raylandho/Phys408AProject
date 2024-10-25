# toolbox.py

import pygame
from settings import TOOLBOX_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, BUTTON_HIGHLIGHT_COLOR, TEXT_COLOR, FONT_SIZE

# Toolbox button definitions and selected tool
buttons = [
    {"label": "Add Positive", "tool": "add_positive"},
    {"label": "Add Negative", "tool": "add_negative"},
    {"label": "Erase", "tool": "erase"},
    {"label": "Zoom In", "tool": "zoom_in"},
    {"label": "Zoom Out", "tool": "zoom_out"},
    {"label": "Pan", "tool": "pan"}
]
selected_tool = "add_positive"

# Function to get the font (after pygame.init())
def get_font():
    return pygame.font.Font(None, FONT_SIZE)

# Draw the toolbox with buttons
def draw_toolbox(screen):
    font = get_font()
    for i, button in enumerate(buttons):
        y = i * BUTTON_HEIGHT
        color = BUTTON_HIGHLIGHT_COLOR if button["tool"] == selected_tool else BUTTON_COLOR
        pygame.draw.rect(screen, color, (0, y, TOOLBOX_WIDTH, BUTTON_HEIGHT))
        text = font.render(button["label"], True, TEXT_COLOR)
        screen.blit(text, (10, y + (BUTTON_HEIGHT - FONT_SIZE) // 2))

# Check if a click is within the toolbox and update the selected tool
def handle_toolbox_click(x, y):
    global selected_tool
    if x < TOOLBOX_WIDTH:
        button_index = y // BUTTON_HEIGHT
        if 0 <= button_index < len(buttons):
            selected_tool = buttons[button_index]["tool"]
    return selected_tool

# Return the currently selected tool
def get_selected_tool():
    return selected_tool
