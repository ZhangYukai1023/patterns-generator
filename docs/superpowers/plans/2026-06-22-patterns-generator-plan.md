# Patterns Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python-based synthetic pattern image generator producing ~4,080 PNG images across 3 categories (Line Space, Contact Hole, Others), each in dense (2000×2000) and isolated (256×256) variants.

**Architecture:** NumPy generates binary pattern arrays (0/255), Pillow applies rotation with LANCZOS anti-aliasing and saves as PNG. Pattern generation functions are separated per file in `patterns/`, driven by a central `generate.py` that iterates parameter combinations.

**Tech Stack:** Python 3, NumPy, Pillow

## Global Constraints

- Images: PNM with pixel values 0–255, mostly binary (0 or 255) with ~1px anti-aliased edges
- HP range: 5–60, step 5 (5, 10, 15, ..., 60)
- Spacing ratio: always 1:1 (extensible)
- Rotation uses `Image.LANCZOS` resampling, `fillcolor=0`
- Output: timestamped folder (YYYY-MM-DD-HH-MM) parallel to `PatternsGeneratorReq.md`
- File naming: `{prefix}_{subtype}_hp{hp}_r{angle}.png` (omit `_r{angle}` for circle)
- Skip existing files (resume support)

---

### Task 1: Create `config.py`

**Files:**
- Create: `patterns_generator/config.py`

**Interfaces:**
- Produces: all config constants consumed by every other module

- [ ] **Step 1: Write config.py**

```python
"""Configuration constants for pattern generation."""

# HP range
HP_MIN = 5
HP_MAX = 60
HP_STEP = 5

# Image dimensions
DENSE_SIZE = 2000
ISOLATED_SIZE = 256

# Rotation angles by pattern type
LINE_SPACE_ANGLES = list(range(0, 181, 5))
CONTACT_HOLE_SQUARE_ANGLES = [round(i * 0.05, 2) for i in range(21)]
OTHERS_ANGLES = list(range(0, 181, 5))

# Spacing ratio (1:1, extensible)
SPACING_RATIO = 1.0

# Generation flags
GENERATE_DENSE = True
GENERATE_ISOLATED = True
```

- [ ] **Step 2: Verify**

```bash
cd /data/PythonProject/patterns_generator && python -c "import config; print(f'HP values: {list(range(config.HP_MIN, config.HP_MAX+1, config.HP_STEP))}')"
```

Expected: `HP values: [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]`

---

### Task 2: Create `utils.py`

**Files:**
- Create: `patterns_generator/utils.py`
- Modify: depends on `config.py`

**Interfaces:**
- Consumes: `config.DENSE_SIZE`, `config.ISOLATED_SIZE`
- Produces: `make_output_dir(base)`, `rotate_image(img, angle)`, `save_image(img, path)`, `format_angle(angle)`

- [ ] **Step 1: Write utils.py**

```python
"""Utility functions: directory creation, rotation, save, angle formatting."""

import os
from datetime import datetime
from PIL import Image
import numpy as np


def make_output_dir(base: str) -> str:
    """Create timestamped output directory and return its path."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    path = os.path.join(base, timestamp)
    os.makedirs(path, exist_ok=True)
    return path


def ensure_subdir(path: str) -> str:
    """Ensure a subdirectory exists."""
    os.makedirs(path, exist_ok=True)
    return path


def rotate_image(img: Image.Image, angle: float) -> Image.Image:
    """Rotate image with anti-aliasing, filling background with black."""
    return img.rotate(angle, resample=Image.LANCZOS, expand=False, fillcolor=0)


def save_image(img: Image.Image, path: str) -> None:
    """Save PIL Image as PNG."""
    img.save(path, format="PNG", compress_level=6)


def format_angle(angle: float) -> str:
    """Format angle for filename: integer if whole, 2 decimals if fractional."""
    if angle == int(angle):
        return str(int(angle))
    return f"{angle:.2f}"


def numpy_to_pil(arr: np.ndarray) -> Image.Image:
    """Convert numpy uint8 array to PIL Image."""
    return Image.fromarray(arr, mode="L")
```

