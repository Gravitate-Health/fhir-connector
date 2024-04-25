from datetime import datetime, timezone
import os, providers.fhir_provider
import utils.mail_client


def connector_fhir_server_sync(mail_client: utils.mail_client.Mail_client):

    MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER = os.getenv(
        "MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER"
    )
    MODE_HAPI_FHIR_SERVER_SYNC_RESOURCES = os.getenv("MODE_HAPI_FHIR_SERVER_SYNC_RESOURCES").strip("][").split(", ")
    DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")

    fhir_provider = providers.fhir_provider.FhirProvider()

    for resource_type in MODE_HAPI_FHIR_SERVER_SYNC_RESOURCES:
        resources = fhir_provider.get_fhir_all_resource_type_from_server(
            MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER, resource_type
        )
        if(resources != None):
            for resource in resources:
                fhir_provider.write_fhir_resource_to_server(
                    resource["resource"], DESTINATION_SERVER
                )
        else:
            print("No resources found")
        errors = {}

    mail_client.create_message(errors)
    print("Email sent")
    return resources
