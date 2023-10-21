import pytest
import tiling_solver as ts
from tiling_objects import TilingProblem, Board
import numpy as np
from tiles import all_tiles, get_tiles_by_name


"""
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
"""

def test_single_solution_solver():
    board_form = np.array([
                        [
                            [1,0,0,0],
                            [1,0,0,0],
                            [1,0,0,1],
                            [0,0,0,1]
                        ],
                        [
                            [1,0,0,0],
                            [1,0,0,0],
                            [1,0,0,1],
                            [0,0,0,1]
                        ]])
    board = Board("test", board_form)
    tiles = all_tiles()
    problem = TilingProblem(tiles, board)
    solution = ts.get_single_solution(problem)
    ts.plot_solution(solution)


def test_all_solutions_solver():
    board_form = np.array([
                        [
                            [1,0,0,0],
                            [1,0,0,0],
                            [1,0,0,1],
                            [0,0,0,1]
                        ],
                        [
                            [1,0,0,0],
                            [1,0,0,0],
                            [1,0,0,1],
                            [0,0,0,1]
                        ]])
    board = Board("test", board_form)
    tiles = all_tiles()
    problem = TilingProblem(tiles, board)
    solutions = ts.dxz_solve(problem)
    print(len(solutions))
    for solution in solutions:
        ts.plot_solution(solution)

if __name__ == "__main__":
    test_all_solutions_solver()
    #pytest.main()