- [ ] **Step 2: Verify imports work**

```bash
cd /data/PythonProject/patterns_generator && python -c "from utils import format_angle; print(format_angle(0), format_angle(0.05), format_angle(180))"
```

Expected: `0 0.05 180`

---

### Task 3: Create `patterns/__init__.py`

**Files:**
- Create: `patterns_generator/patterns/__init__.py`

**Interfaces:**
- Produces: package marker, imports all pattern functions for convenient access

- [ ] **Step 1: Write `patterns/__init__.py`**

```python
"""Pattern generation package."""

from .line_space import generate_line_space
from .contact_hole import generate_contact_hole_square, generate_contact_hole_circle
from .others import generate_zigzag, generate_star, generate_diamond
```

- [ ] **Step 2: Verify**

```bash
cd /data/PythonProject/patterns_generator && python -c "import patterns; print('Package OK')"
```

Expected: `Package OK`

---

### Task 4: Create `patterns/line_space.py`

**Files:**
- Create: `patterns_generator/patterns/line_space.py`

**Interfaces:**
- Consumes: image `size`, `hp`, `dense` bool
- Produces: `generate_line_space(size, hp, dense) -> np.ndarray` (uint8, values 0 or 255)

- [ ] **Step 1: Write `patterns/line_space.py`**

```python
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
        # Periodic horizontal lines: line for first HP rows, space for next HP rows
        period = 2 * hp
        for row_start in range(0, size, period):
            row_end = min(row_start + hp, size)
            arr[row_start:row_end, :] = 255
    else:
        # Single horizontal stripe centered
        center = size // 2
        start = center - hp // 2
        end = start + hp
        # Handle edge cases
        start = max(0, start)
        end = min(size, end)
        if end > start:
            arr[start:end, :] = 255

    return arr
```

- [ ] **Step 2: Verify**

```bash
cd /data/PythonProject/patterns_generator && python -c "
from patterns.line_space import generate_line_space
import numpy as np

dense = generate_line_space(20, 5, dense=True)
assert dense[0,0] == 255  # first row = line
assert dense[5,0] == 255  # 5th row = line
assert dense[10,0] == 0   # 10th row = space
print(f'Dense: unique values={np.unique(dense)}, shape={dense.shape}')

isolated = generate_line_space(20, 5, dense=False)
assert isolated[0,0] == 0   # top is black
center = 20 // 2
assert isolated[center, 0] == 255  # center is stripe
print(f'Isolated: unique values={np.unique(isolated)}, shape={isolated.shape}')
print('OK')
"
```

Expected: Prints shapes and values, ends with `OK`.

---

### Task 5: Create `patterns/contact_hole.py`

**Files:**
- Create: `patterns_generator/patterns/contact_hole.py`

**Interfaces:**
- Consumes: image `size`, `hp`, `dense` bool
- Produces: `generate_contact_hole_square(size, hp, dense) -> np.ndarray`, `generate_contact_hole_circle(size, hp, dense) -> np.ndarray`

- [ ] **Step 1: Write `patterns/contact_hole.py`**

```python
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
        # Unit cell: 2*hp x 2*hp with HP×HP square at top-left
        cell_size = 2 * hp
        cell = np.zeros((cell_size, cell_size), dtype=np.uint8)
        cell[:hp, :hp] = 255
        # Tile to fill
        tiles_y = (size + cell_size - 1) // cell_size
        tiles_x = (size + cell_size - 1) // cell_size
        arr = np.tile(cell, (tiles_y, tiles_x))[:size, :size]
    else:
        # Single square centered
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
        # Unit cell: 2*hp x 2*hp with circle centered
        cell_size = 2 * hp
        cell = np.zeros((cell_size, cell_size), dtype=np.uint8)
        radius = hp / 2.0
        cy, cx = hp - 0.5, hp - 0.5  # center in pixel coordinates
        Y, X = np.ogrid[:cell_size, :cell_size]
        dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        cell[dist <= radius] = 255
        # Tile to fill
        tiles_y = (size + cell_size - 1) // cell_size
        tiles_x = (size + cell_size - 1) // cell_size
        arr = np.tile(cell, (tiles_y, tiles_x))[:size, :size]
    else:
        # Single circle centered
        center = size // 2
        radius = hp / 2.0
        Y, X = np.ogrid[:size, :size]
        dist = np.sqrt((X - center + 0.5) ** 2 + (Y - center + 0.5) ** 2)
        arr[dist <= radius] = 255

    return arr
```

