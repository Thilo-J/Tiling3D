from struct import pack
import subprocess
import exact_cover as ec
from matplotlib import patches
import numpy as np
import matplotlib.pyplot as plt
from tiling_objects import TilingProblem, TilingSolution, SolutionTile
import algorithm_x as ax
import random
import argparse
import json_reader


def create_exact_cover_matrix(problem: TilingProblem) -> tuple[list[SolutionTile], list[list[bool]]]:
    
    def create_row(tile: np.ndarray, board_shape: tuple[int,int,int], pos: tuple[int, int, int], unique_tiles: int, unique_tile_index: int, tile_name: str, tile_color) -> tuple[SolutionTile, list[bool]]:
        # create the row
        size = board_shape[0] * board_shape[2] * board_shape[1]
        extended_tile = np.zeros(board_shape, dtype=bool)
        extended_tile[pos[0]:tile.shape[0] + pos[0], pos[1]:tile.shape[1] + pos[1] , pos[2]:tile.shape[2] + pos[2]] = tile
        row = extended_tile.flatten().tolist()
        row.extend([False] * unique_tiles)
        row[size + unique_tile_index] = True

        # create the row_name for the row
        tile_is_1 = np.where(extended_tile == 1)
        listOfCoordinates = tuple(zip(tile_is_1[2], tile_is_1[1], tile_is_1[0]))
        solution_tile = SolutionTile(tile_name, tile_color, listOfCoordinates)
        return solution_tile, row

    def rotations24(polycube: np.ndarray): 
        """
            List all 24 rotations of the given 3d array
            https://stackoverflow.com/questions/33190042/how-to-calculate-all-24-rotations-of-3d-array
            Colonel Panic   
        """
        def rotations4(polycube, axes):
            """List the four rotations of the given 3d array in the plane spanned by the given axes."""
            for i in range(4):
                yield np.rot90(polycube, i, axes)

        yield from rotations4(polycube, (1,2))

        yield from rotations4(np.rot90(polycube, 2, axes=(0,2)), (1,2))

        yield from rotations4(np.rot90(polycube, axes=(0,2)), (0,1))
        yield from rotations4(np.rot90(polycube, -1, axes=(0,2)), (0,1))

        yield from rotations4(np.rot90(polycube, axes=(0,1)), (0,2))
        yield from rotations4(np.rot90(polycube, -1, axes=(0,1)), (0,2))

    # the 2 lists that will be returned at the end
    solutiion_tiles = []
    exact_cover_matrix = []

    board_constraint = problem.board.form.flatten().tolist()
    board_constraint.extend([False] * len(problem.tiles))

    # tile rows
    for i, tile in enumerate(problem.tiles):
        for tile_rot in rotations24(tile.form):
            for x in range(problem.board.form.shape[0]):
                if tile_rot.shape[0] + x > problem.board.form.shape[0]: break
                for y in range(problem.board.form.shape[1]):
                    if tile_rot.shape[1] + y > problem.board.form.shape[1]: break
                    for z in range(problem.board.form.shape[2]):
                        if tile_rot.shape[2] + z > problem.board.form.shape[2]: break   
                        solution_tile, row = create_row(tile_rot, problem.board.form.shape, (x,y,z), len(problem.tiles), i, tile.name, tile.color)
                        if (row not in exact_cover_matrix):
                            z = list(zip(row, board_constraint))
                            t = (True, True)
                            if(t not in z):
                                solutiion_tiles.append(solution_tile)
                                exact_cover_matrix.append(row)
        tile_not_used_row = [False] * (problem.board.form.size + len(problem.tiles))
        tile_not_used_row[problem.board.form.size + i] = True
        solutiion_tiles.append(SolutionTile(tile.name, "", []))
        exact_cover_matrix.append(tile_not_used_row)
    exact_cover_matrix = np.array(exact_cover_matrix, dtype="int32")

    # remove columns tha the board covers
    cols_to_be_deleted = []
    for i in range(len(board_constraint)):
        if(board_constraint[i]):
            cols_to_be_deleted.append(i) 
    exact_cover_matrix = np.delete(exact_cover_matrix, cols_to_be_deleted, 1)

    return solutiion_tiles, exact_cover_matrix


