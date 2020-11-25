# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 20:59:33 2020

@author: Briggs


"""

import RTSLeague as rt

LID ='6779'
UID = 'a99e678d379292511bf10cb24dd93fb'
X = '922249'
TID = '4996321'
REALTIME = '848795-5edcae50b62a-f0efe4e66ecf529a01c8b6e642848ab07e2caaa84ec97da17e1b'
league = rt.privateLeague(LID,UID,X,REALTIME)

lineup = league.getLineup()
Team = league.getTeam()

csv = league.getRostersCSV(12)
