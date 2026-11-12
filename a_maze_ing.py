"""A-Maze-ing: generate a maze from a config file, save it and show it.

Usage: python3 a_maze_ing.py config.txt
"""

import sys

from config import read_config
from display import render
from mazegen import MazeGenerator

MENU = """=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit"""


def save_maze(maze: MazeGenerator, filename: str) -> None:
    """Write the maze in the hexadecimal format required by the subject."""
    with open(filename, "w") as file:
        for row in maze.grid:
            file.write("".join(f"{cell:x}" for cell in row) + "\n")
        file.write("\n")
        file.write(f"{maze.entry[0]},{maze.entry[1]}\n")
        file.write(f"{maze.exit[0]},{maze.exit[1]}\n")
        file.write(maze.solve() + "\n")


def run_menu(maze: MazeGenerator, output_file: str) -> None:
    """Show the maze and react to the user's choices until they quit."""
    show_path = False
    colour = 0
    while True:
        print("\033[2J\033[H", end="")  # clear the terminal
        print(render(maze, show_path, colour))
        if not maze.pattern:
            print("Error: the maze is too small to draw the '42' pattern")
        print(MENU)
        try:
            choice = input("Choice? (1-4): ").strip()
        except EOFError:
            return
        if choice == "1":
            maze.generate()
            save_maze(maze, output_file)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            colour += 1
        elif choice == "4":
            return


def main() -> None:
    """Read the config, build the maze, save it and start the menu."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)
    try:
        config = read_config(sys.argv[1])
        maze = MazeGenerator(config.width, config.height, config.entry,
                             config.exit, config.perfect, config.seed)
        maze.generate()
        save_maze(maze, config.output_file)
        run_menu(maze, config.output_file)
    except (OSError, ValueError) as error:
        print(f"Error: {error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
