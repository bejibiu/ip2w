import pytest

from app.ip2w import IPWeather, path_to_config
from configparser import ConfigParser


@pytest.fixture
def load_api():
    config = ConfigParser()
    config.read(path_to_config)
    config = config['default']
    return config.get('API_KEY')



@pytest.fixture
def application(load_api):
    return IPWeather(load_api)
