import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///recommender.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-this")







    