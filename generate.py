"""Main entry point for pattern generation.

Usage: python generate.py

Iterates all parameter combinations and generates PNG images.
Output directory is a timestamped folder parallel to this file.
"""

import math
import os
from dataclasses import dataclass

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
from patterns.others import generate_zigzag, generate_star, generate_diamond_grid


@dataclass
class Pattern:
    folder: str
    dense_label: str
    prefix: str
    subtype: str
    size: int
    angle: float
    has_rotation: bool
    gen_fn: callable


PATTERNS: list[Pattern] = []


def _get_sizes():
    """Yield (label, size) tuples based on generation flags."""
    if config.GENERATE_DENSE:
        yield ("dense", config.DENSE_SIZE)
    if config.GENERATE_ISOLATED:
        yield ("isolated", config.ISOLATED_SIZE)


_SIZES_CACHE = None
def _cached_sizes():
    global _SIZES_CACHE
    if _SIZES_CACHE is None:
        _SIZES_CACHE = list(_get_sizes())
    return _SIZES_CACHE


def _register_patterns():
    """Build pattern registry from config."""
    PATTERNS.clear()
    sizes = _cached_sizes()

    for dense_label, size in sizes:
        for angle in config.LINE_SPACE_ANGLES:
            PATTERNS.append(Pattern("line_space", dense_label, "LS", "line",
                                    size, angle, True, generate_line_space))

    for dense_label, size in sizes:
        for angle in config.CONTACT_HOLE_SQUARE_ANGLES:
            PATTERNS.append(Pattern("contact_hole", dense_label, "CH", "square",
                                    size, angle, True, generate_contact_hole_square))

    for dense_label, size in sizes:
        PATTERNS.append(Pattern("contact_hole", dense_label, "CH", "circle",
                                size, 0.0, False, generate_contact_hole_circle))

    for dense_label, size in sizes:
        for angle in config.OTHERS_ANGLES:
            PATTERNS.append(Pattern("others", dense_label, "OT", "zigzag",
                                    size, angle, True, generate_zigzag))

    for dense_label, size in sizes:
        for angle in config.OTHERS_ANGLES:
            PATTERNS.append(Pattern("others", dense_label, "OT", "star",
                                    size, angle, True, generate_star))

    for dense_label, size in sizes:
        for angle in config.OTHERS_ANGLES:
            PATTERNS.append(Pattern("others", dense_label, "OT", "diamond",
                                    size, angle, True, generate_diamond_grid))


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


def _rotate_and_crop(img: Image.Image, angle: float, target_size: int) -> Image.Image:
    """Rotate with expand=True, then center-crop to target size."""
    img = img.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=0)
    crop = (img.width - target_size) // 2
    return img.crop((crop, crop, crop + target_size, crop + target_size))


def generate_all(base_dir: str) -> None:
    """Generate all pattern images."""
    _register_patterns()
    hp_values = list(range(config.HP_MIN, config.HP_MAX + 1, config.HP_STEP))

    output_root = make_output_dir(base_dir)
    total = len(PATTERNS) * len(hp_values)
    count = 0
    skipped = 0

    print(f"Generating {total} images in: {output_root}")

    for p in PATTERNS:
        for hp in hp_values:
            subdir = ensure_subdir(os.path.join(output_root, p.folder, p.dense_label))
            filename = _build_filename(p.prefix, p.subtype, hp, p.angle, p.has_rotation)
            filepath = os.path.join(subdir, filename)

            if os.path.exists(filepath):
                skipped += 1
                continue

            canvas_size = p.size
            needs_expanded = p.has_rotation and p.angle != 0 and p.dense_label == "dense"
            if needs_expanded:
                canvas_size = _expanded_size(p.size)

            arr = p.gen_fn(canvas_size, hp, dense=(p.dense_label == "dense"))
            img = numpy_to_pil(arr)

            if p.has_rotation and p.angle != 0:
                if needs_expanded:
                    img = _rotate_and_crop(img, p.angle, p.size)
                else:
                    img = rotate_image(img, p.angle)

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
