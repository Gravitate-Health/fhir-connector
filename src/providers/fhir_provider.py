from utils.http_client import HttpClient
import logging


class FhirProvider:
    def __init__(self) -> None:
        logging.getLogger("requests").setLevel(logging.INFO)
        logging.getLogger("urllib3").setLevel(logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.http_client = HttpClient()

    def separate_bundle_into_resources(self, bundle) -> list:
        """separate_bundle_into_resources
        Args:
            bundle (_type_): FHIR Bundle
        Raises:
            Exception: If bundle is not a valid value
        Returns:
            resources (list): List of resources contained in the bundle
        """
        if not bundle:
            raise Exception(
                "No resource types were provided to separate_bundle_into_resources()"
            )

        entries = bundle["entry"]

        # Iterate over entries in bundle
        resources = []
        for resource_entry in entries:
            try:
                resource = resource_entry["resource"]
            except:
                pass
            resources.append(resource)
        resources.append(bundle) # This is because the bundle is not included in the entries
        return resources

    def write_fhir_resource_to_server(self, resource, url):
        resource_type = resource["resourceType"]
        resource_id = resource["id"]
        url = f"{url}/{resource_type}/{resource_id}"
        self.logger.info(f"Uploading {url} - {resource_type} with id {resource_id}")
        try:
            error = self.http_client.put(url, resource)
            if(error):
                return error
        except:
            pass
    
    def get_fhir_all_resource_type_from_server(self, url, resource_type):
        url = f"{url}/{resource_type}"
        self.logger.info(f"Getting {url}...")
        try:
            response = self.http_client.get(url)
            if(response):
                return response
        except:
            pass
        
        
        
            
