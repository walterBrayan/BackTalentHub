import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "una_clave_secreta_muy_segura"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://postgres:Atenas12.@localhost:5432/talenthub"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
