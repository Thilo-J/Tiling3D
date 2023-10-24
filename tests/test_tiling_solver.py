import pytest
import numpy as np

import tiling_solver as ts
from tiling_objects import TilingProblem, Cuboid
from tiles import get_all_tiles, get_tiles_by_name

def test_single_solution_solver():
    board_shape = np.array([
        [
            [1,0,0,1],
            [1,0,0,1],
            [0,0,0,0],
        ],
        [
            [1,0,0,1],
            [1,0,0,1],
            [0,0,0,0],
        ]
    ])
    board = ShapeToFill("B10-1", board_shape)
    problem = TilingProblem(get_all_tiles()[0:16], board)
    solution = ts.get_single_solution(problem)
    assert len(solution.solution_tiles) == 4


def test_dxz_solver():
    board = ShapeToFill("B10-2", np.array([
        [
            [1,0,0,0],
            [0,0,0,0],
            [0,1,0,1]
        ],
        [
            [1,0,0,0],
            [0,0,0,0],
            [0,1,0,1]
        ]
    ]))
    tiles = get_all_tiles()[0:16]
    solutions = ts.get_all_solutions(TilingProblem(tiles, board))
    assert len(solutions) == 300

    board = ShapeToFill("B4-1", np.array([
        [
            [1,0,0,1],
            [1,0,0,1],
            [0,0,0,0]
        ],
        [
            [1,0,0,1],
            [1,0,0,1],
            [0,0,0,0]
        ]
    ]))
    tiles = get_tiles_by_name(["t16", "t8", "t14", "t10"])
    solutions = ts.get_all_solutions(TilingProblem(tiles, board))
    assert len(solutions) == 10

    board = ShapeToFill("B1-1", np.array([
        [
            [0,0,0],
            [0,0,0],
            [0,1,0]
        ],
        [
            [0,0,0],
            [0,0,0],
            [0,1,0]
        ]
    ]))
    tiles = get_tiles_by_name(["t16", "t8", "t7", "t10"])
    solutions = ts.get_all_solutions(TilingProblem(tiles, board))
    assert len(solutions) == 38

if __name__ == "__main__":
    pytest.main()