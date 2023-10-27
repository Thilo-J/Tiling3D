# Tiling 3D

This package is for tiling cuboids with tiles/polyominos.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Tiling 3D.

```bash
pip install tiling3d
```

## Usage

Create a cuboid with some parts filled in. The create tiles or use tiles from tiles.py.

```python
import numpy as np
from tiling3d.tiling_objects import Cuboid, TilingProblem
from tiling3d.tiles import get_tiles_by_name 
from tiling3d.tiling_solver import get_all_solutions
from tiling3d.visualization import plot_solution

board = Cuboid("Test", np.array([
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

problem = TilingProblem(tiles, board)

solutions = get_all_solutions(problem)

for solution in soltions:
    plot_solution(solution)


```

<p align="center">
  <img src="https://raw.githubusercontent.com/Thilo-J/Tiling3D/900ac7e43571cef5a449b4a604ef13a8b26224c9/tiling_solution.png" 
  alt="tiling_solutions"/>
</p>

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
