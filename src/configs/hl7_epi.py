# Load variables from .env file
import os

from dotenv import load_dotenv

load_dotenv()

TMP_FOLDER = "/tmp/repos"

EPI_REPO = os.getenv("MODE_GIT_FSH_SOURCE_REPO")
EPI_SERVER = os.getenv("DESTINATION_SERVER")

EPI_ORDER_LIST = [
    "Binary",
    "MedicinalProductDefinition",
    "DocumentReference",
    "Organization",
    "PackagedProductDefinition",
    "RegulatedAuthorization",
    "ManufacturedItemDefinition",
    "AdministrableProductDefinition",
    "SubstanceDefinition",
    "Ingredient",
    "ClinicalUseDefinition",
    "CodeSystem",
    "Observation",
    "Questionnaire",
    "QuestionnaireResponse",
    "StructureDefinition",
    "ValueSet",
    "Composition",
    "Bundle",
    "List",
]


def get_configuration():
    return {
        "repository": EPI_REPO,
        "server": EPI_SERVER,
        "orderList": EPI_ORDER_LIST,
        "paths": {
            "repository": f"{TMP_FOLDER}/epi",
            "fsh": f"{TMP_FOLDER}/epi/input/fsh/examples",
            "json": f"{TMP_FOLDER}/epi/fsh-generated/resources",
        },
    }
