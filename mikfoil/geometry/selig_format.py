import numpy as np
from pathlib import Path
from typing import Tuple
from .geometry_types import AirfoilGeometry

def read_airfoil_file(filepath: Path, chord: float) -> Tuple[str, np.ndarray, np.ndarray]:
    """Reads airfoil coordinates from a Selig or Lednicer .dat file."""
    with open(filepath, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    true_name = "_".join(lines[0].split()[:2]).replace(".", "")

    first_val = float(lines[1].split()[0])

    if first_val > 1.5:
        return _parse_lednicer(lines, true_name, chord)
    else:
        return _parse_selig(lines, true_name, chord)

def _parse_selig(lines: list, true_name: str, chord: float) -> Tuple[str, np.ndarray, np.ndarray]:
    points = []
    for line in lines[1:]:
        parts = line.split()
        points.append([float(parts[0]), float(parts[1])])

    points = np.array(points)
    le_idx = int(np.argmin(points[:, 0]))

    upper = points[: le_idx + 1].copy()[::-1]
    lower = points[le_idx:].copy()

    return true_name, upper * chord, lower * chord

def _parse_lednicer(lines: list, true_name: str, chord: float) -> Tuple[str, np.ndarray, np.ndarray]:
    counts = lines[1].split()
    n_upper = int(float(counts[0]))
    n_lower = int(float(counts[1]))

    points = []
    for line in lines[2:]:
        parts = line.split()
        points.append([float(parts[0]), float(parts[1])])

    points = np.array(points)
    upper = points[:n_upper]
    lower = points[n_upper : n_upper + n_lower]

    return true_name, upper * chord, lower * chord

def export_selig_dat(geometry: AirfoilGeometry, name: str, filepath: Path) -> None:
    """Exports normalized airfoil geometry to a Selig .dat file (TE to LE to TE order)."""
    upper_norm = geometry.upper_surface / geometry.chord
    lower_norm = geometry.lower_surface / geometry.chord
    
    upper_selig = upper_norm[::-1]
    lower_selig = lower_norm[1:]
    
    combined_points = np.vstack((upper_selig, lower_selig))
    
    with open(filepath, "w") as f:
        f.write(f"{name}\n")
        np.savetxt(f, combined_points, fmt="%.6f %.6f")
