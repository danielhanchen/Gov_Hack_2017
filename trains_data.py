##-----------------------------------
## THIS PROGRAM CLEANS AND PREPARES THE OPEN TRAIN DATA
## Daniel Han-Chen
##-----------------------------------

## Get libraries:

import pandas as pd
x = pd.read_csv("trains.csv")
from copy import copy
import warnings
warnings.filterwarnings("ignore")

##-----------------------------------
## Special functions to find and subset data easier:

## Find data is easier

def find(data, col, how, what):
    if how == "==": return data.iloc[(data[col]==what).index[data[col]==what]]
    elif how == ">": return data.iloc[(data[col]>what).index[data[col]==what]]
    elif how == ">=": return data.iloc[(data[col]>what).index[data[col]==what]]
    elif how == "<": return data.iloc[(data[col]<what).index[data[col]==what]]
    elif how == "<=": return data.iloc[(data[col]<=what).index[data[col]==what]]

## Find difference in lists is easier
def diff(want, rem):
    w = copy(want)
    for j in w:
        if j in rem: w.remove(j)
    for j in rem:
        if j in w: w.remove(j)
    return w

## Exclude columns:
def exc(x, l):
    if type(l) == str: l = [l]
    return x[diff(x.columns.tolist(),l)]

##-----------------------------------
## Data Preprocessing

##-----------------------------------
## Convert to numerics

y = copy(x)
y["Occupancy Status"] = y["Occupancy Status"].astype("category")
y["Occupancy Status"] = y["Occupancy Status"].replace({'STANDING_ROOM_ONLY':3,
                                                       'FEW_SEATS_AVAILABLE':2,
                                                      'MANY_SEATS_AVAILABLE':1})

##-----------------------------------
## Convert to datetime format

y["Actual.Station.Dprt.Time"] = y["Actual.Station.Dprt.Time"].astype("datetime64[ns]")
y["Actual.Station.Arrv.Time"] = y["Actual.Station.Arrv.Time"].astype("datetime64[ns]")

y["Start_Time"] = y["Actual.Station.Arrv.Time"].dt.hour
y["Start_Minutes"] = y["Actual.Station.Arrv.Time"].dt.minute

##-----------------------------------
## Get hours

y["Hour"] = (y["Actual.Station.Arrv.Time"].dt.minute>=30)*1 + y["Actual.Station.Arrv.Time"].dt.hour

##-----------------------------------
## Aggregate and summarise data

train = y.groupby(by = ["day","Hour","Actual.Stop.Station"]).agg({'Occupancy Status':'max','Start_Time':'mean',\
                                                                 'Start_Minutes':'mean'}).reset_index()

##-----------------------------------
## Get lowererd strings

train["Actual.Stop.Station"] = train["Actual.Stop.Station"].str.lower()
train["suburb"] = train["Actual.Stop.Station"]

##-----------------------------------
## Export to csv

train.to_csv("train.csv")