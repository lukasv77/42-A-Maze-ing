"""Draw the maze in the terminal with thin walls and ANSI colours."""

from mazegen import EAST, SOUTH, MazeGenerator

RESET = "\033[0m"
PATTERN = "\033[100m"   # grey background
PATH = "\033[46m"       # cyan background
ENTRY = "\033[45m"      # magenta background
EXIT = "\033[41m"       # red background
WALL_COLOURS = [
    "\033[37m",         # white text
    "\033[34m",         # blue text
    "\033[32m",         # green text
    "\033[33m",         # yellow text
]

STEPS = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def render(maze: MazeGenerator, show_path: bool, colour: int) -> str:
    """Return the maze as text ready to print.

    Every cell is a box 3 characters wide. Only the east and south wall
    of each cell is drawn, because its north and west walls are the
    south and east walls of its neighbours.
    """
    wall = WALL_COLOURS[colour % len(WALL_COLOURS)]
    path = path_cells(maze) if show_path else set()

    lines = [wall + "+" + "---+" * maze.width + RESET]
    for y in range(maze.height):
        middle = wall + "|"
        bottom = wall + "+"
        for x in range(maze.width):
            cell = maze.grid[y][x]
            middle += cell_text(maze, x, y, path) + RESET + wall
            if cell & EAST:
                middle += "|"
            elif (x, y) in path and (x + 1, y) in path:
                middle += PATH + " " + RESET + wall
            else:
                middle += " "
            if cell & SOUTH:
                bottom += "---"
            elif (x, y) in path and (x, y + 1) in path:
                bottom += PATH + "   " + RESET + wall
            else:
                bottom += "   "
            bottom += "+"
        lines.append(middle + RESET)
        lines.append(bottom + RESET)
    return "\n".join(lines)


def path_cells(maze: MazeGenerator) -> set[tuple[int, int]]:
    """Return the cells on the shortest path, entry and exit included."""
    x, y = maze.entry
    cells = {(x, y)}
    for letter in maze.solve():
        dx, dy = STEPS[letter]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def cell_text(maze: MazeGenerator, x: int, y: int,
              path: set[tuple[int, int]]) -> str:
    """Return the 3 characters drawn inside one cell."""
    if (x, y) == maze.entry:
        return ENTRY + " E "
    if (x, y) == maze.exit:
        return EXIT + " X "
    if (x, y) in maze.pattern:
        return PATTERN + "   "
    if (x, y) in path:
        return PATH + "   "
    return "   "
