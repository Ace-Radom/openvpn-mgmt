import os

from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from googleapiclient.discovery import build as build_service
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from jinja2 import Environment, FileSystemLoader

from app import config

SCOPES = ["https://mail.google.com/"]
templates = Environment(loader=FileSystemLoader(os.path.join(os.path.split(os.path.realpath(__file__))[0], "templates")))


def auth_gmail_api(token_path: str, secret_path: str):
    creds = None
    if os.path.exists(token_path):
        with open(token_path, "r") as token:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.path.exists(secret_path):
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, SCOPES)
            creds = flow.run_local_server(port=0)
        else:
            raise Exception("secret file not exists")

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build_service("Gmail", "v1", credentials=creds, static_discovery=False)


def create_email(reciever_email_addr: str, subject: str, template_name: str, context: dict):
    template = templates.get_template(template_name)
    mail = MIMEText(template.render(context), "html", "utf-8")
    mail["from"] = config.config["gmail"]["sender_email_addr"]
    mail["to"] = reciever_email_addr
    mail["subject"] = subject

    return {"raw": urlsafe_b64encode(mail.as_bytes()).decode()}


def send_email(reciever_email_addr: str, subject: str, template_name: str, context: dict):
    service = auth_gmail_api(config.config["gmail"]["token_path"], config.config["gmail"]["secret_path"])

    return (
        service.users()
        .messages()
        .send(
            userId="me", body=create_email(reciever_email_addr, subject, template_name, context)
        )
        .execute()
    )
