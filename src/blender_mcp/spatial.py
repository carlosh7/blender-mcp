
import math

def generate_ascii_view(objects, width=40, height=20, scale=2.0):
    """
    Generates a top-down ASCII grid of the scene.
    objects: list of dicts with {'name': str, 'location': [x, y, z], 'type': str}
    scale: meters per character (roughly)
    """
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Center of the grid is (0,0) in Blender
    center_x = width // 2
    center_y = height // 2
    
    # Draw axes
    for x in range(width):
        if grid[center_y][x] == ' ': grid[center_y][x] = '-'
    for y in range(height):
        if grid[y][center_x] == ' ': grid[y][center_x] = '|'
    grid[center_y][center_x] = '+'

    # Place objects
    for obj in objects:
        loc = obj.get('location', [0, 0, 0])
        # Blender Y is depth in top-down, but in terminal Y is vertical (reversed)
        x_idx = center_x + int(loc[0] / scale)
        y_idx = center_y - int(loc[1] / scale)
        
        if 0 <= x_idx < width and 0 <= y_idx < height:
            char = obj['name'][0].upper() if obj['name'] else '?'
            if obj['type'] == 'LIGHT': char = '*'
            elif obj['type'] == 'CAMERA': char = '>'
            grid[y_idx][x_idx] = char

    # Convert to string
    lines = []
    lines.append("Top-Down Scene View (X: Horizontal, Y: Vertical/Depth)")
    lines.append("+" + "-" * width + "+")
    for row in grid:
        lines.append("|" + "".join(row) + "|")
    lines.append("+" + "-" * width + "+")
    lines.append(f"Scale: 1 char ≈ {scale}m. Origin (+) is center.")
    
    return "\n".join(lines)

def get_spatial_summary(scene_info):
    """
    Returns a combined summary including ASCII and object list.
    """
    objects = scene_info.get('objects', [])
    ascii_view = generate_ascii_view(objects)
    
    summary = [
        "### SPATIAL REASONING SUMMARY ###",
        ascii_view,
        "\nDetailed Object List:",
    ]
    
    for obj in objects:
        loc = obj['location']
        summary.append(f"- {obj['name']} ({obj['type']}): pos=[{loc[0]:.2f}, {loc[1]:.2f}, {loc[2]:.2f}]")
        
    return "\n".join(summary)
