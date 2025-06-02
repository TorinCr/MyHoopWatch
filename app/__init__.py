from flask import Flask
from .models import db
from .routes import routes
from dotenv import load_dotenv
from kenpompy.utils import login
import os

def create_app():
  global kenpom_browser

  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recruits.db'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

  load_dotenv()

  KENPOM_EMAIL = os.getenv('KENPOM_EMAIL')
  KENPOM_PASSWORD = os.getenv('KENPOM_PASSWORD')

  kenpom_browser = login(KENPOM_EMAIL, KENPOM_PASSWORD)

  app.register_blueprint(routes)
  db.init_app(app)

  with app.app_context():
    from app import models
    db.create_all()

  return app