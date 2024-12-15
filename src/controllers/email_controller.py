import os,boto3,base64
from dotenv import load_dotenv
from flask import Flask,jsonify, session, request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

def fetch_emails():
    try:
        if "tokens" not in session:
            return jsonify({"error": "User not authenticated. Please login first."}), 401

        tokens = session["tokens"]
        credentials = build_credentials_from_session(tokens)

        service = build('gmail', 'v1', credentials=credentials)

        keyword = request.args.get("keyword", "")
        subject = request.args.get("subject", "")
        from_email = request.args.get("from", "")
        after_date = request.args.get("after", "")
        before_date = request.args.get("before", "")

        query = ""
        if keyword:
            query += f"{keyword} "
        if subject:
            query += f"subject:{subject} "
        if from_email:
            query += f"from:{from_email} "
        if after_date:
            query += f"after:{after_date} "
        if before_date:
            query += f"before:{before_date}"

        response = service.users().messages().list(
            userId="me",
            maxResults=10,
            q=query.strip(),
            fields="messages/id"
        ).execute()

        if "messages" not in response or len(response["messages"]) == 0:
            return jsonify({"message": "No emails found with the provided filters."})

        emails = []
        for message in response["messages"]:
            email = service.users().messages().get(
                userId="me",
                id=message["id"],
                fields="id,snippet,internalDate,payload/headers"
            ).execute()

            email_details = {
                "id": email["id"],
                "snippet": email.get("snippet"),
                "date": email.get("internalDate"),
                "subject": extract_email_header(email, "Subject"),
                "from": extract_email_header(email, "From"),
            }
            emails.append(email_details)

        return jsonify({"emails": emails})

    except HttpError as error:
        print(f"HttpError occurred: {error}")
        return jsonify({"error": str(error)}), 500
    
def fetch_emails_with_attachments():
    try:
        if "tokens" not in session:
            return jsonify({"error": "User not authenticated. Please login first."}), 401

        tokens = session["tokens"]
        credentials = build_credentials_from_session(tokens)

        service = build('gmail', 'v1', credentials=credentials)

        keyword = request.args.get("keyword", "")
        subject = request.args.get("subject", "")
        from_email = request.args.get("from", "")
        after_date = request.args.get("after", "")
        before_date = request.args.get("before", "")

        query = ""
        if keyword:
            query += f"{keyword} "
        if subject:
            query += f"subject:{subject} "
        if from_email:
            query += f"from:{from_email} "
        if after_date:
            query += f"after:{after_date} "
        if before_date:
            query += f"before:{before_date}"

        response = service.users().messages().list(
            userId="me",
            maxResults=10,
            q=query.strip(),
            fields="messages/id"
        ).execute()

        print(response)
        if "messages" not in response or len(response["messages"]) == 0:
            return jsonify({"message": "No emails found with the provided filters."})

        emails_with_attachments = []

        for message in response['messages']:
            email = service.users().messages().get(
                userId='me',
                id=message['id']
            ).execute()

            # Check and process attachments
            attachments_info = process_attachments(email, service)

            if attachments_info:
                emails_with_attachments.append({
                    "id": email["id"],
                    "subject": extract_email_header(email, "Subject"),
                    "from": extract_email_header(email, "From"),
                    "attachments": attachments_info
                })

        return jsonify({"emails": emails_with_attachments})

    except HttpError as error:
        return jsonify({"error": str(error)}), 500
    

def process_attachments(email, service):
    """
    Process attachments of an email and upload them to S3.
    """
    attachments = []

    def extract_attachments_from_parts(parts):
        for part in parts:
            if part.get("filename") and part.get("body", {}).get("attachmentId"):
                attachment_id = part["body"]["attachmentId"]
                attachment = service.users().messages().attachments().get(
                    userId='me',
                    messageId=email["id"],
                    id=attachment_id
                ).execute()

                data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))

                # Upload to S3
                upload_to_s3(part["filename"], data)

                attachments.append(part["filename"])

            # Check if there are nested parts
            if part.get("parts"):
                extract_attachments_from_parts(part["parts"])

    parts = email.get("payload", {}).get("parts", [])
    extract_attachments_from_parts(parts)

    return attachments

def build_gmail_query(filters):
    """
    Build a Gmail API query string from dynamic filters.
    """
    query = []
    if filters.get("subject"):
        query.append(f"subject:{filters['subject']}")
    if filters.get("from"):
        query.append(f"from:{filters['from']}")
    if filters.get("to"):
        query.append(f"to:{filters['to']}")
    if filters.get("keyword"):
        query.append(filters["keyword"])
    if filters.get("after"):
        query.append(f"after:{filters['after']}")
    if filters.get("before"):
        query.append(f"before:{filters['before']}")

    return " ".join(query)

def upload_to_s3(filename, data):
    """
    Upload a file to AWS S3.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=filename,
        Body=data
    )
    print(f"Uploaded {filename} to S3.")

def extract_email_header(email, header_name):
    """Helper function to extract a specific header from email payload."""
    headers = email.get("payload", {}).get("headers", [])
    for header in headers:
        if header["name"].lower() == header_name.lower():
            return header["value"]
    return None


def build_credentials_from_session(tokens):

    credentials = Credentials(
        token=tokens["token"],
        refresh_token=tokens.get("refresh_token"),
        token_uri=tokens["token_uri"],
        client_id=tokens["client_id"],
        client_secret=tokens["client_secret"],
        scopes=tokens["scopes"],
    )
    return credentials