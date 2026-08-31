import numpy as np
from pathlib import Path

from typing import Optional, Union
from mikfoil.case import MeshConfig

from .geometry_types import AirfoilGeometry
from .surface_math import build_surface_coordinates, resample_curve_by_arc_length, compute_thickness_distribution
from .naca4 import compute_naca4_camber
from .naca5 import get_naca5_constants, compute_naca5_camber
from .selig_format import read_airfoil_file





def _create_naca4(digits: str, chord_length: float, x_coordinates: np.ndarray, config: 'MeshConfig') -> AirfoilGeometry:
    max_camber = int(digits[0]) * 0.01
    camber_pos = int(digits[1]) * 0.1
    y_camber, camber_slope = compute_naca4_camber(max_camber, camber_pos, chord_length, x_coordinates)
    return _finalize_airfoil(digits, chord_length, x_coordinates, y_camber, camber_slope, config)

def _create_naca5(digits: str, chord_length: float, x_coordinates: np.ndarray, config: 'MeshConfig') -> AirfoilGeometry:
    lift_coefficient_design = int(digits[0])
    camber_pos_identifier = int(digits[1])
    camber_type_identifier = int(digits[2])

    r_const, k1_const, k2_k1_ratio = get_naca5_constants(camber_pos_identifier, camber_type_identifier, lift_coefficient_design)
    y_camber, camber_slope = compute_naca5_camber(r_const, k1_const, k2_k1_ratio, camber_type_identifier, chord_length, x_coordinates)
    return _finalize_airfoil(digits, chord_length, x_coordinates, y_camber, camber_slope, config)

def _finalize_airfoil(digits: str, chord_length: float, x_coordinates: np.ndarray, y_camber: np.ndarray, camber_slope: np.ndarray, config: 'MeshConfig') -> AirfoilGeometry:
    thickness_distribution = compute_thickness_distribution(
        thickness=int(digits[-2:]) * 0.01,
        chord=chord_length,
        x_coordinates=x_coordinates
    )
    theta = np.arctan(camber_slope)
    upper_surface, lower_surface = build_surface_coordinates(x_coordinates, y_camber, thickness_distribution, theta)

    upper_surface = resample_curve_by_arc_length(upper_surface, config, config.fineness)
    lower_surface = resample_curve_by_arc_length(lower_surface, config, config.fineness)

    return AirfoilGeometry(
        upper_surface=upper_surface,
        lower_surface=lower_surface,
        chord=chord_length
    )

def create_naca_airfoil(name: str, config: Optional[MeshConfig] = None) -> AirfoilGeometry:
    if config is None:
        config = MeshConfig()
    identifier = name
    digits = identifier.split("_")[1] if "_" in identifier else identifier.replace("NACA", "").replace("naca", "")
    chord_length = config.chord

    theta_fine = np.linspace(0.0, np.pi, 2000)
    x_coordinates = chord_length * 0.5 * (1.0 - np.cos(theta_fine))

    if len(digits) == 4:
        return _create_naca4(digits, chord_length, x_coordinates, config)
    elif len(digits) == 5:
        return _create_naca5(digits, chord_length, x_coordinates, config)
    else:
        raise ValueError(f"Unsupported NACA format: {identifier}")

def create_airfoil(airfoil: Union[str, Path], config: Optional[MeshConfig] = None) -> AirfoilGeometry:
    if isinstance(airfoil, Path):
        return create_airfoil_from_file(airfoil, config)
    return create_naca_airfoil(str(airfoil), config)

def create_airfoil_from_file(filepath: Path, config: Optional[MeshConfig] = None) -> AirfoilGeometry:
    
    if config is None:
        config = MeshConfig()
    
    _, upper_surface, lower_surface = read_airfoil_file(filepath, config.chord)
    
    upper_surface = resample_curve_by_arc_length(upper_surface, config, config.fineness)
    lower_surface = resample_curve_by_arc_length(lower_surface, config, config.fineness)
    
    return AirfoilGeometry(
        upper_surface=upper_surface,
        lower_surface=lower_surface,
        chord=config.chord
    )

