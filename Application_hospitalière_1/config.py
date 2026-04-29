import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "hopital_secret_123"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://flask_user:flask123@localhost/application_hospitaliere"
    SQLALCHEMY_TRACK_MODIFICATIONS = False