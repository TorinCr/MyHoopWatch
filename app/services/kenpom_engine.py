import sys
import kenpompy.summary as kp
import pandas as pd
from kenpompy.utils import login
from dotenv import load_dotenv
import os



class GetKPOY:
    def get_kpoy(kenpom_browser):
        kpoy_data = kp.get_kpoy(kenpom_browser)
        kpoy_df = kpoy_data[0]  # Extract DataFrame from list
        top10 = kpoy_df.head(10)
        return top10
    
class CalculateRatings:
    load_dotenv()

    KENPOM_EMAIL = os.getenv('KENPOM_EMAIL')
    KENPOM_PASSWORD = os.getenv('KENPOM_PASSWORD')

    login = login(KENPOM_EMAIL, KENPOM_PASSWORD)




class PlayerDescriptions:
    def get_player_descriptions():

        player_descriptions = {
        "cooper_flagg_duke_": "The consensus #1 NBA Draft pick who delivered the most dominant freshman season in recent memory. Flagg averaged 19.2 points, 7.5 rebounds, "
        "and 4.2 assists while shooting 48.1% from the field and 38.5% from three. His 42-point explosion against Notre Dame set new freshman scoring records for "
        "both Duke and the ACC, showcasing elite versatility as a 6'9\" forward who can handle, shoot, and defend multiple positions.",

        "johni_broome_auburn": "Different unique description...",

        "mark_sears_alabama": "Another unique description...",
        }
        
        return player_descriptions


    if __name__ == "__main__":
        get_player_descriptions()