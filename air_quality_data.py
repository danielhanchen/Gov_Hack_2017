##-----------------------------------
## THIS PROGRAM CLEANS AND PREPARES THE OPEN POSTCODE DATA
## Daniel Han-Chen
##-----------------------------------

## Get libraries:

import pandas as pd
from copy import copy
import warnings
warnings.filterwarnings("ignore")
cleaned = pd.read_csv("cleaned.csv")

## Exclude columns:
def exc(x, l):
    if type(l) == str: l = [l]
    return x[diff(x.columns.tolist(),l)]

##-----------------------------------
## Clean up Air quality data

aq = pd.read_csv("aq.csv", delimiter =";")
aq = aq.iloc[1:]
aq.columns = (aq.T.reset_index()[1]).tolist()
aq = aq.iloc[1:].reset_index()
aq["Date"]=aq["Date"].str.split("/").str[0].str.lstrip("0")
aq["Time"]=(aq["Time"].str.split(":").str[0].str.lstrip("0")).astype("int")-1

##-----------------------------------
## Change column names for easier access

aq.columns=pd.Series(aq.columns.tolist()).str.rstrip("AQI hourly AQI [index]").str.lower().tolist()

aqcols = ['', 'dat', 'tim', 'randwick', 'rozelle', 'lindfield', 'liverpool',
       'bringelly', 'chullor', 'earlwood', 'wyong', 'wallsend', 'carrington',
       'stockton', 'newcastle', 'mayfield', 'beresfield', 'tamworth',
       'wollongong', 'kembla grange', 'richmond', 'bargo', 'albury',
       'wagga wagga', 'st marys', 'vineyard', 'bathurst', 'macarthur',
       'oakdale', 'albion park', 'prospect', 'muswellbrook', 'singleton',
       'maison dieu', 'camberwell', 'singleton', 'mount thorley', 'bulg',
       'wagga wagga', 'muswellbrook', 'wybong', 'aberdeen',
       'singleton', 'jerrys plains', 'warkworth', 'merriw',
       'campbelltown', 'camden']

aq.columns = aqcols

##-----------------------------------
## Make air quality data easier to play with

aq = aq.melt(id_vars=['dat','tim'])
aq.columns = ["day","time","suburb","AQI"]
aq = aq.iloc[(aq["suburb"]!="").index[aq["suburb"]!=""]].reset_index()
aq = aq[["day","time","suburb","AQI"]]
aqposts = pd.DataFrame(aqcols).merge(postcodes, left_on=[0], right_on=["suburb"]).groupby(by="suburb").agg({'postcode':'max'}).reset_index()

##-----------------------------------
## Fill in using flood fill algorithm for air quality for all suburbs

sorts = aqposts.sort_values(by="postcode").reset_index()
df = {}
for j in range(sorts.shape[0]):
    if j == 0:
        for increments in range(sorts.iloc[j]["postcode"]):
            df[sorts.iloc[j]["postcode"]-increments] = sorts.iloc[j]["suburb"]
    elif j+1 < sorts.shape[0]:
        for increments in range(sorts.iloc[j+1]["postcode"]-sorts.iloc[j]["postcode"]):
            df[increments+sorts.iloc[j]["postcode"]] = sorts.iloc[j]["suburb"]
    else:
        for increments in range(2787-sorts.iloc[j]["postcode"]):
            df[sorts.iloc[j]["postcode"]+increments] = sorts.iloc[j]["suburb"]
            
filled = pd.DataFrame.from_dict(df,orient='index').reset_index()
filled.columns = ["postcode","suburb"]

##-----------------------------------
## Fix some silly data errors:

aq=aq.reset_index()
aq=aq.iloc[(aq["AQI"]!='--').index[aq["AQI"]!='--'].tolist()]
aq = exc(aq, "index")

##-----------------------------------
## Merge air quality with cleaned data

aq = aq.dropna(subset=["AQI"])
aq["AQI"] = aq["AQI"].astype("int")
aq_all = filled.merge(aq, on="suburb",how="left").groupby(by=["day","time","postcode"]).agg({"AQI":'max'})

aq_all=aq_all.reset_index()
aq_all["day"]=aq_all["day"].astype(int)

cleaned = cleaned.merge(aq_all, on = ["day","time","postcode"], how = "left")
cleaned = exc(cleaned, "index")

##-----------------------------------
## Export cleaned data:

cleaned.to_csv("data.csv")