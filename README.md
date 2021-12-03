# External IP Checker

## What is it?

External IP Checker checks is your External IP is in sync with a A-record in DNS

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Y8Y078U1V)

## Config

In the directory /config the python script expects a config file called 'external_IP_checker.ini' with the following content:

        [COMMON]
        URL = domain.org

        [PUSHOVER]
        USER_KEY = xxxxxxxxxxxxxxx
        TOKEN_API = xxxxxxxxxxxxxxx
        SOUND = pushover

2021-11-21 11:58:54
