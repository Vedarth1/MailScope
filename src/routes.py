from flask import Blueprint
from dotenv import load_dotenv
from src.controllers.oauth_controller import login,callback,logout
from src.controllers.email_controller import fetch_emails,fetch_emails_with_attachments
load_dotenv()

api = Blueprint('email_routes', __name__)

api.route("/login",methods=['GET'])(login)
api.route("/oauth/callback",methods=['GET'])(callback)
api.route("/logout",methods=['GET'])(logout)
api.route("/fetch-emails", methods=["GET"])(fetch_emails)
api.route("/fetch-emails-with-attachments", methods=["GET"])(fetch_emails_with_attachments)

@api.route("/")
def index():
    return "Welcome to the Email Integration Platform! Go to /login to connect your email."