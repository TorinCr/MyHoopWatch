from flask import Blueprint, render_template
from .services.kenpom_engine import get_kpoy
from .services.kenpom_engine import statistical_excellence
from . services.kenpom_engine import get_player_descriptions
import json
from pathlib import Path

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
  from app import kenpom_browser

  players_df = get_kpoy(kenpom_browser)
  players_list = players_df.to_dict('records')
  
  team_image_path = Path("app/static/data/team_images.json")
  image_path = Path("app/static/data/player_images.json")
  player_images = json.loads(image_path.read_text())
  team_images = json.loads(team_image_path.read_text())


  after_top_10 = statistical_excellence()[:50]

  player_description = get_player_descriptions()


  return render_template('home.html', players = players_list, image = player_images, team_logo = team_images, top_50 = after_top_10, description = player_description)


@routes.route('/test-stats')
def test_stats():
    try:
        # Add debug prints to your statistical_excellence function
        result = statistical_excellence()
        return f"Success! Got {len(result)} players"
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"Error: {str(e)}<br><pre>{error_details}</pre>"