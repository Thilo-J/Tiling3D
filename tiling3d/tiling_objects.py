from dataclasses import dataclass, field
import numpy as np

@dataclass
class Tile:
    """
    A class to represent a Tile.

    Args:
        name (str): Name of the tile.
        color (str): The color of the tile (for example: #fc03d2).
        form (np.array): A 3D array of the form.
    
    """
    name: str
    color: str
    coordinates: list[tuple[int, int, int]]

@dataclass
class Cuboid:
    """
    A class to represent a cuboid with some part filled in.

    Args:
        name (str): Name of the cuboid
        form (np.array): A 3D array of the cuboid with 1s indicating that that part is filled in.
    
    """
    name: str
    form: np.array


@dataclass
class TilingSolution:
    """
    A class to represent a solution to a given TilingProblem

    Args:
        color (str): The color of the polyomino (for example: #fc03d2).
        form (np.array): A 3D array of the form.
        name (str): Name of the solution.
    
    """
    solution_tiles: list[Tile]
    board: Cuboid
    name:str = ""

@dataclass
class TilingProblem:
    """
    A class to represent a tiling problem

    Args:
        tiles (list[Tile]): A list of tiles that can be used to fill the shape
        shape (ShapeToFill): A cuboid with some parts already filled where the tiles need to fill in the rest of the cuboid.
        solutions: (list[TilingSolution]): Possible solutions.
        name (str): Name of the problem.
    
    """
    tiles: list[Tile]
    shape: Cuboid
    solutions: list[TilingSolution] = field(default_factory=list)
    name: str = ""
