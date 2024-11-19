# main.py

import math
import pygame
import sys
import io
from settings import (
    WIDTH,
    HEIGHT,
    GRID_SIZE,
    TOOLBOX_WIDTH,
    CHARGE_RADIUS,
    POSITIVE_COLOR,
    NEGATIVE_COLOR,
    COULOMB_CONSTANT,
    INITIAL_ZOOM_LEVEL,
    ZOOM_STEP,
    MIN_ZOOM_LEVEL,
    MAX_ZOOM_LEVEL,
    BASE_PAN_SPEED,
    FIELD_LINE_STEP,
    NUM_FIELD_LINES,
    LINE_COLOR,
    LINE_WIDTH,
)
from toolbox import draw_toolbox, handle_toolbox_click, get_selected_tool
from electric_field import calculate_field, draw_field_lines
from dielectric import add_dielectric, draw_dielectrics

# Import Matplotlib for rendering math text
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib import rc

# Initialize Pygame
pygame.init()
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w - TOOLBOX_WIDTH
HEIGHT = screen_info.current_h

# Set windowed fullscreen mode (borderless window)
screen = pygame.display.set_mode(
    (screen_info.current_w, screen_info.current_h)
)
pygame.display.set_caption("Electric Field Simulator")

# Zoom and camera variables
zoom_level = INITIAL_ZOOM_LEVEL
camera_offset_x, camera_offset_y = WIDTH // 2, HEIGHT // 2
charges = []
dielectrics = []  # List to store dielectric regions
is_dragging = False
drag_start_pos = (0, 0)
start_drag_pos = None  # For placing dielectrics
current_tool = "add_positive"  # Default tool

# Variables for field probe
probe_point = None  # Stores the position where the user probed the field
field_at_probe = None  # Stores the electric field at the probe point
math_details = None  # Stores detailed calculations

# Scroll offset for probe field text
scroll_offset = 0  # Initialize scroll offset

def render_latex(text, font_size=14, dpi=100, color='black', max_width=None):
    """
    Render math-formatted text to a Pygame surface using Matplotlib and savefig.
    """
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from matplotlib.font_manager import FontProperties
    import io

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

# Draw the grid
def draw_grid():
    scaled_grid_size = int(GRID_SIZE * zoom_level)
    if scaled_grid_size == 0:
        scaled_grid_size = 1  # Prevent division by zero
    start_x = int(-camera_offset_x % scaled_grid_size)
    start_y = int(-camera_offset_y % scaled_grid_size)
    for x in range(start_x, screen_info.current_w, scaled_grid_size):
        pygame.draw.line(screen, (220, 220, 220), (x, 0), (x, screen_info.current_h))
    for y in range(start_y, screen_info.current_h, scaled_grid_size):
        pygame.draw.line(screen, (220, 220, 220), (0, y), (screen_info.current_w, y))

# Draw charges on the screen
def draw_charges():
    for (world_x, world_y, charge_magnitude) in charges:
        color = POSITIVE_COLOR if charge_magnitude > 0 else NEGATIVE_COLOR
        screen_x = int(world_x * zoom_level + camera_offset_x)
        screen_y = int(world_y * zoom_level + camera_offset_y)
        radius = max(1, int(CHARGE_RADIUS * zoom_level))  # Scale radius
        pygame.draw.circle(screen, color, (screen_x, screen_y), radius)

# Add a charge at the specified location
def add_charge(x, y, charge_type):
    world_x = (x - camera_offset_x) / zoom_level
    world_y = (y - camera_offset_y) / zoom_level
    charge_magnitude = 1 if charge_type == "positive" else -1
    charges.append((world_x, world_y, charge_magnitude))
    print(f"Charge added: ({world_x:.2f}, {world_y:.2f}), type: {charge_type}")

# Remove a charge near a specified location
def remove_charge(x, y):
    global charges
    world_x = (x - camera_offset_x) / zoom_level
    world_y = (y - camera_offset_y) / zoom_level
    new_charges = []
    for (cx, cy, q) in charges:
        distance = math.hypot(cx - world_x, cy - world_y)
        if distance > (CHARGE_RADIUS * 2) / zoom_level:
            new_charges.append((cx, cy, q))
    charges = new_charges
    print(f"Charge removed near: ({world_x:.2f}, {world_y:.2f})")