- [ ] **Step 2: Verify**

```bash
cd /data/PythonProject/patterns_generator && python -c "
from patterns.contact_hole import generate_contact_hole_square, generate_contact_hole_circle
import numpy as np

sq = generate_contact_hole_square(20, 5, dense=True)
assert sq[0,0] == 255, 'square top-left should be 255'
assert sq[5,5] == 0, 'square gap should be 0'
print(f'Square dense: unique={np.unique(sq)}, shape={sq.shape}')

sq_iso = generate_contact_hole_square(20, 5, dense=False)
assert sq_iso[0,0] == 0, 'isolated top-left should be 0'
print(f'Square isolated: unique={np.unique(sq_iso)}, shape={sq_iso.shape}')

ci = generate_contact_hole_circle(20, 5, dense=True)
assert ci[0,0] == 255, 'circle cell center should be 255'
print(f'Circle dense: unique={np.unique(ci)}, shape={ci.shape}')

ci_iso = generate_contact_hole_circle(20, 5, dense=False)
assert ci_iso[0,0] == 0
print(f'Circle isolated: unique={np.unique(ci_iso)}, shape={ci_iso.shape}')
print('OK')
"
```

Expected: All assertions pass, prints "OK".

---

### Task 6: Create `patterns/others.py`

**Files:**
- Create: `patterns_generator/patterns/others.py`

**Interfaces:**
- Consumes: image `size`, `hp`, `dense` bool
- Produces: `generate_zigzag(size, hp, dense) -> np.ndarray`, `generate_star(size, hp, dense) -> np.ndarray`, `generate_diamond(size, hp, dense) -> np.ndarray`

- [ ] **Step 1: Write `patterns/others.py`**

