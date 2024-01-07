# Name: Check IP based on DNS
# Coder: Marco Janssen (twitter @marc0janssen)
# date: 2021-11-21 11:57:46
# update: 2024-01-07 13:52:00

import dns.resolver
from requests import get
import logging
import configparser
import shutil
import sys
from chump import Application


class External_IP_Checker():
    def __init__(self):

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)

        self.config_file = "/config/external_IP_checker.ini"

        try:
            with open(self.config_file, "r") as f:
                f.close()
            try:
                self.config = configparser.ConfigParser()
                self.config.read(self.config_file)

                self.url = self.config['COMMON']['URL']

                self.pushover_user_key = self.config['PUSHOVER']['USER_KEY']
                self.pushover_token_api = self.config['PUSHOVER']['TOKEN_API']
                self.pushover_sound = self.config['PUSHOVER']['SOUND']

            except KeyError:
                logging.error(
                    "Can't get keys from INI file. "
                    "Please check for mistakes."
                )

                sys.exit()

        except IOError or FileNotFoundError:
            logging.error(
                f"Can't open file {self.config_file}, "
                f"creating example INI file."
            )

            shutil.copyfile('/app/external_IP_checker.ini.example',
                            '/config/external_IP_checker.ini.example')
            sys.exit()

    def run(self):

        # Setting for PushOver
        self.appPushover = Application(self.pushover_token_api)
        self.userPushover = self.appPushover.get_user(self.pushover_user_key)

        # Get current External IP
        externalIP = get('https://api.ipify.org').text

        # Get all A records
        resolver = dns.resolver.Resolver()
        answers = resolver.resolve(self.url, 'A')
        for answer in answers:
            if answer.to_text() != externalIP:
                self.message = self.userPushover.send_message(
                    message=f'URL = {self.url}\n'
                    f'External IP = {externalIP}\n'
                    f'A-record = {answer.to_text()}', sound=self.pushover_sound
                )

                logging.error(
                    f'Mismatch!'
                    f' - URL = {self.url}'
                    f' - External IP = {externalIP}'
                    f' - A-record = {answer.to_text()}'
                )
            else:
                logging.info(
                    f'Matches!'
                    f' - URL = {self.url}'
                    f' - External IP = {externalIP}'
                    f' - A-record = {answer.to_text()}'
                )


if __name__ == '__main__':

    EIC = External_IP_Checker()
    EIC.run()
    EIC = None
