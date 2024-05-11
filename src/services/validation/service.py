from src.services.validation.dto import ComputeConfig
from pydantic import parse_obj_as
import yaml


class ValidationService:

    @staticmethod
    def get_config_from(file_data) -> ComputeConfig:
        yaml_data = yaml.safe_load(file_data)
        config = ComputeConfig.model_validate(yaml_data)
        return config
