import numpy as np

class Tile:
    def __init__(self, name:str, color:str, form:np.array):
        self.name = name
        self.color = color
        self.form = np.array(form, dtype=bool)

class Board:
    def __init__(self, name:str, form:np.array):
        self.name = name
        self.form = np.array(form, dtype=bool)

class TilingProblem:
    def __init__(self, tiles: list[Tile], board: Board, name: str = ""):
        self.name = name
        self.tiles = tiles
        self.board = board
        self.solutions = []

class SolutionTile:
    def __init__(self, name:str, color:str, coordinates:list[tuple[int, int, int]]):
        self.name = name
        self.color = color
        self.coordinates = coordinates

class TilingSolution:
    def __init__(self, solution_tiles:list[SolutionTile], board:Board, problem_name:str = ""):
        self.solution_tiles = solution_tiles
        self.board = board
        self.problem_name = problem_name
        self.images: list[str] = []

