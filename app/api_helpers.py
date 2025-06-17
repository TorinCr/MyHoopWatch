import os
from dotenv import load_dotenv
import cbbd
import cbbd.configuration
import cbbd.api

load_dotenv()

class APICalls:
    @staticmethod
    def get_cbbd_client():
        """Create and return a configured CFBD API client"""
        try:
            configuration = cbbd.Configuration(
                access_token = os.getenv('COLLEGE_BB_API_KEY')
            )
            return cbbd.ApiClient(configuration)
        except Exception as e:
            print(f"Error creating API client: {e}")
            return None
    
    @staticmethod
    def get_teams(limit=50):
        """Get College Basketball Teams"""
        try:
            api_client = APICalls.get_cbbd_client()
            if not api_client:
                print("Failed to create API Client")
                return []
            
            with api_client as client:
                api_instance = cbbd.TeamsApi(client)
                teams = api_instance.get_teams()

                print(f"API returned {len(teams) if teams else 0} teams")
                return teams[:limit] if teams and len(teams) > limit else teams
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return []
        
    @staticmethod
    def get_team_stats(season=2025, conference=None):
        """Get detailed team statistics for offensive/defensive ratings"""
        return
    
    @staticmethod
    def get_player_season_stats(season=2025):
        """Get detailed player statistics for offensive/defenisve ratings"""
        return
    
    @staticmethod
    def get_player_shooting_stats(season=2025):
        return
    
    @staticmethod
    def get_adjusted_ratings(season=2025):
        return
    
    @staticmethod
    def get_rankings(season=2025, week=None):
        return
    
    @staticmethod
    def get_team_games(season=2025, team=None):
        return


            