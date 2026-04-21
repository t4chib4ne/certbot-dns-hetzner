import urllib3
import logging

TOKEN_HEADER = "Authorization"
HETZNER_API_URL = "https://api.hetzner.cloud/v1"

logger = logging.getLogger(__name__)


class Hetzner:
    def __init__(self, token: str):
        logger.debug("initializing Hetzner")
        self.pool = urllib3.PoolManager()
        self.token = token
        self.created_records = {}

    def _do_request(
        self,
        endpoint: str,
        payload=None,
        method="GET",
        err_msg="bad response",
        expected_status=200,
    ) -> urllib3.response:
        url = f"{HETZNER_API_URL}/{endpoint}"
        logger.debug(f"Doing request to {url}")
        token_header_val = f"Bearer {self.token}"

        if method == "POST" and payload:
            logger.debug("Posting ...")
            res = self.pool.request(
                method,
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    TOKEN_HEADER: token_header_val,
                },
            )
        else:
            logger.debug("Getting ...")
            res = self.pool.request(
                method, url, headers={TOKEN_HEADER: token_header_val}
            )

        logger.debug("Done!")
        if res.status != expected_status:
            raise ValueError(
                f"{err_msg}: status={res.status} message={res.json()['error']['message']}"
            )
        return res

    @staticmethod
    def zone_from_domain(domain: str) -> str:
        parts = domain.split(".")
        return parts[-2] + "." + parts[-1]

    def create_txt_record(self, domain: str, value: str, ttl: int = 60) -> None:
        zone = Hetzner.zone_from_domain(domain)
        rrset_name = domain[: domain.rindex(zone) - 1]

        req_body = {
            "name": rrset_name,
            "type": "TXT",
            "ttl": ttl,
            "records": [
                {
                    "value": f'"{value}"',
                    "comment": "dns01 validation by certbot-dns-hetzner",
                }
            ],
            "labels": {},
        }

        logger.info(f"Creating TXT RRSet {rrset_name} with record {value}")

        res = self._do_request(
            f"zones/{zone}/rrsets",
            method="POST",
            payload=req_body,
            err_msg=f"could not create rrset: {domain}",
            expected_status=201,
        )
        rrset_id = res.json()["rrset"]["id"]
        self.created_records[domain] = rrset_name

        logger.info(f"Created rrset with id {rrset_id}")

    def delete_txt_record(self, domain: str) -> None:
        zone = Hetzner.zone_from_domain(domain)
        logger.debug(f"requesting to delete rrset for domain {domain}")

        rrset_name = self.created_records.get(domain)
        if not rrset_name:
            raise ValueError(f"client never created a rrset for {domain}")

        self._do_request(
            f"zones/{zone}/rrsets/{rrset_name}/TXT",
            method="DELETE",
            err_msg=f"record could not be deleted: {domain}",
            expected_status=201,
        )
