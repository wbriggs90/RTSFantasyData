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


port = 465  # For SSL


scriptdir = os.path.dirname(sys.argv[0])
configpath = os.path.join(scriptdir, 'config_private.ini')


#%%
#instantiate a configparser and read in some parameters from an existing config file
config = cp.ConfigParser()
config.read(configpath)
password  = config['RTS']['EmailPW']
SA = config['RTS']['SA']
DA = config['RTS']['DA']

# Create a secure SSL context for email
context = ssl.create_default_context()

#instantiate a league
league = rt.privateLeague(config)
print()

#read in some pickled variables to create conditions on whether to notify me




#save the current values for next time


# set up the message subject and header
mail = """\
Subject: RTS Transaction Opportunity
   
 
Info Below

"""

#iterate through the positions
slotdata = {}
totalpoints = 0
weeklypoints = 0
summary = ''
datastr = ''
for slot in league.slotvalues:
    print("positional Analysis for ", slot)
    league.positionalAnalysis(slot)
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

try:
    oldweeklypoints,oldtotalpoints,lasttime = pickle.load(open("tran.p","rb"))
except:
    pickle.dump([weeklypoints,totalpoints,time.time()], open("tran.p","wb"))
    oldweeklypoints,oldtotalpoints,lasttime = pickle.load(open("tran.p","rb"))
pickle.dump([weeklypoints,totalpoints,time.time()], open("tran.p","wb")) 
# only email if the totalpoints for the week or season have changed or if a day has passed
# this could be because of a transaction or ranking change
timesincelast = time.time()-lasttime

if (oldweeklypoints != weeklypoints or
    oldtotalpoints != totalpoints or
    timesincelast>86400):
    print("emailing")
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(SA, password)
        server.sendmail(SA,DA,mail+summary+datastr)
else:
    print('no changes')


