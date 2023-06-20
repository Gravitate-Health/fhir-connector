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
from fs_utils import (
    change_directory,
    list_directory_files,
    read_file,
    list_directory_files_paths,
)
from git_utils import *
from fhir_utils import *
from http_utils import *
import json
import logging

logger = logging.getLogger(__name__)

# Load variables from .env file
from dotenv import dotenv_values

config = dotenv_values()

EPI_REPO = config["EPI_REPO"]
EPI_SERVER = config["EPI_SERVER"]
IPS_REPO = config["IPS_REPO"]
IPS_SERVER = config["IPS_SERVER"]

TMP_FOLDER = "/tmp/repos"

EPI_ORDER_LIST = [
    "Binary",
    "MedicinalProductDefinition",
    "Organization",
    "RegulatedAuthorization",
    "ManufacturedItemDefinition",
    "AdministrableProductDefinition",
    "PackagedProductDefinition",
    "SubstanceDefinition",
    "Ingredient",
    "ClinicalUseDefinition" "Composition",
    "Bundle",
    "CodeSystem",
    "Observation",
    "Questionnaire" "QuestionnaireResponse" "StructureDefinition",
    "ValueSet",
]

IPS_ORDER_LIST = [
    "Patient",
    "Practitioner",
    "Condition",
    "Medication",
    "MedicationStatement",
    "Composition",
]

epi_config = {
    "repository": EPI_REPO,
    "server": EPI_SERVER,
    "orderList": EPI_ORDER_LIST,
    "paths": {
        "repository": f"{TMP_FOLDER}/epi",
        "fsh": f"{TMP_FOLDER}/epi/input/fsh/examples",
        "json": f"{TMP_FOLDER}/epi/fsh-generated/resources",
    },
}

ips_config = {
    "repository": IPS_REPO,
    "server": IPS_SERVER,
    "orderList": IPS_ORDER_LIST,
    "paths": {
        "repository": f"{TMP_FOLDER}/ips",
        "fsh": f"{TMP_FOLDER}/ips/input/fsh/examples",
        "json": f"{TMP_FOLDER}/ips/fsh-generated/resources",
    },
}


def read_fhir_resource_from_file(path):
    logger.debug(f"Reading resource: {path}")
    file = read_file(path)
    return json.load(file)


def write_fhir_resource_to_server(resource, url):
    resource_type = resource["resourceType"]
    resource_id = resource["id"]
    url = f"{url}/{resource_type}/{resource_id}"
    logger.info(f"Uploading {url} - {resource_type} with id {resource_id}")
    put_request(url, resource)


def get_resources_from_folder(folder_path, list):
    fhir_resources = []
    for resource_file_name in list:
        path = f"{folder_path}/{resource_file_name}"
        fhir_resources.append(read_fhir_resource_from_file(path))
    return fhir_resources


def get_resources_from_git_repository(config, whitelist=[]):
    clone_git_repo(config["repository"], config["paths"]["repository"])
    execute_sushi(config["paths"]["repository"])  # 2. Converts them to json
    if whitelist:
        resource_list = whitelist.strip("][").split(", ")  # Convert string to list
    else:
        resource_list = list_directory_files(config["paths"]["json"])
    return get_resources_from_folder(config["paths"]["json"], resource_list)


def update_server_from_git_repo(fhir_config, resources_list, whitelist=[]):
    """Uploads a list of resources to a FHIR server"""
    for order_list_type in fhir_config["orderList"]:
        for resource in resources_list:
            resource_type = resource["resourceType"]
            if resource_type != order_list_type:
                continue  # Go to next resource as this is not the type we are looking for

            write_fhir_resource_to_server(resource, fhir_config["server"])


def update_hl7_epi_resource():
    """
    Downloads HL7 EPI repository and updates resources to FHIR server.
    Steps:
        1. Donwloads epi .fsh files
        2. Converts them to json
        4. Upload resources
    """
    logger.info(f"Updating EPI reosurces...")

    fhir_resources = get_resources_from_git_repository(epi_config)
    update_server_from_git_repo(epi_config, fhir_resources)

    return


def update_hl7_ips_resource():
    """
    Downloads HL7 IPS repository and updates resources to FHIR server.
    Steps:
        1. Donwloads ips .fsh files
        2. Convert them to json
        3. Separate bundles into different FHIR resources
        4. Uploads separated resources
    """
    logger.info(f"Updating IPS reosurces...")

    try:
        whitelist = config["IPS_WHITELIST"]
    except:
        whitelist = []
    fhir_resources = get_resources_from_git_repository(ips_config, whitelist)
    sliced_resources = []
    for resource in fhir_resources:
        if resource["resourceType"] == "Bundle":
            pieces = separate_bundle_into_resources(resource)
            for item in pieces:
                sliced_resources.append(item)
        else:
            sliced_resources.append(resource)
    update_server_from_git_repo(ips_config, sliced_resources)

    return
