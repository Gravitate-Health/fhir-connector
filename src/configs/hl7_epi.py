# Load variables from .env file
import os

TMP_FOLDER = "/tmp/repos"

EPI_REPO = os.getenv("EPI_REPO")
EPI_SERVER = os.getenv("EPI_SERVER")

EPI_ORDER_LIST = [
    "Binary",
    "MedicinalProductDefinition",
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
