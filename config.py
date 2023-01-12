import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    BASE_PATH = 'view-source:http://127.0.0.1:5000/'
    SECRET_KEY = 'fgjeroiaulj'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE =  "SimpleCache",  # Flask-Caching related configs
    CACHE_DEFAULT_TIMEOUT = 300
    TOKEN_UPDATE = 60*55 #update token when expires in less than that
    PLAYLIST_UPDATE = 60*60 #update playlist after x seconds
    API_BASE = 'https://accounts.spotify.com'
    REDIRECT_URI = 'http://127.0.0.1:5000/api_callback'
    SCOPE = 'user-library-modify user-library-read'

