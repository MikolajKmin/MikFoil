import yaml
from dataclasses import asdict
from pathlib import Path

from mikfoil.case import Case, MeshConfig
from mikfoil.main import execute_case




def cases_from_yaml(file_path: Path) -> list[Case]:

    with open(file_path, "r", encoding="utf-8") as file:
        yaml_data = yaml.safe_load(file)

    mesh_config_batch = yaml_data.get("mesh_config", {})
    
    su2_config_batch = yaml_data.get("su2_config", "default")

    cases_yaml = yaml_data.get("cases", [])

    cases = []
    for case_yaml in cases_yaml:
        mesh_config_case = case_yaml.pop("mesh_config", {})
        mesh_kwargs = {**mesh_config_batch, **mesh_config_case}
        mesh_config = MeshConfig(**mesh_kwargs)

        su2_config_case = case_yaml.pop("su2_config", su2_config_batch)

        case = Case(
            airfoil=case_yaml.pop("airfoil"),
            aoa=case_yaml.pop("aoa"),
            mach=case_yaml.pop("mach"),
            reynolds=case_yaml.pop("reynolds"),
            mesh_config=mesh_config,
            su2_config=su2_config_case,
            **case_yaml
        )
        cases.append(case)

    cases.sort(key=lambda case: case.aoa)
    return cases


def cases_to_yaml(cases: list[Case], output_path: Path) -> None:

    cases.sort(key=lambda case: case.aoa)
    
    cases_list = []
    for case in cases:
        case_dict = asdict(case)
        # Convert Path objects to strings
        for k, v in case_dict.items():
            if isinstance(v, Path):
                case_dict[k] = str(v)
        cases_list.append(case_dict)
        
    batch_dict = {
        "mesh_config": {}, 
        "su2_config": "default",
        "cases": cases_list
    }

    with open(output_path, mode="w", encoding="utf-8") as file:
        yaml.dump(batch_dict, file, default_flow_style=False, sort_keys=False)



