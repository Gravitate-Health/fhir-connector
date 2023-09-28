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
import sys

sys.path.append("./providers")

from utils.fs_utils import (
    change_directory,
    list_directory_files,
    read_file,
    list_directory_files_paths,
)

from providers.fhir_provider import FhirProvider
from providers.git_provider import gitProvider
from sushi_provider import sushiProvider
import configs.hl7_epi
import configs.hl7_ips
import json
import logging
import configs.hl7_epi
import configs.hl7_ips


class Hl7FhirPRovider:
    logger = logging.getLogger(__name__)
    epi_config = configs.hl7_epi.get_configuration()
    ips_config = configs.hl7_ips.get_configuration()

    def __init__(self):
        self.git_provider = gitProvider()
        self.sushi_provider = sushiProvider()
        self.fhir_provider = FhirProvider()

    def read_fhir_resource_from_file(self, path):
        self.logger.debug(f"Reading resource: {path}")
        file = read_file(path)
        return json.load(file)

    def get_resources_from_folder(self, folder_path, list):
        fhir_resources = []
        for resource_file_name in list:
            path = f"{folder_path}/{resource_file_name}"
            fhir_resources.append(self.read_fhir_resource_from_file(path))
        return fhir_resources

    def get_resources_from_git_repository(self, config, whitelist=[]):
        self.git_provider.clone_git_repo(
            config["repository"], config["paths"]["repository"]
        )
        self.sushi_provider.execute_sushi(
            config["paths"]["repository"]
        )  # 2. Converts them to json
        if whitelist:
            resource_list = whitelist.strip("][").split(", ")  # Convert string to list
        else:
            resource_list = list_directory_files(config["paths"]["json"])
        return self.get_resources_from_folder(config["paths"]["json"], resource_list)

    def update_server_from_git_repo(self, fhir_config, resources_list, whitelist=[]):
        """Uploads a list of resources to a FHIR server"""
        
        errors_object = {}
        for order_list_type in fhir_config["orderList"]:
            for resource in resources_list:
                resource_type = resource["resourceType"]
                if (resource_type not in errors_object.keys()):
                    errors_object[resource_type] = []
                if resource_type != order_list_type:
                    continue  # Go to next resource as this is not the type we are looking for

                error = self.fhir_provider.write_fhir_resource_to_server(
                    resource, fhir_config["server"]
                )
                if(error):
                    errors_object[resource_type].append(error)
        return errors_object

    def read_fhir_server_config(self, type: str):
        if type == "epi":
            config = configs.hl7_epi.get_configuration()
        elif type == "ips":
            config = configs.hl7_ips.get_configuration()
        return config

    def update_hl7_resource(self, type: str, withWhitelist: bool = False):
        """
        Downloads HL7 repository and updates resources to FHIR server.
        Steps:
            1. Donwloads .fsh files
            2. Convert them to json
            3. Separate bundles into different FHIR resources
            4. Uploads separated resources
        """
        
        if (type != "epi" and type != "ips"):
            self.logger.error(f"Invalid FSH type: {type}")
            return
        
        self.logger.info(f"Updating {type} reosurces...")
        config = self.read_fhir_server_config(type)
        
        whitelist = []
        if(withWhitelist):
            try:
                withWhitelist = config["whiteList"]
            except:
                withWhitelist = []
        else:
            whitelist = []
        fhir_resources = self.get_resources_from_git_repository(config, whitelist)
        sliced_resources = []
        for resource in fhir_resources:
            if resource["resourceType"] in ["Bundle"]:
                pieces = self.fhir_provider.separate_bundle_into_resources(resource)
                for item in pieces:
                    sliced_resources.append(item)
            else:
                sliced_resources.append(resource)
        errors = self.update_server_from_git_repo(config, sliced_resources)

        return errors
    