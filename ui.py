# ui.py

import pygame
import io
import math
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from settings import (
    TOOLBOX_WIDTH,
    SIDEBAR_BACKGROUND_COLOR,
    SIDEBAR_TITLE_FONT_SIZE,
    SCROLLBAR_COLOR,
    SCROLLBAR_WIDTH,
    SIDEBAR_TEXT_PADDING,
    LATEX_FONT_SIZE,
    LATEX_DPI,
    DIELECTRIC_PREVIEW_COLOR,
    DIELECTRIC_PREVIEW_WIDTH,
    PROBE_INFO_MAX_WIDTH,
    WHITE,  # Ensure WHITE is imported
    BLACK,  # Ensure BLACK is imported
)

# Global scroll offset for probe information
scroll_offset = 0

def render_latex(text, font_size=LATEX_FONT_SIZE, dpi=LATEX_DPI, color='black', max_width=None):
    """
    Render math-formatted text to a Pygame surface using Matplotlib and savefig.
    """
    # Create a figure and axis with padding
    fig = Figure()
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    ax.axis('off')

    # Set font properties
    font_properties = FontProperties(size=font_size)

    # Add text
    t = ax.text(0.5, 0.5, text, fontproperties=font_properties, color=color,
                horizontalalignment='center', verticalalignment='center')

    # Draw the canvas to compute text size
    canvas.draw()
    renderer = canvas.get_renderer()
    bbox = t.get_window_extent(renderer=renderer).expanded(1.2, 1.2)

    # Calculate width and height in pixels
    width, height = int(bbox.width), int(bbox.height)

    # Adjust figure size
    fig.set_size_inches(width / dpi, height / dpi)
    ax.set_position([0, 0, 1, 1])
    ax.set_xlim(bbox.x0, bbox.x1)
    ax.set_ylim(bbox.y0, bbox.y1)
    t.set_position(((bbox.x0 + bbox.x1) / 2, (bbox.y0 + bbox.y1) / 2))

    # Redraw the canvas with the updated figure size
    canvas.draw()

    # Save the figure to a buffer with tight bounding box
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, format='png', transparent=True,
               bbox_inches='tight', pad_inches=0.05)
    plt.close(fig)
    buf.seek(0)

    # Load image with Pygame
    image = pygame.image.load(buf, 'png')

    # Optionally scale down the image if it exceeds max_width
    if max_width and image.get_width() > max_width:
        scale_factor = max_width / image.get_width()
        new_width = int(image.get_width() * scale_factor)
        new_height = int(image.get_height() * scale_factor)
        image = pygame.transform.smoothscale(image, (new_width, new_height))

    return image.convert_alpha()  # Convert for faster blitting and transparency

