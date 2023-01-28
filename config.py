import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.environ.get("SELF_URL")
load_dotenv(os.path.join(basedir, '.env'))

POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PW = os.environ.get("POSTGRES_PW")
POSTGRES_URL = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL)

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    LOG_DEBUG = os.environ.get('LOG_DEBUG')
    BASE_PATH = f'view-source:{basedir}'
    SQLALCHEMY_DATABASE_URI = POSTGRES_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    if os.environ.get('CACHE_OFF') == "True":
        CACHE_OFF = True
    else:
        CACHE_OFF = False
    CACHE_SERVERS = os.environ.get('MEMCACHIER_SERVERS')
    CACHE_DEFAULT_TIMEOUT = 300
    TOKEN_UPDATE = 60*15 #update token when expires in less than that
    PLAYLIST_UPDATE = 60*60 #update playlist after x seconds
    API_BASE = 'https://accounts.spotify.com'
    REDIRECT_URI = f'{basedir}api_callback'
    SCOPE = 'user-library-modify user-library-read'

