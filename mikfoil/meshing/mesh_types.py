from dataclasses import dataclass
import numpy as np

@dataclass
class Mesh:
    points: np.ndarray
    num_wake_pts: int
    num_airfoil_pts: int

    @property
    def num_points(self) -> int:
        return self.points.shape[0]

    @property
    def num_layers(self) -> int:
        return self.points.shape[1]
