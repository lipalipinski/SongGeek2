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



if app.config["CACHE_SERVERS"] == None:
    cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',
    "CACHE_DEFAULT_TIMEOUT": 600
    })
    cache.init_app(app)
else:
    cache = Cache()
    cache_user = os.environ.get('MEMCACHIER_USERNAME') or ''
    cache_pass = os.environ.get('MEMCACHIER_PASSWORD') or ''
    cache.init_app(app,
        config={'CACHE_TYPE': 'saslmemcached',
                'CACHE_MEMCACHED_SERVERS': app.config["CACHE_SERVERS"].split(','),
                'CACHE_MEMCACHED_USERNAME': cache_user,
                'CACHE_MEMCACHED_PASSWORD': cache_pass,
                'CACHE_OPTIONS': { 'behaviors': {
                    # Faster IO
                    'tcp_nodelay': True,
                    # Keep connection alive
                    'tcp_keepalive': True,
                    # Timeout for set/get requests
                    'connect_timeout': 2000, # ms
                    'send_timeout': 750 * 1000, # us
                    'receive_timeout': 750 * 1000, # us
                    '_poll_timeout': 2000, # ms
                    # Better failover
                    'ketama': True,
                    'remove_failed': 1,
                    'retry_timeout': 2,
                    'dead_timeout': 30}}})

# logging into files
if not app.debug and not app.testing:
    if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/songgeek.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('SongGeek startup')

# spotipy client credentials
auth_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(auth_manager=auth_manager, requests_timeout=4, retries=8, status_retries=3, status_forcelist=[401])


from app import routes, models, errors

