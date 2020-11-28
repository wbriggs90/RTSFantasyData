# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 22:19:04 2020

@author: Briggs
https://docs.google.com/spreadsheets/d/e/2PACX-1vSFim9JZWYDHCB8YwJnCG2T1yKhTgas750EbM7vnraXI1g5hFnsEY3QjNepYoFpKitUizzQbbUhAHzm/pub?output=csv

"""

import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import csv
import urllib.parse
from io import StringIO


slotnames = { 0:'QB', 1:'RB', 2:'WR', 3:'TE', 5:'DEF', 4:'KICKER'}
slotvalues = {}
for slotid in slotnames:
    slotvalues[slotnames[slotid]]=slotid
    
    


class privateLeague():
    '''create an instance of a league for the current year.
    
    to change year use the setyear function'''
    
    
    
        
    
    #teams = {}
      
    def __init__(self, LID, UID,X,REALTIME,Season,MyTeamName):
        self.league_id = LID
        self.year = datetime.datetime.now().year # should change this from calendar year to be within the typical season timeframe
        self.url =  "https://www.rtsports.com/"
        self.user_id = UID
        self.parameters = {'LID': LID,
                           'UID': UID,
                           'X':X}
        self.cookies =  {'REALTIME':REALTIME}
        self.scoreboard = [None] * 16
        self.rosters = {}
        self.teams = {}
        self.rosterFormat = {}
        self.leaguesettings = None
        self.boxscore = None
        self.season = Season
        self.MyTeamName = MyTeamName
        print('Getting the current Week')
        self.setCurrentWeek()
        print('Getting Rosters')
        self.Rosters = self.getRosters(self.CurrentWeek)
        self.MyRoster = self.Rosters[self.Rosters['ffl-team']==self.MyTeamName]
        print('Getting Player Data')
        self.Players = self.getPlayerData()
        self.Players = self.Players.merge(self.Rosters,how='outer')
        self.Players.sort_values(by='Rank',inplace=True)
        print('Getting Rankings')
        self.Rankings = self.getRankings()

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
       currentweek = int(week.string[10:12])
       self.CurrentWeek = currentweek
       return      
    #%% GET RTS DATA
   
    def getRosters(self,Week):

        csvparams={'CID':0,'FWK':Week,'CSV':'YES'}
        csvparams.update(self.parameters)

        data = requests.get(self.url +'football/report-rosters.php',
                           params=csvparams,
                           cookies=self.cookies).text
   
        

        data = pd.read_csv(StringIO(data))
        data.columns = ['ffl-team','Player','Position','nfl-team','Roster Status','']
        data = data.set_index('Player')
        del data['']
        return data
    
    def getPlayerData(self):
        players = pd.DataFrame()
        for Position in slotnames:
            csvparams={'CONF':0,'CSV':'YES','POS':Position, 'STATS':'FFL','TEAM':-1,'SEASON': self.season}
            csvparams.update(self.parameters)

            data = requests.get(self.url +'football/report-top-players.php',
                           params=csvparams,
                           cookies=self.cookies).text
        
            data = pd.read_csv(StringIO(data))
            data = data.iloc[:,0:10]
            data.columns = ["Rank","Player","Position","nfl-team","Bye","injury","ffl-team","pts","avg","avg-3wk"]
            data = data.set_index('Player')
            players = players.append(data)
            
            
        return players
    
    
    
    
    
    
    #%% FREE AGENT STUFF
   
    #%%  RANKINGS
    def getRankings(self):
        QBURL = 'https://www.fantasypros.com/nfl/rankings/qb.php'
        RBURL = 'https://www.espn.com/fantasy/football/story/_/page/WeeklyRanks2020RBPPR'
        KURL = 'https://www.espn.com/fantasy/football/story/_/page/WeeklyRanks2020KPPR/fantasy-football-weekly-kicker-rankings-2020'
        DEFURL = 'https://www.espn.com/fantasy/football/story/_/page/WeeklyRanks2020DSTPPR/fantasy-football-weekly-d-st-rankings-2020'
        WRURL = 'https://www.espn.com/fantasy/football/story/_/page/WeeklyRanks2020WRPPR/fantasy-football-weekly-wide-receiver-ppr-rankings-2020'
        TEURL = 'https://www.espn.com/fantasy/football/story/_/page/WeeklyRanks2020TEPPR/fantasy-football-weekly-tight-ends-ppr-rankings-2020'
        urls = [QBURL]
        #urls = [QBURL,RBURL,KURL,DEFURL,WRURL,TEURL]
        rankings = pd.DataFrame()

        for url in urls:
            
            html = requests.get(url)
            
            if html == None:
                print("Failed to get Rankings Data")
            
            soup = BeautifulSoup(html.content, 'html.parser')
           
            rankingsraw = soup.find_all(class_='player-row')
           
        return rankings
        
        
    #%%  SCRIPTS
        
        
        
        
        
        #%% Archive methods
'''
     def getLineup(self):
       data = requests.get(self.url +'football/lineup.php',
                           params=self.parameters,
                           cookies=self.cookies)
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