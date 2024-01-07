# Name: Check IP based on previous value
# Coder: Marco Janssen (mastodon @marc0janssen@mastodon.online)
# date: 2021-11-21 11:57:46
# update: 2024-01-07 13:52:00

from requests import get
import logging
import configparser
import shutil
import sys
import ipaddress
from chump import Application


class External_IP_Checker():
    def __init__(self):

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)

        self.config_file = "/config/check_ip_based_on_previous_value.ini"
        self.saved_ip = "/config/saved_ip.txt"

        try:
            with open(self.config_file, "r") as f:
                f.close()
            try:
                self.config = configparser.ConfigParser()
                self.config.read(self.config_file)

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

            shutil.copyfile(
                '/app/check_ip_based_on_previous_value.ini.example',
                '/config/check_ip_based_on_previous_value.ini.example'
                )
            sys.exit()

    def is_valid_ip(self, address):
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    def run(self):

        # Setting for PushOver
        self.appPushover = Application(self.pushover_token_api)
        self.userPushover = self.appPushover.get_user(self.pushover_user_key)

        # Get current External IP
        externalIP = get('https://api.ipify.org').text

        if self.is_valid_ip(externalIP):

            # Get saved External IP
            try:
                with open(self.saved_ip, 'r') as file:
                    savedIP = file.readline().rstrip('\n')

            except IOError or FileNotFoundError:

                savedIP = externalIP

                try:
                    # Open a file in write mode
                    file = open(self.saved_ip, "w")

                    # Write data to the file
                    file.write(externalIP)

                    # Close the file
                    file.close()

                    self.message = self.userPushover.send_message(
                        message=f'External IP has been saved!!\n'
                        f'Current IP = {externalIP}\n',
                        sound=self.pushover_sound
                    )
                    logging.info("External IP saved successfully.")

                except IOError:
                    logging.error("An error occurred while saving the file.")
                    sys.exit()

            if savedIP != externalIP:
                self.message = self.userPushover.send_message(
                    message=f'External IP has changed!!\n'
                    f'Previous IP = {savedIP}\n'
                    f'Current IP = {externalIP}\n', sound=self.pushover_sound
                )

                logging.error(
                    f'Mismatch!'
                    f' - Previous IP = {savedIP}'
                    f' - Current IP = {externalIP}'
                )
            else:
                logging.info(
                    f'Mismatch!'
                    f' - Previous IP = {savedIP}'
                    f' - Current IP = {externalIP}'
                )
        else:
            logging.error(
                'Web service dit not responsed with IP address!'
            )


if __name__ == '__main__':

    EIC = External_IP_Checker()
    EIC.run()
    EIC = None
