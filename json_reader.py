import json
from tiling_objects import TilingProblem
from ubongo_tiles import get_tiles_by_name
from ubongo_boards import get_board_by_name

def get_official_ubongo_problem_by_name(name: str) -> TilingProblem:
    try:
        file = open("ubongo_problems/official_ubongo_problems_elephants.json")
        data = json.load(file)
        for problem in data:
            if problem["name"] == name:
                tiles = get_tiles_by_name(problem["tiles"])
                board = get_board_by_name(problem["board"])
                return TilingProblem(tiles,  board, name)
    except Exception as error:
        print('Caught this error: ' + repr(error))

    