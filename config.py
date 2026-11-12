"""Read and check the configuration file (one KEY=VALUE per line)."""

from dataclasses import dataclass

REQUIRED_KEYS = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]


@dataclass
class Config:
    """All settings read from the configuration file."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None


def read_config(path: str) -> Config:
    """Read the configuration file and convert its values.

    Raises:
        OSError: if the file cannot be opened.
        ValueError: if a line or a value is invalid.
    """
    values: dict[str, str] = {}
    with open(path) as file:
        for number, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"line {number}: expected KEY=VALUE")
            key, value = line.split("=", 1)
            values[key.strip().upper()] = value.strip()

    for key in REQUIRED_KEYS:
        if key not in values:
            raise ValueError(f"missing key {key}")
    if not values["OUTPUT_FILE"]:
        raise ValueError("OUTPUT_FILE is empty")

    seed = None
    if "SEED" in values:
        seed = to_int(values["SEED"], "SEED")

    return Config(
        width=to_int(values["WIDTH"], "WIDTH"),
        height=to_int(values["HEIGHT"], "HEIGHT"),
        entry=to_cell(values["ENTRY"], "ENTRY"),
        exit=to_cell(values["EXIT"], "EXIT"),
        output_file=values["OUTPUT_FILE"],
        perfect=to_bool(values["PERFECT"], "PERFECT"),
        seed=seed,
    )


def to_int(text: str, name: str) -> int:
    """Convert text to an int, with a clear error message."""
    try:
        return int(text)
    except ValueError:
        raise ValueError(f"{name} must be an integer, got '{text}'")


def to_cell(text: str, name: str) -> tuple[int, int]:
    """Convert "x,y" to a tuple (x, y)."""
    parts = text.split(",")
    if len(parts) != 2:
        raise ValueError(f"{name} must look like x,y, got '{text}'")
    return to_int(parts[0].strip(), name), to_int(parts[1].strip(), name)


def to_bool(text: str, name: str) -> bool:
    """Convert "True" or "False" (any case) to a bool."""
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    raise ValueError(f"{name} must be True or False, got '{text}'")
