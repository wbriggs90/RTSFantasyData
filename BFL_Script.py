# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 20:59:33 2020

@author: Briggs


"""

import RTSLeague as rt
import configparser as cp
import pickle
import time
import smtplib, ssl
import sys,os


#%%

scriptdir = os.path.dirname(sys.argv[0])
configpath = os.path.join(scriptdir, 'config_private.ini')

#%%
#instantiate a configparser and read in some parameters from an existing config file
config = cp.ConfigParser()
config.read(configpath)


#instantiate a league
league = rt.privateLeague(config)
print()


#save the current values for next time


#iterate through the positions
slotdata = {}
totalpoints = 0
weeklypoints = 0
summary = ''
datastr = ''
for slot in league.slotvalues:
    print("positional Analysis for ", slot)
    
    print()
    slotdata[slot],postotalpoints, posweeklypoints,msg = league.positionalAnalysis(slot)
    totalpoints+=postotalpoints
    weeklypoints += posweeklypoints
    print(slotdata[slot])
    summary = summary + msg
    datastr = datastr+str(slot)+ '\n'
    datastr = datastr+str(slotdata[slot])+ '\n \n'
    
#save all the data to a .csv file
league.saveAllData("data.csv")



