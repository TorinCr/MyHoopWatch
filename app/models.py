from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#Association table for many to many relationship
PlayerPositions = db.Table('player_positions',
    db.Column('player_id', db.Integer, db.ForeignKey('player.id')),
    db.Column('position_id', db.Integer, db.ForeignKey('positions.id'))
)


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)

class School(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  school_name = db.Column(db.String(100), nullable=False)
  conference = db.Column(db.String(10))
  location = db.Column(db.String(100))

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
  highlights_url = db.Column(db.String, nullable=True)

  positions = db.relationship('Positions', secondary=PlayerPositions, backref='players')
  rankings = db.relationship('PlayerRankings', backref='player', lazy=True)

class Watchlist(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
  notes = db.Column(db.String(1000))

class PlayerRankings(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
  source = db.Column(db.String(100))
  rank = db.Column(db.Integer)

class Positions(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(10), unique=True)


#class Offers(db.Model):
