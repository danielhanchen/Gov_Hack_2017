##-----------------------------------
## THIS PROGRAM CLEANS AND PREPARES THE OPEN POSTCODE DATA
## Daniel Han-Chen
##-----------------------------------

## Get libraries:

import pandas as pd
from copy import copy
import warnings
warnings.filterwarnings("ignore")
x = pd.read_csv("trains.csv")

## Exclude columns:
def exc(x, l):
    if type(l) == str: l = [l]
    return x[diff(x.columns.tolist(),l)]

##-----------------------------------
## Get postcode data:

postcodes = pd.read_csv("postcodes.csv")
postcodes["suburb"] = postcodes["suburb"].str.lower()
postcodes = postcodes.iloc[(postcodes["state"]=='NSW').index[(postcodes["state"]=='NSW')]]
postcodes = postcodes[["postcode","suburb","lat","lon"]]

##-----------------------------------
## merge train data:

data = train.merge(postcodes, left_on = "suburb", right_on = "suburb", how = "left")
data.columns = ["day","hour","train_stop","train_crowding","time","journey_time","suburb","postcode","lat","long"]
data = exc(data, ["suburb","seq","hour"])

##-----------------------------------
## write to csv:

data.to_csv("data.csv")