from struct import pack
import subprocess
import exact_cover as ec
from matplotlib import patches
import numpy as np
import matplotlib.pyplot as plt
import time
from tiling_objects import Tile, Board, TilingProblem, TilingSolution, SolutionTile
import json_reader as jr
import algorithm_x as ax
import random
import csv
import tiling_solver as us
import os
import pytask


def group_solutions_by_tiles_used(solutions: list[TilingSolution]) -> dict[frozenset[str], list[TilingSolution]]:
    result: dict[frozenset[str], list[TilingSolution]] = dict()
    for solution in solutions:
        tiles_used = frozenset([tile.name for tile in solution.solution_tiles if len(tile.coordinates) > 0])
        if tiles_used in result:
            result[tiles_used].append(solution)
        else:
            result[tiles_used] = [solution]
    return result


def analyse_official_problems() -> None:
    problems = jr.get_official_ubongo_problems()

    with open("official_boards_analysis.csv", 'w') as file:
        header = ['Animal','Dice Roll',"Board","Solutions","Board","Solutions","Board","Solutions","Board","Solutions",]
        writer=csv.writer(file, delimiter=',',lineterminator='\n',)
        writer.writerow(header)
        print ("{:<15} {:<15} {:<5} {:<10} {:<5} {:<10} {:<5} {:<10} {:<5} {:<10}".format(*header))

        # split problems into game rounds
        rounds = {}
        for problem in problems:
            animal_dice_roll = problem.name.split('-')[0] + problem.name.split('-')[3]
            if animal_dice_roll in rounds:
                rounds[animal_dice_roll].append(problem)
            else:
                rounds[animal_dice_roll] = [problem]

        for round in rounds.values():
            row = []
            row.append(round[0].name.split('-')[0])
            row.append(round[0].name.split('-')[3])
            for problem in round:
                solutions = us.python_solve(problem)
                row.append(problem.name.split('-')[1])
                if len(solutions) == 0:
                    row.append("NONE")
                else:
                    row.append(len(solutions))

            writer.writerow(row)
            print ("{:<15} {:<15} {:<5} {:<10} {:<5} {:<10} {:<5} {:<10} {:<5} {:<10}".format(*row))


def analyse_height_x_boards(x: int) -> None:
    boards = [board for board in jr.get_all_boards() if board.height == x]
    tiles = jr.get_all_tiles()
    with open("height_" + str(x) + "_analysis.csv", 'w') as file:
        writer=csv.writer(file, delimiter=',',lineterminator='\n',)
        for board in boards:
            solutions = us.dxz_solve(TilingProblem(tiles, board))
            tiles_grouped = group_solutions_by_tiles_used(solutions)

            row1 = []
            row2 = []
            for key, value in tiles_grouped.items():
                tiles_used = ""
                for i in key: tiles_used += (i + ' ')
                row1.append(tiles_used)
                row2.append(str(len(value)))
            
            combined_rows = zip(row1, row2)
            sorted_rows = sorted(combined_rows, key=lambda x: int(x[1]), reverse=True)
            row1 = [board.name]
            row2 = ["solutions"]
            for i in sorted_rows:
                row1.append(i[0])
                row2.append(i[1])

            writer.writerow(row1)
            writer.writerow(row2)
            writer.writerow([])


def test_big_problem() -> None:
    tiles = jr.get_tiles_by_list_of_names(["t8"])
    #tiles = jr.get_all_tiles()
    #board = jr.get_board_by_file("./boards/custom_boards/cb1.json")
    board = jr.get_board_by_name("B14-2")
    solutions = us.dxz_solve(TilingProblem(tiles, board))
    print(len(solutions))


    board = jr.get_board_by_name("A1-1")
    tiles = jr.get_tiles_by_list_of_names(["t2"])
    solutions = us.dxz_solve(TilingProblem(tiles, board))
    print(len(solutions))


