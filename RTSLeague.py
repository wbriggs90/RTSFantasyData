# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 22:19:04 2020

@author: Briggs
some usefule links:
Average draft position (ADP) - 'https://fantasyfootballcalculator.com/api/v1/adp/standard?teams=8&year=2019'
Expert consensus Rankings - 'https://partners.fantasypros.com/api/v1/consensus-rankings.php?sport=NFL&year=2019&week=0&id=1054&position=ALL&type=ST&scoring=HALF&filters=1:2:3:4:5:7:8:9:285:699&export=json'

"""

import requests

import datetime
from bs4 import BeautifulSoup
import pandas as pd
import csv
import urllib.parse
from io import StringIO
import time
import os
import json

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class ConfigError(Exception):
    pass

class privateLeague():
    '''create an instance of a league for the current year.
    to change year use the setyear function '''
  
    #teams = {}
      
    def __init__(self, config):
        
        LID =config['RTS']['LID']
        if LID == 'ffff':
            print('This is the wrong League ID for your league. you need to ', 
                  'change the contents of your config file')
            print()
            raise ConfigError
        
        UID = config['RTS']['UID']
        X = config['RTS']['X']
        TID = config['RTS']['TID']
        REALTIME = config['RTS']['REALTIME']
        Season = config['RTS']['Season']
        MyTeamName = config['RTS']['MyTeamName']
        FPKey = config['RTS']['FPKey']
        directory = 'cached-rankings-data'
        self.league_id = LID
        self.year = datetime.datetime.now().year # should change this from calendar year to be within the typical season timeframe
        self.url =  "https://www.rtsports.com/"
        self.user_id = UID
        self.parameters = {'LID': LID,
                           'UID': UID,
                           'X':X}
        self.FPKey = FPKey
        self.cookies =  {'REALTIME':REALTIME}
        self.scoreboard = [None] * 16
        
        self.slotnames = { 0:'QB', 1:'RB', 2:'WR', 3:'TE', 5:'D/ST', 4:'K'}
        self.slotvalues = {}
        for slotid in self.slotnames:
            self.slotvalues[self.slotnames[slotid]]=slotid
        self.rosters = {}
        self.teams = {}
        self.rosterFormat = {}
        self.leaguesettings = None
        self.boxscore = None
        self.season = Season
        self.MyTeamName = MyTeamName
        print()
        print('Getting the current Week')
        self.setCurrentWeek()
        print()
        print('Getting Rosters')
        self.Rosters = self.getRosters(self.CurrentWeek)
        print(self.Rosters)
        self.Rankings = self.getROSECR(directory)
        self.MyRoster = self.Rosters[self.Rosters['ffl-team']==self.MyTeamName]
        print()
        print('Getting Player Data')
        self.Players = self.getPlayerData()
        
        self.Players = pd.merge(self.Players,self.Rosters,how='outer',on='Player')
        self.Players = pd.merge(self.Players,self.Rankings,how='outer',on='Player')
        self.Players = pd.merge(self.Players,self.getWeeklyECR(directory),how='outer',on='Player')
        self.Players.sort_values(by='rank_ecr',inplace=True)
        self.Players['r2p_pts'] = pd.to_numeric(self.Players['r2p_pts'], errors='coerce')
        self.Players['Weekly Projection'] = pd.to_numeric(self.Players['Weekly Projection'], errors='coerce')
        print()
        print('Getting Rankings')
        
        
    #%% SET VALUES
        
    def setCurrentWeek(self):
       data = requests.get(self.url +'football/lineup.php',
                           params=self.parameters,
                           cookies=self.cookies)
       if data == None:
           print("Failed to get Current Week")
           
       soup = BeautifulSoup(data.content, 'html.parser')
       
       week = soup.find(class_='header-notes hidden-tn')
       print(week.string)
       if week.string[5:14]=='Preseason':
           print('setting week as week 0...')
           currentweek = 0
       else:
           currentweek = int(week.string[10:12])
       self.CurrentWeek = currentweek
       return      
    #%% GET RTS DATA
    def getTransactions(self,Week):
        '''
        Parameters
        ----------
        Week : int
            What week do you want transactions for?

        Returns
        -------
        data : TYPE
            Dataframe with columns
            ['Action','Team','Player','Type','Week','Date','Status']
        '''

        csvparams={'CID':0,'FWK':Week,'CSV':'YES'}
        csvparams.update(self.parameters)

        data = requests.get(self.url +'football/report-transactions.php',
                           params=csvparams,
                           cookies=self.cookies).text
   
        #print(data)
        
        data = pd.read_csv(StringIO(data),skiprows=0,header=None)
        #print(data)
        data.columns = ['Action','Team','Player','Type','Week','Date','Status']
        
        data = data.set_index('Date')
        data.index = data.index.str.replace(' II','',regex=True)
        data.index = data.index.str.replace(' V','',regex=True)
        data.index = data.index.str.replace(' IV','',regex=True)
        data.index = data.index.str.replace(' Jr.','',regex=True)
        data.index = data.index.str.replace('  ',' ',regex=True)
        data.index = data.index.str.replace('.','',regex=True)
        return data
        
    def getRosters(self,Week):
        '''
        Parameters
        ----------
        Week : TYPE
            DESCRIPTION.

        Returns
        -------
        data : TYPE
            DESCRIPTION.

        '''

        csvparams={'CID':0,'FWK':Week,'CSV':'YES'}
        csvparams.update(self.parameters)

        data = requests.get(self.url +'football/report-rosters.php',
                           params=csvparams,
                           cookies=self.cookies).text
        if len(data) == 0:
            print('no rosters yet')
            return
        print('retrieved roster data')
        
        data = pd.read_csv(StringIO(data),skiprows=0,header=None)
        
        data.columns = ['ffl-team','Player','Position','nfl-team','Roster Status','']
        data.drop(columns=['','Position','nfl-team'], inplace=True)
        data = data.set_index('Player')
        data.index = data.index.str.replace(' II','',regex=True)
        data.index = data.index.str.replace(' V','',regex=True)
        data.index = data.index.str.replace(' IV','',regex=True)
        data.index = data.index.str.replace(' Jr.','',regex=True)
        data.index = data.index.str.replace('  ',' ',regex=True)
        data.index = data.index.str.replace('.','',regex=True)
        return data
    
    def getPlayerData(self):
        '''
        Gets all players including free agents from RTS site
        Returns
        -------
        players : TYPE
            DESCRIPTION.
        '''
        players = pd.DataFrame()
        for Position in self.slotnames:
            csvparams={'CONF':0,'CSV':'YES','POS':Position, 'STATS':'FFL','TEAM':-1,'SEASON': self.season}
            csvparams.update(self.parameters)

            data = requests.get(self.url +'football/report-top-players.php',
                           params=csvparams,
                           cookies=self.cookies).text
        
            data = pd.read_csv(StringIO(data))
            data = data.iloc[:,0:10]
            data.columns = ["Rank","Player","Position","nfl-team","Bye","injury","ffl-team","pts","avg","avg-3wk"]
            data.drop(columns=['ffl-team'], inplace=True)
            data = data.set_index('Player')
            data.index = data.index.str.replace(' II','',regex=True)
            data.index = data.index.str.replace(' V','',regex=True)
            data.index = data.index.str.replace(' IV','',regex=True)
            data.index = data.index.str.replace(' Jr.','',regex=True)
            data.index = data.index.str.replace('  ',' ',regex=True)
            data.index = data.index.str.replace('.','',regex=True)
            players = players.append(data)
            
            
        return players
    
    
    
   
    
    #%% FREE AGENT STUFF
   
    #%%  RANKINGS

        
    def getDraftECR(self):
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
            params = {'sport':'NFL','year':self.year,'week':0,
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

    def getROSECR(self,directory):
        print('*************Getting ROS Rankings*************')
        headers = {'x-api-key': self.FPKey}
    
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
            df[['r2p_pts']] = df[['stats']].applymap(lambda x: x['points'])
            df.sort_values(by='r2p_pts',inplace=True,ascending=False)
            df['rank_ecr'] = range(1, len(df) + 1)
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

    
    def getWeeklyECR(self,directory):
        print('*************Getting Weekly Rankings*************')
        headers = {'x-api-key': self.FPKey}

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
                                 'rank_ecr':'Weekly ECR'},inplace=True)
        
        rankings = rankings.set_index('Player')
        rankings.index = rankings.index.str.replace(' II','',regex=True)
        rankings.index = rankings.index.str.replace(' V','',regex=True)
        rankings.index = rankings.index.str.replace(' IV','',regex=True)
        rankings.index = rankings.index.str.replace(' Jr.','',regex=True)
        rankings.index = rankings.index.str.replace('  ',' ',regex=True)
        #rankings.index = rankings.index.str.replace(' .',' ',regex=True)
        rankings = rankings[['Weekly Projection',
                             'Weekly ECR',
                             'start_sit_grade',]]
        return rankings

        
    #%%  SCRIPTS
        
        
    def getBestAvailable(self,Pos):
            
        Best = self.Players.loc[(self.Players['Position']==Pos)&
                     (self.Players['ffl-team'].isnull())]
        
        return Best.iloc[0]
    

    
    def positionalAnalysis(self,Pos):
        """
        

        Args:
            Pos (TYPE): The position to analyze.

        Returns:
            TYPE: DESCRIPTION.

        """
        messages = ''
        weeklypoints = 0
        df = self.Players.loc[(self.Players['Position']==Pos)]
        #print(df)
        mydf = df.loc[((df['ffl-team']==self.MyTeamName)),
                    ['ffl-team','rank_ecr','r2p_pts','Weekly Projection','Weekly ECR']]
        
        freedf = df.loc[((df['ffl-team'].isnull())),
                    ['ffl-team','rank_ecr','r2p_pts','Weekly Projection','Weekly ECR']]
        
        # First analysis will be to check the weekly projection. 
        
        # sort my players from worst to best
        mydf.sort_values(by=['Weekly Projection'], ascending=True,inplace = True)
        freedf.sort_values(by=['Weekly Projection'], ascending=False,inplace = True)
        for n in range(len(mydf)):
            
            #find the nth best free agent and compare to the nth worst on my team
            freeagent = freedf.iloc[n]
            myplayer = mydf.iloc[n]
            
            #then compare how many points I might gain this week from this transaction
            pointdelta = float(freeagent['Weekly Projection'])-float(myplayer['Weekly Projection'])
        
            if pointdelta>0:
                message = 'Drop ' + str(myplayer.name) + ' for ' + str(freeagent.name) + ' to gain ' + str(pointdelta) + ' points this week'
                messages = messages + message +  '\n'
                print(message)
                weeklypoints += pointdelta
                #if negative then break
            else:
                break
        
            
            
            
        # Second analysis will be to check the seasonal rank.
        mydf.sort_values(by=['r2p_pts'], ascending=True,inplace = True)
        freedf.sort_values(by=['r2p_pts'], ascending=False,inplace = True)
        totalpoints = 0
        for n in range(len(mydf)):
            
            #find the nth best free agent and compare to the nth worst on my team
            freeagent = freedf.iloc[n]
            myplayer = mydf.iloc[n]
            
            #then compare how many points I might gain this week from this transaction
            pointdelta = float(freeagent['r2p_pts'])-float(myplayer['r2p_pts'])
            if pointdelta>0:
                message = 'Drop ' + str(myplayer.name) + ' for ' + str(freeagent.name) + ' to gain ' + str(pointdelta) + ' points this season'
                messages = messages + message + '\n'
                print(message)
                totalpoints += pointdelta
                #if negative then break
            else:
                break
        
        
        df = df.loc[((df['ffl-team'].isnull()) | 
                      (df['ffl-team']==self.MyTeamName)),
                    ['ffl-team','rank_ecr','r2p_pts','Weekly Projection','Weekly ECR']]
        
        
        
        return [df.head(20), totalpoints, weeklypoints,messages]
    
    def getMyWorst(self,Pos):
        df = self.Players.loc[(self.Players['ffl-team']==self.MyTeamName)&(self.Players['Position']==Pos)]
        Worst = df.loc[df['rank_ecr']==df['rank_ecr'].max()]
        
        return Worst
    
    def saveAllData(self,filename):
        self.Players.to_csv(filename)
        
        #%% Archive methods
'''
     def getLineup(self):
       data = requests.get('https://www.fantasypros.com/nfl/rankings/ros-ppr-rb.php')
       if data == None:
           print("Failed to get Lineup Data")
           
       soup = BeautifulSoup(data.content, 'html.parser')
       
       lineup = soup.find(id='PageInner')
       return lineup
   
    
    
    def getRosterFormat(self):
       data = requests.get(self.url +'football/lineup.php',
                           params=self.parameters,
                           cookies=self.cookies)
       if data == None:
           print("Data Pull Failed")
           
       soup = BeautifulSoup(data.content, 'html.parser')
       roster = soup.find(class_='Starters')
       soup
       
       return roster
       
    def getStarters(self):
        
        data = requests.get(self.url +'football/lineup.php',
                           params=self.parameters,
                           cookies=self.cookies)
        if data == None:
           print("Data Pull Failed")
        
        soup = BeautifulSoup(data.content, 'html.parser')
       
        soup.find_all("a", attrs={"player-id": "nav", "data-foo": "value"})
        return team
    
    
    
    def getTeam(self):
        
        data = requests.get(self.url +'football/lineup.php',
                           params=self.parameters,
                           cookies=self.cookies)
        if data == None:
           print("Data Pull Failed")
        
        team = {}
        
        soup = BeautifulSoup(data.content, 'html.parser')
       
        for tag in soup.find_all('div',class_='row small Player'):
           position = tag.find('div',class_='Column ColPos pos-name')
           name = tag.find('div',class_='Column ColName')
           team[position.text] = name.text
           #print(name.text)
        return team
'''   



