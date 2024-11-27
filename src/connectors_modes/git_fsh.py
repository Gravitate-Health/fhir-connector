import os, json, logging

import utils.mail_client

import sys
sys.path.append("./providers")

from utils.fs_utils import (
    list_directory_files,
    read_file,
)

import providers.fhir_provider, providers.git_provider, providers.sushi_provider
import configs.hl7_epi
import configs.hl7_ips

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
MODE_GIT_FSH_SOURCE_REPO = os.getenv("MODE_GIT_FSH_SOURCE_REPO")
DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")

def connector_git_fsh(mail_client: utils.mail_client.Mail_client):   
    """
    Downloads HL7 repository and updates resources to FHIR server.
    Steps:
        1. Donwloads .fsh files
        2. Convert them to json
        3. Separate bundles into different FHIR resources
        4. Uploads separated resources
    """
    
    git_provider = providers.git_provider.gitProvider()
    sushi_provider = providers.sushi_provider.sushiProvider()
    fhir_provider = providers.fhir_provider.FhirProvider(DESTINATION_SERVER)
    
    # TODO: remove this hardcoded urls
    if(os.getenv("MODE_GIT_FSH_SOURCE_REPO") == "https://github.com/hl7-eu/gravitate-health-ips.git"):
        logger.info(f"Updating IPS git resources...")
        config = read_fhir_server_config("ips")
    elif(os.getenv("MODE_GIT_FSH_SOURCE_REPO") == "https://github.com/hl7-eu/gravitate-health.git"):
        logger.info(f"Updating ePI git resources...")
        config = read_fhir_server_config("epi")
    
    branch=os.getenv("MODE_GIT_FSH_SOURCE_REPO_BRANCH")

    whitelist = []
    try:
        withWhitelist = config["whiteList"]
        print(withWhitelist)
    except:
        pass
    
    fhir_resources = get_resources_from_git_repository(git_provider, sushi_provider, config, whitelist, branch=branch)
    sliced_resources = []
    for resource in fhir_resources:
        if resource["resourceType"] in ["Bundle"]:
            pieces = fhir_provider.separate_bundle_into_resources(resource)
            for item in pieces:
                sliced_resources.append(item)
        else:
            sliced_resources.append(resource)
    errors = update_server_from_git_repo(fhir_provider, config, sliced_resources)

    mail_client.create_message(errors)
    print("Email sent")
    return fhir_resources, errors

def read_fhir_resource_from_file(path):
    logger.debug(f"Reading resource: {path}")
    file = read_file(path)
    return json.load(file)

def get_resources_from_folder(folder_path, list):
    fhir_resources = []
    for resource_file_name in list:
        path = f"{folder_path}/{resource_file_name}"
        fhir_resources.append(read_fhir_resource_from_file(path))
    return fhir_resources

def get_resources_from_git_repository(git_provider, sushi_provider, config, whitelist=[], branch = "master"):
    repo_url = config["paths"]["repository"]
    git_provider.clone_git_repo(
        config["repository"], repo_url, branch=branch
    )
    sushi_provider.execute_sushi(
        config["paths"]["repository"]
    )  # 2. Converts them to json
    if whitelist:
        resource_list = whitelist.strip("][").split(", ")  # Convert string to list
    else:
        resource_list = list_directory_files(config["paths"]["json"])
    return get_resources_from_folder(config["paths"]["json"], resource_list)

def update_server_from_git_repo(fhir_provider, fhir_config, resources_list, whitelist=[]):
    """Uploads a list of resources to a FHIR server"""
    
    fhir_provider.destination_server = fhir_config["server"]
    
    errors_object = {}
    for order_list_type in fhir_config["orderList"]:
        for resource in resources_list:
            resource_type = resource["resourceType"]
            if (resource_type not in errors_object.keys()):
                errors_object[resource_type] = []
            if resource_type != order_list_type:
                continue  # Go to next resource as this is not the type we are looking for
            error = fhir_provider.write_fhir_resource_to_server(resource, MODE_GIT_FSH_SOURCE_REPO)
            if(error):
                errors_object[resource_type].append(error)
    
    return errors_object

def read_fhir_server_config( type: str):
    if type == "epi":
        config = configs.hl7_epi.get_configuration()
    elif type == "ips":
        config = configs.hl7_ips.get_configuration()
    return config
