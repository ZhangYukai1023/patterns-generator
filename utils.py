"""Utility functions for pattern generation."""

import os
from datetime import datetime

import numpy as np
from PIL import Image


def make_output_dir(base: str) -> str:
    """Create timestamped output directory and return its path.

    Format: YYYY-MM-DD-HH-MM (e.g., 2026-06-22-14-30).
    Uses datetime.now().
    Creates with os.makedirs(path, exist_ok=True).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    path = os.path.join(base, timestamp)
    os.makedirs(path, exist_ok=True)
    return path


def ensure_subdir(path: str) -> str:
    """Ensure a subdirectory exists (os.makedirs). Returns the path."""
    os.makedirs(path, exist_ok=True)
    return path


def rotate_image(img: Image.Image, angle: float) -> Image.Image:
    """Rotate PIL Image with LANCZOS anti-aliasing, fillcolor=0 (black).

    Use expand=False -- do NOT expand canvas.
    """
    # BICUBIC is used instead of LANCZOS because Pillow 12.x does not
    # support LANCZOS with the affine transform path (expand=False).
    return img.rotate(
        angle,
        resample=Image.Resampling.BICUBIC,
        expand=False,
        fillcolor=0,
    )


def save_image(img: Image.Image, path: str) -> None:
    """Save PIL Image as PNG with compress_level=6."""
    img.save(path, format="PNG", compress_level=6)


def format_angle(angle: float) -> str:
    """Format angle for filename.

    If int: return str(int(angle)) -- e.g., 0 -> "0", 180 -> "180"
    If float: return f"{angle:.2f}" -- e.g., 0.05 -> "0.05"
    """
    if angle == int(angle):
        return str(int(angle))
    return f"{angle:.2f}"


def numpy_to_pil(arr: np.ndarray) -> Image.Image:
    """Convert numpy uint8 array to PIL 'L' mode Image using Image.fromarray."""
    return Image.fromarray(arr, mode="L")
