import os, datetime, json
from datetime import datetime, timezone

import providers.hl7_git_provider
import utils.mail_client


MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER = os.getenv("MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER")
DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")
fhir_provider = providers.fhir_provider.FhirProvider(DESTINATION_SERVER)

def connector_delete_resources(mail_client: utils.mail_client.Mail_client):
    
    types = os.getenv("DELETE_RESOURCES_TYPES").strip("][").split(", ")
    
    for resource_type in types:
        print(f"Deleting {resource_type} resources")
        resources = fhir_provider.get_fhir_all_resource_type_from_server(resource_type)
        if(resources != None):
            for resource in resources:
                errors = fhir_provider.delete_fhir_resource_from_server(resource["resource"])
        else:
            print("No resources found")