```python
"""Others pattern generator — Zigzag, Star (米字型), Diamond."""

import numpy as np
from PIL import Image, ImageDraw


def _draw_line(arr: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> None:
    """Draw a line on a numpy array using PIL for anti-aliased rendering."""
    h, w = arr.shape
    img = Image.fromarray(arr, mode="L")
    draw = ImageDraw.Draw(img)
    draw.line([(x1, y1), (x2, y2)], fill=255, width=1)
    arr[:, :] = np.array(img, dtype=np.uint8)


# ---- Zigzag ---- #

def generate_zigzag(size: int, hp: int, dense: bool = True) -> np.ndarray:
    """Generate zigzag pattern.

    Dense: periodic V-shape lines tiled across the canvas.
    Isolated: single V-shape centered.

    Args:
        size: Image size.
        hp: Horizontal half-period (width of one zigzag segment).
        dense: True for periodic, False for single.

    Returns:
        uint8 numpy array with values 0 or 255.
    """
    arr = np.zeros((size, size), dtype=np.uint8)

    if dense:
        # Unit cell: 2*hp wide, hp tall with one V shape
        cell_w, cell_h = 2 * hp, hp
        if cell_w == 0 or cell_h == 0:
            return arr
        cell = Image.new("L", (cell_w, cell_h), 0)
        draw = ImageDraw.Draw(cell)
        # V: (0, cell_h) → (hp, 0) → (2*hp, cell_h)
        draw.line([(0, cell_h - 1), (hp, 0), (2 * hp - 1, cell_h - 1)], fill=255, width=1)
        cell_arr = np.array(cell, dtype=np.uint8)

        # Tile vertically and horizontally
        tiles_y = (size + cell_h - 1) // cell_h
        tiles_x = (size + cell_w - 1) // cell_w
        arr = np.tile(cell_arr, (tiles_y, tiles_x))[:size, :size]
    else:
        # Single V centered
        cx, cy = size // 2, size // 2
        half = hp // 2
        # Ensure coordinates are within bounds
        if hp > 1 and cx - half >= 0 and cx + half < size and cy + half < size:
            _draw_line(arr, cx - half, cy + half, cx, cy - half)
            _draw_line(arr, cx, cy - half, cx + half, cy + half)

    return arr


# ---- Star / Cross (米字型) ---- #

def generate_star(size: int, hp: int, dense: bool = True) -> np.ndarray:
    """Generate star/cross (米字型) pattern.

    Dense: periodic 米-shapes.
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
        # Unit cell: 2*hp x 2*hp with 米-shape centered
        cell_size = 2 * hp
        if cell_size == 0:
            return arr
        cell_img = Image.new("L", (cell_size, cell_size), 0)
        draw = ImageDraw.Draw(cell_img)
        c = hp - 0.5  # center
        r = hp / 2.0  # half-diagonal
        # Four lines radiating from center: horizontal, vertical, two diagonals
        draw.line([(c - r, c), (c + r, c)], fill=255, width=line_width)         # horizontal
        draw.line([(c, c - r), (c, c + r)], fill=255, width=line_width)         # vertical
        draw.line([(c - r, c - r), (c + r, c + r)], fill=255, width=line_width)  # diagonal \
        draw.line([(c + r, c - r), (c - r, c + r)], fill=255, width=line_width)  # diagonal /
        cell_arr = np.array(cell_img, dtype=np.uint8)
        # Tile
        tiles = (size + cell_size - 1) // cell_size
        arr = np.tile(cell_arr, (tiles, tiles))[:size, :size]
    else:
        # Single 米-shape centered
        c = size // 2
        r = hp // 2
        r = max(1, r)
        img = Image.fromarray(arr, mode="L")
        draw = ImageDraw.Draw(img)
        draw.line([(c - r, c), (c + r, c)], fill=255, width=line_width)
        draw.line([(c, c - r), (c, c + r)], fill=255, width=line_width)
        draw.line([(c - r, c - r), (c + r, c + r)], fill=255, width=line_width)
        draw.line([(c + r, c - r), (c - r, c + r)], fill=255, width=line_width)
        arr[:, :] = np.array(img, dtype=np.uint8)

    return arr


# ---- Diamond ---- #

def generate_diamond(size: int, hp: int, dense: bool = True) -> np.ndarray:
    """Generate diamond grid pattern.

    Dense: periodic diamond shapes.
    Isolated: single diamond centered.

    Args:
        size: Image size.
        hp: Side length (half-diagonal = hp/2 in L1 metric).
        dense: True for periodic, False for single.

    Returns:
        uint8 numpy array with values 0 or 255.
    """
    arr = np.zeros((size, size), dtype=np.uint8)

    if dense:
        # Unit cell: 2*hp x 2*hp with centered diamond
        cell_size = 2 * hp
        if cell_size == 0:
            return arr
        cell = np.zeros((cell_size, cell_size), dtype=np.uint8)
        cy, cx = hp - 0.5, hp - 0.5
        Y, X = np.ogrid[:cell_size, :cell_size]
        # Diamond defined by L1 distance: |x-cx| + |y-cy| <= hp/2
        half = max(0.5, hp / 2.0)
        mask = np.abs(X - cx) + np.abs(Y - cy) <= half
        cell[mask] = 255
        # Tile
        tiles = (size + cell_size - 1) // cell_size
        arr = np.tile(cell, (tiles, tiles))[:size, :size]
    else:
        # Single diamond centered
        cy, cx = size // 2 - 0.5, size // 2 - 0.5
        half = max(0.5, hp / 2.0)
        Y, X = np.ogrid[:size, :size]
        mask = np.abs(X - cx) + np.abs(Y - cy) <= half
        arr[mask] = 255

    return arr
```

