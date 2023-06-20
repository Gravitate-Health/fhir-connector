from fs_utils import change_directory
from os import system
import logging

def execute_sushi(path):
    change_directory(path)
    command = "sushi ."

    logging.info("----- EXECUTING SUSHI ON .FSH FOLDER ----- \n")
    
    exit_code = system(command)
    logging.info("\n ----- FINISHED EXECUTING SUSHI ON .FSH FOLDER ----- \n")
    return

def separate_bundle_into_resources(data):
    if not data:
        raise Exception(
            "No resource types were provided to separate_bundle_into_resources()")

    bundle_id = data["id"]
    entries = data["entry"]

    # Iterate over entries in bundle

    separated_resources = []
    for resource_entry in entries:
        try:
            resource = resource_entry['resource']
        except:
            pass
        separated_resources.append(resource)
    return separated_resources
