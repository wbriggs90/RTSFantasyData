# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 20:59:33 2020

@author: Briggs


"""

import RTSLeague as rt
import configparser as cp

config = cp.ConfigParser()

config.read("config_private.ini")



league = rt.privateLeague(config)
print()

for slot in league.slotvalues:
    print("positional Analysis for ", slot)
 
league.saveAllData("data.csv")