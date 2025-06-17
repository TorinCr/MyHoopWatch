from flask import Blueprint, render_template
from .services.kenpom_engine import GetKPOY
from .services.kenpom_engine import PlayerDescriptions
from .api_helpers import APICalls
import json

from pathlib import Path

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
  from app import kenpom_browser

  players_df = GetKPOY.get_kpoy(kenpom_browser)
  players_list = players_df.to_dict('records')
  
  team_image_path = Path("app/static/data/team_images.json")
  image_path = Path("app/static/data/player_images.json")
  player_images = json.loads(image_path.read_text())
  team_images = json.loads(team_image_path.read_text())


  player_description = PlayerDescriptions.get_player_descriptions()


  return render_template('home.html', players = players_list, image = player_images, team_logo = team_images,  description = player_description)

@routes.route('/teams')
def teams():
  all_teams = APICalls.get_teams()
  
  print(f"Type of all_teams: {type(all_teams)}")
  print(f"Content: {all_teams}")


  return render_template('teams.html', teams=all_teams)