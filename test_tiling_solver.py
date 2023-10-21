import pytest
from ubongo_boards import get_board_by_name
import tiling_solver as ts
from tiling_objects import TilingProblem
from ubongo_tiles import TILES, get_tiles_by_name
from ubongo_boards import get_board_by_name

def test_python_solver():
    board = get_board_by_name("B11-1")
    tiles = get_tiles_by_name(["t12","t5","t16", "t8"])
    solutions = ts.python_solve(TilingProblem(tiles, board))
    assert len(solutions) == 1

    board = get_board_by_name("B12-1")
    tiles = get_tiles_by_name(["t9","t3","t15", "t8"])
    solutions = ts.python_solve(TilingProblem(tiles, board))
    assert len(solutions) == 3


def test_single_solution_solver():
    board = get_board_by_name("B10-1")
    solution = ts.get_single_solution(TilingProblem(TILES, board))
    assert len([i for i in solution.solution_tiles if len(i.coordinates) != 0]) == 4


def test_dxz_solver():
    board = get_board_by_name("B10-2")
    solutions = ts.dxz_solve(TilingProblem(TILES, board))
    assert len(solutions) == 300
    board = get_board_by_name("B4-1")
    tiles = get_tiles_by_name(["t16", "t8", "t14", "t10"])
    solutions = ts.dxz_solve(TilingProblem(tiles, board))
    assert len(solutions) == 10
    board = get_board_by_name("B1-1")
    tiles = get_tiles_by_name(["t16", "t8", "t7", "t10"])
    solutions = ts.dxz_solve(TilingProblem(tiles, board))
    assert len(solutions) == 38  


if __name__ == "__main__":
    pytest.main()