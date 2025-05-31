from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)

class School(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  school_name = db.Column(db.String(100), nullable=False)

class Recruit(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=True)
  class_year = db.Column(db.Integer)
  committed_school_id = db.Column(db.Integer, db.ForeignKey('school.id'))

# class Watchlists(db.Model):
  
#class Offers(db.Model):
