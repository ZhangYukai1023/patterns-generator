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
