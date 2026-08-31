import numpy as np

def build_farfield_curve(x_te: float, x_center: float, radius: float, num_upper: int, num_lower: int) -> np.ndarray:
    """Constructs the C-shape outer domain boundary (a semi-circle flanked by horizontal wake lines)."""
    total_points = num_upper + num_lower - 1
    straight_length = x_te - x_center
    arc_length = np.pi * radius
    total_length = straight_length + arc_length + straight_length
    
    s = np.linspace(0, total_length, total_points)
    ff = np.zeros((total_points, 2))
    
    mask1 = s <= straight_length
    mask2 = (s > straight_length) & (s <= straight_length + arc_length)
    mask3 = s > straight_length + arc_length
    
    ff[mask1, 0] = x_te - s[mask1]
    ff[mask1, 1] = radius
    
    arc_fraction = (s[mask2] - straight_length) / arc_length
    angle = np.pi / 2 + arc_fraction * np.pi
    ff[mask2, 0] = x_center + radius * np.cos(angle)
    ff[mask2, 1] = radius * np.sin(angle)
    
    overshoot = s[mask3] - straight_length - arc_length
    ff[mask3, 0] = x_center + overshoot
    ff[mask3, 1] = -radius
    
    ff_upper = ff[:num_upper]
    ff_lower = ff[num_upper:]
    
    return np.vstack([ff_upper, ff_lower])
