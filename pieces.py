"""
Piece definitions for the Wood Intelligence puzzle.

Board: 10 wide x 15 tall = 150 cells
Pieces: 8 types, 5 copies each = 40 pieces total

Each piece is defined by its cell offsets from (0,0).
Pieces can be rotated and flipped (all orientations are valid).
"""

BOARD_WIDTH = 10
BOARD_HEIGHT = 15

# Piece definitions: name -> (cell offsets, count)
# Each cell offset is (row, col) relative to top-left of bounding box.
PIECE_DEFS = {
    "white": {
        # I-2: 1x2 domino
        "cells": [(0, 0), (0, 1)],
        "count": 5,
    },
    "black": {
        # I-4: 1x4 straight bar
        "cells": [(0, 0), (1, 0), (2, 0), (3, 0)],
        "count": 5,
    },
    "green": {
        # O: 2x2 square
        "cells": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "count": 5,
    },
    "orange": {
        # U: U-shape, 2 high x 3 wide
        #  X.X
        #  XXX
        "cells": [(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)],
        "count": 5,
    },
    "yellow": {
        # T: T-shape, 2 high x 3 wide
        #  XXX
        #  .X.
        "cells": [(0, 0), (0, 1), (0, 2), (1, 1)],
        "count": 5,
    },
    "red": {
        # S: S/Z-shape, 3 high x 2 wide
        #  X.
        #  XX
        #  .X
        "cells": [(0, 0), (1, 0), (1, 1), (2, 1)],
        "count": 5,
    },
    "blue": {
        # L: L-shape, 3 high x 2 wide
        #  X.
        #  X.
        #  XX
        "cells": [(0, 0), (1, 0), (2, 0), (2, 1)],
        "count": 5,
    },
    "purple": {
        # Corner/L-tromino: 2 high x 2 wide
        #  X.
        #  XX
        "cells": [(0, 0), (1, 0), (1, 1)],
        "count": 5,
    },
}


def normalize(cells):
    """Translate cells so min row and min col are both 0, then sort."""
    min_r = min(r for r, c in cells)
    min_c = min(c for r, c in cells)
    return tuple(sorted((r - min_r, c - min_c) for r, c in cells))


def generate_orientations(cells):
    """Generate all distinct orientations (rotations + reflections) of a piece.

    Returns a list of normalized cell tuples (up to 8 orientations).
    """
    orientations = set()
    current = list(cells)
    for _ in range(4):
        # Add current rotation
        orientations.add(normalize(current))
        # Add horizontal reflection of current rotation
        reflected = [(-r, c) for r, c in current]
        orientations.add(normalize(reflected))
        # Rotate 90 degrees clockwise: (r, c) -> (c, -r)
        current = [(c, -r) for r, c in current]
    return list(orientations)


def validate_pieces():
    """Verify that total piece area equals board area."""
    total = sum(len(d["cells"]) * d["count"] for d in PIECE_DEFS.values())
    board_area = BOARD_WIDTH * BOARD_HEIGHT
    if total != board_area:
        raise ValueError(
            f"Piece area mismatch: pieces cover {total} cells, "
            f"board has {board_area} cells"
        )
    return True


def print_piece(cells, name=""):
    """Print a piece shape to terminal."""
    if name:
        print(f"  {name}:")
    max_r = max(r for r, c in cells)
    max_c = max(c for r, c in cells)
    cell_set = set(cells)
    for r in range(max_r + 1):
        line = "    "
        for c in range(max_c + 1):
            line += "XX" if (r, c) in cell_set else ".."
        print(line)


def show_pieces():
    """Display all piece definitions and their orientations."""
    validate_pieces()
    print(f"Board: {BOARD_WIDTH} x {BOARD_HEIGHT} = {BOARD_WIDTH * BOARD_HEIGHT} cells\n")
    total_pieces = 0
    for name, defn in PIECE_DEFS.items():
        size = len(defn["cells"])
        count = defn["count"]
        total_pieces += count
        orientations = generate_orientations(defn["cells"])
        print(f"{name}: {size} cells, {count} copies, {len(orientations)} orientations")
        print_piece(defn["cells"], "base shape")
        for i, orient in enumerate(orientations):
            print_piece(orient, f"orientation {i+1}")
        print()
    print(f"Total pieces: {total_pieces}")
    print(f"Total cells: {sum(len(d['cells']) * d['count'] for d in PIECE_DEFS.values())}")


if __name__ == "__main__":
    show_pieces()
