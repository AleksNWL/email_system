import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'my_super_secret_key_12345')
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://user:password@db-primary:5432/emails"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
