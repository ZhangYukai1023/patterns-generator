"""Line Space pattern generator."""

import numpy as np


def generate_line_space(size: int, hp: int, dense: bool = True) -> np.ndarray:
    """Generate Line Space pattern.

    Args:
        size: Image size (width and height).
        hp: Line height / space height in pixels.
        dense: If True, periodic tiling; if False, single stripe centered.

    Returns:
        uint8 numpy array with values 0 or 255.
    """
    arr = np.zeros((size, size), dtype=np.uint8)

    if dense:
        # Periodic horizontal lines: 255 for first HP rows, 0 for next HP rows
        period = 2 * hp
        for row_start in range(0, size, period):
            row_end = min(row_start + hp, size)
            arr[row_start:row_end, :] = 255
    else:
        # Single horizontal stripe centered
        center = size // 2
        start = center - hp // 2
        end = start + hp
        start = max(0, start)
        end = min(size, end)
        if end > start:
            arr[start:end, :] = 255

    return arr
