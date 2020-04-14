import urllib.request
import platform
import os
import logging
import json

from configparser import ConfigParser

path_to_config = (
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "windows.ip2w.ini")
    if platform.system() == "Windows"
    else "/usr/local/etc/ip2w.ini"
)

config = ConfigParser()
if not os.path.exists(path_to_config):
    exit(f"File config not found in {path_to_config}")
config.read(path_to_config)
config = config["default"]

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    filename=config.get("PATH_TO_LOG_FILE"),
    datefmt="%Y.%m.%d %H:%M:%S",
)
logging.info("start application")
error_message = """
<html>
<head>
    <title>Error</title>
</head>
<body>
    <h1>Error response</h1>
</body>
</html>
"""


def application(env, start_response):
    apiid = os.environ.get("API_KEY", None) or config.get("API_KEY")
    if apiid is None:
        logging.error("No set api key for openweathermap. Please set key in config")
        raise Exception("No set api key for openweathermap. Please set key in config")
    logging.info(f'Path = {env["PATH_INFO"]}')
    ip_addr = get_ip_from_path(env["PATH_INFO"]) or env["REMOTE_ADDR"]
    try:
        info_by_ip = fetch_info_by_ip(ip_addr)
        body = fetch_weather(info_by_ip, apiid)
    except urllib.error.URLError as e:
        body = error_message.replace(
            "Error response", str(e).replace("<", "&lt").replace(">", "&gt")
        ).encode()
        logging.error(e)
        status = "400 Bad Request"
        type_message_header = ("Content-Type", "text/html")
    else:
        status = "200 OK"
        type_message_header = ("Content-Type", "application/json")
    finally:
        logging.info("finaly")
        start_response(
            status, [type_message_header, ("Content-Length", f"{len(body)}")],
        )
        logging.info(f"body: {body}")
        return [body]


def get_ip_from_path(path_info):
    if path_info:
        return path_info.split("/")[1]


def fetch_info_by_ip(ip_addr):
    ipinfo_address_template = "https://ipinfo.io/{}"
    logging.info(ip_addr)
    try:
        webUrl = get_connection(ipinfo_address_template.format(ip_addr))
    except urllib.error.URLError:
        raise urllib.error.URLError("Ipinfo service return error")
    else:
        data_str = webUrl.read().decode()
        data = json.loads(data_str)
        logging.info(f"data json {data}")
        if "city" in data_str and "country" in data_str:
            return data
        raise urllib.error.URLError(
            f"Ipinfo service did not return information about  {ip_addr}"
        )


def fetch_weather(data, apiid):
    openweather_api_template = (
        "https://api.openweathermap.org/data/2.5/weather?q={},{}&appid={}"
    )
    if data:
        path_to_weather = openweather_api_template.format(
            data["city"], data["country"], apiid
        )
        try:
            webUrl = get_connection(path_to_weather)
        except urllib.error.HTTPError:
            raise urllib.error.URLError(
                f"can not fetch weather status bad status codes"
            )
        else:
            weather = webUrl.read()
            logging.info(f"weather: {weather}")
            return weather


def get_connection(url, attempt=3, timeout=30):
    last_error = None
    for connection_num in range(attempt):
        try:
            return urllib.request.urlopen(url, timeout=timeout)
        except Exception as e:
            last_error = e
    logging.exception(last_error)
    raise last_error
