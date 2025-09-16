from datetime import datetime, timezone
import os, providers.fhir_provider
import utils.mail_client
import logging


LIMIT = os.getenv("MODE_HAPI_FHIR_SERVER_SYNC_LIMIT") or 0 
logger = logging.getLogger(__name__)


def connector_fhir_server_sync(mail_client: utils.mail_client.Mail_client):

    MODE_HAPI_FHIR_SERVER_SYNC_RESOURCES = os.getenv("MODE_HAPI_FHIR_SERVER_SYNC_RESOURCES").strip("][").split(", ")
    
    MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER = os.getenv("MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER")
    DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")
    fhir_provider_source = providers.fhir_provider.FhirProvider(MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER)
    fhir_provider_destination = providers.fhir_provider.FhirProvider(DESTINATION_SERVER)

    errors = []
    for resource_type in MODE_HAPI_FHIR_SERVER_SYNC_RESOURCES:
        logger.info(f"-------------------------------- Retrieving {resource_type} --------------------------------")
        
        if (LIMIT):
            resources = fhir_provider_source.get_fhir_all_resource_type_from_server(resource_type, limit=LIMIT)
        else:
            resources = fhir_provider_source.get_fhir_all_resource_type_from_server(resource_type)
        if(resources != None):
            for resource in resources:
                logger.info("-------------------------------- Resource --------------------------------")
                error = fhir_provider_destination.write_fhir_resource_to_server(resource["resource"], MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER)
                if(error):
                    errors.append(error)
            fhir_provider_destination.run_reindex_job()
        else:
            logger.warn("No resources found")

    if (mail_client != None):
        if errors:
            logger.info("Errors found, sending email")
            mail_client.create_message(errors)
            logger.info("Email sent")
    return resources, errors
