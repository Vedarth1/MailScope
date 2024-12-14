from flask import Flask, Blueprint, redirect, url_for, session, request, jsonify
from google_auth_oauthlib.flow import Flow
import os
import json
import requests

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
    return redirect(authorization_url)

@api.route("/oauth/callback")
def callback():
    flow.fetch_token(
        authorization_response=request.url,
        client_id=flow.client_config["client_id"],
        client_secret=flow.client_config["client_secret"],
        scope=["openid", "email", "profile", "https://www.googleapis.com/auth/gmail.readonly"]
    )
    credentials = flow.credentials
    print("Granted Scopes:", credentials.scopes)

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
    print("UserInfo Response:", userinfo_response.json())

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