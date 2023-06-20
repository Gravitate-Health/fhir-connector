from fs_utils import change_directory
from os import system
import logging

logger = logging.getLogger(__name__)


def execute_sushi(path):
    change_directory(path)
    command = "sushi ."

    logger.info("Executing sushi in .fsh folder")
    exit_code = system(command)
    logger.info("Finished executing sushi")
    return


def separate_bundle_into_resources(data):
    if not data:
        raise Exception(
            "No resource types were provided to separate_bundle_into_resources()"
        )

    bundle_id = data["id"]
    entries = data["entry"]

    # Iterate over entries in bundle

    separated_resources = []
    for resource_entry in entries:
        try:
            resource = resource_entry["resource"]
        except:
            pass
        separated_resources.append(resource)
    return separated_resources
