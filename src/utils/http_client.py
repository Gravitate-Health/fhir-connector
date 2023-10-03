import requests
from requests.sessions import HTTPAdapter
from requests.adapters import Retry
import logging
from datetime import datetime, timezone


class HttpClient:
    timeout = 10

    def __init__(self) -> None:
        logging.getLogger("requests").setLevel(logging.INFO)
        logging.getLogger("urllib3").setLevel(logging.INFO)
        logger = logging.getLogger(__name__)

        self.logger = logger
        self.http_session = self.create_http_session()
        pass

    def create_http_session(self) -> requests.Session:
        session = requests.Session()
        retry_ = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adaptor = HTTPAdapter(max_retries=retry_)

        session.hooks["response"].append(self.__print_response_hook__)
        session.mount("https://", adaptor)
        return session

    def __print_response_hook__(
        self, request: requests.Response, *args, **kwargs
    ) -> None:
        self.logger.info(
            f" {request.status_code} on {request.request.method} {request.url}"
        )

    def get(self, url):
        response = self.http_session.get(url, timeout=self.timeout)
        return response.json()

    def put(self, url, body) -> None:
        try:
            response = requests.put(url, json=body)
        except Exception as error:
            self.logger.error(error)
            self.logger.error(
                f"[HTTP ERROR] Error loading {body['resourceType']} with id {body['id']} to: {url}"
            )
            return

        if response.status_code not in [200, 201]:
            issue_list = response.json()["issue"]
            for issue in issue_list:
                resource_id = body["id"]
                resource_type = body["resourceType"]
                issue_severity = issue["severity"].upper()
                issue_diagnostic = issue["diagnostics"]
                self.logger.warning(
                    f"{issue_severity}: {resource_type} with id {resource_id} || Status_code {response.status_code} || Reason: {issue_diagnostic}"
                )

                error_object = {
                    "operation": "http_put",
                    "date": datetime.now()
                    .astimezone(timezone.utc)
                    .strftime("%d/%m/%Y - %H:%M:%S %z"),
                    "status_code": response.status_code,
                    "severity": issue_severity,
                    "fhir_error": {
                        "resource_id": resource_id,
                        "resource_type": resource_type,
                        "diagnostic": issue_diagnostic,
                    },
                }
                return error_object
        return
