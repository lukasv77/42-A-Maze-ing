*This project has been created as part of the 42 curriculum by llinda, mmankows.*

# A-Maze-ing

## Description

A-Maze-ing reads a configuration file, generates a random maze, writes it to
a file (one hexadecimal digit per cell) and shows it in the terminal with an
interactive menu. The maze always contains a "42" drawn with fully closed
cells (when the maze is big enough, at least 9x7).

Two modes:

- `PERFECT=True`: exactly one path between any two cells (no loops).
- `PERFECT=False`: a Pac-Man-like board with loops and almost no dead-ends.

## Instructions

Requirements: Python 3.10 or later.

```
make install      # install flake8 and mypy
make run          # python3 a_maze_ing.py config.txt
make debug        # run with pdb
make lint         # flake8 + mypy
make build        # rebuild mazegen-1.0.0-py3-none-any.whl
make clean        # remove caches
```

Menu while the program runs:

1. Re-generate a new maze (the output file is updated too)
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit

Colours: walls (rotating), entry magenta, exit red, path cyan, "42" grey.

## Configuration file

One `KEY=VALUE` per line, lines starting with `#` are ignored.

| Key           | Meaning                          | Example            |
|---------------|----------------------------------|--------------------|
| `WIDTH`       | width in cells (at least 2)      | `WIDTH=20`         |
| `HEIGHT`      | height in cells (at least 2)     | `HEIGHT=15`        |
| `ENTRY`       | entry cell `x,y`                 | `ENTRY=0,0`        |
| `EXIT`        | exit cell `x,y`                  | `EXIT=19,14`       |
| `OUTPUT_FILE` | output file name                 | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | `True` or `False`                | `PERFECT=True`     |
| `SEED`        | optional, same seed = same maze  | `SEED=42`          |

All keys except `SEED` are mandatory. `(0, 0)` is the top-left cell.

## Output file

One line per row, one hex digit per cell. A set bit means a closed wall:
1 = North, 2 = East, 4 = South, 8 = West. Then an empty line, the entry,
the exit and the shortest path written with `N`, `E`, `S`, `W`.

## Algorithm

**Recursive backtracker (depth-first search)**, written with a stack instead
of recursion:

1. Start with every wall closed.
2. From the current cell, pick a random unvisited neighbour, open the wall
   between them and move there.
3. If there is no unvisited neighbour, go back (pop the stack).

The "42" cells are never visited, so they stay fully closed.
This gives a perfect maze (a spanning tree): one path between any two cells
and no open areas.

For `PERFECT=False`, every dead-end gets one extra wall opened, which creates
loops. A wall is put back if opening it would make a 3x3 open area.
The only dead-ends left are the two small pockets inside the "2" of "42".

The shortest path is found with a **breadth-first search (BFS)**.

**Why this algorithm:** it is short, easy to explain and to debug, it always
gives a fully connected maze, and its long corridors look good.

## Reusable code

The generator is the `MazeGenerator` class in `mazegen.py`, packaged as
`mazegen-1.0.0-py3-none-any.whl` (built from `pyproject.toml` with
`make build`).

```
pip install mazegen-1.0.0-py3-none-any.whl
```

```python
from mazegen import MazeGenerator

maze = MazeGenerator(width=20, height=15, entry=(0, 0), exit_=(19, 14),
                     perfect=True, seed=42)
maze.generate()

maze.grid[y][x]   # int, wall bits: 1=N, 2=E, 4=S, 8=W
maze.pattern      # set of (x, y) cells of the "42"
maze.solve()      # shortest path, e.g. "EESSE..."
maze.generate()   # call again for a new maze
```

Custom parameters: `width`, `height`, `entry`, `exit_`, `perfect`
(default `True`) and `seed` (default `None` = random). Invalid parameters
raise `ValueError`.

## Team and project management

- Roles: <login> - everything (generation, output file, display, packaging).
- Planning: generator first, then output file, then display and menu,
  then packaging and README. <describe how it evolved>
- What worked well / what could be improved: <fill in>
- Tools: Python 3, flake8, mypy, setuptools, git.

## Resources

- Maze generation algorithms - Jamis Buck, "Maze Generation: Recursive
  Backtracking": https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking
- Maze generation algorithm (Wikipedia):
  https://en.wikipedia.org/wiki/Maze_generation_algorithm
- Breadth-first search (Wikipedia):
  https://en.wikipedia.org/wiki/Breadth-first_search
- Python packaging tutorial: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- ANSI escape codes: https://en.wikipedia.org/wiki/ANSI_escape_code

**AI usage:** <describe honestly, e.g. which parts were written or explained
with AI, and how you checked and understood them>.