- [ ] **Step 2: Verify**

```bash
cd /data/PythonProject/patterns_generator && python -c "
from patterns.others import generate_zigzag, generate_star, generate_diamond
import numpy as np

# Zigzag
zz = generate_zigzag(30, 10, dense=True)
assert zz.shape == (30, 30)
assert zz.dtype == np.uint8
print(f'Zigzag dense: unique={np.unique(zz)}, any_255={np.any(zz==255)}')

zz_iso = generate_zigzag(30, 10, dense=False)
print(f'Zigzag isolated: unique={np.unique(zz_iso)}, any_255={np.any(zz_iso==255)}')

# Star
st = generate_star(30, 10, dense=True)
print(f'Star dense: unique={np.unique(st)}, any_255={np.any(st==255)}')

st_iso = generate_star(30, 10, dense=False)
print(f'Star isolated: unique={np.unique(st_iso)}, any_255={np.any(st_iso==255)}')

# Diamond
dm = generate_diamond(30, 10, dense=True)
print(f'Diamond dense: unique={np.unique(dm)}, any_255={np.any(dm==255)}')

dm_iso = generate_diamond(30, 10, dense=False)
print(f'Diamond isolated: unique={np.unique(dm_iso)}, any_255={np.any(dm_iso==255)}')
print('OK')
"
```

Expected: All patterns generate with values [0 255], ends with "OK".

---

### Task 7: Create `generate.py`

**Files:**
- Create: `patterns_generator/generate.py`

**Interfaces:**
- Consumes: all config, utils, and patterns modules
- Produces: the full batch of PNG images in timestamped directory

- [ ] **Step 1: Write generate.py**

```python
"""Main entry point for pattern generation.

Usage: python generate.py

Iterates all parameter combinations and generates PNG images.
Output directory is a timestamped folder parallel to this file.
"""

import os
import sys
import config
from utils import (
    make_output_dir, ensure_subdir, rotate_image,
    save_image, numpy_to_pil, format_angle,
)
from patterns.line_space import generate_line_space
from patterns.contact_hole import generate_contact_hole_square, generate_contact_hole_circle
from patterns.others import generate_zigzag, generate_star, generate_diamond


# Pattern registry: (name, subtype, generator, angles, needs_rotation)
# Each entry describes a pattern variant to generate.
PATTERNS = [
    # (folder_name, prefix, subtype, generator_fn, angles, needs_rotation)
]


def _register_patterns():
    """Build pattern registry from config."""
    hp_values = list(range(config.HP_MIN, config.HP_MAX + 1, config.HP_STEP))
    sizes = []
    if config.GENERATE_DENSE:
        sizes.append(("dense", config.DENSE_SIZE))
    if config.GENERATE_ISOLATED:
        sizes.append(("isolated", config.ISOLATED_SIZE))

    PATTERNS.clear()

    # Line Space
    for dense_label, size in sizes:
        for angle in config.LINE_SPACE_ANGLES:
            PATTERNS.append((
                "line_space", dense_label, "LS", "line",
                size, angle, True, generate_line_space,
            ))

    # Contact Hole Square
    for dense_label, size in sizes:
        for angle in config.CONTACT_HOLE_SQUARE_ANGLES:
            PATTERNS.append((
                "contact_hole", dense_label, "CH", "square",
                size, angle, True, generate_contact_hole_square,
            ))

    # Contact Hole Circle (no rotation)
    for dense_label, size in sizes:
        PATTERNS.append((
            "contact_hole", dense_label, "CH", "circle",
            size, 0.0, False, generate_contact_hole_circle,
        ))

    # Others - Zigzag
    for dense_label, size in sizes:
        for angle in config.OTHERS_ANGLES:
            PATTERNS.append((
                "others", dense_label, "OT", "zigzag",
                size, angle, True, generate_zigzag,
            ))

    # Others - Star
    for dense_label, size in sizes:
        for angle in config.OTHERS_ANGLES:
            PATTERNS.append((
                "others", dense_label, "OT", "star",
                size, angle, True, generate_star,
            ))

    # Others - Diamond
    for dense_label, size in sizes:
        for angle in config.OTHERS_ANGLES:
            PATTERNS.append((
                "others", dense_label, "OT", "diamond",
                size, angle, True, generate_diamond,
            ))


def _build_filename(prefix: str, subtype: str, hp: int, angle: float, has_rotation: bool) -> str:
    """Build output filename."""
    if has_rotation:
        return f"{prefix}_{subtype}_hp{hp}_r{format_angle(angle)}.png"
    else:
        return f"{prefix}_{subtype}_hp{hp}.png"


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
            # Build path
            subdir = ensure_subdir(os.path.join(output_root, folder, dense_label))
            filename = _build_filename(prefix, subtype, hp, angle, has_rotation)
            filepath = os.path.join(subdir, filename)

            # Skip existing
            if os.path.exists(filepath):
                skipped += 1
                continue

            # Generate
            arr = gen_fn(size, hp, dense=(dense_label == "dense"))

            # Convert to PIL
            img = numpy_to_pil(arr)

            # Rotate if needed
            if has_rotation and angle != 0:
                img = rotate_image(img, angle)

            # Save
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
```

