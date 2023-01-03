from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
pl_update_time = app.config["PLAYLIST_UPDATE"]

db = SQLAlchemy(app)
migrate = Migrate(app,db,render_as_batch=True)

login = LoginManager(app)
login.login_message = None
login.login_view = "login"

auth_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=10, retries=5)

from app import routes, models

