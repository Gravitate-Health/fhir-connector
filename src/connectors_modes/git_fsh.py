import os, datetime, json
from datetime import datetime, timezone

import providers.hl7_git_provider
import utils.mail_client


def connector_git_fsh(mail_client: utils.mail_client.Mail_client):

    hl7_git_provider = providers.hl7_git_provider.Hl7FhirPRovider()

    ## TODO de-hardcode this
    errors = hl7_git_provider.update_hl7_resource(
        branch=os.getenv("MODE_GIT_FSH_SOURCE_REPO_BRANCH")
    )

    mail_client.create_message(errors)
    print("Email sent")
    return
