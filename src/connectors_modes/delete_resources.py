import os
import logging

import providers.fhir_provider
import utils.mail_client

logger = logging.getLogger(__name__)
MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER = os.getenv("MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER")
DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")
fhir_provider = providers.fhir_provider.FhirProvider(DESTINATION_SERVER)

def connector_delete_resources(mail_client: utils.mail_client.Mail_client):
    
    types = os.getenv("DELETE_RESOURCES_TYPES").strip("][").split(", ")
    
    for resource_type in types:
        resources = fhir_provider.get_fhir_all_resource_type_from_server(resource_type)
        print(f"Deleting {len(resources)} {resource_type} resources")
        if(resources != None):
            for resource in resources:
                errors = fhir_provider.delete_fhir_resource_from_server(resource["resource"])
        else:
            print("No resources found")

def delete_all_resources(mail_client: utils.mail_client.Mail_client):

    response = fhir_provider.expunge_server()
    if (mail_client != None):
        logger.info("Expunge response:")
        logger.info(response)
        if response[0].status_code != 200:
            logger.info("Errors found, sending email")
            mail_client.create_message(response[0].json())
        logger.info("Email sent")
