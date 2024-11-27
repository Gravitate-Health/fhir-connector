import base64
import os, datetime, json
from datetime import datetime, timezone
import copy
import requests

import providers.smm_tool_provider
import providers.fhir_provider
import utils.mail_client


def connector_smm_tool(mail_client: utils.mail_client.Mail_client):
    smm_server_url = os.getenv("SMM_SERVER_URL")
    object_storage_url = os.getenv("OBJECT_STORAGE_URL")
    smm_app_id = os.getenv("SMM_APP_ID")
    smm_table_id = os.getenv("SMM_TABLE_ID")
    smm_api_key = os.getenv("SMM_API_KEY")
    smm_tool_provider = providers.smm_tool_provider.SmmToolProvider(smm_server_url, object_storage_url, smm_app_id, smm_table_id, smm_api_key)
    
    DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")
    fhir_provider = providers.fhir_provider.FhirProvider(DESTINATION_SERVER)
    

    ## TODO de-hardcode this
    smm_resources, errors = smm_tool_provider.get_all_smm()
    if smm_resources is None:
        mail_client.create_message(errors)
        print("Error occurred, email sent")
        return

    smm_fhir_resources = []
    for resource in smm_resources:
        print("____________________ NEW RESOURCE _______________________")
        fhir_resource = {}
        fhir_resource["id"] = resource["_id"].replace("_", "")[0:63]
        fhir_resource["resourceType"] = "DocumentReference"
        fhir_resource["status"] = "current"
        fhir_resource["docStatus"] = "final"
        fhir_resource["description"] = resource["description"]
        
        try:
            if resource["subject"] != None:
                subject_row_id = resource["subject"][0]["_id"]
                subject_table_split = subject_row_id.split("_")
                subject_tabe_id = f"{subject_table_split[1]}_{subject_table_split[2]}"
                subject, subject_errors = smm_tool_provider.get_row_by_id(subject_tabe_id, subject_row_id)
                fhir_resource["subject"] = {
                    "display": subject["Display"],
                    "reference": subject["Reference"]
                }
        except Exception as e:
            print(f"Error getting subject: {e}")
            pass
        # TODO: Ignore Author for now. Change in future
        #try:
        #    fhir_resource["author"] = {
        #        "reference": resource["author"][0]["primaryDisplay"],
        #        "display": resource["author"][0]["primaryDisplay"]
        #    }
        #except:
        #    pass
        fhir_resource["content"] = [
            {
                "attachment": {
                    "contentType": "",
                    "language": "",
                    "url": ""
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
            content_counter = 0
            for content in resource["contentData"]:
                try:
                    if(content_counter > 0):
                        fhir_resource["content"].append(copy.deepcopy(fhir_resource["content"][0]))
                    response, errors = smm_tool_provider.get_file_from_budibase(content["url"])
                    response.raise_for_status()
                    file_name = content["key"].split("/")[2]
                    response_create_object, errors = smm_tool_provider.create_object_in_bucket(response.content,{
                        "resourceName": file_name,
                        #"author": "X-Plain Patient Education",
                        "description" : fhir_resource["description"],
                            "attachment" : {
                                "contentType" : response.headers["Content-Type"], 
                                "language" : fhir_resource["content"][0]["attachment"]["language"], 
                                #"url" : "hello.com",  
                                #"size" : "", 
                                #"hash" : "ADE1234FE", 
                                #"title" : "How to take Xarelto", 
                                "creation" : datetime.now(timezone.utc).isoformat(),
                        }
                    })
                    fhir_resource["content"][content_counter]["attachment"]["url"] = f"{object_storage_url}/resource/{file_name}"
                    fhir_resource["content"][content_counter]["attachment"]["contentType"] = response.headers["Content-Type"].split(";")[0]
                except requests.RequestException as e:
                    print(f"Error fetching content from {resource['contentData'][content_counter]['url']}: {e}")
                content_counter += 1
        smm_fhir_resources.append(fhir_resource)

    for fhir_resource in smm_fhir_resources:
        error = fhir_provider.write_fhir_resource_to_server(fhir_resource, DESTINATION_SERVER)
    fhir_provider.run_reindex_job()
    mail_client.create_message(errors)
    return smm_fhir_resources, errors
