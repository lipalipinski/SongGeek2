from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache
from logging.handlers import RotatingFileHandler
import logging
import spotipy
import os
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

# logging into files
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/songgeek.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.DEBUG)
    app.logger.info('SongGeek startup')

# spotipy client credentials
auth_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=4, retries=8, status_retries=3, status_forcelist=[401])


from app import routes, models, errors

