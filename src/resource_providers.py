#!/usr/bin/env python
# Copyright 2023 Universidad Politécnica de Madrid
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from fs_utils import change_directory, list_directory_files, read_file, list_directory_files_paths
from git_utils import *
from fhir_utils import *
from http_utils import *
import json
import logging 

# Load variables from .env file
from dotenv import dotenv_values
config = dotenv_values()

EPI_REPO = config["EPI_REPO"]
EPI_SERVER = config["EPI_SERVER"]
IPS_REPO = config["IPS_REPO"]
IPS_SERVER = config["IPS_SERVER"]


TMP_FOLDER = "/tmp/repos"

############################################
################## HL7 EPI #################
############################################

PATH_EPI_REPO = f"{TMP_FOLDER}/epi"
PATH_EPI_FSH = f"{PATH_EPI_REPO}/input/fsh/examples"
PATH_EPI_JSON = f"{PATH_EPI_REPO}/fsh-generated/resources"


def update_hl7_epi_resource():
    '''
    Uploads and updates HL7 EPI repository resources to FHIR server.
    Steps:
        1. Donwloads ips .fsh files
        2. Converts them to json 
        3. Iterates over different kind of epis (raw, preprocessed, etc.)
        4. Upload resources
    '''
    clone_git_repo(EPI_REPO, PATH_EPI_REPO)
    execute_sushi(PATH_EPI_REPO)
    return


############################################
################## HL7 IPS #################
############################################

PATH_IPS_REPO = f"{TMP_FOLDER}/ips"
PATH_IPS_FSH = f"{PATH_IPS_REPO}/input/fsh/examples"
PATH_IPS_JSON = f"{PATH_IPS_REPO}/fsh-generated/resources"

def update_hl7_ips_resource():
    '''
    Uploads and updates HL7 IPS repository resources to FHIR server.
    Steps:
        1. Donwloads ips .fsh files
        2. Convert them to json 
        3. Separate bundles into different FHIR resources
        4. Uploads separated resources
    '''
    try:
        whitelist = config["IPS_WHITELIST"]
        IPS_LIST = whitelist.strip('][').split(', ') # Convert string to list
    except:
        IPS_LIST = list_directory_files(PATH_IPS_JSON)
    
    clone_git_repo(IPS_REPO, PATH_IPS_REPO) # 1. Download ips .fsh files
    execute_sushi(PATH_IPS_REPO) # 2. Convert .fsh files to json

    for resource_file_name in IPS_LIST:
        logger = logging.getLogger(__name__)
        logger.info(f"______ Reading IPS bundle: {resource_file_name} ______")

        path = f"{PATH_IPS_JSON}/{resource_file_name}"
        file = read_file(path)
        bundle_json = json.load(file)
        separated_resources = separate_bundle_into_resources(bundle_json) # 3. Separate bundles into different FHIR resources

        
        ORDER_LIST = ["Patient", "Practitioner", "Condition", "Medication", "MedicationStatement",  "Composition"]
        for order_list_type in ORDER_LIST: # Iterate over resource types in the specified order
            for resource in separated_resources: # Iterate over resources inside bundle
                resource_type = resource["resourceType"]
                if resource_type != order_list_type:
                    continue # Go to next resource as this is not the type we are looking for

                resource_id = resource["id"]
                url = F"{IPS_SERVER}/{resource_type}/{resource_id}"
                logger.info(f"Uploading {url} - {resource_type} with id {resource_id}")
                put_request(url, resource) # 4. Uploads separated resources

    return
