# Patterns Generator Design

Date: 2026-06-22

## 1. Overview

Generate synthetic pattern images (PNG) for three pattern categories: Line Space, Contact Hole, and Others. Each pattern is generated in both dense (2000×2000, periodic tiling) and isolated (256×256, single instance centered) variants across a sweep of HP size and rotation angle parameters.

## 2. Requirements Summary

| Item | Value |
|------|-------|
| Image sizes | 2000×2000 (dense), 256×256 (isolated) |
| Format | PNG, pixel values 0–255, mostly binary (0/255) with ~1px anti-aliased edge |
| Language | Python 3 |
| Dependencies | Pillow, NumPy |
| HP range | 5–60px, step 5 (i.e. 5, 10, 15, ..., 60) |
| Spacing ratio | 1:1 (1-region : 0-region), extensible |
| Isolated vs dense | Same params, different image size; dense = periodic tiling, isolated = single instance centered |

## 3. Project Structure

```
patterns_generator/
├── generate.py              # Main entry: iterate param combos, dispatch generation + save
├── config.py                # All tunable constants
├── utils.py                 # Rotation (anti-alias), PNG save, directory creation
└── patterns/
    ├── __init__.py
    ├── line_space.py        # Line Space pattern
    ├── contact_hole.py      # Contact Hole (square + circle)
    └── others.py            # Zigzag, Star/Cross (米字型), Diamond grid
```

## 4. Output Directory Structure

Parent directory is the `patterns_generator/` folder. Named by generation timestamp (YYYY-MM-DD-HH-MM).

```
YYYY-MM-DD-HH-MM/
├── line_space/
│   ├── dense/
│   │   └── LS_hp{HP}_r{ANGLE}.png
│   └── isolated/
│       └── LS_hp{HP}_r{ANGLE}.png
├── contact_hole/
│   ├── dense/
│   │   ├── CH_square_hp{HP}_r{ANGLE}.png
│   │   └── CH_circle_hp{HP}.png
│   └── isolated/
│       ├── CH_square_hp{HP}_r{ANGLE}.png
│       └── CH_circle_hp{HP}.png
└── others/
    ├── dense/
    │   ├── OT_zigzag_hp{HP}_r{ANGLE}.png
    │   ├── OT_star_hp{HP}_r{ANGLE}.png
    │   └── OT_diamond_hp{HP}_r{ANGLE}.png
    └── isolated/
        ├── OT_zigzag_hp{HP}_r{ANGLE}.png
        ├── OT_star_hp{HP}_r{ANGLE}.png
        └── OT_diamond_hp{HP}_r{ANGLE}.png
```

Naming conventions:
- Prefix: `LS_` (Line Space), `CH_` (Contact Hole), `OT_` (Others)
- Sub-type: `square`, `circle`, `zigzag`, `star`, `diamond`
- `hp{HP}` — e.g., hp10, hp55
- `r{ANGLE}` — angle in degrees, e.g., r0, r45, r0.05. Omitted for rotation-invariant patterns (circle).

## 5. Pattern Specifications

### 5.1 Line Space

| Property | Value |
|----------|-------|
| Rotation | [0:5:180]° → 37 angles |
| HP | 5–60, step 5 → 12 values |
| Spacing ratio | 1:1 (line width = space width = HP) |
| Dense/Isolated | Both |

**Dense**: Full 2000×2000 array of alternating rows. Period = 2×HP rows. First HP rows = 255, next HP rows = 0.

**Isolated**: 256×256. Single horizontal stripe of height HP, centered vertically, value 255. Rest is 0.

**Rotation**: Rotate around center. Post-rotation fill color = 0 (black). LANCZOS resampling for anti-aliasing.

### 5.2 Contact Hole — Square

| Property | Value |
|----------|-------|
| Rotation | [0:0.05:1]° → 21 angles |
| HP | 5–60, step 5 → 12 values |
| Spacing ratio | 1:1 (hole side length = gap between holes = HP) |
| Dense/Isolated | Both |

**Dense**: Grid of HP×HP squares. Each square is placed at intervals of 2×HP (hole + gap) in both X and Y. Value 255 inside squares, 0 elsewhere.

**Isolated**: 256×256. Single HP×HP square centered, value 255. Rest is 0.

**Rotation**: Small-angle rotation (0–1°). LANCZOS resampling.

### 5.3 Contact Hole — Circle

| Property | Value |
|----------|-------|
| Rotation | None (rotation-invariant) |
| HP | 5–60, step 5 → 12 values |
| Spacing ratio | 1:1 (diameter = gap between circles = HP) |
| Dense/Isolated | Both |

**Dense**: Grid of circles with diameter HP, spaced at 2×HP intervals. Value 255 inside circles, 0 elsewhere.

