import pandas as pd
from pathlib import Path

from mikfoil.case import Case, MeshConfig




def read_experimental_surface_data(case: Case) -> pd.DataFrame:
    file_path = case.experimental_data_file

    experimental_data = pd.read_csv(file_path, names=["x", "cp"], skiprows=1, usecols=[0, 1])

    experimental_data["source"] = "EXPERIMENT"
    experimental_data = _split_experimental_data(experimental_data)

    return experimental_data


def _split_experimental_data(surface_data: pd.DataFrame) -> pd.DataFrame:
    '''Splits surface data into upper and lower basing on the format in which aspire data is defined'''
    tagged_data = surface_data.copy()

    leading_edge_index = tagged_data["x"].idxmin()

    is_upper_surface = tagged_data.index <= leading_edge_index
    is_lower_surface = tagged_data.index > leading_edge_index

    tagged_data.loc[is_upper_surface, "surface"] = "upper"
    tagged_data.loc[is_lower_surface, "surface"] = "lower"

    tagged_data = tagged_data.sort_values(by="x")
    tagged_data = tagged_data.reset_index(drop=True)

    return tagged_data
