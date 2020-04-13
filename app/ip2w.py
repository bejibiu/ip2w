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


class IPWeather:
    ipinfo_address_template = "https://ipinfo.io/{}"
    openweather_api_template = (
        "https://api.openweathermap.org/data/2.5/weather?q={},{}&appid={}"
    )
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

    def __init__(self, apiid):
        self.body = None
        self.apiid = apiid
        self.data = None
        self.error = ("400 Bad request", "Error response")

    def __call__(self, env, start_response):
        if self.apiid is None:
            logging.error("No set api key for openweathermap. Please set key in config")
            raise Exception("No set api key for openweathermap. Please set key in config")
        self.env = env
        logging.info(f'Path = {env["PATH_INFO"]}')
        ip_addr = self.get_ip_from_path(env["PATH_INFO"]) or env["REMOTE_ADDR"]
        self.fetch_info_by_ip(ip_addr)
        self.fetch_weather()
        if self.body:
            start_response(
                "200 OK",
                [
                    ("Content-Type", "application/json"),
                    ("Content-Length", f"{len(self.body)}"),
                ],
            )
            return [self.body]
        message = self.error_message.replace("Error response", self.error[1]).encode()
        logging.info(f"send error message {message}")
        start_response(
            self.error[0],
            [("Content-Type", "text/html"), ("Content-Length", f"{len(message)}")],
        )
        return [message]

    @staticmethod
    def get_ip_from_path(path_info):
        if path_info:
            return path_info.split("/")[1]

    def fetch_info_by_ip(self, ip_addr):
        logging.info(ip_addr)
        webUrl = self.get_connection(self.ipinfo_address_template.format(ip_addr))
        if webUrl.getcode() == 200:
            data_str = webUrl.read().decode()
            data = json.loads(data_str)
            logging.info(f"data json {data}")
            if "city" in data_str and "country" in data_str:
                self.data = data
                return
            message = f"Ipinfo service did not return information about  {ip_addr}"
            logging.error(message)
            self.error = ("400 Bad request", message)
            return
        logging.error(f"can not fetch ipinfo")
        self.error = ("400 Bad request", "Ipinfo service return error")

    def fetch_weather(self):
        if self.data and self.apiid:
            path_to_weather = self.openweather_api_template.format(
                self.data["city"], self.data["country"], self.apiid
            )
            webUrl = self.get_connection(path_to_weather)
            if webUrl.getcode() == 200:
                self.body = webUrl.read()
                logging.info(f"weather: {self.body}")
                return
            logging.error(f"can not fetch weather status code={webUrl.getcode()}")
            self.error = ("400 Bad request", "Server openweather not available")
            return

    @staticmethod
    def get_connection(url, attempt=3, timeout=30):
        last_error = None
        for connection_num in range(attempt):
            try:
                return urllib.request.urlopen(url, timeout=timeout)
            except Exception as e:
                last_error = e
        logging.exception(last_error)
        raise last_error


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
application = IPWeather(os.environ.get("API_KEY", None) or config.get("API_KEY"))
