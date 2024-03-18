from datetime import datetime, timezone
import os, providers.fhir_provider
import utils.mail_client


def connector_fhir_server_sync(mail_client: utils.mail_client.Mail_client):

    MODE_FHIR_SERVER_SYNC_SOURCE_SERVER = os.getenv(
        "MODE_FHIR_SERVER_SYNC_SOURCE_SERVER"
    )
    MODE_FHIR_SERVER_SYNC_RESOURCES = os.getenv("MODE_FHIR_SERVER_SYNC_RESOURCES")

    fhir_provider = providers.fhir_provider.FhirProvider()

    for resource_type in MODE_FHIR_SERVER_SYNC_RESOURCES:
        resources = fhir_provider.get_fhir_all_resource_type_from_server(
            MODE_FHIR_SERVER_SYNC_SOURCE_SERVER, resource_type
        )
        for resource in resources:
            fhir_provider.write_fhir_resource_to_server(
                resource,
            )

        errors = {}

    mail_client.create_message(errors)
    print("Email sent")
    return
