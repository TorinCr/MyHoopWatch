from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)

class School(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  school_name = db.Column(db.String(100), nullable=False)
  conference = db.Column(db.String(10))
  location = db.Column(db.String(100))

class Recruit(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=True)
  class_year = db.Column(db.Integer)
  committed_school_id = db.Column(db.Integer, db.ForeignKey('school.id'))

class Player(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  position = db.Column(db.String(20))
  graduation_year = db.Column(db.Integer)
  height = db.Column(db.String(10))
  weight = db.Column(db.Integer)
  committed_to = db.Column(db.String(120), default="Undecided")
  ranking = db.Column(db.Integer)
  school = db.Column(db.String, db.ForeignKey('school.school_name'))
  state = db.Column(db.String(2))
  updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Watchlist(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
  notes = db.Column(db.String(1000))
#class Offers(db.Model):
