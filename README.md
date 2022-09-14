# RTSFantasyData
Software to pull league information and use it to make informed roster moves for Realtime Fantasy Sports Leagues


The following is how to instantiate a league object:
```python
import RTSLeague as rt
import configparser as cp

config = cp.ConfigParser()
config.read("config_private.ini")

league = rt.privateLeague(config)
```
the output is:
```
Getting the current Week
FFL: Week 2 | NFL: Week 2

Getting Rosters

Getting Player Data

Getting Rankings
```


Slot names are used to query statistics for particular positions.  you must use the expected names for each position:
```python
self.slotnames = { 0:'QB', 1:'RB', 2:'WR', 3:'TE', 5:'D/ST', 4:'K'}
```


The following shows how to evaluate all the available Quarterbacks against your own.
```python
slot = "QB"
print("positional Analysis for ", slot)
print(league.positionalAnalysis(slot))
print()

```

the output is:
```
positional Analysis for  QB
                      ffl-team  rank_ecr Weekly Projection
Player                                                    
Justin Fields              NaN      12.0              16.1
Kirk Cousins               NaN      13.0              19.3
Tua Tagovailoa             NaN      16.0              16.5
Trevor Lawrence            NaN      17.0              15.9
Jameis Winston             NaN      18.0              16.8
Matt Ryan                  NaN      19.0              16.0
Daniel Jones               NaN      20.0              15.2
Dak Prescott     The Gingineer      21.0               1.1
Jared Goff                 NaN      22.0              15.8
Carson Wentz               NaN      23.0              17.2
Mac Jones                  NaN      24.0              13.8
Ryan Tannehill             NaN      25.0              14.9
Baker Mayfield             NaN      26.0              14.6
Davis Mills                NaN      27.0              14.3
Marcus Mariota             NaN      28.0              15.5
Deshaun Watson             NaN      29.0               NaN
Zach Wilson                NaN      30.0               NaN
Jacoby Brissett            NaN      31.0              13.0
Kenny Pickett              NaN      33.0               1.3
Geno Smith                 NaN      34.0              13.5
```

The following will save all data to the working directory with the given name "data.csv"
```python
league.saveAllData("data.csv")
```


The following will show you the transactions for a given week
```python
transactions = league.getTransactions(1)
```

the output is:
```
"On I/R","The Wowie Zowies","Brian Robinson Jr. RB WAS WAS","Owner","Week 1","Mon Sep 5 9:58pm ET","official"
"On I/R","The Gingineer","Dak Prescott QB DAL DAL","Owner","Week 2","Tue Sep 13 10:02pm ET","official"
"On I/R","Team Beezo","Elijah Mitchell RB SF SF","Owner","Week 2","Tue Sep 13 6:38pm ET","official"
```




