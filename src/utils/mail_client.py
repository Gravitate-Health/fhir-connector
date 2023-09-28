from email.message import EmailMessage
import os.path
import mimetypes

import smtplib

def create_message(sender, recipient, subject, body = ""):
    message = EmailMessage()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = subject
    message.set_content(body)
    return message

def add_attachment(message, attachment_path):
    attachment_filename = os.path.basename(attachment_path)

    mime_type, _ = mimetypes.guess_type(attachment_path)
    mime_type, mime_subtype = mime_type.split('/', 1)
    
    with open(attachment_path, 'rb') as ap:
        message.add_attachment(
            ap.read(),
            maintype=mime_type,
            subtype=mime_subtype,
            filename=attachment_filename
        )
    return message
    

def object_is_email_message(obj):
    return type(obj) == EmailMessage
    

def send_mail(message: EmailMessage, mail_server: str, sender_email: str, sender_pass: str ):
    mail_server = smtplib.SMTP_SSL(mail_server)
    # mail_server.set_debuglevel(1) # Set the debug level to see SMTP messages (optional)
    
    mail_server.login(sender_email, sender_pass) # Authenticate to the email server
    mail_server.send_message(message) # Send the email message
    mail_server.quit() # Close the connection
    return
