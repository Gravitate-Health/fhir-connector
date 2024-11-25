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
        
        session.cache_disabled = True
        return session

    def __print_response_hook__(
        self, request: requests.Response, *args, **kwargs
    ) -> None:
        id = ""
        if(request.encoding == None):
            request.encoding = 'utf-8'
        try:
            if (request.json() != None):
                resource_type = request.json()["resourceType"]
                id = request.json()["id"]
        except:
            resource_type = ""
        self.logger.info(
            f" {request.status_code} {request.request.method} {resource_type} {id} ({request.url})"
        )

    def get(self, url, headers = {'Cache-Control': 'no-cache'}):
        #self.logger.info(f"GET {url}")
        errors = []
        try:
            response = self.http_session.get(url, timeout=self.timeout, headers = headers)
        except Exception as error:
            self.logger.error(error)
            self.logger.error(f"[HTTP ERROR] Error in GET to: {url}")
            return response, [error]
        if response.status_code not in [200, 201]:
            #self.logger.error(f"Unsuccessful GET request for {url}" )
            errors = self.parse_issues(url, response)
            return response, errors
        return response, errors

    def put(self, url, body):
        self.logger.info(f"PUT {url}")
        errors = []
        try:
            response = self.http_session.put(url, json=body, headers = {'Cache-Control': 'no-cache'})
        except Exception as error:
            self.logger.error(error)
            self.logger.error(
                f"[HTTP ERROR] Error in PUT {body['resourceType']} with id {body['id']} to: {url}"
            )
            return response, [error]
        if response.status_code not in [200, 201]:
            #self.logger.error(f"Unsuccessful PUT request for {body['resourceType']}" )
            errors = self.parse_issues(body, response)
        return response, errors

    def post(self, url, body = {}, headers = {'Cache-Control': 'no-cache'}):
        #self.logger.info(f"POST {url}")
        errors = []
        try:
            response = self.http_session.post(url, json=body, headers = headers)
        except Exception as error:
            self.logger.error(error)
            self.logger.error(
                f"[HTTP ERROR] Error in POST {body['resourceType']} with id {body['id']} to: {url}"
            )
            return response, [error]
        if response.status_code not in [200, 201]:
            #self.logger.error(f"Unsuccessful POST request for {body['resourceType']}" )
            errors = self.parse_issues(body, response)
        return response, errors

    def post_form_data(self, url, data, files, body = {}):
        #self.logger.info(f"POST form-data {url}")
        errors = []
        try:
            response = self.http_session.post(url, data=data, files=files, json=body)
        except Exception as error:
            self.logger.error(error)
            self.logger.error(f"[HTTP ERROR] Error in POST form-data to: {url}")
            return response, [error]
        if response.status_code not in [200, 201]:
            #self.logger.error(f"Unsuccessful POST request for {url}" )
            errors = self.parse_issues(url, response)
        return response, errors

    def delete(self, url):
        #self.logger.info(f"DELETE {url}")
        errors = []
        try:
            response = self.http_session.delete(url, headers = {'Cache-Control': 'no-cache'})
        except Exception as error:
            self.logger.error(error)
            self.logger.error(f"[HTTP ERROR] Error in DELETE to: {url}")
            return response, [error]
        if response.status_code not in [200, 201]:
            #self.logger.error(f"Unsuccessful DELETE request for {url}" )
            errors = self.parse_issues(url, response)
        return response, errors

    def parse_issues(self, resource, response):
        errors = []
        status_code = response.status_code
        issue_list = response.json()["issue"]
        for issue in issue_list:
            resource_id = resource["id"]
            resource_type = resource["resourceType"]
            issue_severity = issue["severity"].upper()
            issue_diagnostic = issue["diagnostics"]
            self.logger.warning(
                f"{issue_severity}: {resource_type} with id {resource_id} || Status_code {status_code} || Reason: {issue_diagnostic}"
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
            errors.append(error_object)
        return errors