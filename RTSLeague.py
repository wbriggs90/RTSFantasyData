# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 22:19:04 2020

@author: Briggs


"""

import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import csv
import urllib.parse
from io import StringIO


 

class privateLeague():
    '''create an instance of a league for the current year.
    
    to change year use the setyear function'''
    
    slotnames = {20:"BENCH", 0:'QB', 2:'RB', 4:'WR', 6:'TE', 23:'FLEX', 16:'DEF', 17:'KICKER'}
    slotvalues = {}
    for slotid in slotnames:
        slotvalues[slotnames[slotid]]=slotid
        
    
    #teams = {}
      
    def __init__(self, LID, UID,X,REALTIME):
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

    #%% SET VALUES
    def setYear(self, year):
        '''The reason this is a method is for future implementation of fault checking'''
        self.year = year
        
    #%% GET DATA
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
           print(name.text)
        return team
   
    def getRostersCSV(self,Week):

        csvparams={'CID':0,'FWK':Week,'CSV':'YES'}
        csvparams.update(self.parameters)

        data = requests.get(self.url +'football/report-rosters.php',
                           params=csvparams,
                           cookies=self.cookies).text
        

        print(data)
        data = pd.read_csv(data)
        data.columns = ['Team Name']
        
        return data
    
    
    #%% FREE AGENT STUFF
   
    #%%  RANKINGS
    
    #%%  SCRIPTS
