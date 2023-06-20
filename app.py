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
from dotenv import dotenv_values
import sys
import logging
import logging.config

sys.path.append("./src")
from resource_providers import *
from loggers import configure_logging


def configure_environment():
    config = dotenv_values()


# TODO: pass parameter to choose which git repos will be synced. If parameter is missing or is equal to "all", sync all repos
# TODO: Be able to set fixed ids to patient/IPS, to match them with the ones in keycloak.
if __name__ == "__main__":
    configure_environment()
    configure_logging(config["LOG_LEVEL"])

    update_hl7_epi_resource()
    update_hl7_ips_resource()
    
    exit()