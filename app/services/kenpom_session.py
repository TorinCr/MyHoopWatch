from kenpompy.utils import login
import os
from dotenv import load_dotenv

load_dotenv()
KENPOM_EMAIL = os.getenv('KENPOM_EMAIL')
KENPOM_PASSWORD = os.getenv('KENPOM_PASSWORD')

kenpom_browser = login(KENPOM_EMAIL, KENPOM_PASSWORD)