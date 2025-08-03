import urllib3
import logging

TOKEN_HEADER = "Auth-API-Token"
HETZNER_API_URL = "https://dns.hetzner.com/api/v1"

logger = logging.getLogger(__name__)


class Hetzner:
    def __init__(self, token: str):
        logger.debug("initializing Hetzner")
        self.pool = urllib3.PoolManager()
        self.token = token
        self.created_records = {}

    def _do_request(
        self, endpoint: str, payload=None, method="GET", err_msg="bad response"
    ) -> urllib3.response:
        url = f"{HETZNER_API_URL}/{endpoint}"
        logger.debug(f"Doing request to {url}")

        if method == "POST" and payload:
            logger.debug("Posting ...")
            res = self.pool.request(
                method,
                url,
                json=payload,
                headers={"Content-Type": "application/json", TOKEN_HEADER: self.token},
            )
        else:
            logger.debug("Getting ...")
            res = self.pool.request(method, url, headers={TOKEN_HEADER: self.token})

        logger.debug("Done!")
        if res.status != 200:
            raise ValueError(f"{err_msg}: status {res.status}")
        return res

    def _get_zone_id(self, zone: str):
        logger.info(f"Getting id for zone {zone}")
        res = self._do_request(f"zones?name={zone}", err_msg=f"zone not found {zone}")
        body = res.json()

        zoneInfo = body["zones"][0]
        logger.info(f"Id of zone is {zoneInfo["id"]}")

        return zoneInfo["id"]

    @staticmethod
    def zone_from_domain(domain: str) -> str:
        parts = domain.split(".")
        return parts[-2] + "." + parts[-1]

    def create_txt_record(self, domain: str, value: str, ttl: int = 60) -> None:
        zone = Hetzner.zone_from_domain(domain)
        zone_id = self._get_zone_id(zone)

        req_body = {
            "zone_id": zone_id,
            "type": "TXT",
            "name": domain[: len(domain) - len(zone) - 1],
            "value": value,
            "ttl": ttl,
        }
        logger.info(
            f"Requesting TXT record with name {
                req_body['name']} value {req_body['value']}"
        )

        res = self._do_request(
            "records",
            method="POST",
            payload=req_body,
            err_msg=f"could not create record: {domain}",
        )
        body = res.json()

        record_id = body["record"]["id"]
        self.created_records[domain] = record_id

        logger.info(f"Created record with id {record_id}")

    def delete_txt_record(self, domain: str) -> None:
        logger.debug(f"requesting to delete record for domain {domain}")

        record_id = self.created_records.get(domain)
        if not record_id:
            raise ValueError(f"client never created a record for {domain}")

        self._do_request(
            f"records/{record_id}",
            method="DELETE",
            err_msg=f"record could not be deleted: {domain}",
        )
