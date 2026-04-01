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
    inv = (~mask) & FULL_MASK
    if inv == 0:
        return -1, -1
    bit = inv & (-inv)
    pos = bit.bit_length() - 1
    return pos // W, pos % W


def _precompute_placements():
    """Precompute all valid placements for each piece type, indexed by cell."""
    piece_types = list(PIECE_DEFS.keys())
    all_orientations = {}
    for ptype, defn in PIECE_DEFS.items():
        all_orientations[ptype] = generate_orientations(defn["cells"])

    placements_by_cell = {}

    for pt_idx, ptype in enumerate(piece_types):
        for orient in all_orientations[ptype]:
            fr, fc = orient[0]

            for anchor_r in range(H):
                for anchor_c in range(W):
                    off_r = anchor_r - fr
                    off_c = anchor_c - fc

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
                        pos = anchor_r * W + anchor_c
                        if pos not in placements_by_cell:
                            placements_by_cell[pos] = []
                        placements_by_cell[pos].append((pt_idx, mask, cells))

    return piece_types, placements_by_cell


def _grid_to_key(grid):
    """Convert grid to a hashable key."""
    return tuple(
        grid[r][c]
        for r in range(H)
        for c in range(W)
    )


def _key_from_cell_piece(cell_piece):
    """Convert cell_piece array directly to a canonical key."""
    return tuple(cell_piece)


def _mirror_h_key(key):
    """Compute H-mirror of a key (flip left-right)."""
    result = []
    for r in range(H):
        for c in range(W):
            result.append(key[r * W + (W - 1 - c)])
    return tuple(result)


def _mirror_v_key(key):
    """Compute V-mirror of a key (flip top-bottom)."""
    result = []
    for r in range(H):
        for c in range(W):
            result.append(key[(H - 1 - r) * W + c])
    return tuple(result)


def _mirror_hv_key(key):
    """Compute HV-mirror of a key (flip both)."""
    result = []
    for r in range(H):
        for c in range(W):
            result.append(key[(H - 1 - r) * W + (W - 1 - c)])
    return tuple(result)


def _canonical_key(key):
    """Return the canonical form (min of 4 mirror variants)."""
    return min(key, _mirror_h_key(key), _mirror_v_key(key), _mirror_hv_key(key))


def solve_puzzle(progress_interval=5.0, max_display=1000):
    """Find all unique solutions to the puzzle.

    Args:
        progress_interval: seconds between progress reports
        max_display: maximum number of solution grids to keep for display

    Returns:
        tuple of (unique_count, display_grids)
    """
    validate_pieces()

    piece_types, placements_by_cell = _precompute_placements()
    remaining = [PIECE_DEFS[pt]["count"] for pt in piece_types]

    board_mask = [0]
    cell_piece = [None] * (W * H)

    # Track unique solutions by canonical key
    seen_keys = set()
    display_grids = []  # only store first max_display grids
    raw_count = [0]

    start_time = time.time()
    last_report = [start_time]
    nodes_explored = [0]

    def backtrack():
        r, c = _first_empty_cell(board_mask[0])
        if r == -1:
            # Board is full!
            raw_count[0] += 1

            # Compute canonical key for deduplication
            key = _key_from_cell_piece(cell_piece)
            canon = _canonical_key(key)

            if canon not in seen_keys:
                seen_keys.add(canon)

                # Save grid for display (up to limit)
                if len(display_grids) < max_display:
                    grid = [[None] * W for _ in range(H)]
                    for rr in range(H):
                        for cc in range(W):
                            grid[rr][cc] = cell_piece[rr * W + cc]
                    display_grids.append(grid)

                if len(seen_keys) == 1:
                    from display import print_grid_ansi
                    grid = [[None] * W for _ in range(H)]
                    for rr in range(H):
                        for cc in range(W):
                            grid[rr][cc] = cell_piece[rr * W + cc]
                    print("\n  *** First unique solution found! ***\n")
                    print_grid_ansi(grid, "  Solution 1:")

            now = time.time()
            if now - last_report[0] >= progress_interval:
                elapsed = now - start_time
                print(f"  Raw: {raw_count[0]:,}, "
                      f"Unique: {len(seen_keys):,}, "
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

        # Progress at dead ends too
        now = time.time()
        if now - last_report[0] >= progress_interval:
            elapsed = now - start_time
            print(f"  Raw: {raw_count[0]:,}, "
                  f"Unique: {len(seen_keys):,}, "
                  f"Nodes: {nodes_explored[0]:,}, "
                  f"Time: {elapsed:.1f}s")
            last_report[0] = now

    print("Solving puzzle...")
    print(f"  Board: {W} x {H} = {W * H} cells")
    print(f"  Piece types: {len(piece_types)}, "
          f"Total pieces: {sum(remaining)}")
    total_placements = sum(len(v) for v in placements_by_cell.values())
    print(f"  Precomputed placements: {total_placements}")
    print(f"  Saving first {max_display} solutions for display")
    print()

    backtrack()

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"  Search complete!")
    print(f"  Raw solutions: {raw_count[0]:,}")
    print(f"  Unique solutions (after mirror dedup): {len(seen_keys):,}")
    print(f"  Nodes explored: {nodes_explored[0]:,}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'='*60}")

    return len(seen_keys), display_grids


if __name__ == "__main__":
    count, grids = solve_puzzle()
    print(f"\nTotal unique solutions: {count}")
