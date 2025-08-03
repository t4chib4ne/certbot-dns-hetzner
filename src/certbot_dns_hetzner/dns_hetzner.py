import logging
from typing import Callable

from .api_hetzner import Hetzner

from certbot.plugins import dns_common
from certbot.errors import PluginError


logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    """Hetzner DNS Authenticator
    Authentication Plugin for dns-01 Validation via Hetzner.
    """

    description = "Sets TXT records via Hetzner DNS API for obtaining certificates."

    def __init__(self, *args, **kwargs):
        logger.debug("Initializing Authenticator for Hetzner")
        super().__init__(*args, **kwargs)
        self.client = None

    @classmethod
    def add_parser_arguments(cls, add: Callable[..., None]) -> None:
        # Call super class to add propagation secords
        super().add_parser_arguments(add, default_propagation_seconds=300)

        # Add our own config
        add("tokenfile", help="path to the file containing the access token")

    def more_info(self):
        return "Uses the Hetzner DNS API to create a TXT record to fulfill "
        +"the dns-01 challenge."

    def _setup_credentials(self) -> None:
        tokenfile = self.conf("tokenfile")
        if tokenfile:
            with open(tokenfile, "r") as file:
                token = "".join(file.readlines()).replace("\n", "")
                logger.info("Loaded token from file!")
        else:
            token = input("Please enter your Hetzner Token: ")

        if not token:
            raise ValueError("invalid token")

        self.client = Hetzner(token)

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        try:
            self.client.create_txt_record(validation_name, validation)
        except Exception as e:
            raise PluginError(e)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        try:
            self.client.delete_txt_record(validation_name)
        except Exception as e:
            logger.error(f"dns-hetzner: failed to cleanup {domain}: {e}")
