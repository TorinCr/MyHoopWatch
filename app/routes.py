from flask import Blueprint, render_template

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
  return render_template('home.html')

@routes.route('/players')
def players():
  return render_template('players.html')

@routes.route('/players/<int:player_id>')
def player_profile(player_id):
  return render_template('player_profile.html', player_id=player_id)