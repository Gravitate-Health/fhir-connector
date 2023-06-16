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
from fs_utils import change_direcotry, list_directory_files
from git_utils import *
from fsh_utils import *
from http_utils import *
# Load variables from .env file
from dotenv import dotenv_values
config = dotenv_values()


TMP_FOLDER = "/tmp/repos"

############################################
################## HL7 EPI #################
############################################

PATH_EPI_REPO = f"{TMP_FOLDER}/epi"
PATH_EPI_FSH = f"{PATH_EPI_REPO}/input/fsh/examples"
PATH_EPI_JSON = f"{PATH_EPI_REPO}/fsh-generated/resources"

""" 
This function:
  1. Donwloads epi .fsh files
  2. Iterating over different kind of epis (raw, preprocessed, etc.):
    2.1 Convert them to json 
    2.2 Upload the generated json directly
"""
def update_hl7_epi_resource():
    clone_git_repo(config["EPI_REPO"], PATH_EPI_REPO)
    execute_sushi(PATH_EPI_REPO)
    return


############################################
################## HL7 IPS #################
############################################

PATH_IPS_REPO = f"{TMP_FOLDER}/ips"
PATH_IPS_FSH = f"{PATH_IPS_REPO}/input/fsh/examples"
PATH_IPS_JSON = f"{PATH_IPS_REPO}/fsh-generated/resources"

""" 
This function:
  1. Donwloads epi .fsh files
  2. Convert them to json 
  3. Separate bundles into different FHIR resources
  4. Uploads separated resources
"""
def update_hl7_ips_resource():
    clone_git_repo(config["IPS_REPO"], PATH_IPS_REPO)
    execute_sushi(PATH_IPS_REPO)
    change_direcotry(PATH_IPS_JSON)
    files = list_directory_files(PATH_IPS_JSON)
    print(files)
    #delete_folder(IPS_REPO_PATH)
    return
