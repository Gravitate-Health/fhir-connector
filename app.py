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
import enum
import sys
import logging
import logging.config

sys.path.append("./src")
sys.path.append("./src/providers")
sys.path.append("./src/utils")

from utils.loggers import configure_logging


import utils.mail_client
import os

""" from connectors_modes import git_fsh
from connectors_modes import fhir_server_sync """

from connectors_modes import git_fsh, fhir_server_sync, delete_resources, fhir_server_proxy, smm_tool
from datetime import datetime, timezone

"""

Environment Variables
 
CONNECTOR_MODE:
    - HAPI_FHIR_SERVER_PROXY   -   Get resources from another FHIR server
    - HAPI_FHIR_SERVER_SYNC    -   Periodically syncs resources from a HAPI FHIR server.
    - GIT_FSH                  -   Get .fsh files from a git repository, transform to json and upload to FHIR server.

MODE_HAPI_SYNC_URL - Base url for HAPI FHIR server
MODE_HAPI_SYNC_RESOURCES - List of resources to sync (in order of sync)

"""

from dotenv import load_dotenv

load_dotenv()


class Connector_Modes(enumerate):
    HAPI_FHIR_SERVER_PROXY = "HAPI_FHIR_SERVER_PROXY"
    HAPI_FHIR_SERVER_SYNC = "HAPI_FHIR_SERVER_SYNC"
    GIT_FSH = "GIT_FSH"
    DELETE_RESOURCES = "DELETE_RESOURCES"
    SMM_TOOL = "SMM_TOOL"


# TODO: pass parameter to choose which git repos will be synced. If parameter is missing or is equal to "all", sync all repos
# TODO: Be able to set fixed ids to patient/IPS, to match them with the ones in keycloak.
if __name__ == "__main__":

    configure_logging(os.getenv("LOG_LEVEL"))
    logger = logging.getLogger(__name__)
    MODE = os.getenv("CONNECTOR_MODE")

    mail_client = utils.mail_client.Mail_client()
    
    logger.info("Running connector...")
    logger.info("  Date: " + datetime.now().astimezone(timezone.utc).strftime("%d/%m/%Y - %H:%M:%S %z"))
    logger.info("  MODE: " + MODE)
    

    # Working mode: GIT_FSH
    resources = []
    errors = []
    if MODE == Connector_Modes.GIT_FSH:
        logger.info("  MODE_GIT_FSH_SOURCE_REPO: " + os.getenv("MODE_GIT_FSH_SOURCE_REPO"))
        logger.info("  MODE_GIT_FSH_SOURCE_REPO_BRANCH: " + os.getenv("MODE_GIT_FSH_SOURCE_REPO_BRANCH"))
        logger.info("  DESTINATION_SERVER: " + os.getenv("DESTINATION_SERVER"))
        resources, errors = git_fsh.connector_git_fsh(mail_client)

    # Working mode: HAPI_FHIR_SERVER_SYNC
    elif MODE == Connector_Modes.HAPI_FHIR_SERVER_SYNC:
        logger.info("  MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER: " + os.getenv("MODE_HAPI_FHIR_SERVER_SYNC_SOURCE_SERVER"))
        logger.info("  MODE_HAPI_FHIR_SERVER_SYNC_RESOURCES: " + ''.join(os.getenv("MODE_HAPI_FHIR_SERVER_SYNC_RESOURCES").strip("][").split(", ")))
        logger.info("  DESTINATION_SERVER: " + os.getenv("DESTINATION_SERVER"))
        
        resources, errors = fhir_server_sync.connector_fhir_server_sync(mail_client)

    # Working mode: HAPI_FHIR_SERVER_SYNC
    elif MODE == Connector_Modes.HAPI_FHIR_SERVER_PROXY:
        fhir_server_proxy.run()
    
    elif MODE == Connector_Modes.DELETE_RESOURCES:
        logger.info("  DESTINATION_SERVER: " + os.getenv("DESTINATION_SERVER"))
        delete_resources.delete_all_resources(mail_client)
    # Working mode: other
    elif MODE == Connector_Modes.SMM_TOOL:
        logger.info("  SMM_SERVER_URL: " + os.getenv("SMM_SERVER_URL"))
        logger.info("  DESTINATION_SERVER: " + os.getenv("DESTINATION_SERVER"))
        smm_tool.connector_smm_tool(mail_client)
    else:
        logger.error("Connector working mode not implemented: " + MODE)

    print("Sending email...")
    # Send email
    try:
        mail_client.send_mail()
    except Exception as e:
        pass
    exit()
