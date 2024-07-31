from datetime import datetime, timezone
import os
from utils.http_client import HttpClient
import logging

class FhirProvider:
    def __init__(self, server_url) -> None:
        logging.getLogger("requests").setLevel(logging.INFO)
        logging.getLogger("urllib3").setLevel(logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.http_client = HttpClient()
        
        self.server_url = server_url

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

    def get_resource_by_id(self, resource_type, resource_id):
        url = f"{self.server_url}/{resource_type}/{resource_id}"
        #self.logger.info(f"Getting {resource_type} with id {resource_id} from {url}")
        response = None
        try:
            response = self.http_client.get(url)
        except:
            pass
        return response

    def generate_new_version(self, resource):
        newVersion = int(resource["meta"]["versionId"]) + 1
        if (resource["meta"] == None):
            resource["meta"] = {}
        resource["meta"]["versionId"] = str(newVersion)
        resource["meta"]["lastUpdated"] = datetime.now(timezone.utc).isoformat()
        return resource

    def write_fhir_resource_to_server(self, resource, source_server = ""):
        resource_type = resource["resourceType"]
        #self.logger.info(f"Writing resource of type {resource_type} to server.")
        url = self.server_url
        
        # Before writing the resource, try to get it from the server
        # If it exists, we will update it, if not, we will create it
        
        # First try to retrieve the resource
        try:
            if(resource_type == "Provenance"):
                resource_retrieved = self.get_provenance_object(resource["target"][0]["reference"])
            else:
                resource_retrieved = self.get_resource_by_id(resource_type, resource["id"])
        except:
            resource_retrieved = None
        try:
            original_version = int(resource_retrieved["meta"]["versionId"])
        except:
            original_version = 0
        #print(resource_retrieved)
        if (resource_retrieved != None):
            # If resource existed
            if (resource_retrieved != resource):
                # And it's different, create new version if it is different fom before
                resource = self.generate_new_version(resource)
                pass
            else:
                # If nothing changed, do nothing
                return
        # If resource did not exist, create        
        #self.logger.debug(f"Trying to write {resource_type} to {url}")
        errors = []
        try:
            new_version = int(resource["meta"]["versionId"])
        except:
            new_version = 1
        try:
            resource_id = resource["id"]
            url = f"{url}/{resource_type}/{resource_id}"
        except:
            resource_id = None
            url = f"{url}/{resource_type}"
        #self.logger.info(f"Uploading {resource_type} with id {resource_id}")
        
        # PUT resource to server
        response = None
        try:
            response, error = self.http_client.put(url, resource)
        except Exception as e:
            print(e)
        status_code = response.status_code
        if(error and len(error) > 0):
            errors.append(error)
            return errors
        
        # Generate provenance for the resource
        #print("original_version: ", original_version)
        #print("new_version: ", new_version)
        if(resource_type in ["Bundle", "DocumentReference", "Library"]):
            if (status_code == 200):
                # Nothing happpened
                pass
            elif (status_code == 201):
                # Created
                pass
            elif (status_code == 204):
                # Don't know
                pass
            else:
                # Error
                pass
            #if (new_version == 1 or new_version > original_version ):
                # Generate provenance only if resource is new or if a new version was created
            try:
                provenance = self.generate_provenance(resource_retrieved, resource, source_server)
            except Exception as e:
                self.logger.error(e)
            try:
                target = provenance["target"][0]["reference"]
                provenance_response, provenance_errors = self.handle_provenance(provenance, target)
                if (len(provenance_errors) > 0):
                    errors.extend(provenance_errors)
            except Exception as e:
                self.logger.error(e)
        return errors
    
    def get_fhir_all_resource_type_from_server(self, resource_type, url = "",all_entries = [], limit = 100000):
        if (limit == 0):
            limit = 100000
        #self.logger.info(f"Getting resourceType {resource_type} from server. Limit: {limit} urL: {url}")
        if url == "":
            url = f"{self.server_url}/{resource_type}?_count={limit}"
        #self.logger.info(f"Getting {url}...")
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
                        return self.get_fhir_all_resource_type_from_server(resource_type=resource_type, url=link[1]["url"], all_entries=all_entries)  # Return the recursive call
        except:
            pass
        self.logger.info(f"Got a total of {len(all_entries)} {resource_type} from {self.server_url}")  # Use len() instead of __len__()
        return all_entries

    def delete_fhir_resource_from_server(self, resource):
        url = self.server_url
        self.logger.info(f"Deleting {resource['resourceType']} with id {resource['id']} from {url}")
        location = f"{url}/{resource['resourceType']}/{resource['id']}"
        try:
            response = self.http_client.delete(location)
        except:
            self.logger.error(f"Error deleting resource from server: {location}")
            pass
        return response

    def get_provenance_object(self, target):
        url = f"{self.server_url}/Provenance?target={target}"
        self.logger.debug(f"Getting Provenance from {url}")
        try:
            response = self.http_client.get(url)
        except:
            pass
        return response

    def handle_provenance(self, provenance, target = ""):
        url = self.server_url + "/Provenance"
        # Before writing the resource, try to get it from the server
        # If it exists, we will update it, if not, we will create it
        
        # First try to retrieve the resource
        searchset = self.get_provenance_object(target)
        provenances_retrieved = []
        if (searchset["total"] == 0):
            self.logger.info(f"No provenance found for target {target}")
        else:
            provenances_retrieved = searchset["entry"]
            if (len(provenances_retrieved) > 0):
                self.logger.info(f"PROVENANCE: Found {len(provenances_retrieved)} provenances for target {target}. Not creating provenance")
        
        errors = []
        response = None
        if (len(provenances_retrieved) > 0):
            return response, errors
        try:
            response, error = self.http_client.post(url, provenance)
        except:
            pass
        status_code = response.status_code
        if(error):
            errors.append(error)
        return response, errors


    def generate_provenance(self, resource_retrieved, resource, source_server = ""):
        self.logger.debug(f"Generating provenance for {resource['resourceType']} with id {resource['id']}")
        try:
            resource_id = resource["id"]
        except:
            self.logger.warning(f"Resource {resource['resourceType']} does not have an id")
            resource_id = None
        version = {resource['meta']['versionId']}
        if (version == None or version == 0):
            version = 1
        provenance = {
            "resourceType": "Provenance",
            "target": [
                {
                    "reference": f"{self.server_url}/{resource['resourceType']}/{resource['id']}/_history/{version}"
                }
            ],
            "recorded": datetime.now(timezone.utc).isoformat(),
            "activity": {
                "coding" : [{
                "system" : "http://terminology.hl7.org/CodeSystem/iso-21089-lifecycle",
                "code" : "originate",
                "display" : "Originate/Retain Record Lifecycle Event"
                }]
            },
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
            ],
            "entity" : [{
                "role" : "source",
                "what" : {
                "reference" : f"{source_server}/{resource['resourceType']}/{resource_id}/_history/{resource['meta']['versionId']}"
                }
            }]
        }
        return provenance
    
    def delete_all_resource_type_from_server(self, resource_type):
        url = self.server_url
        self.logger.info(f"Deleting all {resource_type} from {url}")
        
        entries = self.get_fhir_all_resource_type_from_server(url, resource_type)
        for entry in entries:
            self.delete_fhir_resource_from_server(entry["resource"], url)
        try:
            response = self.http_client.delete(url)
        except:
            pass
        return response

    def generic_search(self, query):
        url = f"{self.server_url}"
        self.logger.info(f"Searching {url}... with query {query}")
        try:
            response, errors = self.http_client.post(url, query)
        except:
            pass
        return response