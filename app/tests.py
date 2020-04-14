import pytest
import urllib

from app.ip2w import fetch_info_by_ip, fetch_weather, get_ip_from_path


@pytest.fixture
def mock_urlopen_with_invalid_request(monkeypatch, request):
    status_code = request.param

    class HTTPResponseFake:
        def __init__(self):
            if status_code != 200:
                raise urllib.error.HTTPError(None, status_code, "error", None, None)

        def getcode(self):
            return status_code

        def read(self):
            return b'{"1":"1"}'

    def wrap_url_open(*args, **kwargs):
        return HTTPResponseFake()

    monkeypatch.setattr(urllib.request, "urlopen", wrap_url_open)


@pytest.fixture
def mock_urlopen_with_valid_request(monkeypatch):
    class HTTPResponseFake:
        def getcode(self):
            return 200

        def read(self):
            return b'{"country":"RU","city":"city17"}'

    def wrapp_url_open(*args, **kwargs):
        return HTTPResponseFake()

    monkeypatch.setattr(urllib.request, "urlopen", wrapp_url_open)


@pytest.mark.parametrize(
    "path, ip", (("/127.0.0.1", "127.0.0.1"), ("/1/2/3/4/5", "1"), ("", None),)
)
def test_ip_from_path(path, ip):
    ip_ = get_ip_from_path(path)
    assert ip_ == ip


@pytest.mark.parametrize(
    "mock_urlopen_with_invalid_request, ip, expected ",
    [(400, "invalid_ip", None), (200, "1.1.1.1", None)],
    indirect=["mock_urlopen_with_invalid_request"],
)
def test_fetch_info_by_ip_with_no_ip(mock_urlopen_with_invalid_request, ip, expected):
    with pytest.raises(urllib.error.URLError):
        fetch_info_by_ip("invalid_ip") is None


def test_fetch_info_by_ip_with_success_request(mock_urlopen_with_valid_request):
    data = fetch_info_by_ip("1.1.1.1")
    assert data["city"] == "city17"
    assert data["country"] == "RU"


@pytest.mark.parametrize("mock_urlopen_with_invalid_request", [400], indirect=True)
def test_fetch_weather_when_non_ok_request(api_key, mock_urlopen_with_invalid_request):
    data = {"city": "city17", "country": "HL"}

    with pytest.raises(urllib.error.URLError):
        fetch_weather(data, api_key)


def test_fetch_weather_when_good_request(api_key, mock_urlopen_with_valid_request):
    data = {"city": "city17", "country": "HL"}

    body = fetch_weather(data, api_key)

    assert body == b'{"country":"RU","city":"city17"}'
