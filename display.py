"""
Display solutions graphically: HTML output and terminal ANSI output.
"""

from pieces import BOARD_WIDTH, BOARD_HEIGHT

# CSS colors for each piece type
CSS_COLORS = {
    "white":  "#f0f0f0",
    "black":  "#333333",
    "green":  "#4caf50",
    "orange": "#ff9800",
    "yellow": "#ffeb3b",
    "red":    "#f44336",
    "blue":   "#2196f3",
    "purple": "#9c27b0",
}

# ANSI background colors for terminal
ANSI_COLORS = {
    "white":  "\033[47m",
    "black":  "\033[40m",
    "green":  "\033[42m",
    "orange": "\033[48;5;208m",
    "yellow": "\033[43m",
    "red":    "\033[41m",
    "blue":   "\033[44m",
    "purple": "\033[45m",
}

ANSI_RESET = "\033[0m"

# Text colors for contrast on each background
CSS_TEXT_COLORS = {
    "white":  "#333",
    "black":  "#fff",
    "green":  "#fff",
    "orange": "#000",
    "yellow": "#333",
    "red":    "#fff",
    "blue":   "#fff",
    "purple": "#fff",
}


def print_grid_ansi(grid, label=""):
    """Print a solution grid using ANSI colors in the terminal."""
    if label:
        print(label)
    for r in range(BOARD_HEIGHT):
        line = ""
        for c in range(BOARD_WIDTH):
            ptype = grid[r][c]
            color = ANSI_COLORS.get(ptype, "")
            # Use first letter as label
            ch = ptype[0].upper() if ptype else "?"
            line += f"{color} {ch} {ANSI_RESET}"
        print(line)
    print()


def _cell_borders(grid, r, c):
    """Determine which borders a cell needs (where it borders a different piece)."""
    ptype = grid[r][c]
    borders = []
    if r == 0 or grid[r-1][c] != ptype:
        borders.append("top")
    if r == BOARD_HEIGHT - 1 or grid[r+1][c] != ptype:
        borders.append("bottom")
    if c == 0 or grid[r][c-1] != ptype:
        borders.append("left")
    if c == BOARD_WIDTH - 1 or grid[r][c+1] != ptype:
        borders.append("right")
    return borders


def generate_html(solutions, filename="solutions.html"):
    """Generate an HTML file showing all solutions with colored grids.

    Each solution is rendered as a CSS grid with colored cells and borders
    between different piece types.
    """
    html_parts = ["""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wood Intelligence Puzzle Solutions</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #1a1a2e;
    color: #eee;
    padding: 20px;
}
h1 {
    text-align: center;
    margin-bottom: 10px;
    font-size: 2em;
    color: #e0e0ff;
}
.summary {
    text-align: center;
    margin-bottom: 30px;
    font-size: 1.1em;
    color: #aaa;
}
.legend {
    display: flex;
    justify-content: center;
    gap: 15px;
    margin-bottom: 30px;
    flex-wrap: wrap;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.9em;
}
.legend-swatch {
    width: 20px;
    height: 20px;
    border: 1px solid #555;
    border-radius: 3px;
}
.solutions-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 30px;
}
.solution-card {
    background: #16213e;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.solution-label {
    text-align: center;
    margin-bottom: 8px;
    font-weight: bold;
    color: #7ec8e3;
}
.grid {
    display: grid;
    grid-template-columns: repeat(""" + str(BOARD_WIDTH) + """, 28px);
    grid-template-rows: repeat(""" + str(BOARD_HEIGHT) + """, 28px);
    gap: 0;
}
.cell {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: bold;
}
/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 30px 0;
    flex-wrap: wrap;
}
.pagination button {
    background: #16213e;
    color: #7ec8e3;
    border: 1px solid #7ec8e3;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
}
.pagination button:hover {
    background: #7ec8e3;
    color: #1a1a2e;
}
.pagination button.active {
    background: #7ec8e3;
    color: #1a1a2e;
}
</style>
</head>
<body>
"""]

    total = len(solutions)
    html_parts.append(f'<h1>Wood Intelligence Puzzle Solutions</h1>\n')
    html_parts.append(f'<div class="summary">Found <strong>{total}</strong> unique solution{"s" if total != 1 else ""}</div>\n')

    # Legend
    html_parts.append('<div class="legend">\n')
    for ptype, color in CSS_COLORS.items():
        html_parts.append(
            f'  <div class="legend-item">'
            f'<div class="legend-swatch" style="background:{color}"></div>'
            f'{ptype}</div>\n'
        )
    html_parts.append('</div>\n')

    # Pagination setup
    per_page = 50
    num_pages = max(1, (total + per_page - 1) // per_page)

    if num_pages > 1:
        html_parts.append('<div class="pagination" id="pagination-top">\n')
        for p in range(num_pages):
            start = p * per_page + 1
            end = min((p + 1) * per_page, total)
            active = ' class="active"' if p == 0 else ''
            html_parts.append(
                f'  <button{active} onclick="showPage({p})">'
                f'{start}-{end}</button>\n'
            )
        html_parts.append('</div>\n')

    # Solution grids
    for page in range(num_pages):
        display = "flex" if page == 0 else "none"
        html_parts.append(
            f'<div class="solutions-container" id="page-{page}" '
            f'style="display:{display}">\n'
        )
        start = page * per_page
        end = min(start + per_page, total)

        for idx in range(start, end):
            grid = solutions[idx]
            html_parts.append(f'<div class="solution-card">\n')
            html_parts.append(f'  <div class="solution-label">Solution {idx + 1}</div>\n')
            html_parts.append(f'  <div class="grid">\n')

            for r in range(BOARD_HEIGHT):
                for c in range(BOARD_WIDTH):
                    ptype = grid[r][c]
                    bg = CSS_COLORS.get(ptype, "#888")
                    fg = CSS_TEXT_COLORS.get(ptype, "#000")
                    borders = _cell_borders(grid, r, c)

                    border_style = []
                    for side in ["top", "right", "bottom", "left"]:
                        if side in borders:
                            border_style.append(f"border-{side}: 2px solid rgba(0,0,0,0.6)")
                        else:
                            border_style.append(f"border-{side}: 1px solid rgba(0,0,0,0.1)")

                    style = f"background:{bg};color:{fg};" + ";".join(border_style)
                    label = ptype[0].upper() if ptype else "?"
                    html_parts.append(
                        f'    <div class="cell" style="{style}" '
                        f'title="{ptype}">{label}</div>\n'
                    )

            html_parts.append('  </div>\n')
            html_parts.append('</div>\n')

        html_parts.append('</div>\n')

    # Pagination JS
    if num_pages > 1:
        html_parts.append("""
<script>
function showPage(page) {
    const pages = document.querySelectorAll('.solutions-container');
    pages.forEach((p, i) => {
        p.style.display = i === page ? 'flex' : 'none';
    });
    document.querySelectorAll('.pagination button').forEach((btn, i) => {
        btn.classList.toggle('active', i % """ + str(num_pages) + """ === page);
    });
}
</script>
""")

    html_parts.append('</body>\n</html>')

    with open(filename, 'w') as f:
        f.write(''.join(html_parts))

    print(f"HTML output written to {filename}")
