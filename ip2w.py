import urllib.request
import os
import logging
import json

my_ip = "95.131.149.111"


class IPWeather:
    ipinfo_address_template = 'https://ipinfo.io/{}'
    openweather_api_template = 'https://api.openweathermap.org/data/2.5/weather?q={},{}&appid={}'
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

    def __init__(self):
        self.body = None
        self.apiid = os.environ.get('API_KEY', None)
        self.data = None
        self.error = ("400 Bad request", "Error response")

    def __call__(self, env, start_response):

        self.env = env
        logging.info(f'Path = {env["PATH_INFO"]}')
        ip_addr = self.get_ip_from_path(env['PATH_INFO']) or env['REMOTE_ADDR']
        self.fetch_info_by_ip(ip_addr)
        self.fetch_weather()
        if self.body:
            start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', f'{len(self.body)}')])
            return [self.body]
        message = self.error_message.replace('Error response', self.error[1]).encode()
        logging.info(f'send error message {message}')
        start_response(self.error[0], [('Content-Type', 'text/html'), ('Content-Length', f'{len(message)}')])
        return [message]

    @staticmethod
    def get_ip_from_path(path_info):
        if path_info:
            return path_info.split('/')[1]

    def fetch_info_by_ip(self, ip_addr):
        logging.info(ip_addr)
        webUrl = urllib.request.urlopen(self.ipinfo_address_template.format(ip_addr))
        if webUrl.getcode() == 200:
            data_str = webUrl.read().decode()
            data = json.loads(data_str)
            logging.info(f"data json {data}")
            if 'city' in data_str and 'country' in data_str:
                self.data = data
                return
            message = f'Ipinfo service did not return information about  {ip_addr}'
            logging.error(message)
            self.error = ('400 Bad request', message)
            return
        logging.error(f'can not fetch ipinfo')
        self.error = ('400 Bad request', "Ipinfo service return error")

    def fetch_weather(self):
        if self.data and self.apiid:
            path_to_weather = self.openweather_api_template.format(self.data['city'], self.data['country'], self.apiid)
            webUrl = urllib.request.urlopen(path_to_weather)
            if webUrl.getcode() == 200:
                self.body = webUrl.read()
                logging.info(f"weather: {self.body}")
                return
            logging.error(f'can not fetch weather status code={webUrl.getcode()}')
            self.error = ('400 Bad request', "Server openweather not available")
            return


logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s',
                    filename=None,
                    datefmt='%Y.%m.%d %H:%M:%S')

application = IPWeather()
