##-----------------------------------
## THIS PROGRAM CLEANS AND PREPARES THE OPEN POSTCODE DATA
## Daniel Han-Chen
##-----------------------------------

## Get libraries:

import pandas as pd
import numpy as np
from sciblox import *
data = read("data.csv")
from copy import copy

## Exclude columns:
def exc(x, l):
    if type(l) == str: l = [l]
    return x[diff(x.columns.tolist(),l)]

##-----------------------------------
## Explore some data to get Markov Modelling paramaters

x = copy(data)
x["income"]=(x["total_income"]+x["capital_gain"]*5+x["$2000+"]*10)/x["population"]
sort(x[(x["time"]==6)&(x["day"]==10)], by = "income", des = True)

##-----------------------------------
## Read in some data for probability computation:

sleep = array(pd.read_excel("Markov.xlsx", sheetname = "night", header = None))
work = array(pd.read_excel("Markov.xlsx", sheetname = "work", header = None))
home = array(pd.read_excel("Markov.xlsx", sheetname = "home", header = None))
places = pd.read_excel("Markov.xlsx", sheetname = "21-5").reset_index().iloc[0].dropna().tolist()

##-----------------------------------
## Scale columns by maximum:

aq_worse = max(x["AQI"]); transport = 1+2+3
max_y = max(x["income"]); max_pop = max(x["population"])
p = len(places)

##-----------------------------------
## Check if worked

sub = x[(x["day"]==1)&(x["time"]==0)&(x["train_stop"]=="blacktown")]

##-----------------------------------
## Prepare infection matrices

i_i = ((sleep*eye(len(places))+100)*eye(len(places))+((J(len(places))-eye(len(places)))*sleep))
i_i = i_i/sum(i_i)
tabs = reset(hcat(table(Z(len(places))),i_i).reset_index(),column=True)
b = tabs.pop(0)
tabs = array(tabs)

place_total = places+["inf_"+x for x in places]

work = array(table(work).fillna(0))

##-----------------------------------
## Prepare postcodes, lats and longs for easier access

codess = []; latss = []; longss = []
for q in places:
    ty = (x[x["train_stop"]==q]).dropna().max()
    codess.append(ty["postcode"])
    latss.append(ty["lat"])
    longss.append(ty["long"])
latss = (-1*abs(latss)).tolist()
codess = codess+codess; latss = latss+latss; longss= longss+longss

##-----------------------------------
## Intialise markov model with population and point of infection:

s = matrix([36185,9039,17926,12432,47870,14122,8896,17767,32929,17252,24485,9528,21895,12045,16100,10414, 0,0,0,0,0,0,10,0,0,0,0,0,0,0,0,0]).T
pop = matrix([36185,9039,17926,12432,47870,14122,8896,17767,32929,17252,24485,9528,21895,12045,16100,10414, 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]).T
rt = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,"Inf","Inf","Inf","Inf","Inf","Inf","Inf","Inf","Inf","Inf","Inf","Inf","Inf","Inf","Inf","Inf"]
suburb_check = places+places

##-----------------------------------
## Markov model: iteration each hour, day for each 16 places

names = []
result = []
for day in range(1,28):
    for time in range(24):
        s_i = []
        for gg in range(len(places)):
            station = places[gg]

            ##-----------------------------------
            ## subset to find place

            sub = x[(x["day"]==day)&(x["time"]==time)&(x["train_stop"]==station)]
            try: 
                infect = ((((sub["bus_crowding"]/transport)*0.4)+((sub["train_crowding"]/transport)*0.5)+(sub["AQI"]/aq_worse)*0.1)\
                            *(sub["income"]/max_y)*sub["population"]/max_pop).iloc[0]
                if infect==np.nan: infect = (np.random.rand(1)*0.075)[0]*0.001
            except: 
                infect = (np.random.rand(1)*0.075)[0]*0.001
            s_i.append(infect)
        s_i = (array(s_i)*eye(p))*(np.random.rand(1)*10)[0]*0.001
        s_i = array(table(s_i).fillna(0))

        ##-----------------------------------
        ## Calculate residuals

        residual = 1-s_i
        if time <= 5:  scaled = residual*sleep
        elif time <= 16: scaled = residual*work
        else: scaled = residual*home

        ##-----------------------------------
        ## Combine data:

        sssi = table(np.hstack((scaled,s_i)))
        sssi = array(pd.DataFrame(np.divide(array(sssi), matrix(sssi.sum(axis=1)).T)).fillna(0))
        msi = array(table(matrix(np.vstack((sssi,tabs)))).fillna(0))
        msi = array(table(msi).fillna(0))

        ##-----------------------------------
        ## Update paramaters

        msi = msi.T
        s = msi*s
        s = s+pop*0.0001
        
        ##-----------------------------------
        ## Add to list for concatenation:

        a = (table(s))
        b = hcat(a, place_total)
        c = hcat(b, [time for x in range(32)])
        d = hcat(c, [day for x in range(32)])
        e = hcat(d, rt, suburb_check, codess, longss, latss)
        e.columns = ["population", "suburb", "time","day","infection","check","postcode","long","lat"]
        result.append(e)

##-----------------------------------
## Compute infection rate

x["IR"] = (x["train_crowding"]/transport*0.5)+(x["bus_crowding"]/transport*0.4)+((x["AQI"]/aq_worse)*0.1)\
                *(x["income"]/max_y)*x["population"]/max_pop

##-----------------------------------
## merge results into table

first = result[0]
for j in result[1:]: first = vcat(first,j)

##-----------------------------------
## Export markov infection rates as sep file

first.to_csv("Markov_Data.csv")

##-----------------------------------
## Clean up ALL data

x = exc(x, "Unnamed: 0")

ALL = x.merge(first, left_on = ["day","time","train_stop"], right_on = ["day","time","check"], how = "left")
ALL = exc(ALL, ["suburb","check","postcode_y","long_y","lat_y"])
ALL.columns = ['day', 'time', 'train_stop', 'train_crowding', 'journey_time', 'lat',
       'long', 'bus_crowding', 'postcode', 'population', 'capital_gain',
       'total_income', '0-4_years', '5-9_years', '10-14_years', '15-19_years',
       '20-24_years', '25-29_years', '30-34_years', '35-39_years',
       '40-44_years', '45-49_years', '50-54_years', '55-59_years',
       '60-64_years', '65-69_years', '70-74_years', '75-79_years',
       '80-84_years', '85-89_years', '90-94_years', '95-99_years',
       '100_years+', 'oceanian', 'north-west_european',
       'southern_eastern_european', 'north_african_middle_eastern',
       'south-east_asian', 'north-east_asian', 'southern_central_asian',
       'americas', 'sub-saharan_african', 'm', 'f', '$<=0', '$1-1000',
       '$1000-1999', '$2000+', 'married', 'defacto', 'single', 'AQI', 'income',
       'IR', 'MARKOV_POP', 'infection']

##-----------------------------------
## Fix some silly errors

ALL["lat"] = -1*abs(ALL["lat"])
ALL["long"] = abs(ALL["long"])

##-----------------------------------
## Export all data

ALL.to_csv("ALL.csv")