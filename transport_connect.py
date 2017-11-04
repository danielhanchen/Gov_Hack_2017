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
bus = pd.read_csv("bus.csv")

## Exclude columns:
def exc(x, l):
    if type(l) == str: l = [l]
    return x[diff(x.columns.tolist(),l)]

##-----------------------------------
## Clean up some postcode data:

longs = {"wynyard":151.205547, "central":151.206667, "town hall":151.204758, "circular quay":151.212056, "martin place": 151.210358,
        "museum":151.20963}
lats = {"wynyard":-33.865868, "central":-33.8825, "town hall":33.873682, "circular quay":-33.860705, "martin place":-33.867733,
       "museum":-33.87575}

data["change"] = data["train_stop"]

for j in longs.keys():
    tochange = find(data, "train_stop", "==", j)
    tochange["lat"] = tochange["lat"].fillna(lats[j])
    tochange["long"] = tochange["long"].fillna(longs[j])
    tochange["postcode"] = tochange["postcode"].fillna(2000)
    tochange["change"] = "sydney"
    data.iloc[tochange.index] = tochange

##-----------------------------------
## Clean up some more data:

data["time"] = data["time"].astype('float')
data["time"] = round(data["time"])
data["time"] = data["time"].astype('int')

##-----------------------------------
## Connect train+bus+postcodes:

cleaned = data.merge(bus, left_on = ["day","time","change"], right_on = ["day","time","bus_stop"])\
            .groupby(by = ["day","time","train_stop"]).agg({'train_crowding':'max','journey_time':'mean',
                                                           'postcode':'max','lat_x':'median',
                                                            'long_x':'median',
                                                           'bus_crowding':'max'}).reset_index()
cleaned = cleaned.dropna(subset=["postcode"])
cleaned.columns = ['day', 'time', 'train_stop', 'train_crowding', 'journey_time','postcode', 'lat', 'long', 'bus_crowding']
cleaned["postcode"] = cleaned["postcode"].astype(int)

##-----------------------------------
## Export cleaned data:

cleaned.to_csv("cleaned.csv")