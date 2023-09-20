# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 22:19:04 2020

@author: Briggs
some useful links:
Average draft position (ADP) - 'https://fantasyfootballcalculator.com/api/v1/adp/standard?teams=8&year=2019'
Expert consensus Rankings - 'https://partners.fantasypros.com/api/v1/consensus-rankings.php?sport=NFL&year=2019&week=0&id=1054&position=ALL&type=ST&scoring=HALF&filters=1:2:3:4:5:7:8:9:285:699&export=json'

"""

import requests
import datetime
import pandas as pd
import time
import os
import json




   
    #%%  RANKINGS

    
def getDraftECR(FPKey,year):
    '''
    valid position codes:
        "QB, RB, WR, TE, K, OP, FLX, DST, IDP, DL, LB, DB, TK, TQB, TRB, TWR, TTE, TOL, HC, P"}
    
    Valid type codes:
            ST, weekly, Draft Half PPR, ROS
            ROS will give rest of season rankings
            weekly will give just this week
            I am not sure what the type is for?
            
    id: 1054
    
    Unused params
    'filters':'1:2:3:4:5:7:8:9:285:699',
       filters are a whitelist of 
Returns
    -------
    ecr : TYPE
        DESCRIPTION.

    '''

    rankings = pd.DataFrame()
    positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DST']
    
    for position in positions:
        print('getting draft rankings for ', position)
        params = {'sport':'NFL','year':year,'week':0,
                  'position':position,'id':1054,"ranking_type_name":"ros",'scoring':'PPR',
                  'export':'json'}
        
        url ='https://partners.fantasypros.com/api/v1/consensus-rankings.php' #?sport=NFL&year=2020&week=0&id=1054&position=ALL&type=ST&scoring=HALF&filters=1:2:3:4:5:7:8:9:285:699&export=json'
        
            
        data = requests.get(url,params=params)
        
        ecr = data.json()
        
        positionrankings = pd.DataFrame(ecr['players'])
        
        rankings = rankings.append(positionrankings)
    
    rankings.drop(columns=['player_id',  'sportsdata_id', 
    'player_yahoo_positions', 'player_page_url','player_short_name',
    'player_positions','player_filename', 'player_square_image_url',
    'player_image_url','player_yahoo_id', 'cbs_player_id',
    'player_bye_week','player_owned_yahoo','player_owned_espn',
    'player_position_id','player_eligibility','player_eligibility'], inplace=True )
    
    rankings.rename(columns={'player_name':'Player'},inplace=True)
    rankings = rankings.set_index('Player')
    #Sanitize some data
    rankings.index = rankings.index.str.replace(' II','',regex=True)
    rankings.index = rankings.index.str.replace(' V','',regex=True)
    rankings.index = rankings.index.str.replace(' IV','',regex=True)
    rankings.index = rankings.index.str.replace(' Jr.','',regex=True)
    rankings.index = rankings.index.str.replace('  ',' ',regex=True)
    rankings.index = rankings.index.str.replace('.','',regex=True)
    
    return rankings

def getROSECR(FPKey,directory):
    print('*************Getting ROS Rankings*************')
    headers = {'x-api-key': FPKey}

    #  'valid_format': 'QB, RB, WR, TE, K, OP, FLX, DST, IDP, DL, LB, DB, TK, TQB, TRB, TWR, TTE, TOL, HC, P'}
    positions = ['QB','RB','WR','TE','K','DST']
    datadict = {}
    rankings = pd.DataFrame()
        
    for position in positions:
        print('Loading data for ',position)
        filename = os.path.join(directory, position+'-ROS.txt')
        time_difference = datetime.timedelta(minutes=0)
        nofile=0
        try:
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
                timestamp_str = data.get("timestamp", "")
                timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                # Calculate the current time
                current_time = datetime.datetime.now()
    
                # Calculate the time difference
                time_difference = current_time - timestamp
                
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
            nofile = 1    
    
        
            # Check if the timestamp is older than 30 minutes
        if (time_difference > datetime.timedelta(minutes=30) or nofile):
            print("The data is older than 30 minutes or the file doesn't exist")
            params = {'position': position,'scoring':'PPR'}
            url ='https://api.fantasypros.com/public/v2/json/nfl/2023/projections'
            
            print('getting Fantasy Pros data for ',position)
            time.sleep(1)  # not supposed to poll the api faster than 1 second
            response = requests.get(url,headers=headers,params=params)
            
            data = response.json()
            data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print('saving json data')
            with open(filename, "w") as fp:
                json.dump(data, fp)
                
                
        else:
            print("The data is NOT older than 30 minutes.")
            print("using Loaded data")
        
        playerdata = data['players']
        
        filename = os.path.join(directory, position+'-ROS.csv')
        datadict[position]=playerdata
        
        print('saving player data to csv')
        df = pd.DataFrame(playerdata)
        df.set_index('name')
        df[['ros_projection']] = df[['stats']].applymap(lambda x: x['points'])
        df.sort_values(by='ros_projection',inplace=True,ascending=False)
        df['ros_rank_ecr'] = range(1, len(df) + 1)
        df.to_csv(filename)
    
        
        #append this data to the output
        rankings = pd.concat([df,rankings])
        print()
    rankings.drop(columns=['fpid', 'mflid', 'filename'], inplace=True )
    
    rankings.rename(columns={'name':'Player'},inplace=True)
    rankings = rankings.set_index('Player')
    
    
    #Sanitize some data
    rankings.index = rankings.index.str.replace(' II','',regex=True)
    rankings.index = rankings.index.str.replace(' V','',regex=True)
    rankings.index = rankings.index.str.replace(' IV','',regex=True)
    rankings.index = rankings.index.str.replace(' Jr.','',regex=True)
    rankings.index = rankings.index.str.replace('  ',' ',regex=True)
    rankings.index = rankings.index.str.replace('.','',regex=True)
    
    rankings.to_csv(os.path.join(directory,'ROS-rankings.csv') )
    
    return rankings


def getWeeklyECR(FPKey,directory):
    print('*************Getting Weekly Rankings*************')
    headers = {'x-api-key': FPKey}

    #  'valid_format': 'QB, RB, WR, TE, K, OP, FLX, DST, IDP, DL, LB, DB, TK, TQB, TRB, TWR, TTE, TOL, HC, P'}
    positions = ['qb','rb','wr','te','k','dst']
    datadict = {}
    rankings = pd.DataFrame()
        
    for position in positions:
        print('Loading data for ',position)
        filename = os.path.join(directory, position+'-weekly.txt')
        time_difference = datetime.timedelta(minutes=0)
        nofile=0
        try:
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
                timestamp_str = data.get("timestamp", "")
                timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                # Calculate the current time
                current_time = datetime.datetime.now()
    
                # Calculate the time difference
                time_difference = current_time - timestamp
                
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
            nofile = 1    
    
             
             
    
        
        
            # Check if the timestamp is older than 30 minutes
        if (time_difference > datetime.timedelta(minutes=30) or nofile):
            print("The data is older than 30 minutes or the file doesn't exist")
            #params = {'position': position,'scoring':'PPR','type':'Weekly','week':1} 
            params = {'position': position,'scoring':'PPR','week':1}
            url ='https://api.fantasypros.com/public/v2/json/nfl/2023/consensus-rankings'
            
            print('getting Fantasy Pros data for ',position)
            time.sleep(1)  # not supposed to poll the api faster than 1 second
            response = requests.get(url,headers=headers,params=params)
            
            data = response.json()
            data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print('saving json data')
            with open(filename, "w") as fp:
                json.dump(data, fp)
                
                
        else:
            print("The data is NOT older than 30 minutes.")
            print("using Loaded data")
        
        playerdata = data['players']
        
        filename = os.path.join(directory, position+'-weekly.csv')
        datadict[position]=playerdata
        
        print('saving player data to csv')
        df = pd.DataFrame(playerdata)
        df.set_index('player_name')
        df.to_csv(filename)
    
        
        #append this data to the output
        rankings = pd.concat([df,rankings])
        print()
        
        
    #return the rankings dataframe
    rankings.to_csv(os.path.join(directory,'weekly-rankings.csv') )
    rankings.rename(columns={'player_name':'Player',
                             'r2p_pts':'Weekly Projection',
                             'rank_ecr':'Weekly ECR',
                             'rank_min':'weekly_rank_min',
                             'rank_max':'weekly_rank_max'},inplace=True)
    
    rankings = rankings.set_index('Player')
    
    rankings['weekly_rank_max'] = pd.to_numeric(rankings['weekly_rank_max'], errors='coerce')
    rankings['weekly_rank_min'] = pd.to_numeric(rankings['weekly_rank_min'], errors='coerce')
    rankings['Weekly ECR'] = pd.to_numeric(rankings['Weekly ECR'], errors='coerce')
    
    
    rankings.index = rankings.index.str.replace(' II','',regex=True)
    rankings.index = rankings.index.str.replace(' V','',regex=True)
    rankings.index = rankings.index.str.replace(' IV','',regex=True)
    rankings.index = rankings.index.str.replace(' Jr.','',regex=True)
    rankings.index = rankings.index.str.replace('  ',' ',regex=True)
    #rankings.index = rankings.index.str.replace(' .',' ',regex=True)
    rankings = rankings[['Weekly Projection',
                         'Weekly ECR',
                         'start_sit_grade',
                         'weekly_rank_min',
                         'weekly_rank_max',]]
    return rankings

    