def get_single_solution(problem: TilingProblem) -> TilingSolution:
    solution_tiles, exact_cover_matrix = create_exact_cover_matrix(problem) 
    m = np.array(exact_cover_matrix.tolist(), dtype='int32')
    solution_indices = ec.get_exact_cover(m)
    solution = []
    for index in solution_indices:
            solution.append(solution_tiles[index])
    return TilingSolution(solution, problem.board, problem_name=problem.name)


def dxz_solve(problem: TilingProblem) -> list[TilingSolution]:
    solution_tiles, exact_cover_matrix = create_exact_cover_matrix(problem)
    np.savetxt("matrix.csv", exact_cover_matrix, delimiter=",", fmt='%1.0f')

    subprocess.check_call(['my_dxz.exe'])
    


    solutions_indexes = np.genfromtxt("solution.csv", delimiter=',', dtype="int32")
    if solutions_indexes.size == 0: return []
    if solutions_indexes.ndim == 1:
        solutions_indexes = np.expand_dims(solutions_indexes, axis=0)
    solutions = []
    solution = []
    for s in solutions_indexes:
        for i in s:
            solution.append(solution_tiles[i])
        solutions.append(TilingSolution(solution, problem.board, problem.name))
        solution = []
    return solutions


def python_solve(problem: TilingProblem) -> list[TilingSolution]:
    solution_tiles, exact_cover_matrix = create_exact_cover_matrix(problem)
    X = list(range(len(exact_cover_matrix[0])))
    Y = {}
    for i, name in enumerate(solution_tiles):
        l = []
        for j, b, in enumerate(exact_cover_matrix[i]):
            if b:
                l.append(j)
        Y[name] = l
    
    X = {j: set(filter(lambda i: j in Y[i], Y)) for j in X}

    list_solutions = list(ax.solve(X, Y, solution=[]))
    solutions = []
    for solution in list_solutions:
        solutions.append(TilingSolution(solution, problem.board, problem.name))
    return solutions

    
def plot_solution(solution: TilingSolution) -> None:
    if len(solution.solution_tiles) == 0:
        return
    voxelarray = np.ones(solution.board.form.shape)
    inv = np.invert(solution.board.form)
    voxelarray = np.logical_and(inv , voxelarray)

    colors = np.empty(voxelarray.shape, dtype=object)
    colors[:] = "#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])

    handles = []
    for solution_tile in solution.solution_tiles:
        if len(solution_tile.coordinates) > 0:
            patch = patches.Patch(color=solution_tile.color, label=solution_tile.name)
            handles.append(patch)
            for j in solution_tile.coordinates:
                colors[j[2], j[1], j[0]] = solution_tile.color
  
    
    ax = plt.figure().add_subplot(projection='3d')
    ax.set_title(solution.problem_name)
    #ax.set_aspect("auto")
    ax.set_xlabel('z')
    ax.set_ylabel('y')
    ax.set_zlabel('x')
    ax.w_xaxis.set_pane_color((0, 0, 0, 0.5))
    ax.legend(handles=handles, loc='upper right', bbox_to_anchor=(1.3, 1.05))
    ax.voxels(voxelarray, facecolors=colors, edgecolor='k')
    ax.view_init(elev=5., azim=170, roll=-90)
    ax.invert_yaxis()
    ax.invert_xaxis()


    axis_labels = list(np.arange(0.5,max(solution.board.form.shape), 1))# + ['']
    axis_positions = list(np.arange(0, max(solution.board.form.shape), 1))

    ax.set_xticklabels('')
    ax.set_xticks(axis_positions)
    ax.set_xticklabels(axis_labels, minor=True)

    ax.set_yticklabels('')
    ax.set_yticks(axis_positions)
    ax.set_yticklabels(axis_labels, minor=True)

    
    ax.set_zticklabels('')
    ax.set_zticks(axis_positions)
    ax.set_zticklabels(axis_labels, minor=True)

    plt.show()


def solve_given_problem(file_name: str, all: bool=False):
    problem = json_reader.get_problem_by_file_name(file_name)

    if all:
        solutions = dxz_solve(problem)
        random.shuffle(solutions)
        print("Solutions found:", len(solutions))
        for s in solutions:
            plot_solution(s)
    else:
        solution = get_single_solution(problem)
        plot_solution(solution)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', help="file name", type= str)
    parser.add_argument('--all', '-a', help="show all solutions", type= str, default= "False")
    args = parser.parse_args()
    solve_given_problem(args.file, args.all)



