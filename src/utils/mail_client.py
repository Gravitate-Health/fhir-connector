import os.path, json, mimetypes, smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
from utils.fs_utils import write_file, create_directory_if_not_exists

import os
from dotenv import load_dotenv
load_dotenv()


class Mail_client:
    

    def __init__(self):
        self.message = EmailMessage()
        self.attachemnts = []


    def create_message(self,  errors: list):
        print(errors)
        msg = EmailMessage()
        msg["From"] = os.getenv("EMAIL_SENDER")
        msg["To"] = os.getenv("EMAIL_RECIPIENT")

        # Get date of execution
        date_string = datetime.now().astimezone(timezone.utc).strftime("%d_%m_%Y-%H_%M")
        full_date_string = (
            datetime.now().astimezone(timezone.utc).strftime("%d/%m/%Y - %H:%M:%S %z")
        )
        
        subject = f"FOSPS: FHIR connector logs at {date_string}"
        msg["Subject"] = subject

        # Count how many errors there are
        error_count = 0
        for resource_type in errors:
            try:
                error_count += len(errors[resource_type])
            except:
                pass
            
        # Write errors to disk 
        file_name = f"fhir_connector_{date_string}-log.json"
        file_folder = "/tmp/logs"

        file_path = f"{file_folder}/{file_name}"
        create_directory_if_not_exists(file_folder)
        write_file(file_path, json.dumps(errors))
        self.add_attachment(file_path)


        body = (
            body
        ) = f"""Logs from fhir-connector. 
        
        - Date: {full_date_string}
        
        - DESTINATION SERVER: {os.getenv("DESTINATION_SERVER")}
        - Pulled git repo: {os.getenv("MODE_GIT_FSH_SOURCE_REPO")}
        - Pulled git branch: {os.getenv("MODE_GIT_FSH_SOURCE_REPO_BRANCH")}
        
        - Number of errors: {error_count}

        You can find the errors here, or in the attached json file.
        - Errors: {json.dumps(errors, indent=1)}
        """
        msg.set_content(body)
        self.message = msg

    def add_attachment(self, attachment_path):
        attachment_filename = os.path.basename(attachment_path)

        mime_type, _ = mimetypes.guess_type(attachment_path)
        mime_type, mime_subtype = mime_type.split("/", 1)

        with open(attachment_path, "rb") as ap:
            self.message.add_attachment(
                ap.read(),
                maintype=mime_type,
                subtype=mime_subtype,
                filename=attachment_filename,
            )

    def object_is_email_message(obj):
        return type(obj) == EmailMessage

    def send_mail(self):
        mail_server = smtplib.SMTP_SSL(os.getenv("EMAIL_SMTP_SERVER"))
        # mail_server.set_debuglevel(1) # Set the debug level to see SMTP messages (optional)

        mail_server.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))  # Authenticate to the email server
        mail_server.send_message(self.message)  # Send the email message
        mail_server.quit()  # Close the connection
        return
