import json
import os
import requests

from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from googleapiclient.discovery import build_from_document as build_service
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from jinja2 import Environment, FileSystemLoader

from app import config

GMAIL_DISCOVERY_URL = "https://www.googleapis.com/discovery/v1/apis/gmail/v1/rest"
SCOPES = ["https://mail.google.com/"]
templates = Environment(
    loader=FileSystemLoader(
        os.path.join(os.path.split(os.path.realpath(__file__))[0], "templates")
    )
)


def fetch_gmail_discovery() -> None:
    res = requests.get(GMAIL_DISCOVERY_URL, timeout=10)
    res.raise_for_status()
    with open(
        config.config["gmail"]["discovery_path"], "w", encoding="utf-8"
    ) as discovery:
        json.dump(res.json(), discovery)
    return


def auth_gmail_api():
    discovery_path = config.config["gmail"]["discovery_path"]
    token_path = config.config["gmail"]["token_path"]
    secret_path = config.config["gmail"]["secret_path"]

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

    with open(discovery_path, "r", encoding="utf-8") as discovery:
        gmail_service = json.load(discovery)

    return build_service(gmail_service, credentials=creds)


def secure_gmail_related_files() -> None:
    os.chmod(config.config["gmail"]["discovery_path"], 0o644)
    os.chmod(config.config["gmail"]["token_path"], 0o600)
    os.chmod(config.config["gmail"]["secret_path"], 0o600)
    return


def create_email(
    reciever_email_addr: str, subject: str, template_name: str, context: dict
):
    template = templates.get_template(template_name)
    mail = MIMEText(template.render(context), "html", "utf-8")
    mail["from"] = config.config["gmail"]["sender_email_addr"]
    mail["to"] = reciever_email_addr
    mail["subject"] = subject

    return {"raw": urlsafe_b64encode(mail.as_bytes()).decode()}


def send_email(
    reciever_email_addr: str, subject: str, template_name: str, context: dict
):
    service = auth_gmail_api()

    return (
        service.users()
        .messages()
        .send(
            userId="me",
            body=create_email(reciever_email_addr, subject, template_name, context),
        )
        .execute()
    )
