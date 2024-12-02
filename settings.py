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

# **Additions Start Here**

# UI Settings

# Sidebar Settings
SIDEBAR_BACKGROUND_COLOR = (230, 230, 230)  # Light gray background for the sidebar
SIDEBAR_TITLE_FONT_SIZE = 30              # Font size for the sidebar title
SIDEBAR_TEXT_PADDING = 10                  # Padding for text within the sidebar

# Scrollbar Settings
SCROLLBAR_COLOR = (150, 150, 150)          # Dark gray color for the scrollbar
SCROLLBAR_WIDTH = 10                       # Width of the scrollbar in pixels

# LaTeX Rendering Settings
LATEX_FONT_SIZE = 16                       # Font size for LaTeX-rendered text
LATEX_DPI = 100                            # DPI for LaTeX rendering

# Dielectric Preview Settings
DIELECTRIC_PREVIEW_COLOR = (0, 255, 255)   # Cyan color for dielectric outlines
DIELECTRIC_PREVIEW_WIDTH = 2               # Thickness of the dielectric outline

# Toolbox Button Settings
TOOLBOX_BUTTON_PADDING = 10                # Padding inside toolbox buttons

# Probe Information Sidebar Settings
PROBE_INFO_MAX_WIDTH = TOOLBOX_WIDTH - 20  # Maximum width for content inside the sidebar

# Color Definitions
WHITE = (255, 255, 255)  # White color
BLACK = (0, 0, 0)        # Black color (in case it's needed separately)

# Shield Settings
SHIELD_COLOR = (0, 0, 0)  # Black color for shields
SHIELD_WIDTH = 3          # Thickness of the shield boundary
SHIELD_EPSILON_R = 1.0    # Relative permittivity for shields (conductors have high epsilon)

# Conductor settings
CONDUCTOR_COLOR = (128, 128, 128)  # Gray
INDUCED_CHARGE_RADIUS = 5          # Radius for induced charges
INDUCED_CHARGE_COLOR = (0, 255, 0) 