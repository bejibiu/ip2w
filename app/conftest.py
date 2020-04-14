import pytest

from app.ip2w import path_to_config
from configparser import ConfigParser


@pytest.fixture
def api_key():
    config = ConfigParser()
    config.read(path_to_config)
    config = config["default"]
    return config.get("API_KEY")
