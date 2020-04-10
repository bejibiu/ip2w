import os

import pytest

from app.ip2w import IPWeather


@pytest.fixture
def load_env():
    if not os.environ.get("API_KEY", None):
        with open('app/.env', 'r') as ini:
            env = ini.read()
            os.environ['API_KEY'] = env.split('=')[-1]


@pytest.fixture
def application(load_env):
    return IPWeather()
