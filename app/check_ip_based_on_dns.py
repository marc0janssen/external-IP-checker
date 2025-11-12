# Name: Check IP based on DNS
# Coder: Marco Janssen (twitter @marc0janssen)
# date: 2021-11-21 11:57:46
# update: 2024-01-07 13:52:00

"""Monitor external IP against DNS A-records and alert via Pushover."""

import dns.resolver
from requests import get
import logging
import configparser
import shutil
import sys
from typing import Optional
from chump import Application

logger = logging.getLogger(__name__)


class External_IP_Checker:
    """Check if external IP matches DNS A-records for a given domain."""

    CONFIG_FILE = "/config/check_ip_based_on_dns.ini"
    EXAMPLE_FILE = "/app/check_ip_based_on_dns.ini.example"
    API_URL = "https://api.ipify.org"
    REQUEST_TIMEOUT = 10

    def __init__(self) -> None:
        """Initialize the IP checker with configuration from INI file."""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)

        self.config: Optional[configparser.ConfigParser] = None
        self.url: Optional[str] = None
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

                self.url = self.config['COMMON']['URL']
                self.pushover_user_key = self.config['PUSHOVER']['USER_KEY']
                self.pushover_token_api = self.config['PUSHOVER']['TOKEN_API']
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
            shutil.copyfile(self.EXAMPLE_FILE,
                            f'{self.CONFIG_FILE}.example')
            sys.exit(1)

    def run(self) -> None:
        """
        Check external IP against DNS A-records.

        Sends Pushover notification if external IP doesn't match
        any A-record.
        """
        try:
            # Setup Pushover
            app_pushover = Application(self.pushover_token_api)
            self.user_pushover = app_pushover.get_user(self.pushover_user_key)

            # Get current External IP
            try:
                external_ip = get(
                    self.API_URL,
                    timeout=self.REQUEST_TIMEOUT
                ).text
            except Exception as e:
                logger.error(f"Failed to fetch external IP: {e}")
                return

            # Get all A records
            try:
                resolver = dns.resolver.Resolver()
                answers = resolver.resolve(self.url, 'A')
            except dns.resolver.NXDOMAIN:
                logger.error(f"Domain {self.url} does not exist")
                return
            except dns.resolver.NoAnswer:
                logger.error(f"No A records found for {self.url}")
                return
            except Exception as e:
                logger.error(f"DNS resolution failed: {e}")
                return

            # Check if external IP matches any A record
            matched = False
            for answer in answers:
                dns_ip = answer.to_text()
                if dns_ip == external_ip:
                    matched = True
                    logger.info(
                        f"Matches! - URL={self.url} "
                        f"- External IP={external_ip} - A-record={dns_ip}"
                    )
                    break

            if not matched:
                # Send notification for all mismatches
                for answer in answers:
                    dns_ip = answer.to_text()
                    message = (
                        f"URL = {self.url}\n"
                        f"External IP = {external_ip}\n"
                        f"A-record = {dns_ip}"
                    )
                    self.user_pushover.send_message(
                        message=message,
                        sound=self.pushover_sound
                    )
                    logger.error(
                        f"Mismatch! - URL={self.url} "
                        f"- External IP={external_ip} - A-record={dns_ip}"
                    )

        except Exception as e:
            logger.error(f"Unexpected error in run: {e}")


if __name__ == '__main__':
    try:
        checker = External_IP_Checker()
        checker.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
