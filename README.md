IP2W - ip to weather
=============
Traing **uwsgi** daemon project. The service returns the weather depending on your ip address. Via the ' ip 'service `info.io` location is determined, and via the service  `openweathermap.org' weather. ATTENTION for the Openweathermap service, you need to register and get the api key, which must then be put in the initial settings.

Reqrements
----------
* Centos 7,8
* Systemd
* uwsgi
* nginx

How to run
-----------
install rpm packages
```shell sсript
rpm -i ip2w-0.0.1-1.noarch.rpm
# Run services 
systemctl start ip2w.service
systemctl start nginx.service
# after service will be avalible at local hosr
curl http://localhost/1.1.1.1
```

Settings
------
file settings locate into /usr/local/etc/ip2w.ini

- `PATH_TO_LOG_FILE` - by default in `/var/log/ip2w/ip2w.log
- `API_KEY` - **reqirement** settings. It's tokent from openweathermap site.


Testings
----------------
Tests write by pytest and may be run by command `python3 -m pytest` in directory with project.

Troubleshooter
-------
Change settings nginx if you want connect from internet
Check selinux. Iptables (firewalld). 