def draw_probe_info_sidebar(screen, probe_point, field_at_probe, math_details):
    """
    Display probe information in a fixed sidebar on the right side of the screen with a scrollbar.
    """
    global scroll_offset  # Use the global scroll offset

    sidebar_width = TOOLBOX_WIDTH
    sidebar_x = screen.get_width() - sidebar_width
    sidebar_y = 0
    sidebar_height = screen.get_height()

    # Draw sidebar background
    pygame.draw.rect(screen, SIDEBAR_BACKGROUND_COLOR, (sidebar_x, sidebar_y, sidebar_width, sidebar_height))

    # Title
    title_font = pygame.font.Font(None, SIDEBAR_TITLE_FONT_SIZE)
    title_text = title_font.render("Probe Information", True, BLACK)  # Using BLACK
    screen.blit(title_text, (sidebar_x + 10, 10))

    # Prepare the math-formatted text
    lines = []

    # Add the formula
    lines.append(r"Electric Field at Probe Point:")
    lines.append(r"$\vec{E} = \sum_i \vec{E}_i$")
    lines.append(r"$\vec{E}_i = \frac{k q_i}{\varepsilon_r r_i^2} \hat{r}_i$")
    lines.append(r"$E_{x} = \sum E_{i_x}$")
    lines.append(r"$E_{y} = \sum E_{i_y}$")
    lines.append(r"$|\vec{E}| = \sqrt{E_x^2 + E_y^2}$")
    lines.append(r"$\theta = \tan^{-1}\left( \frac{E_y}{E_x} \right)$")
    lines.append(r"")

    # Add dielectric information
    if math_details['epsilon_r'] > 1.0:
        dielectric_info = r"Inside dielectric ($\varepsilon_r = {:.2f}$)".format(math_details['epsilon_r'])
    else:
        dielectric_info = r"In free space ($\varepsilon_r = 1.00$)"
    lines.append(dielectric_info)
    lines.append(r"")

    # Show contributions from each charge
    lines.append(r"Contributions from Charges:")
    for idx, charge_info in enumerate(math_details['charges']):
        q = charge_info['q']
        r = math.sqrt(charge_info['r_squared'])
        angle_deg = math.degrees(math.atan2(charge_info['ey'], charge_info['ex']))
        ex = charge_info['ex']
        ey = charge_info['ey']
        lines.append(rf"Charge {idx+1}:")
        lines.append(rf"$q_{{{idx+1}}} = {q:+.2e}\ \mathrm{{C}}$")
        lines.append(rf"$r_{{{idx+1}}} = {r:.2f}\ \mathrm{{m}}$")
        lines.append(rf"$\theta_{{{idx+1}}} = {angle_deg:.2f}^\circ$")
        lines.append(rf"$E_{{{idx+1}x}} = {ex:.2e}\ \mathrm{{N/C}}$")
        lines.append(rf"$E_{{{idx+1}y}} = {ey:.2e}\ \mathrm{{N/C}}$")
        lines.append(r"")

    # Total electric field
    Ex = field_at_probe['Ex']
    Ey = field_at_probe['Ey']
    E_magnitude = field_at_probe['E_magnitude']
    E_angle = math.degrees(math.atan2(Ey, Ex))

    # Show the total electric field calculation
    lines.append(r"Total Electric Field:")
    lines.append(rf"$E_x = {Ex:.2e}\ \mathrm{{N/C}}$")
    lines.append(rf"$E_y = {Ey:.2e}\ \mathrm{{N/C}}$")
    lines.append(rf"$|\vec{{E}}| = {E_magnitude:.2e}\ \mathrm{{N/C}}$")
    lines.append(rf"$\theta = {E_angle:.2f}^\circ$")
    lines.append(r"")

    # Render each line and calculate total content height
    rendered_lines = []
    max_line_width = 0
    total_content_height = 0
    for line in lines:
        if line.strip() == "":
            # Add space for empty lines
            rendered_lines.append((None, 10))
            total_content_height += 10 + 5  # Line height + spacing
            continue

        rendered_line = render_latex(line, font_size=LATEX_FONT_SIZE, dpi=LATEX_DPI, max_width=PROBE_INFO_MAX_WIDTH)
        line_width, line_height = rendered_line.get_size()
        rendered_lines.append((rendered_line, line_height))
        if line_width > max_line_width:
            max_line_width = line_width
        total_content_height += line_height + 5  # Line height + spacing

    # Clamp scroll_offset to valid range
    if total_content_height > sidebar_height - 50:  # 50px reserved for title
        max_scroll = total_content_height - (sidebar_height - 50)
        scroll_offset = max(0, min(scroll_offset, max_scroll))
    else:
        scroll_offset = 0  # Reset if content fits

    # Blit the rendered lines onto the sidebar with scroll_offset
    y_offset = 50 - scroll_offset  # Starting y position for text within sidebar

    for rendered_line, line_height in rendered_lines:
        if rendered_line:
            # Only blit if within the visible area
            if y_offset + line_height > 50 and y_offset < sidebar_height - 20:
                screen.blit(rendered_line, (sidebar_x + 10, y_offset))
        y_offset += line_height + 5  # Move down for the next line

    # Draw scrollbar if content exceeds sidebar height
    if total_content_height > (sidebar_height - 50):
        scrollbar_height = max(20, (sidebar_height - 50) * (sidebar_height - 50) // total_content_height)
        scrollbar_y = 50 + (scroll_offset * (sidebar_height - 50 - scrollbar_height) // (total_content_height - (sidebar_height - 50)))
        scrollbar_rect = pygame.Rect(sidebar_x + sidebar_width - 15, scrollbar_y, SCROLLBAR_WIDTH, scrollbar_height)
        pygame.draw.rect(screen, SCROLLBAR_COLOR, scrollbar_rect)

def handle_scroll(event):
    """
    Handles scrolling within the probe information sidebar.
    """
    global scroll_offset
    scroll_speed = 20  # Adjust scroll speed as needed
    if event.type == pygame.MOUSEWHEEL:
        scroll_offset -= event.y * scroll_speed
        # Clamp scroll_offset to prevent over-scrolling
        if scroll_offset < 0:
            scroll_offset = 0
        # The maximum scroll limit is handled in draw_probe_info_sidebar
        print(f"Scroll offset updated: {scroll_offset}")

def draw_dielectric_preview(screen, start_pos, end_pos):
    """
    Draw a preview of the dielectric being added as a rectangle while dragging.
    """
    # These constants are imported from settings.py
    # Ensure DIELECTRIC_PREVIEW_COLOR and DIELECTRIC_PREVIEW_WIDTH are imported
    start_x, start_y = start_pos
    end_x, end_y = end_pos

    rect_x = min(start_x, end_x)
    rect_y = min(start_y, end_y)
    rect_width = abs(end_x - start_x)
    rect_height = abs(end_y - start_y)

    rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    pygame.draw.rect(screen, DIELECTRIC_PREVIEW_COLOR, rect, DIELECTRIC_PREVIEW_WIDTH)  # Cyan outline
