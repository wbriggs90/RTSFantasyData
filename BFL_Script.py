# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 20:59:33 2020

@author: Briggs


"""

import RTSLeague as rt
import configparser as cp
import sys,os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

plt.close('all')


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

#%% Plot some data

# Create a PDF file to save the plots
pdf_pages = PdfPages('plots.pdf')

for slot in slotdata:
    df = slotdata[slot]
    # Create a custom plot with lines and dots
    fig = plt.figure(slot,figsize=(12, 6))
    
    # Iterate through each row in the DataFrame
    
    for i, row in df.iterrows():
        min_val = row['weekly_rank_min']
        max_val = row['weekly_rank_max']
        avg_val = row['Weekly ECR']
    
        # Plot a line from min to max
        plt.plot([min_val, max_val], [i, i], color='blue')
    
        # Plot a dot for the average
        plt.scatter(avg_val, i, color='red', marker='o')
        
      
    
    
    # Set the color of y-labels based on 'status'
    for i, team in enumerate(df['ffl-team']):
        if team == 'The Gingineer':
            plt.gca().get_yticklabels()[i].set_color('red')  # Color the y-label red for my players
        
    
    
    
    # Customize plot
    plt.title(slot)
    plt.xlabel('Rank Value')
    plt.yticks(np.arange(len(df)), df.index)  # Use row names as y-axis labels
    yticks = np.arange(len(df))
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    ytick_labels = [f"{label} ({number})" for label, number in zip(df.index, df['ros_rank_ecr'])]  # Combine label and number
    plt.yticks(yticks, ytick_labels)  # Use modified y-axis labels
    plt.subplots_adjust(left=0.2)
    # Show the plot
    plt.show()
    
    # Save the plot to the PDF
    pdf_pages.savefig(fig)
    
# Close the PDF file
pdf_pages.close()

