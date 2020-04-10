import pytest
import urllib


@pytest.fixture
def mock_urlopen_with_invalid_request(monkeypatch, request):
    status_code = request.param

    class HTTPResponseFake:
        def getcode(self):
            return status_code

        def read(self):
            return b'{"1":"1"}'

    def wrap_url_open(*args, **kwargs):
        return HTTPResponseFake()

    monkeypatch.setattr(urllib.request, 'urlopen', wrap_url_open)


@pytest.fixture
def mock_urlopen_with_valid_request(monkeypatch):
    class HTTPResponseFake:
        def getcode(self):
            return 200

        def read(self):
            return b'{"country":"RU","city":"city17"}'

    def wrapp_url_open(*args, **kwargs):
        return HTTPResponseFake()

    monkeypatch.setattr(urllib.request, 'urlopen', wrapp_url_open)


@pytest.mark.parametrize('path, ip', (
        ('/127.0.0.1', '127.0.0.1'),
        ('/1/2/3/4/5', '1'),
        ('', None),
))
def test_ip_from_path(application, path, ip):
    ip_ = application.get_ip_from_path(path)
    assert ip_ == ip


@pytest.mark.parametrize('mock_urlopen_with_invalid_request, ip, expected ', [
    (400, 'invalid_ip', None),
    (200, '1.1.1.1', None)
], indirect=['mock_urlopen_with_invalid_request'])
def test_fetch_info_by_ip_with_no_ip(application, mock_urlopen_with_invalid_request, ip, expected):
    application.fetch_info_by_ip('invalid_ip')
    assert application.data is None


def test_fetch_info_by_ip_with_success_request(application, mock_urlopen_with_valid_request):
    application.fetch_info_by_ip('1.1.1.1')
    assert application.data['city'] == 'city17'
    assert application.data['country'] == 'RU'


def test_fetch_weather_without_info_about_ip(application):
    application.fetch_weather()
    assert application.body is None


def test_fetch_weather_without_api_key(application):
    application.data = True
    application.apiid = False

    application.fetch_weather()

    assert application.body is None


@pytest.mark.parametrize('mock_urlopen_with_invalid_request', [400], indirect=True)
def test_fetch_weather_when_non_ok_request(application, mock_urlopen_with_invalid_request):
    application.data = {"city": "city17", "country": "HL"}

    application.fetch_weather()

    assert application.body is None


def test_fetch_weather_when_good_request(application, mock_urlopen_with_valid_request):
    application.data = {"city": "city17", "country": "HL"}

    application.fetch_weather()

    assert application.body == b'{"country":"RU","city":"city17"}'
