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

################ GRAVITATE-HEALTH FHIR CONNECTOR ################
# This Python app syncs the following repositories with GH's FOSPS FHIR servers.
# - https://github.com/hl7-eu/gravitate-health
# - https://github.com/hl7-eu/gravitate-health-ips
#################################################################
import sys
import logging
import logging.config
import json
from datetime import datetime, timezone

sys.path.append("./src")
sys.path.append("./src/providers")
sys.path.append("./src/utils")

import providers.hl7_git_provider
from utils.loggers import configure_logging

from utils.mail_client import create_message, add_attachment, object_is_email_message, send_mail
from utils.fs_utils import write_file, create_directory_if_not_exists
from utils.mail_client import create_message, add_attachment, send_mail

import os


# TODO: pass parameter to choose which git repos will be synced. If parameter is missing or is equal to "all", sync all repos
# TODO: Be able to set fixed ids to patient/IPS, to match them with the ones in keycloak.
if __name__ == "__main__":
    
    hl7_git_provider = providers.hl7_git_provider.Hl7FhirPRovider()
    configure_logging(os.getenv("LOG_LEVEL"))
    
    epi_errors = hl7_git_provider.update_hl7_resource("epi", branch=os.getenv("EPI_REPO_BRANCH"))
    ips_errors = hl7_git_provider.update_hl7_resource("ips", branch=os.getenv("IPS_REPO_BRANCH"))
    
    errors = {
        "epi": epi_errors,
        "ips": ips_errors
    }
    date_string = datetime.now().astimezone(timezone.utc).strftime("%d_%m_%Y-%H_%M")
    full_date_string = datetime.now().astimezone(timezone.utc).strftime("%d/%m/%Y - %H:%M:%S %z")
    file_name = f'fhir_connector_{date_string}-log.json'
    file_folder = '/tmp/logs'
    
    file_path = f'{file_folder}/{file_name}'
    create_directory_if_not_exists(file_folder)
    write_file(file_path, json.dumps(errors))
    
    # Count how many errors there are
    error_count = 0
    for type in ["epi", "ips"]:
        for resource_type in errors[type]:
            error_count += len(errors[type][resource_type])
            
    
    # Create email
    subject = f"FOSPS: FHIR connector logs at {date_string}"
    body = f"""Logs from fhir-connector. 
    
    - Date: {full_date_string}
    
    - IPS server: {os.getenv("IPS_SERVER")}
    - IPS branch: {os.getenv("IPS_REPO_BRANCH")}
    - EPI server: {os.getenv("EPI_SERVER")}
    - EPI branch: {os.getenv("EPI_REPO_BRANCH")}
    
    
    - Number of errors: {error_count}

    You can find the errors here, or in the attached json file.
    - Errors: {json.dumps(errors, indent=1)}
    """
    message = create_message(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_RECIPIENT"), subject, body)
    message = add_attachment(message, file_path)
    print("Sending email...")
    # Send email
    send_mail(message, os.getenv("EMAIL_SMTP_SERVER"), os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
    print('Email sent')
    exit()