- [ ] **Step 2: Quick smoke test with minimal config**

Create a temp override config to test with just a few parameters:

```bash
cd /data/PythonProject/patterns_generator && python -c "
import config
# Temporarily override for quick test
config.HP_MIN = 10
config.HP_MAX = 20
config.HP_STEP = 10
config.LINE_SPACE_ANGLES = [0, 45]
config.CONTACT_HOLE_SQUARE_ANGLES = [0.0, 0.05]
config.OTHERS_ANGLES = [0, 90]
config.GENERATE_DENSE = True
config.GENERATE_ISOLATED = True

from generate import generate_all
import tempfile, os
# Generate into a temp dir
generate_all(tempfile.mkdtemp())
print('Smoke test passed')
"
```

Expected: Generates images into temp dir, prints progress, ends with "Smoke test passed".

---

### Task 8: Full production run

**Files:**
- Run: `generate.py` from project root

- [ ] **Step 1: Run full generation**

```bash
cd /data/PythonProject/patterns_generator && python generate.py
```

Expected: Generates ~4,080 images, progress printed every 500 files.

- [ ] **Step 2: Spot-check output**

```bash
cd /data/PythonProject/patterns_generator && python -c "
import os
from PIL import Image

# Find the latest output folder
dirs = [d for d in os.listdir('.') if os.path.isdir(d) and '-' in d and d.count('-') >= 4]
if dirs:
    latest = max(dirs)
    print(f'Checking: {latest}')
    # Count files
    total_png = sum(
        len([f for f in files if f.endswith('.png')])
        for _, _, files in os.walk(latest)
    )
    print(f'Total PNGs: {total_png}')

    # Check first PNG found
    for root, _, files in os.walk(latest):
        for f in files:
            if f.endswith('.png'):
                path = os.path.join(root, f)
                img = Image.open(path)
                print(f'Sample: {f} -> size={img.size}, mode={img.mode}')
                # Verify it has some values != 0 and != 255 (anti-aliasing edge)
                extrema = img.getextrema()
                print(f'  Pixel range: {extrema}')
                break
        break
"
```

Expected: Shows total file count (~4,080), checks a sample image's dimensions and pixel range.

---

## Spec Coverage Check

| Spec Requirement | Task |
|---|---|
| config.py constants | Task 1 |
| utils.py (dirs, rotate, save, format) | Task 2 |
| patterns/__init__.py | Task 3 |
| Line Space (dense + isolated) | Task 4 |
| Contact Hole Square (dense + isolated) | Task 5 |
| Contact Hole Circle (dense + isolated) | Task 5 |
| Others — Zigzag | Task 6 |
| Others — Star (米字型) | Task 6 |
| Others — Diamond | Task 6 |
| generate.py main loop | Task 7 |
| Production verification run | Task 8 |
