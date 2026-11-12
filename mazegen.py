"""mazegen - a small, reusable maze generator.

Basic example::

    from mazegen import MazeGenerator

    maze = MazeGenerator(width=20, height=15, entry=(0, 0),
                         exit_=(19, 14), perfect=True, seed=42)
    maze.generate()
    print(maze.grid[0][0])   # walls of the top-left cell
    print(maze.solve())      # shortest path, e.g. "EESSE..."

Parameters:
    width, height: size of the maze in cells.
    entry, exit_: (x, y) coordinates, (0, 0) is the top-left cell.
    perfect: True -> exactly one path between any two cells.
             False -> loops are added and dead-ends are removed.
    seed: any int gives the same maze every time, None gives a random one.

Generated structure:
    maze.grid[y][x] is an int. Each set bit is a closed wall:
    1 = North, 2 = East, 4 = South, 8 = West (15 = fully closed).
    maze.pattern is the set of (x, y) cells used to draw "42".
    maze.solve() returns the shortest path as letters N, E, S, W.
    Call maze.generate() again to get a new maze.
"""

import random
from collections import deque

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = 15

# direction -> (dx, dy) to reach the neighbouring cell
MOVES: dict[int, tuple[int, int]] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}
OPPOSITE: dict[int, int] = {NORTH: SOUTH, EAST: WEST, SOUTH: NORTH, WEST: EAST}
LETTERS: dict[int, str] = {NORTH: "N", EAST: "E", SOUTH: "S", WEST: "W"}

# The "42" drawn with closed cells ('#'), 7 cells wide and 5 cells high.
PATTERN_42 = [
    "#...###",
    "#.....#",
    "###.###",
    "..#.#..",
    "..#.###",
]

Cell = tuple[int, int]


class MazeGenerator:
    """Generate a random maze and find its shortest path."""

    def __init__(self, width: int, height: int, entry: Cell, exit_: Cell,
                 perfect: bool = True, seed: int | None = None) -> None:
        """Check the parameters and prepare the generator.

        Raises:
            ValueError: if the parameters cannot give a valid maze.
        """
        if width < 2 or height < 2:
            raise ValueError("WIDTH and HEIGHT must be at least 2")
        for name, (x, y) in (("ENTRY", entry), ("EXIT", exit_)):
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"{name} {x},{y} is outside the maze")
        if entry == exit_:
            raise ValueError("ENTRY and EXIT must be different")

        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_
        self.perfect = perfect
        self.rng = random.Random(seed)
        self.pattern = self._place_pattern()
        if entry in self.pattern or exit_ in self.pattern:
            raise ValueError("ENTRY or EXIT is inside the '42' pattern")
        self.grid: list[list[int]] = []

    def generate(self) -> None:
        """Build a new maze. Every call gives a different maze."""
        self.grid = [[ALL_WALLS] * self.width for _ in range(self.height)]
        self._carve_paths()
        if not self.perfect:
            self._remove_dead_ends()

    def solve(self) -> str:
        """Return the shortest path from entry to exit (BFS).

        Returns:
            A string of letters N, E, S, W.
        """
        came_from: dict[Cell, tuple[Cell, int] | None] = {self.entry: None}
        queue = deque([self.entry])
        while queue:
            x, y = queue.popleft()
            if (x, y) == self.exit:
                break
            for direction, (dx, dy) in MOVES.items():
                neighbour = (x + dx, y + dy)
                if self.grid[y][x] & direction or neighbour in came_from:
                    continue
                came_from[neighbour] = ((x, y), direction)
                queue.append(neighbour)

        if self.exit not in came_from:
            return ""
        letters = []
        step = came_from[self.exit]
        while step is not None:
            previous, direction = step
            letters.append(LETTERS[direction])
            step = came_from[previous]
        return "".join(reversed(letters))

    def _place_pattern(self) -> set[Cell]:
        """Return the cells of "42", centred in the maze.

        Returns an empty set when the maze is too small for it.
        """
        pattern_width = len(PATTERN_42[0])
        pattern_height = len(PATTERN_42)
        left = self.width // 2 - pattern_width // 2
        top = self.height // 2 - pattern_height // 2
        # keep at least one free cell between the pattern and the border
        if (left < 1 or top < 1
                or left + pattern_width > self.width - 1
                or top + pattern_height > self.height - 1):
            return set()

        cells = set()
        for row, line in enumerate(PATTERN_42):
            for col, char in enumerate(line):
                if char == "#":
                    cells.add((left + col, top + row))
        return cells

    def _neighbours(self, x: int, y: int) -> list[tuple[int, int, int]]:
        """Return (nx, ny, direction) for each usable neighbour of a cell."""
        result = []
        for direction, (dx, dy) in MOVES.items():
            nx, ny = x + dx, y + dy
            inside = 0 <= nx < self.width and 0 <= ny < self.height
            if inside and (nx, ny) not in self.pattern:
                result.append((nx, ny, direction))
        return result

    def _open_wall(self, x: int, y: int, direction: int) -> None:
        """Remove the wall on one side of a cell and on its neighbour."""
        dx, dy = MOVES[direction]
        self.grid[y][x] &= ~direction
        self.grid[y + dy][x + dx] &= ~OPPOSITE[direction]

    def _close_wall(self, x: int, y: int, direction: int) -> None:
        """Put back the wall on one side of a cell and on its neighbour."""
        dx, dy = MOVES[direction]
        self.grid[y][x] |= direction
        self.grid[y + dy][x + dx] |= OPPOSITE[direction]

    def _carve_paths(self) -> None:
        """Recursive backtracker (depth-first search) with a stack.

        Gives a perfect maze: every cell is reachable by exactly one path.
        """
        visited = {self.entry}
        stack = [self.entry]
        while stack:
            x, y = stack[-1]
            options = [(nx, ny, direction)
                       for nx, ny, direction in self._neighbours(x, y)
                       if (nx, ny) not in visited]
            if not options:
                stack.pop()
                continue
            nx, ny, direction = self.rng.choice(options)
            self._open_wall(x, y, direction)
            visited.add((nx, ny))
            stack.append((nx, ny))

    def _remove_dead_ends(self) -> None:
        """Open one extra wall in each dead-end, which creates loops."""
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern:
                    continue
                if bin(self.grid[y][x]).count("1") != 3:
                    continue
                closed = [direction
                          for _, _, direction in self._neighbours(x, y)
                          if self.grid[y][x] & direction]
                self.rng.shuffle(closed)
                for direction in closed:
                    self._open_wall(x, y, direction)
                    if not self._has_open_area(x, y):
                        break
                    self._close_wall(x, y, direction)

    def _has_open_area(self, x: int, y: int) -> bool:
        """Check for a forbidden 3x3 open area around a cell."""
        for top in range(y - 3, y + 2):
            for left in range(x - 3, x + 2):
                if self._is_open_3x3(left, top):
                    return True
        return False

    def _is_open_3x3(self, left: int, top: int) -> bool:
        """Return True if the 3x3 block has no wall inside it."""
        if left < 0 or top < 0:
            return False
        if left + 3 > self.width or top + 3 > self.height:
            return False
        for y in range(top, top + 3):
            for x in range(left, left + 3):
                cell = self.grid[y][x]
                if x < left + 2 and cell & EAST:
                    return False
                if y < top + 2 and cell & SOUTH:
                    return False
        return True
