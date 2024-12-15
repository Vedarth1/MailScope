from flask import Flask
from flask_cors import CORS
from flask_session import Session
from src.routes import api
from dotenv import load_dotenv
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

load_dotenv()

def create_app(config):
    app = Flask(__name__)
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    CORS(app, supports_credentials=True, origins="*")

    app.secret_key = os.getenv("SECRET_KEY")
    app.config.from_object(config)
    
    app.register_blueprint(api, url_prefix="/api")
    
    return app
