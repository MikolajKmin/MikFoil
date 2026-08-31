import math
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from mikfoil.case import Case


def generate_su2_config(case: Case) -> str:
    core_templates_dir = Path(__file__).resolve().parent / "core_configs"
    
    config_input = str(case.su2_config)
    config_path = Path(config_input)
    
    # 1. Check if user provided a special core template word (e.g., "default", "multigrid")
    core_file = core_templates_dir / f"{config_input}.cfg"
    if core_file.is_file():
        search_dir = core_templates_dir
        template_name = core_file.name
    else:
        # 2. Treat as a user-provided file path exactly as written
        project_relative_path = case.project_dir / config_input
        
        if config_path.is_absolute() and config_path.is_file():
            search_dir = config_path.parent
            template_name = config_path.name
        elif config_path.is_file():
            search_dir = config_path.parent
            template_name = config_path.name
        elif project_relative_path.is_file():
            search_dir = project_relative_path.parent
            template_name = project_relative_path.name
        else:
            raise FileNotFoundError(
                f"Could not find SU2 configuration template '{case.su2_config}'. "
                f"Searched for core template, absolute path '{config_path}', and relative path '{project_relative_path}'."
            )

    env = Environment(loader=FileSystemLoader(str(search_dir)))
    
    # Expose the math module to Jinja2 so templates can do geometry calculations natively
    env.globals['math'] = math

    template = env.get_template(template_name)
    
    # Render base config
    base_config_str = template.render(case=case)
    return base_config_str
