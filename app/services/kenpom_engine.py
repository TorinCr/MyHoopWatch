import kenpompy.summary as kp
import pandas as pd

metrics = {
    "ortg": "ORtg",
    "min": "Min",
    "efg": "eFG",
    "poss": "Poss",
    "shots": "Shots",
    "or": "OR",
    "dr": "DR",
    "to": "TO",
    "arate": "ARate",
    "blk": "Blk",
    "ftrate": "FTRate",
    "stl": "Stl",
    "ts": "TS",
    "fc40": "FC40",
    "fd40": "FD40",
    "2p": "2P",
    "3p": "3P",
    "ft": "FT",
}

def get_kpoy(kenpom_browser):
    from app import kenpom_browser

    kpoy_data = kp.get_kpoy(kenpom_browser)
    kpoy_df = kpoy_data[0]

    top10 = kpoy_df.head(10)
    
    return top10

def kenpom_(metrics):
    return