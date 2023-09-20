# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 22:19:04 2020

@author: Briggs
some useful links:
Average draft position (ADP) - 'https://fantasyfootballcalculator.com/api/v1/adp/standard?teams=8&year=2019'
Expert consensus Rankings - 'https://partners.fantasypros.com/api/v1/consensus-rankings.php?sport=NFL&year=2019&week=0&id=1054&position=ALL&type=ST&scoring=HALF&filters=1:2:3:4:5:7:8:9:285:699&export=json'

"""

import requests
import rankings
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
        
        if leaguetype = 'RTS':
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
            self.Rankings = rankings.getROSECR(self.FPKey,directory)
            self.MyRoster = self.Rosters[self.Rosters['ffl-team']==self.MyTeamName]
            print()
            print('Getting Player Data')
            self.Players = self.getPlayerData()
            print()
            print('Getting Rankings')
            self.Players = pd.merge(self.Players,self.Rosters,how='outer',on='Player')
            self.Players = pd.merge(self.Players,self.Rankings,how='outer',on='Player')
            self.Players = pd.merge(self.Players,rankings.getWeeklyECR(self.FPKey,directory),how='outer',on='Player')
            self.Players.sort_values(by='ros_rank_ecr',inplace=True)
            self.Players['ros_projection'] = pd.to_numeric(self.Players['ros_projection'], errors='coerce')
            self.Players['Weekly Projection'] = pd.to_numeric(self.Players['Weekly Projection'], errors='coerce')
            #if any of the weekly rankings are NaN then replace them with the ROS ranking
            self.Players['weekly_rank_min'].fillna(self.Players['ros_rank_ecr'], inplace=True)
            self.Players['weekly_rank_max'].fillna(self.Players['ros_rank_ecr'], inplace=True)
            self.Players['Weekly ECR'].fillna(self.Players['ros_rank_ecr'], inplace=True)
        else:
            auth_dir
            league_id = config['Yahoo']['consumer_key']
            game_key = "423"
            game_id = 423
            game_code = "nfl"
            consumer_key = config['Yahoo']['LID']
            consumer_secret = config['Yahoo']['consumer_secret']
            yahoo_query = YahooFantasySportsQuery(auth_dir,
                                                league_id,
                                                game_id=game_id,
                                                game_code=game_code,
                                                offline=False,
                                                all_output_as_json_str=False,
                                                consumer_key=os.environ["YFPY_CONSUMER_KEY"],
                                                consumer_secret=os.environ["YFPY_CONSUMER_SECRET"],
                                                browser_callback=True)
        
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
                    ['ffl-team','ros_rank_ecr','ros_projection','Weekly Projection','Weekly ECR']]
        
        freedf = df.loc[((df['ffl-team'].isnull())),
                    ['ffl-team','ros_rank_ecr','ros_projection','Weekly Projection','Weekly ECR']]
        
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
        mydf.sort_values(by=['ros_projection'], ascending=True,inplace = True)
        freedf.sort_values(by=['ros_projection'], ascending=False,inplace = True)
        totalpoints = 0
        for n in range(len(mydf)):
            
            #find the nth best free agent and compare to the nth worst on my team
            freeagent = freedf.iloc[n]
            myplayer = mydf.iloc[n]
            
            #then compare how many points I might gain this week from this transaction
            pointdelta = float(freeagent['ros_projection'])-float(myplayer['ros_projection'])
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
                    ['ffl-team','ros_rank_ecr','ros_projection',
                     'Weekly Projection','Weekly ECR', 'weekly_rank_min', 'weekly_rank_max']]
        
        
        
        return [df.head(20), totalpoints, weeklypoints,messages]
    
    def getMyWorst(self,Pos):
        df = self.Players.loc[(self.Players['ffl-team']==self.MyTeamName)&(self.Players['Position']==Pos)]
        Worst = df.loc[df['rank_ecr']==df['rank_ecr'].max()]
        
        return Worst
    
    def saveAllData(self,filename):
        self.Players.to_csv(filename)
        


