from datetime import datetime, timezone
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
        resource_id, url
        try:
            resource_id = resource["id"]
            url = f"{url}/{resource_type}/{resource_id}"
        except:
            resource_id = None
            url = f"{url}/{resource_type}"
        self.logger.info(f"Uploading {url} - {resource_type} with id {resource_id}")
        try:
            error = self.http_client.put(url, resource)
            if(error):
                return error
            else:
                # Generate provenance for the resource
                if(resource_type in ["Bundle", "DocumentReference", "Library"]):    
                    provenance = self.generate_provenance(resource, url)
                    self.write_fhir_resource_to_server(provenance, url)
        except:
            pass
        
    
    def get_fhir_all_resource_type_from_server(self, url, resource_type, all_entries = []):
        url = f"{url}/{resource_type}"
        self.logger.info(f"Getting {url}...")
        try:
            response = self.http_client.get(url)
            if(response):
                all_entries.extend(response["entry"])  # Append the entries to the accumulated list
                if(response["link"]):
                    if(response["link"][1]["relation"] == "next"):
                        return self.get_fhir_all_resource_type_from_server(response["link"][1]["url"], resource_type, all_entries)  # Return the recursive call
        except:
            pass
        print(len(all_entries))  # Use len() instead of __len__()
        return all_entries

    def generate_provenance(self, resource, source_server):
        provenance = {
            "resourceType": "Provenance",
            "target": [
                {
                    "reference": f"{source_server}/{resource['resourceType']}/{resource['id']}"
                }
            ],
            "recorded": datetime.now(timezone.utc).isoformat(),
            "agent": [
                {
                    "type": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                                "code": "source"
                            }
                        ]
                    },
                    "who": source_server,
                    "onBehalfOf": {
                        "reference": "Organization/1"
                    }
                }
            ]
        }
        return provenance