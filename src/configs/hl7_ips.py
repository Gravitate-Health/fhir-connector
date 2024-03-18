# Load variables from .env file
import os

TMP_FOLDER = "/tmp/repos"

IPS_REPO = os.getenv("MODE_GIT_FSH_SOURCE_REPO")
IPS_SERVER = os.getenv("DESTINATION_SERVER")
IPS_WHITELIST = os.getenv("IPS_WHITELIST")

IPS_ORDER_LIST = [
    "Patient",
    "Practitioner",
    "Condition",
    "Medication",
    "MedicationStatement",
    "AllergyIntolerance",
    "Immunization",
    "Composition",
]

def get_configuration():
    return {
    "repository": IPS_REPO,
    "server": IPS_SERVER,
    "orderList": IPS_ORDER_LIST,
    "whiteList": IPS_WHITELIST,
    "paths": {
        "repository": f"{TMP_FOLDER}/ips",
        "fsh": f"{TMP_FOLDER}/ips/input/fsh/examples",
        "json": f"{TMP_FOLDER}/ips/fsh-generated/resources",
    },
}
