from matplotlib import patches, pyplot as plt
import numpy as np
from tiling3d.tiling_objects import TilingSolution


def plot_solution(solution: TilingSolution) -> None:
    """Plots the tiling solution

    Args:
        solution (TilingSolution): A tiling solution.
    """
    if len(solution.solution_tiles) == 0:
        return
    voxelarray = np.ones(solution.board.form.shape)
    inv = np.invert(solution.board.form.astype(bool))
    voxelarray = np.logical_and(inv , voxelarray)

    colors = np.empty(voxelarray.shape, dtype=object)

    handles = []
    for solution_tile in solution.solution_tiles:
        if len(solution_tile.coordinates) > 0:
            patch = patches.Patch(color=solution_tile.color, label=solution_tile.name)
            handles.append(patch)
            for j in solution_tile.coordinates:
                colors[j[2], j[1], j[0]] = solution_tile.color + "f5"
  
    
    ax = plt.figure().add_subplot(projection='3d')
    ax.set_title(solution.name)

    ax.set_xlim([0, max(solution.board.form.shape) + 1])
    
    ax.legend(handles=handles, loc='upper right', bbox_to_anchor=(1.3, 1.05))
    ax.voxels(voxelarray, facecolors=colors, edgecolor='k')
    ax.view_init(elev=5., azim=30, roll=-90)
    ax.invert_yaxis()
    ax.invert_xaxis()

    ax.set_aspect('equal')

    ax.w_xaxis.set_pane_color((0, 0, 0, 0.5))
    ax.w_zaxis.set_pane_color((0, 0, 0, 0.0))
    ax.w_yaxis.set_pane_color((0, 0, 0, 0.0))

    ax.w_xaxis.line.set_lw(0.)
    ax.set_xticks([])
    ax.w_zaxis.line.set_lw(0.)
    ax.set_zticks([])
    ax.w_yaxis.line.set_lw(0.)
    ax.set_yticks([])

    plt.show()

