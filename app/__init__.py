from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache
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

cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',
    "CACHE_DEFAULT_TIMEOUT": 600
    })
cache.init_app(app)

auth_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=1, retries=8, status_retries=3, status_forcelist=[401])


from app import routes, models

