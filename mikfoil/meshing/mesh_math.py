import numpy as np

def solve_growth_rate(first_cell: float, total_length: float, num_intervals: int) -> float:
    """Solves for the geometric growth rate (r) using the geometric series sum: L = h_1 * (r^N - 1) / (r - 1)"""
    low = 1.000001
    high = 2.0
    
    for _ in range(50):
        mid = (low + high) / 2.0
        current_length = first_cell * (mid**num_intervals - 1.0) / (mid - 1.0)
        
        if current_length > total_length:
            high = mid
        else:
            low = mid
            
    return (low + high) / 2.0

def smooth_geometric_spacing(h_start: float, h_end: float, total_length: float) -> np.ndarray:
    """Calculates normalized spline parameter values for a continuous geometric stretching."""
    if h_start >= h_end or total_length <= h_end:
        num_intervals = max(2, int(total_length / h_start))
        return np.linspace(0.0, 1.0, num_intervals + 1)
    
    ideal_growth_rate = (total_length - h_start) / (total_length - h_end)
    exact_intervals = 1.0 + np.log(h_end / h_start) / np.log(ideal_growth_rate)
    num_intervals = max(2, int(np.round(exact_intervals)))
    
    actual_growth_rate = solve_growth_rate(h_start, total_length, num_intervals)
    cell_sizes = h_start * (actual_growth_rate ** np.arange(num_intervals))
    
    points = np.zeros(num_intervals + 1)
    points[1:] = np.cumsum(cell_sizes)
    
    return points / total_length

def first_layer_from_yplus(reynolds: float, y_plus: float, chord: float) -> float:
    """Estimates wall spacing (y) using the Schlichting skin friction correlation: C_f = (2*log10(Re) - 0.65)^-2.3"""
    import math
    skin_friction = math.pow(2.0 * math.log10(reynolds) - 0.65, -2.3)
    friction_velocity = math.sqrt(skin_friction / 2.0)
    return y_plus / (reynolds * friction_velocity) * chord
