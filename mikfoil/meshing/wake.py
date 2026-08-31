import numpy as np

def calculate_wake_x_positions(wake_length: float, initial_height: float, growth_rate: float) -> np.ndarray:
    """Calculates geometric x-coordinate progression for the wake."""
    positions = [0.0]
    current_cell_width = initial_height
    
    while positions[-1] < wake_length:
        positions.append(positions[-1] + current_cell_width)
        current_cell_width *= growth_rate
        
    return np.array(positions)

def extrude_wake_meshes(upper_te_line: np.ndarray, lower_te_line: np.ndarray, wake_x_positions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Extrudes trailing edge radial lines into 2D wake blocks along calculated x-positions."""
    num_wake_pts = len(wake_x_positions)
    num_layers = len(upper_te_line)
    
    # Create the 3D offset array (wake_pts, layers, coordinates)
    offsets = np.zeros((num_wake_pts, num_layers, 2))
    offsets[:, :, 0] = wake_x_positions[:, None]
    
    # Broadcast the trailing edge line across the wake points and add the horizontal offset
    wake_upper = upper_te_line[None, :, :] + offsets
    wake_lower = lower_te_line[None, :, :] + offsets
    
    return wake_upper, wake_lower
