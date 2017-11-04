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
## Clean up ATO + ABS data:

ato = pd.read_excel("ato.xlsx",sheetname = "Data")

ato = ato[["Postcode","Individuals1","Net capital gain","Total income or loss","0-4 years","5-9 years",
"10-14 years","15-19 years","20-24 years","25-29 years","30-34 years","35-39 years","40-44 years","45-49 years","50-54 years","55-59 years","60-64 years",
"65-69 years","70-74 years","75-79 years","80-84 years","85-89 years","90-94 years","95-99 years","100 years and over","Oceanian","North-West European",
"Southern and Eastern European","North African and Middle Eastern","South-East Asian","North-East Asian","Southern and Central Asian",
"People of the Americas","Sub-Saharan African","Male","Female","under or 0","$1 to 1000","1000-1999","2000+","Married in a registered marriage",
"Married in a de facto marriage","Not married"]]

newcols = ["postcode","population","capital_gain","total_income","0-4_years","5-9_years",
"10-14_years","15-19_years","20-24_years","25-29_years","30-34_years","35-39_years","40-44_years","45-49_years","50-54_years","55-59_years","60-64_years",
"65-69_years","70-74_years","75-79_years","80-84_years","85-89_years","90-94_years","95-99_years","100_years+","Oceanian","North-West_European",
"Southern_Eastern_European","North_African_Middle_Eastern","South-East_Asian","North-East_Asian","Southern_Central_Asian",
"Americas","Sub-Saharan_African","m","f","$<=0","$1-1000","$1000-1999","$2000+","Married",
"defacto","single"]

##-----------------------------------
## Make new column names

newcols = [x.lower() for x in newcols]
ato.columns = newcols

##-----------------------------------
## Merge and aggregate data:

aggs = {'train_crowding':'max','journey_time':'mean','lat':'median','long':'median','bus_crowding':'max'}
for k in newcols: aggs[k]='max'

cleaned = cleaned.merge(ato, on="postcode").groupby(by=["day","time","train_stop"]).agg(aggs).reset_index()

##-----------------------------------
## Export cleaned data:

cleaned.to_csv("cleaned.csv")