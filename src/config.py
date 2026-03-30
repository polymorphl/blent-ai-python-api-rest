from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()


class Config:
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "just-one-secret-but-not-very-secure"
