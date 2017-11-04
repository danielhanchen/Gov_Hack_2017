##-----------------------------------
## THIS PROGRAM CLEANS AND PREPARES THE OPEN POSTCODE DATA
## Daniel Han-Chen
##-----------------------------------

## Get libraries:

import pandas as pd
from copy import copy
import warnings
warnings.filterwarnings("ignore")
data = pd.read_csv("data.csv")

## Exclude columns:
def exc(x, l):
    if type(l) == str: l = [l]
    return x[diff(x.columns.tolist(),l)]

##-----------------------------------
## Get bus data:

bus = pd.read_csv("bus_capacity_clean.csv")
bus["capacity"] = bus["capacity"].replace({'STANDING_ROOM_ONLY':3,
                                                       'FEW_SEATS_AVAILABLE':2,
                                                      'MANY_SEATS_AVAILABLE':1})
##-----------------------------------
## Clean bus data:

bus["suburb"] = bus["suburb"].str.lower()
bus = exc(bus, "Unnamed: 0")
bus.columns = ["time","bus_stop","lat","long","bus_crowding","day"]

##-----------------------------------
## Export bus data:

bus.to_csv("bus.csv")