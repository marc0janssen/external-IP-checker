# Name: Check IP based on previous value
# Coder: Marco Janssen (mastodon @marc0janssen@mastodon.green)
# date: 2021-11-21 11:57:46
# update: 2024-01-07 13:52:00

"""Monitor external IP changes and alert via Pushover on changes."""

from requests import get
import logging
import configparser
import shutil
import sys
import ipaddress
from typing import Optional
from chump import Application

logger = logging.getLogger(__name__)


class External_IP_Checker:
    """Monitor external IP and alert when it changes from saved value."""

    CONFIG_FILE = "/config/check_ip_based_on_previous_value.ini"
    EXAMPLE_FILE = "/app/check_ip_based_on_previous_value.ini.example"
    SAVED_IP_FILE = "/config/saved_ip.txt"
    API_URL = "https://api.ipify.org"
    REQUEST_TIMEOUT = 10

    def __init__(self) -> None:
        """Initialize the IP checker with configuration from INI file."""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)

        self.config: Optional[configparser.ConfigParser] = None
        self.pushover_user_key: Optional[str] = None
        self.pushover_token_api: Optional[str] = None
        self.pushover_sound: Optional[str] = None
        self.user_pushover: Optional[object] = None

        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from INI file."""
        try:
            # Check if config file exists
            with open(self.CONFIG_FILE, "r"):
                pass  # File exists, proceed
            try:
                self.config = configparser.ConfigParser()
                self.config.read(self.CONFIG_FILE)

                self.pushover_user_key = (
                    self.config['PUSHOVER']['USER_KEY']
                )
                self.pushover_token_api = (
                    self.config['PUSHOVER']['TOKEN_API']
                )
                self.pushover_sound = self.config['PUSHOVER']['SOUND']

            except KeyError as e:
                logger.error(
                    f"Missing key in INI file: {e}. "
                    "Please check for mistakes."
                )
                sys.exit(1)

        except (IOError, FileNotFoundError):
            logger.error(
                f"Can't open file {self.CONFIG_FILE}, "
                f"creating example INI file."
            )
            shutil.copyfile(
                self.EXAMPLE_FILE,
                f'{self.CONFIG_FILE}.example'
            )
            sys.exit(1)

    @staticmethod
    def is_valid_ip(address: str) -> bool:
        """Validate if address is a valid IPv4 or IPv6 address."""
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    def _read_saved_ip(self) -> Optional[str]:
        """Read saved IP from file, return None if file doesn't exist."""
        try:
            with open(self.SAVED_IP_FILE, 'r') as file:
                return file.readline().rstrip('\n')
        except (IOError, FileNotFoundError):
            return None

    def _save_ip(self, ip_address: str) -> bool:
        """Save IP address to file."""
        try:
            with open(self.SAVED_IP_FILE, "w") as file:
                file.write(ip_address)
            logger.info("External IP saved successfully.")
            return True
        except IOError as e:
            logger.error(f"An error occurred while saving the file: {e}")
            return False

    def run(self) -> None:
        """
        Check external IP and compare with saved value.

        Sends Pushover notification if IP has changed.
        """
        try:
            # Setup Pushover
            app_pushover = Application(self.pushover_token_api)
            self.user_pushover = app_pushover.get_user(
                self.pushover_user_key
            )

            # Get current External IP
            try:
                external_ip = get(
                    self.API_URL,
                    timeout=self.REQUEST_TIMEOUT
                ).text
            except Exception as e:
                logger.error(f"Failed to fetch external IP: {e}")
                return

            if not self.is_valid_ip(external_ip):
                logger.error(
                    'Web service did not respond with a valid IP address!'
                )
                return

            # Get saved External IP
            saved_ip = self._read_saved_ip()

            if saved_ip is None:
                # First time running, save the IP
                if self._save_ip(external_ip):
                    self.user_pushover.send_message(
                        message=(
                            f'External IP has been saved!\n'
                            f'Current IP = {external_ip}\n'
                        ),
                        sound=self.pushover_sound
                    )
                return

            # Compare with saved IP
            if saved_ip != external_ip:
                message = (
                    f'External IP has changed!\n'
                    f'Previous IP = {saved_ip}\n'
                    f'Current IP = {external_ip}\n'
                )
                self.user_pushover.send_message(
                    message=message,
                    sound=self.pushover_sound
                )
                logger.error(
                    f'Mismatch! - Previous IP = {saved_ip} '
                    f'- Current IP = {external_ip}'
                )
                # Update saved IP
                self._save_ip(external_ip)
            else:
                logger.info(
                    f'Match! - Previous IP = {saved_ip} '
                    f'- Current IP = {external_ip}'
                )

        except Exception as e:
            logger.error(f"Unexpected error in run: {e}", exc_info=True)


if __name__ == '__main__':
    try:
        checker = External_IP_Checker()
        checker.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
