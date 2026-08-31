import numpy as np

def calculate_surface_normals(points: np.ndarray) -> np.ndarray:
    """Computes outward-facing surface normals using central differences."""
    dx = np.gradient(points[:, 0])
    dy = np.gradient(points[:, 1])
    normals = np.column_stack((dy, -dx))
    magnitudes = np.linalg.norm(normals, axis=1, keepdims=True)
    magnitudes[magnitudes == 0] = 1e-10
    return normals / magnitudes

def smooth_normals(normals: np.ndarray, iterations: int = 15) -> np.ndarray:
    """Applies Laplacian smoothing to normal vectors to remove high-frequency noise."""
    smoothed = np.copy(normals)
    for _ in range(iterations):
        smoothed[1:-1] = 0.25 * smoothed[:-2] + 0.5 * smoothed[1:-1] + 0.25 * smoothed[2:]
        magnitudes = np.linalg.norm(smoothed, axis=1, keepdims=True)
        magnitudes[magnitudes == 0] = 1e-10
        smoothed = smoothed / magnitudes
    return smoothed

def compute_blended_normals(surface_normals: np.ndarray, x_coords: np.ndarray, x_le: float, chord: float) -> np.ndarray:
    """Blends surface normals with vertical vectors near the trailing edge to prevent grid crossing."""
    vertical_normals = np.zeros_like(surface_normals)
    vertical_normals[:, 1] = np.sign(surface_normals[:, 1])
    vertical_normals[vertical_normals[:, 1] == 0, 1] = 1.0
    
    weights = np.clip((x_coords - x_le) / chord, 0.0, 1.0) ** 2.0
    weights_expanded = weights[:, None]
    
    blended = surface_normals * (1.0 - weights_expanded) + vertical_normals * weights_expanded
    magnitudes = np.linalg.norm(blended, axis=1, keepdims=True)
    magnitudes[magnitudes == 0] = 1e-10
    return blended / magnitudes

def get_airfoil_normals(airfoil_points: np.ndarray, chord: float) -> np.ndarray:

    x_le = np.min(airfoil_points[:, 0])
    raw_normals = calculate_surface_normals(airfoil_points)
    smoothed_normals = smooth_normals(raw_normals, iterations=15)
    return compute_blended_normals(smoothed_normals, airfoil_points[:, 0], x_le, chord)
