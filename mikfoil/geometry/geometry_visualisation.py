"""just simple 2d plot of airfoil shape"""
import matplotlib.pyplot as plt
from typing import Optional
from pathlib import Path

from .geometry_types import AirfoilGeometry

def plot_airfoil(geometry: AirfoilGeometry, show: Optional[bool] = None, filepath: Optional[str | Path] = None) -> None:
    """Plots the upper and lower 2D surfaces of the airfoil."""
    if show is None:
        show = filepath is None
        
    plt.figure(figsize=(10, 4))
    
    # Extract coordinates
    upper_x = geometry.upper_surface[:, 0]
    upper_y = geometry.upper_surface[:, 1]
    lower_x = geometry.lower_surface[:, 0]
    lower_y = geometry.lower_surface[:, 1]
    
    # Plot surfaces
    plt.plot(upper_x, upper_y, 'b-', label='Upper Surface', linewidth=2)
    plt.plot(lower_x, lower_y, 'r-', label='Lower Surface', linewidth=2)
    
    # Formatting
    plt.title(f"Airfoil Geometry (Chord: {geometry.chord} m)")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.axis("equal")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    if filepath:
        plt.savefig(filepath, bbox_inches='tight', dpi=300)
    
    if show:
        plt.show()
    plt.close()