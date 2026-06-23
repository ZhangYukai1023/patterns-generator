"""Others pattern generator — Zigzag (Z字形), Star (米字型)."""

import numpy as np
from PIL import Image, ImageDraw


# ---- Zigzag (Z字形) ---- #


def generate_zigzag(size: int, hp: int, dense: bool = True) -> np.ndarray:
    """Generate Z-shaped pattern.

    Dense: grid of Z-shapes tiled across the canvas, each isolated in its cell.
    Isolated: single Z-shape centered.

    Each Z = top bar → diagonal ↘ → bottom bar.
    Cell: 2*hp × 2*hp, Z centered in the middle hp×hp area.

    Args:
        size: Image size.
        hp: Z bounding box width (= height).
        dense: True for grid, False for single.

    Returns:
        uint8 numpy array with values 0 or 255.
    """
    arr = np.zeros((size, size), dtype=np.uint8)
    thickness = max(2, hp // 4)

    if hp <= 0:
        return arr

    if dense:
        # Cell: 2*hp × 2*hp with Z centered in the hp×hp middle area
        cell_size = 2 * hp
        cell = Image.new("L", (cell_size, cell_size), 0)
        draw = ImageDraw.Draw(cell)

        margin = hp // 2
        left = margin
        right = margin + hp - 1
        top = margin
        bottom = margin + hp - 1

        # Three segments of a standard Z
        draw.line([(left, top), (right, top)], fill=255, width=thickness)
        draw.line([(right, top), (left, bottom)], fill=255, width=thickness)
        draw.line([(left, bottom), (right, bottom)], fill=255, width=thickness)

        cell_arr = np.array(cell, dtype=np.uint8)
        tiles = (size + cell_size - 1) // cell_size
        arr = np.tile(cell_arr, (tiles, tiles))[:size, :size]
    else:
        # Single Z centered
        c = size // 2
        half = hp // 2
        left, right = c - half, c + half
        top, bottom = c - half, c + half

        img = Image.fromarray(arr, mode="L")
        draw = ImageDraw.Draw(img)
        draw.line([(left, top), (right, top)], fill=255, width=thickness)
        draw.line([(right, top), (left, bottom)], fill=255, width=thickness)
        draw.line([(left, bottom), (right, bottom)], fill=255, width=thickness)
        arr[:, :] = np.array(img, dtype=np.uint8)

    return arr


# ---- Star / Cross (米字型) ---- #


def generate_star(size: int, hp: int, dense: bool = True) -> np.ndarray:
    """Generate star/cross (米字型) pattern.

    Dense: periodic 米-shapes across the canvas.
    Isolated: single 米-shape centered.

    Args:
        size: Image size.
        hp: Bounding box size.
        dense: True for periodic, False for single.

    Returns:
        uint8 numpy array with values 0 or 255.
    """
    arr = np.zeros((size, size), dtype=np.uint8)
    line_width = max(1, hp // 5)

    if dense:
        cell_size = 2 * hp
        if cell_size == 0:
            return arr
        cell_img = Image.new("L", (cell_size, cell_size), 0)
        draw = ImageDraw.Draw(cell_img)
        c = hp - 0.5
        r = hp / 2.0
        draw.line([(c - r, c), (c + r, c)], fill=255, width=line_width)
        draw.line([(c, c - r), (c, c + r)], fill=255, width=line_width)
        draw.line([(c - r, c - r), (c + r, c + r)], fill=255, width=line_width)
        draw.line([(c + r, c - r), (c - r, c + r)], fill=255, width=line_width)
        cell_arr = np.array(cell_img, dtype=np.uint8)
        tiles = (size + cell_size - 1) // cell_size
        arr = np.tile(cell_arr, (tiles, tiles))[:size, :size]
    else:
        c = size // 2
        r = max(1, hp // 2)
        img = Image.fromarray(arr, mode="L")
        draw = ImageDraw.Draw(img)
        draw.line([(c - r, c), (c + r, c)], fill=255, width=line_width)
        draw.line([(c, c - r), (c, c + r)], fill=255, width=line_width)
        draw.line([(c - r, c - r), (c + r, c + r)], fill=255, width=line_width)
        draw.line([(c + r, c - r), (c - r, c + r)], fill=255, width=line_width)
        arr[:, :] = np.array(img, dtype=np.uint8)

    return arr


# ---- Diamond Grid (菱形网格) ---- #


def generate_diamond_grid(size: int, hp: int, dense: bool = True) -> np.ndarray:
    """Generate diamond grid pattern.

    Dense: periodic diamond shapes tiled across the canvas.
    Isolated: single diamond shape centered.

    A diamond is a rotated square. Its extent from leftmost to rightmost
    vertex is hp (diameter = hp). Cell: 2*hp × 2*hp, diamond centered.

    Args:
        size: Image size.
        hp: Diamond diameter (full width/height of the diamond).
        dense: True for grid, False for single.

    Returns:
        uint8 numpy array with values 0 or 255.
    """
    arr = np.zeros((size, size), dtype=np.uint8)

    if dense:
        cell_size = 2 * hp
        cell = np.zeros((cell_size, cell_size), dtype=np.uint8)
        cx, cy = hp - 0.5, hp - 0.5
        radius = hp / 2.0
        Y, X = np.ogrid[:cell_size, :cell_size]
        mask = np.abs(X - cx) + np.abs(Y - cy) <= radius
        cell[mask] = 255
        tiles_y = (size + cell_size - 1) // cell_size
        tiles_x = (size + cell_size - 1) // cell_size
        arr = np.tile(cell, (tiles_y, tiles_x))[:size, :size]
    else:
        center = size // 2
        radius = hp / 2.0
        Y, X = np.ogrid[:size, :size]
        mask = np.abs(X - center + 0.5) + np.abs(Y - center + 0.5) <= radius
        arr[mask] = 255

    return arr
