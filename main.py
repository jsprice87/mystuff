#!/usr/bin/env python3
"""
Wood Intelligence Puzzle Solver

Finds all unique solutions to the Wood Intelligence wooden Tetris puzzle.

Usage:
    python main.py                  # Run full solver, generate HTML
    python main.py --show-pieces    # Display piece definitions
    python main.py --validate       # Validate piece definitions only
"""

import sys
from pieces import validate_pieces, show_pieces
from solver import solve_puzzle
from display import generate_html, print_grid_ansi


def main():
    args = sys.argv[1:]

    if "--show-pieces" in args:
        show_pieces()
        return

    if "--validate" in args:
        try:
            validate_pieces()
            print("Validation passed: piece areas sum to board area.")
        except ValueError as e:
            print(f"Validation FAILED: {e}")
            sys.exit(1)
        return

    # Full solve
    print("=" * 60)
    print("  Wood Intelligence Puzzle Solver")
    print("=" * 60)
    print()

    try:
        validate_pieces()
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    unique_count, display_grids = solve_puzzle()

    if unique_count == 0:
        print("\nNo solutions found!")
        return

    # Show first few solutions in terminal
    show_count = min(3, len(display_grids))
    if show_count > 1:
        print(f"\nShowing first {show_count} solution(s) in terminal:\n")
        for i in range(1, show_count):  # skip 1 since it was already shown
            print_grid_ansi(display_grids[i], f"Solution {i + 1}:")

    # Generate HTML
    output_file = "solutions.html"
    generate_html(display_grids, output_file, total_unique=unique_count)

    print(f"\n{'=' * 60}")
    print(f"  RESULT: {unique_count:,} unique solutions found")
    print(f"  HTML shows {len(display_grids)} of them")
    print(f"{'=' * 60}")
    print(f"\nOpen {output_file} in a browser to view solutions graphically.")


if __name__ == "__main__":
    main()
