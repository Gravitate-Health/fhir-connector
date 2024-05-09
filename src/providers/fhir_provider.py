from datetime import datetime, timezone
import os
from utils.http_client import HttpClient
import logging

DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")

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

    def write_fhir_resource_to_server(self, resource, url, method = "PUT"):
        self.logger.info("------------- New resource to write to server -------------")
        resource_type = resource["resourceType"]        
        self.logger.debug(f"Trying to write {resource_type} to {url}")
        
        errors = []
        try:
            resource_id = resource["id"]
            url = f"{url}/{resource_type}/{resource_id}"
        except:
            resource_id = None
            url = f"{url}/{resource_type}"
        self.logger.info(f"Uploading {resource_type} with id {resource_id}")
        try:
            if method == "PUT":
                error = self.http_client.put(url, resource)
            elif method == "POST":
                error = self.http_client.post(url, resource)
            if(error):
                errors.append(error)
            else:
                # Generate provenance for the resource
                if(resource_type in ["Bundle", "DocumentReference", "Library"]):
                    provenance = self.generate_provenance(resource, DESTINATION_SERVER)
                    errors.append(self.write_fhir_resource_to_server(provenance, DESTINATION_SERVER, "POST"))
        except:
            pass
        return errors
        
    
    def get_fhir_all_resource_type_from_server(self, url, resource_type, all_entries = [], limit = 100000):
        url = f"{url}/{resource_type}"
        self.logger.info(f"Getting {url}...")
        try:
            response = self.http_client.get(url)
            link = response["link"]
            entries = response["entry"]
            if(response):
                all_entries.extend(entries)  # Append the entries to the accumulated list
                limit -= len(entries)  # Decrement the limit by the number of entries
                if(limit <= 0):  # If the limit is less than or equal to 0, return the accumulated list
                    self.logger.debug(f"Got a total of {len(all_entries)} entries from FHIR server")  # Use len() instead of __len__()
                    return all_entries
                if(link):
                    if(link[1]["relation"] == "next"):
                        return self.get_fhir_all_resource_type_from_server(link[1]["url"], resource_type, all_entries)  # Return the recursive call
        except:
            pass
        self.logger.info(f"Got a total of {len(all_entries)} entries from FHIR server")  # Use len() instead of __len__()
        return all_entries

    def generate_provenance(self, resource, source_server):
        self.logger.info(f"Generating provenance for {resource['resourceType']} with id {resource['id']}")
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
                                "code": "author",
                                "display": "Author",
                            }
                        ],
                        "text": "Author",
                    },
                    "who": "Gravitate-Health-connector",
                    "onBehalfOf": {
                        "reference": "Organization/1"
                    }
                }
            ]
        }
        #print(provenance)
        return provenance