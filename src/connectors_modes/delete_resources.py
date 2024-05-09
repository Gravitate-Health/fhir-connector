import os, datetime, json
from datetime import datetime, timezone

import providers.hl7_git_provider
import utils.mail_client

fhir_provider = providers.fhir_provider.FhirProvider()

def connector_delete_resources(mail_client: utils.mail_client.Mail_client):
    DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")
    
    types = os.getenv("DELETE_RESOURCES_TYPES").strip("][").split(", ")
    
    for resource_type in types:
        print(f"Deleting {resource_type} resources")
        resources = fhir_provider.get_fhir_all_resource_type_from_server(
            DESTINATION_SERVER, resource_type
        )
        if(resources != None):
            for resource in resources:
                errors = fhir_provider.delete_fhir_resource_from_server(
                    resource["resource"], DESTINATION_SERVER
                )
        else:
            print("No resources found")