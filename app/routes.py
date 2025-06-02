from flask import Blueprint, render_template
from .services.kenpom_engine import get_kpoy


routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
  from app import kenpom_browser
  players_df = get_kpoy(kenpom_browser)
  players_list = players_df.to_dict('records')
  return render_template('home.html', players = players_list)

'''
@routes.route('/player/<player_id>')
def player_profile(player_id):
  player = get_player_by_id(player_id)
  return render_template("player_profile.html", player_id=player_id)
'''