def create_solution_images(solution: TilingSolution, file_name: str) -> None:
    if len(solution.solution_tiles) == 0:
        return
    voxelarray = np.ones(solution.board.form.shape)
    inv = np.invert(solution.board.form)
    voxelarray = np.logical_and(inv , voxelarray)

    colors = np.empty(voxelarray.shape, dtype=object)
    colors[:] = "#"+''.join([random.choice('ABCDEF0123456789') for i in range(6)])

    for solution_tile in solution.solution_tiles:
        if len(solution_tile.coordinates) > 0:
            for j in solution_tile.coordinates:
                colors[j[2], j[1], j[0]] = solution_tile.color

    # Create images
    for i in range(4): 
        ax = plt.figure().add_subplot(projection='3d')

        # Remove tick labels
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])
        
        ax.w_xaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_yaxis.line.set_color((1.0, 1.0, 1.0, 0.0))
        ax.w_zaxis.line.set_color((1.0, 1.0, 1.0, 0.0))


        ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        ax.w_xaxis.set_pane_color((0.8, 0.8, 0.8, 0.9))

        ax.set_title(solution.problem_name)
        ax.voxels(voxelarray, facecolors=colors, edgecolor='k')
        ax.view_init(elev=60. - 40*i, azim=50, roll=-90)
    
        # No ticks
        tick_pos = list(np.arange(0, max(solution.board.form.shape), 1))
        ax.set_xticks([]) 
        ax.set_yticks([]) 
        ax.set_zticks([])

        plt.gca().set_aspect('equal')
        name = "images/" + file_name + '-' + str(i) + ".png"
        solution.images.append(name)
        plt.savefig(name, bbox_inches='tight')


def create_fair_height_3_rounds():
    ranges = [(1, 1),
        (2, 2),
        (3, 4),
        (10, 19),
        (20, 29),
        (30, 39),
        (40, 49),
        (50, 59),
        (60, 69),
        (70, 79)]

    for i in ranges:
        create_fair_height_3_round(i)


