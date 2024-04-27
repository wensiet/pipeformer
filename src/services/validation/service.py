from src.services.validation.dto import ComputeConfig
from pydantic import parse_obj_as
import yaml
from pydantic import ValidationError


class ValidationService:

    def get_config_from(self, file_data) -> ComputeConfig:
        yaml_data = yaml.safe_load(file_data)
        config = parse_obj_as(ComputeConfig, yaml_data)
        return config
