from flask import Flask, Blueprint, redirect, url_for, session, request, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os, json ,requests,base64,datetime
from dotenv import load_dotenv

load_dotenv()

CLIENT_SECRET_FILE=os.getenv("CLIENT_SECRET_FILE")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
scopes = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
]
flow = Flow.from_client_secrets_file(
    CLIENT_SECRET_FILE,
    scopes=scopes,
    redirect_uri="http://localhost:5000/api/oauth/callback"
)

api = Blueprint('email_routes', __name__)

@api.route("/login")
def login():
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["state"] = state
    return jsonify({
            "auth_url": authorization_url
        }), 200

@api.route("/oauth/callback")
def callback():
    flow.fetch_token(
        authorization_response=request.url,
        client_id=flow.client_config["client_id"],
        client_secret=flow.client_config["client_secret"],
        scope=["openid", "email", "profile", "https://www.googleapis.com/auth/gmail.readonly"]
    )
    credentials = flow.credentials

    session["tokens"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    userinfo_endpoint = "https://www.googleapis.com/oauth2/v1/userinfo"
    userinfo_response = requests.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {credentials.token}"}
    )

    user_info = userinfo_response.json()
    session["email"] = user_info.get("email")

    return jsonify({"message": "Login successful!", "email": session["email"]})

@api.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@api.route("/")
def index():
    return "Welcome to the Email Integration Platform! Go to /login to connect your email."

@api.route("/fetch-emails", methods=["GET"])
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


def extract_email_header(email, header_name):
    """Helper function to extract a specific header from email payload."""
    headers = email.get("payload", {}).get("headers", [])
    for header in headers:
        if header["name"].lower() == header_name.lower():
            return header["value"]
    return None


def build_credentials_from_session(tokens):
    from google.oauth2.credentials import Credentials

    # Build credentials from session tokens
    credentials = Credentials(
        token=tokens["token"],
        refresh_token=tokens.get("refresh_token"),
        token_uri=tokens["token_uri"],
        client_id=tokens["client_id"],
        client_secret=tokens["client_secret"],
        scopes=tokens["scopes"],
    )
    return credentials