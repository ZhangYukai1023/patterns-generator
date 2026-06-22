"""Main entry point for pattern generation.

Usage: python generate.py

Iterates all parameter combinations and generates PNG images.
Output directory is a timestamped folder parallel to this file.
"""

import math
import os

from PIL import Image

import config
from utils import (
    make_output_dir,
    ensure_subdir,
    rotate_image,
    save_image,
    numpy_to_pil,
    format_angle,
)
from patterns.line_space import generate_line_space
from patterns.contact_hole import generate_contact_hole_square, generate_contact_hole_circle
from patterns.others import generate_zigzag, generate_star


# Pattern registry entry: (folder, dense_label, prefix, subtype, size, angle, has_rotation, gen_fn)
PATTERNS = []


def _register_patterns():
    """Build pattern registry from config."""
    hp_values = list(range(config.HP_MIN, config.HP_MAX + 1, config.HP_STEP))

    PATTERNS.clear()

    # --- Line Space ---
    for dense_label, size in _get_sizes():
        for angle in config.LINE_SPACE_ANGLES:
            PATTERNS.append((
                "line_space", dense_label, "LS", "line",
                size, angle, True, generate_line_space,
            ))

    # --- Contact Hole Square ---
    for dense_label, size in _get_sizes():
        for angle in config.CONTACT_HOLE_SQUARE_ANGLES:
            PATTERNS.append((
                "contact_hole", dense_label, "CH", "square",
                size, angle, True, generate_contact_hole_square,
            ))

    # --- Contact Hole Circle (no rotation) ---
    for dense_label, size in _get_sizes():
        PATTERNS.append((
            "contact_hole", dense_label, "CH", "circle",
            size, 0.0, False, generate_contact_hole_circle,
        ))

    # --- Others - Zigzag ---
    for dense_label, size in _get_sizes():
        for angle in config.OTHERS_ANGLES:
            PATTERNS.append((
                "others", dense_label, "OT", "zigzag",
                size, angle, True, generate_zigzag,
            ))

    # --- Others - Star ---
    for dense_label, size in _get_sizes():
        for angle in config.OTHERS_ANGLES:
            PATTERNS.append((
                "others", dense_label, "OT", "star",
                size, angle, True, generate_star,
            ))



def _get_sizes():
    """Yield (label, size) tuples based on generation flags."""
    if config.GENERATE_DENSE:
        yield ("dense", config.DENSE_SIZE)
    if config.GENERATE_ISOLATED:
        yield ("isolated", config.ISOLATED_SIZE)


def _build_filename(prefix: str, subtype: str, hp: int, angle: float, has_rotation: bool) -> str:
    """Build output filename."""
    if has_rotation:
        return f"{prefix}_{subtype}_hp{hp}_r{format_angle(angle)}.png"
    else:
        return f"{prefix}_{subtype}_hp{hp}.png"


def _expanded_size(size: int) -> int:
    """Calculate canvas size needed so a rotated image fills the target size."""
    expanded = int(math.ceil(size * math.sqrt(2)))
    if expanded % 2 != 0:
        expanded += 1
    return expanded


def generate_all(base_dir: str) -> None:
    """Generate all pattern images."""
    _register_patterns()
    hp_values = list(range(config.HP_MIN, config.HP_MAX + 1, config.HP_STEP))

    output_root = make_output_dir(base_dir)
    total = len(PATTERNS) * len(hp_values)
    count = 0
    skipped = 0

    print(f"Generating {total} images in: {output_root}")

    for folder, dense_label, prefix, subtype, size, angle, has_rotation, gen_fn in PATTERNS:
        for hp in hp_values:
            subdir = ensure_subdir(os.path.join(output_root, folder, dense_label))
            filename = _build_filename(prefix, subtype, hp, angle, has_rotation)
            filepath = os.path.join(subdir, filename)

            if os.path.exists(filepath):
                skipped += 1
                continue

            # For rotated dense patterns: use expanded canvas so the rotated
            # result fills the entire output image with no empty corners.
            canvas_size = size
            if has_rotation and angle != 0 and dense_label == "dense":
                canvas_size = _expanded_size(size)

            arr = gen_fn(canvas_size, hp, dense=(dense_label == "dense"))
            img = numpy_to_pil(arr)

            if has_rotation and angle != 0:
                if canvas_size != size:
                    # Rotate with expand=True to capture full rotated content,
                    # then center-crop to target size so pattern fills the image.
                    img = img.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=0)
                    crop = (img.width - size) // 2
                    img = img.crop((crop, crop, crop + size, crop + size))
                else:
                    img = rotate_image(img, angle)

            save_image(img, filepath)
            count += 1

            if count % 500 == 0:
                print(f"  Progress: {count}/{total}")

    print(f"Done: {count} generated, {skipped} skipped, {total} total")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    generate_all(base_dir)


if __name__ == "__main__":
    main()
