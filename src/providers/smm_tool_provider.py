import json
import logging
from utils.http_client import HttpClient

class SmmToolProvider:
    
    def __init__(self, server_url, object_storage_url, app_id, table_id, api_key) -> None:
        logging.getLogger('git').setLevel(logging.INFO)
        logger = logging.getLogger(__name__)
        self.logger = logger
        self.http_client = HttpClient()
        
        self.bucket_storage_url = object_storage_url
        
        self.server_url = server_url
        self.app_id = app_id
        self.table_id = table_id
        self.api_key = api_key
    
    def get_all_smm(self):
        #self.logger.info(f"Getting all SMM from {self.server_url}")
        try:
            rows_url = f"{self.server_url}/api/public/v1/tables/{self.table_id}/rows/search"
            headers = {
                "x-budibase-app-id": self.app_id,
                "x-budibase-api-key": self.api_key,
            }
            response, errors = self.http_client.post(url=rows_url, headers=headers, body={})
            
            # Verify if response is None
            if response is None:
                error_msg = f"No response received from server. Errors: {errors}"
                self.logger.error(f"Error getting SMM: {error_msg}")
                return None, error_msg
            
            if response.status_code not in [200, 201]:
                error_msg = f"HTTP {response.status_code} error from server"
                self.logger.error(f"Error getting SMM: {error_msg}")
                return None, error_msg
                
            return response.json()["data"], errors
        except Exception as e:
            self.logger.error(f"Error getting SMM: {e}")
            return None, str(e)

    def get_row_by_id(self, table_id, row_id):
        #self.logger.info(f"Getting row {row_id} from table {table_id} from {self.server_url}")
        try:
            row_url = f"{self.server_url}/api/public/v1/tables/{table_id}/rows/{row_id}"
            headers = {
                "x-budibase-app-id": self.app_id,
                "x-budibase-api-key": self.api_key,
            }
            response, errors = self.http_client.get(url=row_url, headers=headers)
            
            # Verificar si response es None
            if response is None:
                error_msg = f"No response received from server. Errors: {errors}"
                self.logger.error(f"Error getting row: {error_msg}")
                return None, error_msg
            
            if response.status_code not in [200, 201]:
                error_msg = f"HTTP {response.status_code} error from server"
                self.logger.error(f"Error getting row: {error_msg}")
                return None, error_msg
                
            return response.json()["data"], errors
        except Exception as e:
            self.logger.error(f"Error getting row: {e}")
            return None, str(e)
    
    def get_file_from_budibase(self, file_endpoint):
        #self.logger.info(f"Getting file from Budibase {file_endpoint}")
        try:
            headers = {
                "x-budibase-app-id": self.app_id,
                "x-budibase-api-key": self.api_key,
            }
            response, errors = self.http_client.get(url=f"{self.server_url}{file_endpoint}", headers=headers)
            
            # Verificar si response es None
            if response is None:
                error_msg = f"No response received from server. Errors: {errors}"
                self.logger.error(f"Error getting file from Budibase: {error_msg}")
                return None, error_msg
            
            return response, errors
        except Exception as e:
            self.logger.error(f"Error getting file from Budibase: {e}")
            return None, str(e)
    
    def create_object_in_bucket(self, file, file_info):
        self.logger.info(f"Creating object {file_info['resourceName']} in object storage")
        try:
            files = {"file": (file_info["resourceName"], file, 'application/pdf'), "fileInfo": (None, json.dumps(file_info), 'application/json')}
            response, errors = self.http_client.post_form_data(url=self.bucket_storage_url + "/create", files=files, data=file_info)
            return response, errors
        except Exception as e:
            self.logger.error(f"Error creating object in bucket: {e}")
            return None, str(e)