# Load variables from .env file
from dotenv import dotenv_values

config = dotenv_values()

TMP_FOLDER = "/tmp/repos"

IPS_REPO = config["IPS_REPO"]
IPS_SERVER = config["IPS_SERVER"]
IPS_WHITELIST = config["IPS_WHITELIST"]

IPS_ORDER_LIST = [
    "Patient",
    "Practitioner",
    "Condition",
    "Medication",
    "MedicationStatement",
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
