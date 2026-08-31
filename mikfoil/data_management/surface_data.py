from mikfoil.case import Case
import pandas as pd
import pyvista as pv
import numpy as np
def save_surface_data(case: Case, surface_df: pd.DataFrame) -> None:
    file_path = case.dir / "surface_data.csv"
    surface_df.to_csv(file_path, index=False)


def add_surface_data(case: Case, surface_df: pd.DataFrame) -> None:
    file_path = case.dir / "surface_data.csv"
    existing_df = pd.read_csv(file_path)
    sources_to_add = surface_df["source"].unique()
    existing_df = existing_df[~existing_df["source"].isin(sources_to_add)]
    combined_df = pd.concat([existing_df, surface_df], ignore_index=True)
    combined_df.to_csv(file_path, index=False)


def load_surface_data(case: Case, source: str, surface: str, variable: str) -> np.ndarray:
    """Extracts a 1D contiguous array of a specific aerodynamic variable."""
    file_path = case.dir / "surface_data.csv"
    surface_data = pd.read_csv(file_path)
    surface_data = surface_data[(surface_data["source"] == source) & (surface_data["surface"] == surface)]
    return surface_data[variable].to_numpy()


def read_SU2_surface_data(case: Case) -> pd.DataFrame:
    """Parses raw SU2 unstructured grid VTU output into structured surface parameters."""
    file_path = str(case.su2_dir / "surface.vtu")
    surface_data = pv.read(file_path)

    x_coords = surface_data.points[:, 0]
    y_coords = surface_data.points[:, 1]
    cp = surface_data.point_data["Pressure_Coefficient"]
    yplus = surface_data.point_data["Y_Plus"]
    cf = surface_data.point_data["Skin_Friction_Coefficient"][:, 0]

    su2_surface_data = pd.DataFrame({"x": x_coords, "y": y_coords, "cp": cp, "yplus": yplus, "cf": cf})
    if "LM_gamma" in surface_data.point_data:
        su2_surface_data["LM_gamma"] = surface_data.point_data["LM_gamma"]
        su2_surface_data["LM_gamma_sep"] = surface_data.point_data["LM_gamma_sep"]
        su2_surface_data["LM_gamma_eff"] = surface_data.point_data["LM_gamma_eff"]
        su2_surface_data["LM_Re_t"] = surface_data.point_data["LM_Re_t"]

    su2_surface_data["source"] = "SU2"
    su2_surface_data = _split_surface_data(su2_surface_data)

    return su2_surface_data


def _split_surface_data(surface_df: pd.DataFrame) -> pd.DataFrame:
    surface_df = surface_df[surface_df["x"] <= 0.995]

    is_upper = surface_df["y"] >= 0
    is_lower = surface_df["y"] < 0

    surface_df.loc[is_upper, "surface"] = "upper"
    surface_df.loc[is_lower, "surface"] = "lower"

    surface_df = surface_df.sort_values(by="x")
    surface_df = surface_df.reset_index(drop=True)

    return surface_df
