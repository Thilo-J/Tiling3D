import exact_cover as ec
import numpy as np
import dxz
from tiling_objects import TilingProblem, TilingSolution, Tile


def create_exact_cover_matrix(problem: TilingProblem) -> tuple[list[Tile], list[list[bool]]]:
    def tile_coordinates_to_array(tile: Tile):
        max_x = max([i[0] for i in tile.coordinates])
        max_y = max([i[1] for i in tile.coordinates])
        max_z = max([i[2] for i in tile.coordinates])

        array = np.zeros((max_x+1, max_y+1, max_z+1), dtype=bool)
        for coordinate in tile.coordinates:
            array[coordinate[0], coordinate[1], coordinate[2]] = True
        return array

    def create_row(tile: np.ndarray, board_shape: tuple[int,int,int], pos: tuple[int, int, int], unique_tiles: int, unique_tile_index: int, tile_name: str, tile_color) -> tuple[Tile, list[bool]]:
        # Create the row
        size = board_shape[0] * board_shape[2] * board_shape[1]
        extended_tile = np.zeros(board_shape, dtype=bool)
        extended_tile[pos[0]:tile.shape[0] + pos[0], pos[1]:tile.shape[1] + pos[1] , pos[2]:tile.shape[2] + pos[2]] = tile
        row = extended_tile.flatten().tolist()
        row.extend([False] * unique_tiles)
        row[size + unique_tile_index] = True

        # Create the row_name for the row
        tile_is_1 = np.where(extended_tile == 1)
        listOfCoordinates = tuple(zip(tile_is_1[2], tile_is_1[1], tile_is_1[0]))
        solution_tile = Tile(tile_name, tile_color, listOfCoordinates)
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

    # The 2 lists that will be returned at the end
    solutiion_tiles = []
    exact_cover_matrix = []

    board_constraint = problem.shape.form.flatten().tolist()
    board_constraint.extend([False] * len(problem.tiles))

    # Create the matrix

    # Loop over each tile
    for i, tile in enumerate(problem.tiles):
        # Rotate tile in all 24 possible rotations
        tile_array = tile_coordinates_to_array(tile)
        for tile_rot in rotations24(tile_array):
            for x in range(problem.shape.form.shape[0]):
                if tile_rot.shape[0] + x > problem.shape.form.shape[0]: break
                for y in range(problem.shape.form.shape[1]):
                    if tile_rot.shape[1] + y > problem.shape.form.shape[1]: break
                    for z in range(problem.shape.form.shape[2]):
                        if tile_rot.shape[2] + z > problem.shape.form.shape[2]: break   
                        solution_tile, row = create_row(tile_rot, problem.shape.form.shape, (x,y,z), len(problem.tiles), i, tile.name, tile.color)
                        if (row not in exact_cover_matrix):
                            z = list(zip(row, board_constraint))
                            t = (True, True)
                            if(t not in z):
                                solutiion_tiles.append(solution_tile)
                                exact_cover_matrix.append(row)
        tile_not_used_row = [False] * (problem.shape.form.size + len(problem.tiles))
        tile_not_used_row[problem.shape.form.size + i] = True
        solutiion_tiles.append(Tile(tile.name, "", []))
        exact_cover_matrix.append(tile_not_used_row)
    exact_cover_matrix = np.array(exact_cover_matrix, dtype="int32")

    # Remove columns tha the board covers
    cols_to_be_deleted = []
    for i in range(len(board_constraint)):
        if(board_constraint[i]):
            cols_to_be_deleted.append(i) 
    exact_cover_matrix = np.delete(exact_cover_matrix, cols_to_be_deleted, 1)

    return solutiion_tiles, exact_cover_matrix


def get_single_solution(problem: TilingProblem) -> TilingSolution:
    """Gets a single soltion to a given tiling problem.

    Args:
        problem (TilingProblem): A tiling problem.

    Returns:
        TilingSolution: A solution to the tiling problem
    """
    solution_tiles, exact_cover_matrix = create_exact_cover_matrix(problem) 
    m = np.array(exact_cover_matrix.tolist(), dtype='int32')
    solution_indices = ec.get_exact_cover(m)
    solution = []
    for index in solution_indices:
        if len(solution_tiles[index].coordinates) > 0:
                solution.append(solution_tiles[index])
    return TilingSolution(solution, problem.shape, name=problem.name)


def dxz_solve(problem: TilingProblem, max_solutions = 0) -> list[TilingSolution]:
    """Uses dxz to calculate all solutions to a given TilingProblem

    Args:
        problem (TilingProblem): A tiling problem.
        max_solutions (int, optional): Max number of solutions to be returned. 0 for all solutions to be returned. Defaults is 0.

    Returns:
        list[TilingSolution]: All the solutions for the given tiling problem.
    """
    solution_tiles, exact_cover_matrix = create_exact_cover_matrix(problem)
    
    number_of_rows = exact_cover_matrix.shape[0]
    number_of_collumns = exact_cover_matrix.shape[1]
    flat = exact_cover_matrix.flatten()

    all_solutions_indices = dxz.dxz_solve(number_of_rows, number_of_collumns, flat, max_solutions)

    solutions = []

    for indices in all_solutions_indices:
        solution = []
        for index in indices:
            if len(solution_tiles[index].coordinates) > 0:
                solution.append(solution_tiles[index])
        solutions.append(TilingSolution(solution, problem.shape, name=problem.name))

    return solutions


def dxz_count(problem: TilingProblem) -> int:
    """Returns the number of possible solutions.

    Args:
        problem (TilingProblem): A tiling problem.

    Returns:
        int: Number of solutions for the given tiling problem.
    """
    _, exact_cover_matrix = create_exact_cover_matrix(problem)
    
    number_of_rows = exact_cover_matrix.shape[0]
    number_of_collumns = exact_cover_matrix.shape[1]
    flat = exact_cover_matrix.flatten()

    return dxz.dxz_count(number_of_rows, number_of_collumns, flat)




