# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 22:41:29 2023

@author: Will Briggs
"""
import os
import rankings
from yfpy import Data
from yfpy.logger import get_logger
from yfpy.query import YahooFantasySportsQuery
from dotenv import load_dotenv
from pathlib import Path


consumer_key= "dj0yJmk9Qmp3VUE5VmpWYTRRJmQ9WVdrOWVVZFZhVTVYUlVrbWNHbzlNQT09JnM9Y29uc3VtZXJzZWNyZXQmc3Y9MCZ4PWFh"
consumer_secret= "006891166cd6339cf440cd26d9a1e5cb29c063c6"



# set desired season year
season = 2023

# set desired Yahoo Fantasy Sports game code
game_code = "nfl"

# set desired Yahoo Fantasy Sports game ID (see the get_all_yahoo_fantasy_game_keys query to retrieve values)
game_id = 423  # NFL - 2023
 
# set desired league ID (see README.md for finding value)
league_id = "67339"  # NFL - 2023

# set desired team ID within desired league
team_id = 12  

# set desired team name within desired league
team_name = "Gingineer"  # NFL

# set the maximum number players you wish the get_league_players query to retrieve
league_player_limit = 101





# set directory location of private.json for authentication
auth_dir = Path(__file__).parent / "auth"

# set target directory for data output
data_dir = Path(__file__).parent / "output"

# create YFPY Data instance for saving/loading data
data = Data(data_dir)




# configure the Yahoo Fantasy Sports query (change all_output_as_json_str=True if you want to output JSON strings)
yahoo_query = YahooFantasySportsQuery(
    auth_dir,
    league_id,
    game_id=game_id,
    game_code=game_code,
    offline=False,
    all_output_as_json_str=False,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    browser_callback=True
)

teams = yahoo_query.get_league_teams()
for team in teams:
    print()
    print(team.name)
    team.roster = yahoo_query.get_team_roster_player_stats(team.team_id)
    for player in team.roster:
        print(player.name.full,' ',player.player_id)
        