# Scale zoom function to adjust camera offsets
def scale_zoom(previous_zoom, new_zoom):
    """
    Adjust the camera offsets to maintain the same view when zooming in or out.
    """
    global camera_offset_x, camera_offset_y
    scale_factor = new_zoom / previous_zoom
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Adjust camera offsets to zoom relative to mouse position
    camera_offset_x = mouse_x - (mouse_x - camera_offset_x) * scale_factor
    camera_offset_y = mouse_y - (mouse_y - camera_offset_y) * scale_factor
    print(
        f"Camera offset after zoom: ({camera_offset_x}, {camera_offset_y}), Zoom level: {new_zoom:.2f}"
    )

def draw_probe_info(screen, probe_point, field_at_probe, math_details, scroll_offset):
    """
    Draw a marker at the probe point and display the electric field information and calculations.
    Returns the bounding rectangle of the text area and scrollbar.
    """
    mouse_x, mouse_y = probe_point
    # Draw a small circle at the probe point
    pygame.draw.circle(screen, (255, 0, 0), (mouse_x, mouse_y), 5)

    # Prepare the math-formatted text
    lines = []

    # Add the formula
    lines.append(r"Electric Field at a Point:")
    lines.append(r"$\vec{E} = \sum_i \vec{E}_i$")
    lines.append(r"$\vec{E}_i = \frac{k q_i}{\varepsilon_r r_i^2} \hat{r}_i$")
    lines.append(r"$E_{i_x} = E_i \cos{\theta_i},\quad E_{i_y} = E_i \sin{\theta_i}$")
    lines.append(r"")

    # Add whether the point is inside a dielectric
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
        angle_deg = math.degrees(charge_info['angle'])
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
    lines.append(rf"$E_x = \sum E_{{i_x}} = {Ex:.2e}\ \mathrm{{N/C}}$")
    lines.append(rf"$E_y = \sum E_{{i_y}} = {Ey:.2e}\ \mathrm{{N/C}}$")
    lines.append(rf"$|\vec{{E}}| = \sqrt{{E_x^2 + E_y^2}} = {E_magnitude:.2e}\ \mathrm{{N/C}}$")
    lines.append(rf"$\theta = \tan^{{-1}}\left( \frac{{E_y}}{{E_x}} \right) = {E_angle:.2f}^\circ$")

    # Render each line and collect their sizes
    rendered_lines = []
    max_line_width = 0
    total_height = 0
    for line in lines:
        if line.strip() == "":
            line_height = 10  # Add extra space for empty lines
            rendered_lines.append((None, line_height))
            total_height += line_height + 5
            continue

        rendered_line = render_latex(line, font_size=14, dpi=100)
        line_width = rendered_line.get_width()
        line_height = rendered_line.get_height()
        rendered_lines.append((rendered_line, line_height))
        if line_width > max_line_width:
            max_line_width = line_width
        total_height += line_height + 5  # Adjust spacing between lines

    # Adjust text_x and text_y if text would go off the screen
    screen_width, screen_height = screen.get_size()
    text_x = mouse_x + 10
    text_y = mouse_y + 10

    if text_x + max_line_width > screen_width:
        text_x = mouse_x - max_line_width - 30  # Position text to the left of the probe point
        if text_x < 0:
            text_x = 10  # Ensure it's not off the left edge

    # Apply scroll offset
    text_y -= scroll_offset

    # Limit scroll_offset
    max_scroll = max(0, total_height - (screen_height - text_y - 20))
    if scroll_offset > max_scroll:
        scroll_offset = max_scroll
    if scroll_offset < 0:
        scroll_offset = 0

    # Blit the rendered lines onto the screen
    current_y = text_y
    for rendered_line, line_height in rendered_lines:
        if rendered_line:
            # Check if the line is within the visible area
            if current_y + line_height > 0 and current_y < screen_height:
                screen.blit(rendered_line, (text_x, current_y))
        current_y += line_height + 5  # Adjust spacing between lines

    # Optional: Draw a scroll bar
    scrollbar_rect = None
    visible_height = screen_height - text_y - 20
    if total_height > visible_height:
        scrollbar_height = visible_height * (visible_height / total_height)
        scrollbar_range = visible_height - scrollbar_height
        scrollbar_y = text_y + (scroll_offset / (total_height - visible_height)) * scrollbar_range
        scrollbar_rect = pygame.Rect(text_x + max_line_width + 5, scrollbar_y, 10, scrollbar_height)
        pygame.draw.rect(screen, (150, 150, 150), scrollbar_rect)

    # Calculate the bounding rectangle of the text area
    text_area_rect = pygame.Rect(
        text_x,
        text_y,
        max_line_width + 15,  # Include scrollbar width
        min(total_height, visible_height)
    )

    # Return the updated scroll_offset, text area rectangle, scrollbar rectangle, and dimensions
    return scroll_offset, text_area_rect, scrollbar_rect, total_height, visible_height

