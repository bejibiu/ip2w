import os


def test_success_integration_with_ipinfo(application):
    application.fetch_info_by_ip("8.8.8.8")
    assert application.data == {
        "ip": "8.8.8.8",
        "hostname": "dns.google",
        "city": "Mountain View",
        "region": "California",
        "country": "US",
        "loc": "37.3860,-122.0838",
        "org": "AS15169 Google LLC",
        "postal": "94035",
        "timezone": "America/Los_Angeles",
        "readme": "https://ipinfo.io/missingauth"}


def test_success_integration_with_openweather(application):
    assert application.apiid
    application.data = {"city": "London", "country": "UK"}

    application.fetch_weather()

    assert 'temp' in application.body.decode()
