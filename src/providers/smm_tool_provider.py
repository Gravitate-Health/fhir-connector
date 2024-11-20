import git
import logging
from utils.http_client import HttpClient

class SmmToolProvider:
    
    def __init__(self, server_url, app_id, table_id, api_key) -> None:
        logging.getLogger('git').setLevel(logging.INFO)
        logger = logging.getLogger(__name__)
        self.logger = logger
        self.http_client = HttpClient()
        
        self.server_url = server_url
        self.app_id = app_id
        self.table_id = table_id
        self.api_key = api_key
    
    def get_all_smm(self):
        self.logger.info(f"Getting all SMM from {self.server_url}")
        try:
            rows_url = f"{self.server_url}/api/public/v1/tables/{self.table_id}/rows/search"
            headers = {
                "x-budibase-app-id": self.app_id,
                "x-budibase-api-key": self.api_key,
            }
            response, errors = self.http_client.post(url=rows_url, headers=headers, body={})
            return response.json()["data"], errors
        except Exception as e:
            self.logger.error(f"Error getting SMM: {e}")
            return None, str(e)

    def get_row_by_id(self, table_id, row_id):
        self.logger.info(f"Getting row {row_id} from table {table_id} from {self.server_url}")
        try:
            row_url = f"{self.server_url}/api/public/v1/tables/{table_id}/rows/{row_id}"
            headers = {
                "x-budibase-app-id": self.app_id,
                "x-budibase-api-key": self.api_key,
            }
            response, errors = self.http_client.get(url=row_url, headers=headers)
            return response.json()["data"], errors
        except Exception as e:
            self.logger.error(f"Error getting row: {e}")
            return None, str(e)