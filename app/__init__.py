from flask import Flask
from .models import db
from .routes import routes

def create_app():
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recruits.db'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  app.register_blueprint(routes)
  db.init_app(app)

  with app.app_context():
    db.create_all()

  return app