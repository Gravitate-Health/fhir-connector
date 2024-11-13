import base64
import os, datetime, json
from datetime import datetime, timezone

import requests

import providers.smm_tool_provider
import providers.fhir_provider
import utils.mail_client


def connector_smm_tool(mail_client: utils.mail_client.Mail_client):
    smm_server_url = os.getenv("SMM_SERVER_URL")
    smm_app_id = os.getenv("SMM_APP_ID")
    smm_table_id = os.getenv("SMM_TABLE_ID")
    smm_api_key = os.getenv("SMM_API_KEY")
    smm_tool_provider = providers.smm_tool_provider.SmmToolProvider(smm_server_url, smm_app_id, smm_table_id, smm_api_key)
    
    DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")
    fhir_provider = providers.fhir_provider.FhirProvider(DESTINATION_SERVER)
    

    ## TODO de-hardcode this
    smm_resources, errors = smm_tool_provider.get_all_smm()
    if smm_resources is None:
        mail_client.create_message(errors)
        print("Error occurred, email sent")
        return

    smm_resources = smm_resources.json()["data"]
    smm_fhir_resources = []
    for resource in smm_resources:
        fhir_resource = {}
        fhir_resource["id"] = resource["_id"].replace("_", "")[0:63]
        fhir_resource["resourceType"] = "DocumentReference"
        fhir_resource["status"] = "current"
        fhir_resource["docStatus"] = "final"
        fhir_resource["description"] = resource["description"]
        #fhir_resource["subject"] = {
        #    "reference": resource["subject"],
        #    "display": resource["subject"]
        #}
        try:
            fhir_resource["author"] = {
                "reference": resource["author"][0]["primaryDisplay"],
                "display": resource["author"][0]["primaryDisplay"]
            }
        except:
            pass
        fhir_resource["content"] = [
            {
                "attachment": {
                }
            }
        ]
        try:
            fhir_resource["subject"] = {
                "display": resource["subject"][0]["primaryDisplay"],
                "reference": resource["subject"][0]["reference"]
            }
        except:
            pass
        try:
            fhir_resource["content"][0]["attachment"]["contentType"]= resource["contentMIMEtype"][0]["primaryDisplay"],
        except:
            pass
        fhir_resource["content"][0]["attachment"]["language"]= resource["language"][0]["primaryDisplay"],
        if (resource["isRemote"] == True):
            fhir_resource["content"][0]["attachment"]["url"] = resource["contentURL"]
        elif (resource["isRemote"] == False):
            try:
                response = requests.get(smm_tool_provider.server_url + resource["contentData"][0]["url"])
                response.raise_for_status()
                content_base64 = base64.b64encode(response.content).decode('utf-8')
                fhir_resource["content"][0]["attachment"]["data"] = content_base64
            except requests.RequestException as e:
                print(f"Error fetching content from {resource['contentData'][0]['url']}: {e}")

            #fhir_resource["content"][0]["attachment"]["data"] =         
        smm_fhir_resources.append(fhir_resource)

    for fhir_resource in smm_fhir_resources:
        error = fhir_provider.write_fhir_resource_to_server(fhir_resource, DESTINATION_SERVER)

    mail_client.create_message(errors)
    return smm_fhir_resources, errors
