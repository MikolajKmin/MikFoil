from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Literal, Union

import yaml
import json

@dataclass
class Case:
    airfoil: Union[str, Path]
    aoa: float
    mach: float
    reynolds: float

    mesh_config: 'MeshConfig'
    
    su2_config: Union[str, Path] = "default"
    target_y_plus: Optional[float] = 1.0
    
    #SU2 (default, incompressible, multigrid, transition, wall_functions)
    restart: bool = False
    
    # XFoil parameters
    xfoil_config: Union[str, Path] = "default"
    
    #Other variables to define
    project_dir: Union[Path, str] = field(default_factory=Path.cwd)
    suffix: str = ""
    experimental_data_file: Optional[Union[Path, str]] = None
    
    # Results and state
    results: 'Results' = field(default_factory=lambda: Results(), init=False)

    def __post_init__(self):
        """So both pathlib Paths and strings work"""
        if isinstance(self.project_dir, str):
            self.project_dir = Path(self.project_dir)
        if isinstance(self.experimental_data_file, str):
            self.experimental_data_file = Path(self.experimental_data_file)

    @property
    def airfoil_name(self) -> str:
        return Path(self.airfoil).stem

    @property
    def name(self) -> str:
        re_formatted = f"{self.reynolds:.1e}".replace("+", "").replace(".0", "")
        base_name = f"{self.airfoil_name}_AoA_{self.aoa:g}_M_{self.mach:g}_Re_{re_formatted}"

        if not self.suffix:
            return base_name

        return f"{base_name}_{self.suffix}"

    @property
    def dir(self) -> Path:
        return self.project_dir / "cases" / self.name

    @property
    def su2_dir(self) -> Path:
        return self.dir / "su2"

    @property
    def validation_dir(self) -> Path:
        return self.dir / "validation"

    @property
    def plots_dir(self) -> Path:
        return self.dir / "plots"

    @property
    def contours_dir(self) -> Path:
        return self.dir / "contours"

    @property
    def mesh_path(self) -> Path:
        return self.su2_dir / "mesh.su2"

    def setup(self) -> None:
        self.su2_dir.mkdir(parents=True, exist_ok=True)
        self.validation_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        self.contours_dir.mkdir(parents=True, exist_ok=True)

    def write_config(self, content: str) -> None:
        self.setup()
        config_path = self.su2_dir / "config.cfg"
        config_path.write_text(content)


@dataclass
class MeshConfig:
    """Structural parameters and resolution of the generated mesh."""
    use_normals: bool = True
    fineness: float = 1.0
    domain_radius: float = 10.0
    wake_length: float = 8.0
    chord: float = 1.0
    first_layer_height: float = 0.001
    
    s_le: float = 0.00625 
    s_mid: float = 0.05
    s_te: float = 0.0375
    
    radial_growth_rate: float = 1.03
    wake_growth_rate: float = 1.05

@dataclass
class Results:
    """Stores all output metrics and state flags generated during execution."""
    success: bool = False
    xfoil_converged: bool = False
    execution_time: float = 0.0

    cl: Optional[float] = None
    cd: Optional[float] = None
    cm: Optional[float] = None

    xfoil_cl: Optional[float] = None
    xfoil_cd: Optional[float] = None
    xfoil_cm: Optional[float] = None

    mesh_number_of_cells: Optional[int] = None
    mesh_min_angle: Optional[float] = None
    mesh_max_skewness: Optional[float] = None

    upper_transition_x: Optional[float] = None
    upper_separation_x: Optional[float] = None

    def save_to_yaml(self, case_dir: Path) -> None:
        from dataclasses import asdict
        
        # Save only fields that are not None
        data = {k: v for k, v in asdict(self).items() if v is not None}
        case_data_file = case_dir / "case_data.yaml"
        case_data_file.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False), encoding="utf-8")

    def load_from_yaml(self, case_dir: Path) -> None:
        case_data_file = case_dir / "case_data.yaml"
        data = {}
        if case_data_file.exists():
            data = yaml.safe_load(case_data_file.read_text(encoding="utf-8")) or {}
        else:
            case_data_json = case_dir / "case_data.json"
            if case_data_json.exists():
                data = json.loads(case_data_json.read_text(encoding="utf-8")) or {}

        # Base fields
        self.success = data.get("success", self.success)
        self.execution_time = data.get("execution_time", self.execution_time)
        self.xfoil_converged = data.get("xfoil_converged", self.xfoil_converged)

        # Aerodynamics
        self.cl = data.get("cl", self.cl)
        self.cd = data.get("cd", self.cd)
        self.cm = data.get("cm", self.cm)

        # XFoil
        self.xfoil_cl = data.get("xfoil_cl", self.xfoil_cl)
        self.xfoil_cd = data.get("xfoil_cd", self.xfoil_cd)
        self.xfoil_cm = data.get("xfoil_cm", self.xfoil_cm)

        # Mesh metrics
        self.mesh_number_of_cells = data.get("mesh_number_of_cells", self.mesh_number_of_cells)
        self.mesh_min_angle = data.get("mesh_min_angle", self.mesh_min_angle)
        self.mesh_max_skewness = data.get("mesh_max_skewness", self.mesh_max_skewness)

        # Transition metrics
        self.upper_transition_x = data.get("upper_transition_x", self.upper_transition_x)
        self.upper_separation_x = data.get("upper_separation_x", self.upper_separation_x)
