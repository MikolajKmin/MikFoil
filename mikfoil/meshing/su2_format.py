import numpy as np
from mikfoil.meshing.mesh_types import Mesh

SU2_QUAD_TYPE = 9
SU2_LINE_TYPE = 3

def build_quad_elements(num_points: int, num_layers: int) -> np.ndarray:
    point_indices = np.arange(num_points - 1)
    layer_indices = np.arange(num_layers - 1)
    
    point_grid, layer_grid = np.meshgrid(point_indices, layer_indices, indexing='ij')
    
    node_bottom_left = point_grid * num_layers + layer_grid
    node_bottom_right = (point_grid + 1) * num_layers + layer_grid
    node_top_right = (point_grid + 1) * num_layers + (layer_grid + 1)
    node_top_left = point_grid * num_layers + (layer_grid + 1)
    
    quads = np.column_stack((
        np.full(node_bottom_left.size, SU2_QUAD_TYPE),
        node_bottom_left.flatten(),
        node_bottom_right.flatten(),
        node_top_right.flatten(),
        node_top_left.flatten()
    ))
    
    return quads

def build_boundary_edges(grid: Mesh) -> dict[str, np.ndarray]:
    num_points = grid.num_points
    num_layers = grid.num_layers
    nw = grid.num_wake_pts
    na = grid.num_airfoil_pts
    
    start_idx = nw - 1
    airfoil_pts = np.arange(start_idx, start_idx + na - 1)
    airfoil_n1 = airfoil_pts * num_layers
    airfoil_n2 = (airfoil_pts + 1) * num_layers
    airfoil_edges = np.column_stack((
        np.full(airfoil_n1.size, SU2_LINE_TYPE),
        airfoil_n1,
        airfoil_n2
    ))
    
    point_indices = np.arange(num_points - 1)
    farfield_n1 = point_indices * num_layers + (num_layers - 1)
    farfield_n2 = (point_indices + 1) * num_layers + (num_layers - 1)
    farfield_edges = np.column_stack((
        np.full(farfield_n1.size, SU2_LINE_TYPE),
        farfield_n1,
        farfield_n2
    ))
    
    layer_indices = np.arange(num_layers - 1)
    
    wake_out_upper_n1 = 0 * num_layers + layer_indices + 1
    wake_out_upper_n2 = 0 * num_layers + layer_indices
    wake_out_upper_edges = np.column_stack((
        np.full(wake_out_upper_n1.size, SU2_LINE_TYPE),
        wake_out_upper_n1,
        wake_out_upper_n2
    ))
    
    wake_out_lower_n1 = (num_points - 1) * num_layers + layer_indices
    wake_out_lower_n2 = (num_points - 1) * num_layers + (layer_indices + 1)
    wake_out_lower_edges = np.column_stack((
        np.full(wake_out_lower_n1.size, SU2_LINE_TYPE),
        wake_out_lower_n1,
        wake_out_lower_n2
    ))
    
    farfield_combined = np.vstack([
        farfield_edges,
        wake_out_upper_edges,
        wake_out_lower_edges
    ])
    
    return {
        "airfoil": airfoil_edges,
        "farfield": farfield_combined
    }

def export_su2_mesh(grid: Mesh, filepath: str) -> None:
    num_points = grid.num_points
    num_layers = grid.num_layers
    total_nodes = num_points * num_layers
    flat_coords = grid.points.reshape(total_nodes, 2)
    
    node_ids = np.arange(total_nodes)
    nw = grid.num_wake_pts
    na = grid.num_airfoil_pts
    
    # ONLY merge layer 0 (the exact physical boundary of the wake cut)
    layer = 0
    for w in range(nw):
        idx_upper = w * num_layers + layer
        idx_lower = (num_points - 1 - w) * num_layers + layer
        node_ids[idx_lower] = node_ids[idx_upper]
            
    quads = build_quad_elements(num_points, num_layers)
    for q in range(len(quads)):
        quads[q, 1] = node_ids[quads[q, 1]]
        quads[q, 2] = node_ids[quads[q, 2]]
        quads[q, 3] = node_ids[quads[q, 3]]
        quads[q, 4] = node_ids[quads[q, 4]]
        
    boundaries = build_boundary_edges(grid)
    farfield_combined = boundaries["farfield"]
    airfoil_edges = boundaries["airfoil"]
    
    for e in range(len(airfoil_edges)):
        airfoil_edges[e, 1] = node_ids[airfoil_edges[e, 1]]
        airfoil_edges[e, 2] = node_ids[airfoil_edges[e, 2]]
        
    for e in range(len(farfield_combined)):
        farfield_combined[e, 1] = node_ids[farfield_combined[e, 1]]
        farfield_combined[e, 2] = node_ids[farfield_combined[e, 2]]
        
    unique_ids, unique_indices = np.unique(node_ids, return_index=True)
    mapping = {old_id: new_id for new_id, old_id in enumerate(unique_ids)}
    
    for q in range(len(quads)):
        quads[q, 1] = mapping[quads[q, 1]]
        quads[q, 2] = mapping[quads[q, 2]]
        quads[q, 3] = mapping[quads[q, 3]]
        quads[q, 4] = mapping[quads[q, 4]]
        
    for e in range(len(airfoil_edges)):
        airfoil_edges[e, 1] = mapping[airfoil_edges[e, 1]]
        airfoil_edges[e, 2] = mapping[airfoil_edges[e, 2]]
        
    for e in range(len(farfield_combined)):
        farfield_combined[e, 1] = mapping[farfield_combined[e, 1]]
        farfield_combined[e, 2] = mapping[farfield_combined[e, 2]]

    with open(filepath, "w") as f:
        f.write("NDIME= 2\n")
        f.write(f"NELEM= {len(quads)}\n")
        np.savetxt(f, quads, fmt="%d")

        f.write(f"NPOIN= {len(unique_ids)}\n")
        points_export = np.column_stack((flat_coords[unique_indices], np.arange(len(unique_ids))))
        np.savetxt(f, points_export, fmt=["%.8f", "%.8f", "%d"])

        f.write(f"NMARK= 2\n")
        f.write(f"MARKER_TAG= airfoil\n")
        f.write(f"MARKER_ELEMS= {len(airfoil_edges)}\n")
        np.savetxt(f, airfoil_edges, fmt="%d")

        f.write(f"MARKER_TAG= farfield\n")
        f.write(f"MARKER_ELEMS= {len(farfield_combined)}\n")
        np.savetxt(f, farfield_combined, fmt="%d")
