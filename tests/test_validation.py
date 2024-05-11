import pydantic
import yaml
import pytest
import os

from src.services.validation.dto import ComputeConfig
from src.services.validation.service import ValidationService

CONFIGS_DIR = 'tests/presets/configs/'

INVALID_CONFIGS_DIR = CONFIGS_DIR + 'invalid/'
VALID_CONFIGS_DIR = CONFIGS_DIR + 'valid/'

invalid_configs = [INVALID_CONFIGS_DIR + filename for filename in os.listdir(INVALID_CONFIGS_DIR)]
valid_configs = [VALID_CONFIGS_DIR + filename for filename in os.listdir(VALID_CONFIGS_DIR)]


@pytest.mark.parametrize("config_file", invalid_configs)
def test_invalid_configs(config_file):
    with open(config_file) as f:
        file_data = f.read()
        with pytest.raises(pydantic.ValidationError):
            ValidationService.get_config_from(file_data)


@pytest.mark.parametrize("config_file", valid_configs)
def test_valid_configs(config_file):
    with open(config_file) as f:
        file_data = f.read()
    config = ValidationService.get_config_from(file_data)
    assert config is not None
