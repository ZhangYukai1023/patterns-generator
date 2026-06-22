"""Contact Hole pattern generator — square and circle."""

import numpy as np


def generate_contact_hole_square(size: int, hp: int, dense: bool = True) -> np.ndarray:
    """Generate square Contact Hole pattern.

    Dense: grid of HP×HP squares spaced 2×HP apart.
    Isolated: single HP×HP square centered.

    Args:
        size: Image size.
        hp: Square side length and gap width.
        dense: True for periodic grid, False for single hole.

    Returns:
        uint8 numpy array with values 0 or 255.
    """
    arr = np.zeros((size, size), dtype=np.uint8)

    if dense:
        cell_size = 2 * hp
        cell = np.zeros((cell_size, cell_size), dtype=np.uint8)
        cell[:hp, :hp] = 255
        tiles_y = (size + cell_size - 1) // cell_size
        tiles_x = (size + cell_size - 1) // cell_size
        arr = np.tile(cell, (tiles_y, tiles_x))[:size, :size]
    else:
        center = size // 2
        start = center - hp // 2
        end = start + hp
        start = max(0, start)
        end = min(size, end)
        if end > start:
            arr[start:end, start:end] = 255

    return arr


def generate_contact_hole_circle(size: int, hp: int, dense: bool = True) -> np.ndarray:
    """Generate circular Contact Hole pattern.

    Dense: grid of circles with diameter HP, spaced 2×HP apart.
    Isolated: single circle of diameter HP centered.

    Args:
        size: Image size.
        hp: Circle diameter and gap width.
        dense: True for periodic grid, False for single hole.

    Returns:
        uint8 numpy array with values 0 or 255.
    """
    arr = np.zeros((size, size), dtype=np.uint8)

    if dense:
        cell_size = 2 * hp
        cell = np.zeros((cell_size, cell_size), dtype=np.uint8)
        radius = hp / 2.0
        cy, cx = hp - 0.5, hp - 0.5
        Y, X = np.ogrid[:cell_size, :cell_size]
        dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        cell[dist <= radius] = 255
        tiles_y = (size + cell_size - 1) // cell_size
        tiles_x = (size + cell_size - 1) // cell_size
        arr = np.tile(cell, (tiles_y, tiles_x))[:size, :size]
    else:
        center = size // 2
        radius = hp / 2.0
        Y, X = np.ogrid[:size, :size]
        dist = np.sqrt((X - center + 0.5) ** 2 + (Y - center + 0.5) ** 2)
        arr[dist <= radius] = 255

    return arr