def draw_dielectric_preview(screen, start_pos, end_pos):
    """
    Draw a preview of the dielectric being added as a rectangle while dragging.
    """
    start_x, start_y = start_pos
    end_x, end_y = end_pos

    rect_x = min(start_x, end_x)
    rect_y = min(start_y, end_y)
    rect_width = abs(end_x - start_x)
    rect_height = abs(end_y - start_y)

    rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    pygame.draw.rect(screen, (0, 255, 255), rect, 2)  # Outline

def main():
    global zoom_level, camera_offset_x, camera_offset_y, is_dragging, drag_start_pos
    global start_drag_pos, current_tool, probe_point, field_at_probe, math_details
    global scroll_offset  # Declare scroll_offset as global

    running = True
    text_area_rect = None  # Initialize text_area_rect

    # New variables for scrollbar dragging
    is_dragging_scrollbar = False
    scrollbar_start_pos = None
    scrollbar_start_offset = 0
    scrollbar_rect = None
    total_height = 0
    visible_height = 0

    while running:
        screen.fill((255, 255, 255))  # Clear screen with white background
        draw_toolbox(screen)
        draw_grid()
        draw_charges()
        draw_field_lines(
            screen,
            charges,
            dielectrics,
            zoom_level,
            camera_offset_x,
            camera_offset_y,
            screen_info,
        )
        draw_dielectrics(
            screen, zoom_level, camera_offset_x, camera_offset_y, dielectrics
        )  # Draw dielectric regions

        # Draw dielectric preview if in progress
        if current_tool == "add_dielectric" and start_drag_pos:
            end_drag_pos = pygame.mouse.get_pos()
            draw_dielectric_preview(screen, start_drag_pos, end_drag_pos)

        # Draw the probe point and field info if available
        if probe_point and field_at_probe and math_details:
            # Pass scroll_offset to draw_probe_info and get updated values
            scroll_offset, text_area_rect, scrollbar_rect, total_height, visible_height = draw_probe_info(
                screen, probe_point, field_at_probe, math_details, scroll_offset)
        else:
            text_area_rect = None  # No text area when probe info is not displayed
            scrollbar_rect = None

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if event.button == 1:  # Left mouse button clicked
                    if text_area_rect and text_area_rect.collidepoint(mouse_x, mouse_y):
                        if scrollbar_rect and scrollbar_rect.collidepoint(mouse_x, mouse_y):
                            # Clicked on scrollbar
                            is_dragging_scrollbar = True
                            scrollbar_start_pos = (mouse_x, mouse_y)
                            scrollbar_start_offset = scroll_offset
                        else:
                            # Clicked inside text area but not on scrollbar
                            # Do nothing or handle text selection if needed
                            pass
                    elif mouse_x < TOOLBOX_WIDTH:
                        # Clicked inside toolbox
                        previous_tool = current_tool
                        current_tool = handle_toolbox_click(mouse_x, mouse_y)
                        # Clear probe point if switching from probe tool
                        if previous_tool == "probe_field" and current_tool != "probe_field":
                            probe_point = None
                            field_at_probe = None
                            math_details = None
                            scroll_offset = 0  # Reset scroll offset
                        if current_tool == "zoom_in":
                            previous_zoom = zoom_level
                            zoom_level = min(zoom_level + ZOOM_STEP, MAX_ZOOM_LEVEL)
                            scale_zoom(previous_zoom, zoom_level)
                        elif current_tool == "zoom_out":
                            previous_zoom = zoom_level
                            zoom_level = max(zoom_level - ZOOM_STEP, MIN_ZOOM_LEVEL)
                            scale_zoom(previous_zoom, zoom_level)
                    else:
                        # Clicked outside text area and toolbox
                        tool = get_selected_tool()
                        if tool == "add_positive":
                            add_charge(mouse_x, mouse_y, "positive")
                        elif tool == "add_negative":
                            add_charge(mouse_x, mouse_y, "negative")
                        elif tool == "erase":
                            remove_charge(mouse_x, mouse_y)
                        elif tool == "pan":
                            is_dragging = True
                            drag_start_pos = (mouse_x, mouse_y)
                        elif tool == "add_dielectric":
                            start_drag_pos = (mouse_x, mouse_y)  # Start rectangle for dielectric
                        elif tool == "probe_field":
                            # Set the probe point and calculate the field with details
                            probe_point = (mouse_x, mouse_y)
                            ex, ey, math_details = calculate_field_with_details(
                                mouse_x, mouse_y, charges, dielectrics, zoom_level, camera_offset_x, camera_offset_y)
                            field_magnitude = math.hypot(ex, ey)
                            field_at_probe = {
                                'Ex': ex,
                                'Ey': ey,
                                'E_magnitude': field_magnitude
                            }
                            scroll_offset = 0  # Reset scroll offset when new probe point is set
                            print(f"Probed field at ({mouse_x}, {mouse_y}): Ex={ex}, Ey={ey}, |E|={field_magnitude}")

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button released
                    if is_dragging_scrollbar:
                        is_dragging_scrollbar = False
                        scrollbar_start_pos = None
                        scrollbar_start_offset = 0
                    else:
                        tool = get_selected_tool()
                        if tool == "pan":
                            is_dragging = False
                        elif tool == "add_dielectric" and start_drag_pos:
                            end_drag_pos = pygame.mouse.get_pos()
                            add_dielectric(
                                *start_drag_pos,
                                *end_drag_pos,
                                epsilon_r=10.0,  # Adjust as needed
                                zoom_level=zoom_level,
                                camera_offset_x=camera_offset_x,
                                camera_offset_y=camera_offset_y,
                                dielectrics=dielectrics,
                            )
                            print(f"Dielectric drawn from {start_drag_pos} to {end_drag_pos}")
                            start_drag_pos = None

            elif event.type == pygame.MOUSEMOTION:
                if is_dragging_scrollbar:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    dy = mouse_y - scrollbar_start_pos[1]
                    # Map dy to scroll_offset
                    scrollbar_range = visible_height - (visible_height * (visible_height / total_height))
                    if scrollbar_range > 0:
                        delta_scrollbar = dy
                        scroll_ratio = delta_scrollbar / scrollbar_range
                        max_scroll = total_height - visible_height
                        scroll_offset = scrollbar_start_offset + scroll_ratio * max_scroll
                        # Clamp scroll_offset
                        scroll_offset = max(0, min(scroll_offset, max_scroll))
                elif is_dragging:
                    if event.buttons[0]:  # Left mouse button is pressed
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        dx = mouse_x - drag_start_pos[0]
                        dy = mouse_y - drag_start_pos[1]
                        camera_offset_x += dx
                        camera_offset_y += dy
                        drag_start_pos = (mouse_x, mouse_y)
                    else:
                        is_dragging = False  # Left mouse button not pressed anymore

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    previous_zoom = zoom_level
                    zoom_level = min(zoom_level + ZOOM_STEP, MAX_ZOOM_LEVEL)
                    scale_zoom(previous_zoom, zoom_level)
                    print(f"Zooming in via keyboard. New zoom level: {zoom_level:.2f}")
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    previous_zoom = zoom_level
                    zoom_level = max(zoom_level - ZOOM_STEP, MIN_ZOOM_LEVEL)
                    scale_zoom(previous_zoom, zoom_level)
                    print(f"Zooming out via keyboard. New zoom level: {zoom_level:.2f}")

            elif event.type == pygame.MOUSEWHEEL:
                # Handle mouse wheel scrolling when probe field is active and mouse is over text area
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if text_area_rect and text_area_rect.collidepoint(mouse_x, mouse_y):
                    # Adjust scroll_offset
                    scroll_speed = 20  # Adjust scroll speed as needed
                    scroll_offset -= event.y * scroll_speed
                    # Limit scroll_offset will be handled in draw_probe_info
                    print(f"Scroll offset updated: {scroll_offset}")
                else:
                    # Mouse wheel used outside text area; handle as needed (e.g., zoom)
                    pass

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def calculate_field_with_details(px, py, charges, dielectrics, zoom_level, camera_offset_x, camera_offset_y):
    """
    Calculate the electric field at a point (px, py) and collect detailed calculation steps.
    """
    total_ex, total_ey = 0.0, 0.0
    math_details = {'charges': []}

    # Convert screen coordinates to world coordinates
    world_px = (px - camera_offset_x) / zoom_level
    world_py = (py - camera_offset_y) / zoom_level

    # Check if the point is inside any dielectric region
    epsilon_r = 1.0  # Default relative permittivity (vacuum)
    for (x1, y1, width, height, dielectric_epsilon) in dielectrics:
        x2 = x1 + width
        y2 = y1 + height
        if x1 <= world_px <= x2 and y1 <= world_py <= y2:
            epsilon_r = dielectric_epsilon
            break
    math_details['epsilon_r'] = epsilon_r

    # Calculate contributions from each charge
    for (cx, cy, q) in charges:
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

if __name__ == "__main__":
    main()
