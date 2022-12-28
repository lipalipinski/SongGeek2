import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'fgjeroiaulj'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PLAYLIST_UPDATE = 60 #update playlist after x seconds
    API_BASE = 'https://accounts.spotify.com'
    REDIRECT_URI = 'http://127.0.0.1:5000/api_callback'
    SCOPE = 'user-library-modify user-library-read'