def create_fair_height_3_round(solution_range: tuple[int, int]):  
    def select_tile_set_foreach_board(round_not_filtered: dict) -> dict:
        def enough_tiles_avalaible(tiles_available, tiles_used) -> bool:
            for key, value in tiles_available.items():
                if tiles_used[key] > value:
                    return False
            return True

        tiles_used = {
            "t1": 0,
            "t2": 0,
            "t3": 0,
            "t4": 0,
            "t5": 0,
            "t6": 0,
            "t7": 0,
            "t8": 0,
            "t9": 0,
            "t10": 0,
            "t11": 0,
            "t12": 0,
            "t13": 0,
            "t14": 0,
            "t15": 0,
            "t16": 0,
        }
        
        s = list(round_not_filtered.values())
        m = list(round_not_filtered.keys())

        for l1 in random.sample(s[0], len(s[0])):
            for g in l1.split(' ')[:-1]:
                tiles_used[g] += 1
            for l2 in random.sample(s[1], len(s[1])):
                for g in l2.split(' ')[:-1]:
                    tiles_used[g] += 1
                for l3 in random.sample(s[2], len(s[2])):
                    for g in l3.split(' ')[:-1]:
                        tiles_used[g] += 1
                    for l4 in random.sample(s[3], len(s[3])):
                        for g in l4.split(' ')[:-1]:
                            tiles_used[g] += 1
                        
                        if(enough_tiles_avalaible(tiles_available, tiles_used)):
                            result =  {
                                m[0]: l1,
                                m[1]: l2,
                                m[2]: l3,
                                m[3]: l4
                            }
                            return result
                        
                        for g in l4.split(' ')[:-1]:
                            tiles_used[g] -= 1
                    for g in l3.split(' ')[:-1]:
                        tiles_used[g] -= 1
                for g in l2.split(' ')[:-1]:
                    tiles_used[g] -= 1
            for g in l1.split(' ')[:-1]:
                tiles_used[g] -= 1

        return dict()

    filtered_rounds_result = {}
    tiles_available = {
        "t1": 2,
        "t2": 2,
        "t3": 3,
        "t4": 2,
        "t5": 2,
        "t6": 2,
        "t7": 3,
        "t8": 4,
        "t9": 3,
        "t10": 2,
        "t11": 2,
        "t12": 2,
        "t13": 2,
        "t14": 2,
        "t15": 2,
        "t16": 4,
    }

    
    with open('height_3_analysis.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile, delimiter=',',lineterminator='\n'))
        for i in range(0, len(data), 48):
            for j in range(0, 11, 3):
                round_name = "round-"+ str(int(i / 48)) + "-"
                if int(j/3) == 0:
                    round_name += "A-Up"
                elif int(j/3) == 1:
                    round_name += "A-Down"
                elif int(j/3) == 2:
                    round_name += "B-Up"
                elif int(j/3) == 3:
                    round_name += "B-Down"
                    
                round = dict()
                
                for k in range(0, 47, 12):
                    mm = data[i+j+k][0]
                    round[mm] = possible_tile_sets = set()
                    for x in range(1 , len(data[i+j+k][1:])): 
                        a = int(data[i+j+k+1][x])
                        b = data[i+j+k][x]
                        if solution_range[0] <= a and a <= solution_range[1] and b.count('t') == 5:
                            possible_tile_sets.add(b) # include tile set if the range matches and uses 5 tiles
                        else:
                            pass

                result = select_tile_set_foreach_board(round)
                filtered_rounds_result[round_name] = result

    with open("fair_rounds_height_3_range" + str(solution_range[0]) + "-" + str(solution_range[1]) + ".csv", 'w') as file:
        writer=csv.writer(file, delimiter=',',lineterminator='\n')

        for key, value in filtered_rounds_result.items(): 
            row1 = [key]
            row2 = [""]
            for k, v in value.items():
                row1.append(k)
                row2.append(v)
            writer.writerow(row1)
            writer.writerow(row2)
            writer.writerow([])


def create_2_player_rounds():
    tiles = jr.get_all_tiles()
    rounds = {}


    for i in range(1, 36, 4):
        board1 = jr.get_board_by_name("Height3-B" + str(i) + "-1")
        solutions1 = us.dxz_solve(TilingProblem(tiles,board1))
        grouped1 = group_solutions_by_tiles_used(solutions1)

        board2 = jr.get_board_by_name("Height3-B" + str(i + 1) + "-1")
        solutions2 = us.dxz_solve(TilingProblem(tiles,board2))
        grouped2 = group_solutions_by_tiles_used(solutions2)

        fair_pair = {}
        for key1, value1 in grouped1.items():
            for key2, value2 in grouped2.items():
                if len(value1) == len(value2) and len(key1) == len(key2):
                    fair_pair[len(value1)] = (key1, key2)
        rounds[round_to_animal_mapper(int(i / 4))] = fair_pair

    print(len(rounds))

    with open("fair_2_player_game_height_3.csv", 'w') as file:
        writer = csv.writer(file, delimiter=',',lineterminator='\n',)

        for key, value in rounds.items():
            row1 = [key]
            row2 = ["Player 1"]
            row3 = ["Player 2"]
            for key2, value2 in value.items():
                row1.append(key2)
                tiles_player_1 = ""
                for i in value2[0]:
                    tiles_player_1 += i + " "
                row2.append(tiles_player_1)
                tiles_player_2 = ""
                for i in value2[1]:
                    tiles_player_2 += i + " "
                row3.append(tiles_player_2)
            writer.writerow(row1)
            writer.writerow(row2)
            writer.writerow(row3)
            writer.writerow([])


def visualize_38_sol_problem() -> None:
    board = jr.get_board_by_name("B1-1")
    tiles = jr.get_tiles_by_list_of_names(["t10", "t7", "t16", "t8"])
    solutions = us.dxz_solve(TilingProblem(tiles, board))
    for i in range(len(solutions)):
        create_solution_images(solutions[i], board.name + "-" + str(i))


def round_to_animal_mapper(i: int):
    if i == 0:
        return "Elephant"
    elif i == 1:
        return "Antelope"
    elif i == 2:
        return "Snake"
    elif i == 3:
        return "Bull"
    elif i == 4:
        return "Ostrich"
    elif i == 5:
        return "Rhinoceros"
    elif i == 6:
        return "Giraffe"
    elif i == 7:
        return "Zebra"
    elif i == 8:
        return "Hyenas"
    else:
        return ""


def small_problem_for_presentation():
    board = jr.get_board_by_file("very-small.json")
    tiles = jr.get_tiles_by_list_of_names(["t8", "t16"])
    solutions = us.dxz_solve(TilingProblem(tiles, board))
    print(len(solutions))


def create_fair_height_2_round():  
    def select_tile_set_foreach_board(round_not_filtered: dict) -> dict:
        def enough_tiles_avalaible(tiles_available, tiles_used) -> bool:
            for key, value in tiles_available.items():
                if tiles_used[key] > value:
                    return False
            return True

        tiles_used = {
            "t1": 0,
            "t2": 0,
            "t3": 0,
            "t4": 0,
            "t5": 0,
            "t6": 0,
            "t7": 0,
            "t8": 0,
            "t9": 0,
            "t10": 0,
            "t11": 0,
            "t12": 0,
            "t13": 0,
            "t14": 0,
            "t15": 0,
            "t16": 0,
        }
        
        s = list(round_not_filtered.values())
        m = list(round_not_filtered.keys())

        for l1 in random.sample(s[0], len(s[0])):
            for g in l1.split(' ')[:-1]:
                tiles_used[g] += 1
            for l2 in random.sample(s[1], len(s[1])):
                for g in l2.split(' ')[:-1]:
                    tiles_used[g] += 1
                for l3 in random.sample(s[2], len(s[2])):
                    for g in l3.split(' ')[:-1]:
                        tiles_used[g] += 1
                    for l4 in random.sample(s[3], len(s[3])):
                        for g in l4.split(' ')[:-1]:
                            tiles_used[g] += 1
                        
                        if(enough_tiles_avalaible(tiles_available, tiles_used)):
                            result =  {
                                m[0]: l1,
                                m[1]: l2,
                                m[2]: l3,
                                m[3]: l4
                            }
                            return result
                        
                        for g in l4.split(' ')[:-1]:
                            tiles_used[g] -= 1
                    for g in l3.split(' ')[:-1]:
                        tiles_used[g] -= 1
                for g in l2.split(' ')[:-1]:
                    tiles_used[g] -= 1
            for g in l1.split(' ')[:-1]:
                tiles_used[g] -= 1

        return dict()

    filtered_rounds_result = {}
    tiles_available = {
        "t1": 2,
        "t2": 2,
        "t3": 3,
        "t4": 2,
        "t5": 2,
        "t6": 2,
        "t7": 3,
        "t8": 4,
        "t9": 3,
        "t10": 2,
        "t11": 2,
        "t12": 2,
        "t13": 2,
        "t14": 2,
        "t15": 2,
        "t16": 4,
    }

    
    with open('height_2_analysis.csv', newline='') as csvfile:
        data = list(csv.reader(csvfile, delimiter=',',lineterminator='\n'))
        for i in range(0, len(data), 48):
            for j in range(0, 11, 3):
                round_name = "Round-"+ round_to_animal_mapper(int(i / 48)) + "-"
                if int(j/3) == 0:
                    round_name += "A-Up"
                elif int(j/3) == 1:
                    round_name += "A-Down"
                elif int(j/3) == 2:
                    round_name += "B-Up"
                elif int(j/3) == 3:
                    round_name += "B-Down"
                    
                round = dict()
                
                for k in range(0, 47, 12):
                    mm = data[i+j+k][0]
                    round[mm] = possible_tile_sets = set()
                    for x in range(1 , len(data[i+j+k][1:])): 
                        a = int(data[i+j+k+1][x])
                        b = data[i+j+k][x]
                        if 2 == a and b.count('t') == 4:
                            possible_tile_sets.add(b)

                result = select_tile_set_foreach_board(round)
                filtered_rounds_result[round_name] = result

    with open("fair_rounds_height_2.csv", 'w') as file:
        writer=csv.writer(file, delimiter=',',lineterminator='\n')

        for key, value in filtered_rounds_result.items():
            if(key.split("-")[2] == "B" ):
                writer.writerow([key.split("-")[1] + key.split("-")[3]])
                row1 = []
                row2 = []
                for k, v in value.items():
                    row1.append(k)
                    row2.append(v)
                writer.writerow(row1)
                writer.writerow(row2)
                writer.writerow([])
                


def main():
    #create_2_player_rounds()
    create_fair_height_2_round()


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("seconds used: " + str(end - start))
