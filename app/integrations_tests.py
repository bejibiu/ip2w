from app.ip2w import fetch_info_by_ip, fetch_weather


def test_success_integration_with_ipinfo():
    data = fetch_info_by_ip("8.8.8.8")
    assert data == {
        "ip": "8.8.8.8",
        "hostname": "dns.google",
        "city": "Mountain View",
        "region": "California",
        "country": "US",
        "loc": "37.3860,-122.0838",
        "org": "AS15169 Google LLC",
        "postal": "94035",
        "timezone": "America/Los_Angeles",
        "readme": "https://ipinfo.io/missingauth",
    }


def test_success_integration_with_openweather(api_key):
    data = {"city": "London", "country": "UK"}

    body = fetch_weather(data, api_key)

    assert "temp" in body.decode()
