from os import environ,path,urandom
from dotenv import load_dotenv


# Grabs the folder where the script runs.
basedir = path.abspath(path.dirname(__file__))

load_dotenv(path.join(basedir, '.env'))

# Enable debug mode.


# Connect to the database

class Config:
    
    FLASK_ENV = environ.get('FLASK_ENV')
    FLASK_APP = environ.get('FLASK_APP')
    PGUSER = environ.get('PGUSER')
    SECRET_KEY = urandom(32)
    DEBUG =environ.get('DEBUG')
    PASSWORD=environ.get('PASSWORD')

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