**Isolated**: 256×256. Single circle of diameter HP centered, value 255. Rest is 0.

No rotation applied.

### 5.4 Others — Zigzag

| Property | Value |
|----------|-------|
| Rotation | [0:5:180]° → 37 angles |
| HP | 5–60, step 5 → 12 values |
| Spacing ratio | 1:1 |
| Dense/Isolated | Both |

**Dense**: Periodic zigzag lines across 2000×2000. HP defines the horizontal width of one zigzag segment (half-period). Amplitude = HP.

**Isolated**: 256×256. Single zigzag segment centered, value 255. Rest is 0.

### 5.5 Others — Star/Cross (米字型)

| Property | Value |
|----------|-------|
| Rotation | [0:5:180]° → 37 angles |
| HP | 5–60, step 5 → 12 values |
| Spacing ratio | 1:1 |
| Dense/Isolated | Both |

**Dense**: Periodic 米-shaped patterns across 2000×2000. HP defines the bounding box size. Four lines (horizontal, vertical, two diagonals) crossing at center of each unit cell. Line width = max(1, HP/5).

**Isolated**: 256×256. Single 米-shape centered, value 255. Rest is 0.

### 5.6 Others — Diamond Grid

| Property | Value |
|----------|-------|
| Rotation | [0:5:180]° → 37 angles |
| HP | 5–60, step 5 → 12 values |
| Spacing ratio | 1:1 |
| Dense/Isolated | Both |

**Dense**: Periodic diamond shapes across 2000×2000. HP = side length of diamond. Grid spacing = 2×HP.

**Isolated**: 256×256. Single diamond centered, value 255. Rest is 0.

## 6. Image Processing Pipeline

1. **Generate binary NumPy array** → values are either 0 or 255
2. **Convert to PIL Image** → `Image.fromarray(np.uint8(array))`
3. **Rotate** (if applicable) → `image.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=0)`
   - BICUBIC resampling produces ~1px anti-aliased edge transition
   - `fillcolor=0` prevents corner artifacts by filling with black
4. **Save as PNG** → `image.save(path, compress_level=6)`

## 7. Configuration (config.py)

```python
# HP range
HP_MIN = 5
HP_MAX = 60
HP_STEP = 5

# Image dimensions
DENSE_SIZE = 2000
ISOLATED_SIZE = 256

# Rotation angles by pattern type
LINE_SPACE_ANGLES = list(range(0, 181, 5))                     # 37 values
CONTACT_HOLE_SQUARE_ANGLES = [round(i * 0.05, 2) for i in range(21)]  # 21 values
OTHERS_ANGLES = list(range(0, 181, 5))                         # 37 values

# Spacing ratio (currently fixed at 1:1, extensible)
SPACING_RATIO = 1.0

# Pattern flags
GENERATE_DENSE = True
GENERATE_ISOLATED = True

# Anti-aliasing resample filter
RESAMPLE_FILTER = "LANCZOS"

# Output directory (relative to project root)
OUTPUT_BASE = "."  # same directory as PatternsGeneratorReq.md

# Filename format
FILENAME_FORMAT = "{prefix}_{subtype}_hp{hp}_r{angle}.png"
```

## 8. Total Image Count Estimate

| Pattern | Angles | HP values | Dense/Isolated | Sub-total |
|---------|--------|-----------|----------------|-----------|
| Line Space | 37 | 12 | 2 | 888 |
| Contact Hole Square | 21 | 12 | 2 | 504 |
| Contact Hole Circle | 1 | 12 | 2 | 24 |
| Others — Zigzag | 37 | 12 | 2 | 888 |
| Others — Star | 37 | 12 | 2 | 888 |
| Others — Diamond | 37 | 12 | 2 | 888 |
| **Total** | | | | **~4,080** |

## 9. Error Handling & Edge Cases

- **HP value vs image size**: Contact Hole Circle with HP=60 in 256×256 isolated: diameter 60px fits easily. Line Space HP=5 in 256×256 isolated: a 5px-high stripe is small but valid.
- **File exists**: Skip (do not overwrite) if output file already exists, supporting resume.
- **Directory creation**: Create output directory structure automatically.
- **Memory**: 2000×2000 uint8 array ≈ 4 MB. Processing is single-image, memory is negligible.
- **Angle formatting**: Angles stored with appropriate precision (no decimals for integer angles, 2 decimals for fractional).

## 10. Future Extensibility

- Additional spacing ratios: add a `spacing_ratio` parameter to each pattern generator function
- New pattern types: add new file in `patterns/`, register in `config.py` and `generate.py`
- Additional image formats: extend `save()` in `utils.py`
