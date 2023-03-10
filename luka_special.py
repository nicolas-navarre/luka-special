#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Created on Tue May 17 22:26:30 2022

@author: navarre
"""

import pandas as pd
import time
import warnings
warnings.filterwarnings('ignore')

# useful link for getting just half
# https://github.com/swar/nba_api/issues/74

from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import boxscoretraditionalv2


#%%
# add in any season you want. 20th century seasons are 21960, 21961,..
seasons = []

# 1983 is first year with games
# let's go back to 95 to be sure
# maybe print out the year when it's done to a file. 
START_YEAR = 1983
END_YEAR = 2022 

# seasons.append('41993')
# seasons.append('51993')
# 1983-2021 reg and playoffs done for luka
# 1983-2009   reg and playoffs done for kobe
for year in range(START_YEAR, END_YEAR):
    seasons.append('2'+str(year)) # regular season
    seasons.append('4'+str(year)) # playoffs
    seasons.append('5'+str(year)) # not sure but they exist

the_special = pd.read_excel('special_games.xlsx')

problem_games = []
all_teams = teams.get_teams()
for season_year in seasons: 
    
    # reset game ids and points for each season.
    print(season_year)
    game_ids = pd.DataFrame()

    for team in all_teams: 
        team_name = team['full_name']
        print(team_name)
        team_id = team['id']
        
        # get game id of each team.
        team_games = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id).get_data_frames()[0]
        team_games = pd.DataFrame(team_games.loc[team_games['SEASON_ID'] == season_year])
        team_games = team_games[team_games['GAME_ID'].str.match('0')]
        
        game_ids = pd.concat([game_ids, team_games])
        
        # need this to not get shut out by the api
        time.sleep(0.750)
    
    # every game will be listed twice since two teams play in one game. drop the duplicates to
    # to  avoid double counting. 
    game_ids = game_ids.drop_duplicates(['GAME_ID'],keep='first')

    
    # just a catch all list to see if there are any data issues
    problem_games = []
    for game in game_ids['GAME_ID'].unique():
        print(game)
        try: 
            
            # get traditional box score data by game for just the first half
            trad_boxscore_ht = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id = game, end_period = '10', start_period = '1',
                                                                      start_range = '0', end_range = '14400',
                                                                      range_type = '2').get_data_frames()
            
            player_points_max = trad_boxscore_ht[0]['PTS'].max()
            team_points_min = trad_boxscore_ht[1]['PTS'].min()
            
            # if a player has more points than an entire team it's a Luka special
            if player_points_max >= team_points_min:
                the_special = the_special.append({'Game': game, "Type": "Luka Special"}, ignore_index=True)
                print(f'Luka special on game {game}!')
            
            
            # # get traditional box score data by game for just the second half
            # trad_boxscore_2nd = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id = game, end_period = '10', start_period = '1',
            #                                                           start_range = '14400', end_range = '28800',
            #                                                           range_type = '2').get_data_frames()
            
            # player_points_max_2nd = trad_boxscore_2nd[0]['PTS'].max()
            # team_points_min_2nd = trad_boxscore_2nd[1]['PTS'].min()
            
            # # if a player has more 2nd half points than an entire team it's a Kobe special
            # if player_points_max_2nd >= team_points_min_2nd:
            #     the_special = the_special.append({'Game': game, "Type": "Kobe Special"}, ignore_index=True)
            #     print(f'Kobe special on game {game}!')
            
        except:
            problem_games.append(game)
            continue
    

        # need this to not get shut out by the api
        time.sleep(0.750)
    
    the_special.to_excel('special_games2nd.xlsx')#, header=False, index=False)
    
