import os,requests
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from flask import session, jsonify,request

load_dotenv()

CLIENT_SECRET_FILE=os.getenv("CLIENT_SECRET_FILE")

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


def logout():
    session.clear()
    return jsonify({"message": "Logout successful!"})