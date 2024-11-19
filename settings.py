# settings.py

# Screen settings
WIDTH = 800  # Width of the main display area (excluding toolbox)
HEIGHT = 600  # Height of the display area

# Toolbox settings
TOOLBOX_WIDTH = 200  # Width of the toolbox section on the side
BUTTON_HEIGHT = 50   # Height of each button in the toolbox
BUTTON_COLOR = (200, 200, 200)  # Light gray for buttons
BUTTON_HIGHLIGHT_COLOR = (150, 150, 150)  # Darker gray for selected button
TOOLBOX_COLOR = (220, 220, 220)  # Background color for the toolbox
TEXT_COLOR = (0, 0, 0)  # Black for text
FONT_SIZE = 20  # Font size for button labels

# Grid and charge settings
GRID_SIZE = 40
CHARGE_RADIUS = 10
POSITIVE_COLOR = (255, 0, 0)
NEGATIVE_COLOR = (0, 0, 255)
COULOMB_CONSTANT = 8.9875e9
NUM_FIELD_LINES = 32
LINE_COLOR = (0, 200, 0)
LINE_WIDTH = 1
INITIAL_ZOOM_LEVEL = 1.0
ZOOM_STEP = 0.1
MIN_ZOOM_LEVEL = 0.5
MAX_ZOOM_LEVEL = 3.0
BASE_PAN_SPEED = 2
FIELD_LINE_STEP = 5
