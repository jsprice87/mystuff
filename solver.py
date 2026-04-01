"""
Puzzle solver: backtracking with bitmask board representation.

Uses a counter-based approach where pieces of the same type are interchangeable,
avoiding the combinatorial explosion of assigning identical pieces to distinct slots.

The board is represented as a bitmask for fast operations.
"""

import time
from pieces import (
    BOARD_WIDTH, BOARD_HEIGHT, PIECE_DEFS,
    generate_orientations, validate_pieces,
)

W = BOARD_WIDTH
H = BOARD_HEIGHT
FULL_MASK = (1 << (W * H)) - 1


def _cell_bit(r, c):
    return 1 << (r * W + c)


def _first_empty_cell(mask):
    """Find the first empty cell (lowest unset bit in the board area)."""
    # We want the lowest bit that is NOT set in mask
    # inv = ~mask gives us 1s where mask has 0s
    # inv & (-inv) isolates the lowest set bit of inv = lowest unset bit of mask
    inv = (~mask) & FULL_MASK
    if inv == 0:
        return -1, -1  # board is full
    bit = inv & (-inv)
    pos = bit.bit_length() - 1
    return pos // W, pos % W


def _precompute_placements():
    """Precompute all valid placements for each piece type, indexed by cell.

    Returns:
        piece_types: list of piece type names
        placements_by_cell: dict[cell_pos] -> list of (ptype_index, mask, cells_list)

    For each cell position, placements_by_cell gives all placements where
    that cell is the first cell (in scan order) of the placed piece.
    """
    piece_types = list(PIECE_DEFS.keys())
    all_orientations = {}
    for ptype, defn in PIECE_DEFS.items():
        all_orientations[ptype] = generate_orientations(defn["cells"])

    # Precompute: for each cell, what placements have that cell as their
    # first-in-scan-order cell
    placements_by_cell = {}

    for pt_idx, ptype in enumerate(piece_types):
        for orient in all_orientations[ptype]:
            # orient is normalized: first cell in scan order is orient[0]
            fr, fc = orient[0]

            for anchor_r in range(H):
                for anchor_c in range(W):
                    off_r = anchor_r - fr
                    off_c = anchor_c - fc

                    # Compute all cell positions and bitmask
                    mask = 0
                    cells = []
                    valid = True
                    for dr, dc in orient:
                        cr, cc = off_r + dr, off_c + dc
                        if cr < 0 or cr >= H or cc < 0 or cc >= W:
                            valid = False
                            break
                        mask |= _cell_bit(cr, cc)
                        cells.append((cr, cc))

                    if valid:
                        # Key by the first cell in scan order = (anchor_r, anchor_c)
                        pos = anchor_r * W + anchor_c
                        if pos not in placements_by_cell:
                            placements_by_cell[pos] = []
                        placements_by_cell[pos].append((pt_idx, mask, cells))

    return piece_types, placements_by_cell


def solve_puzzle(progress_interval=5.0):
    """Find all unique solutions to the puzzle."""
    validate_pieces()

    piece_types, placements_by_cell = _precompute_placements()
    remaining = [PIECE_DEFS[pt]["count"] for pt in piece_types]

    # Board bitmask
    board_mask = [0]  # mutable container

    # Track which piece is at each cell for solution reconstruction
    cell_piece = [None] * (W * H)

    raw_solutions = []
    start_time = time.time()
    last_report = [start_time]
    nodes_explored = [0]

    def backtrack():
        # Find first empty cell
        r, c = _first_empty_cell(board_mask[0])
        if r == -1:
            # Board is full - record solution!
            grid = [[None] * W for _ in range(H)]
            for rr in range(H):
                for cc in range(W):
                    grid[rr][cc] = cell_piece[rr * W + cc]
            raw_solutions.append(grid)

            if len(raw_solutions) == 1:
                from display import print_grid_ansi
                print("\n  *** First solution found! ***\n")
                print_grid_ansi(grid, "  Solution 1:")

            now = time.time()
            if now - last_report[0] >= progress_interval:
                elapsed = now - start_time
                print(f"  Solutions: {len(raw_solutions)}, "
                      f"Nodes: {nodes_explored[0]:,}, "
                      f"Time: {elapsed:.1f}s")
                last_report[0] = now
            return

        pos = r * W + c
        placements = placements_by_cell.get(pos, [])

        for pt_idx, mask, cells in placements:
            if remaining[pt_idx] == 0:
                continue

            nodes_explored[0] += 1

            # Check no overlap
            if board_mask[0] & mask:
                continue

            # Place piece
            board_mask[0] |= mask
            remaining[pt_idx] -= 1
            ptype_name = piece_types[pt_idx]
            for cr, cc in cells:
                cell_piece[cr * W + cc] = ptype_name

            backtrack()

            # Unplace piece
            board_mask[0] &= ~mask
            remaining[pt_idx] += 1
            for cr, cc in cells:
                cell_piece[cr * W + cc] = None

        # Progress reporting (also report at dead ends for long searches)
        now = time.time()
        if now - last_report[0] >= progress_interval:
            elapsed = now - start_time
            print(f"  Solutions: {len(raw_solutions)}, "
                  f"Nodes: {nodes_explored[0]:,}, "
                  f"Time: {elapsed:.1f}s")
            last_report[0] = now

    print("Solving puzzle...")
    print(f"  Board: {W} x {H} = {W * H} cells")
    print(f"  Piece types: {len(piece_types)}, "
          f"Total pieces: {sum(remaining)}")
    total_placements = sum(len(v) for v in placements_by_cell.values())
    print(f"  Precomputed placements: {total_placements}")
    print()

    backtrack()

    elapsed = time.time() - start_time
    print(f"\nSearch complete!")
    print(f"  Raw solutions found: {len(raw_solutions)}")
    print(f"  Nodes explored: {nodes_explored[0]:,}")
    print(f"  Time: {elapsed:.1f}s")

    # Deduplicate mirror images
    print("\nDeduplicating mirror images...")
    unique = _deduplicate_mirrors(raw_solutions)
    print(f"  Unique solutions (after mirror dedup): {len(unique)}")

    return unique


def _grid_to_key(grid):
    """Convert grid to a hashable key."""
    return tuple(
        grid[r][c]
        for r in range(H)
        for c in range(W)
    )


def _mirror_h(grid):
    """Flip grid horizontally (left-right)."""
    return [[grid[r][W - 1 - c] for c in range(W)]
            for r in range(H)]


def _mirror_v(grid):
    """Flip grid vertically (top-bottom)."""
    return [[grid[H - 1 - r][c] for c in range(W)]
            for r in range(H)]


def _deduplicate_mirrors(solutions):
    """Remove duplicate solutions that are H/V/HV mirror images."""
    seen = set()
    unique = []

    for grid in solutions:
        h = _mirror_h(grid)
        v = _mirror_v(grid)
        hv = _mirror_h(v)

        keys = (
            _grid_to_key(grid),
            _grid_to_key(h),
            _grid_to_key(v),
            _grid_to_key(hv),
        )
        canon = min(keys)

        if canon not in seen:
            seen.add(canon)
            unique.append(grid)

    return unique


if __name__ == "__main__":
    solutions = solve_puzzle()
    print(f"\nTotal unique solutions: {len(solutions)}")
