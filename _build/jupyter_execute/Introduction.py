#!/usr/bin/env python
# coding: utf-8

# # Introduction
# 
# This document contains the Initial Exploratory Data Analysis carried out by [JNCTION](https://jnction.uk/) on behalf of [Trenitalia c2c Limited T/A c2c](https://www.c2c-online.co.uk/).  
# 
# _______________
# 
# c2c required initial insights regarding some key aspects of their business, including:
# - Data Outages and Strikes
# - Active Trains Over Time
# - Key Route: Pitsea - Benfleet
# 
# Which can be found in the following pages of this document.  
#   
# JNCTION have also suggested some future work based on this analysis which we believe will assist in optimising resource allocation and providing a better customer experience.
# 
# _______________
# 
# 
# The provided csv file **train_timings_data.csv** contains 4 months of data (125 days) between April 1 2022 and July 31 2022 for trains running in the area east of London.  
# It contains a total of 2,520,092 records.
# 
# The columns included in the file are as follows:
# - **origin_date**: the date the record was issued
# - **train_id**: the train identification number
# - **signal**: the railway signal identification number
# - **signal_passing_time**: the time the railway signal was passed
# 
# - **planned_event_type**: this field is populated if the record corresponds to a departure or arrival from a station (or arrival at destination)
# - **planned_event_location**: the location of the event in the form of a STANOX code is recorded (if the record corresponds to a planned event)
# - **planned_event_time**: the intended time for the passing of the railway signal (if the record corresponds to a planned event)
# - **actual_event_time**: the actual time the passing of the railway signal occured (if the record corresponds to a planned event)
# 
# In summary:  
# Each row represents a record of a train passing a railway signal, with some rows containing information relating to a planned event (departure or arrival from a station).
# 
# _______________

# ## File Stats

# In[1]:


get_ipython().run_line_magic('reset', '')
import pandas as pd
import plotly.io as pio
import plotly.express as px
import plotly.offline as py
import plotly.graph_objects as go
from convertbng.util import convert_etrs89_to_lonlat

train_timings = pd.read_csv('../data/train_timings_data.csv', parse_dates=['origin_date', 'signal_passing_time', 'planned_event_time', 'actual_event_time'], dtype={'planned_event_location': str})


# ### Unique Values

# In[2]:


# Get the number of unique records in each column
# for column in train_timings.columns:
#     print(column + ': ' + str(len(train_timings[column].unique())))


# - origin_date: 125 unique values (124 without NaN)
# - train_id: 36091 unique values (36090 without NaN)
# - signal: 343 unique values
# - signal_passing_time: 2160710 unique values
# - planned_event_type: 4 unique values (3 without NaN)
# - planned_event_location: 27 unique values (26 without NaN)
# - planned_event_time: 279172 unique values (279171 without NaN)
# - actual_event_time: 843325 unique values (843324 without NaN)

# ### Missing and Duplicate Values

# In[3]:


print('There are {} missing values or NaNs in train_timings_data.csv.'
      .format(train_timings.isnull().values.sum()))

print()
print("Number of missing values in each column:")
print(train_timings.isnull().sum(axis=0))


# In[4]:


temp_train_timings = train_timings.duplicated(keep='first').sum()

print('There are {} duplicate rows in train_timings_data.csv based on all columns.'
      .format(temp_train_timings))


# In total, there are **6,569,326 missing values** or NaNs in train_timings_data.csv.  
# However, we know this is not an accurate measure as half of the columns are empty when the signal is not departing or arriving at a station.  
# When we look at the 'origin_date' column, we can see that there are 22,319 values missing.   

# ## Expanding the dataset
# 
# In order to help with readaibility and understanding of the dataset, we have merged data from some other datasets.  
# We want two main things: 
# - Longitude and Latitude to be able to create a simple map of the stations in the dataset
# - Station Names to know which station we are looking at when analysing data
# 
# We used the [CORPUS](https://wiki.openraildata.com/index.php?title=Reference_Data) (Codes for Operations, Retail & Planning – a Unified Solution) dataset to convert stanox to TIPLOC codes.  
# Then, we obtained Eastings and Northings from [this](https://wiki.openraildata.com/index.php?title=File:TIPLOC_Eastings_and_Northings.xlsx.gz) dataset.  
# We converted these to Longitude and Latitude Coordinates.  
# We also merged the data with a [NaPTAN](https://beta-naptan.dft.gov.uk/) file from 2016 which also contains STANOX Codes to get readable station names.
# 
# For missing station names, we can use [this](http://www.railwaycodes.org.uk/crs/crs0.shtm) website.  
# For missing station coordinates, we will use Google Maps.

# In[5]:


# we will join the data with CORPUS to get tiploc.
# Then we will join the data with NaPTAN. This will also give us the names of each stop
# Then we can create a map of the coordinates

# get unique stations in dataset
unique_stanox_values = train_timings.planned_event_location.unique()
stanox_map_data = pd.DataFrame(data = {'dataset_stations': unique_stanox_values})
stanox_map_data.dropna(inplace=True)

# get and merge corpus
corpus = pd.read_json('../data/CORPUSExtract.json', orient='records')
stanox_map_data = stanox_map_data.merge(corpus, how='left',left_on='dataset_stations', right_on='STANOX')

# get and merge naptan 2016
naptan_2016 = pd.read_csv('../data/NaPTAN-2016.csv')
stanox_map_data = stanox_map_data.merge(naptan_2016, how='left',left_on='TIPLOC', right_on='TiplocCode')

# get and merge tiploc EN
tiploc_EN = pd.read_excel('../data/TIPLOC Eastings and Northings.xlsx')
stanox_map_data = stanox_map_data.merge(tiploc_EN, how='left',left_on='TIPLOC', right_on='TIPLOC')

# lets drop all columns apart from dataset_stations, StationName, Easting, Northing. We will keep NLCDESC too as our dataframe is still missing some of the values we want..
stanox_map_data.drop(stanox_map_data.columns.difference(['dataset_stations', 'StationName', 'EASTING', 'NORTHING', 'NLCDESC']), axis=1, inplace=True)

# convert EN to LL
# using this function isn't super accurate, but it will do for the purposes of simple visualisation
# if more accurate coordinates are needed convert_to_lonlat can be used, but its takes a long time.
lat_long = convert_etrs89_to_lonlat(list(stanox_map_data['EASTING']), list(stanox_map_data['NORTHING'])); # close enough
stanox_map_data['LONGITUDE'] = lat_long[0]
stanox_map_data['LATITUDE'] = lat_long[1]

# drop duplicates on dataset stations
stanox_map_data.drop_duplicates(subset=['dataset_stations'], keep='first', inplace=True)

# we will fill the rest manually. found on http://www.railwaycodes.org.uk/crs/crsg.shtm and google maps
stanox_map_data.at[6, 'StationName'] = 'Shoeburyness Depot London End Junction'
stanox_map_data.at[13, 'StationName'] = 'Barking Station Junction'
stanox_map_data.at[21, 'StationName'] = 'Gas Factory Junction'
stanox_map_data.at[23, 'StationName'] = 'Christian Street Junction'
stanox_map_data.at[25, 'StationName'] = 'East Ham Electric Multiple Unit Depot'
stanox_map_data.at[26, 'StationName'] = 'Shoeburyness Carriage Servicing Depot'
stanox_map_data.at[29, 'StationName'] = 'Gas Factory Loop'

stanox_map_data.at[0, 'LONGITUDE'] = '0.6406116596973183'
stanox_map_data.at[0, 'LATITUDE'] = '51.54120825152502'

stanox_map_data.at[3, 'LONGITUDE'] = '0.710359938504039'
stanox_map_data.at[3, 'LATITUDE'] = '51.53721361264267'

stanox_map_data.at[16, 'LONGITUDE'] = '0.4573321689628452'
stanox_map_data.at[16, 'LATITUDE'] = '51.5681286353167'

# we can drop easting, northing and nlcdesc
stanox_map_data.drop(['EASTING', 'NORTHING', 'NLCDESC'], axis=1, inplace=True)

# merge this information to our main dataframe in case we want to use it later. it will also help with readability
train_timings = train_timings.merge(stanox_map_data, how='left',left_on='planned_event_location', right_on='dataset_stations')

print("Stations in the Dataset with coordinates")
stanox_map_data


# In[6]:


pio.renderers
pio.renderers.default = "notebook_connected"

fig = go.Figure(data=go.Scattergeo(
        lon = stanox_map_data['LONGITUDE'],
        lat = stanox_map_data['LATITUDE'],
        text = stanox_map_data['dataset_stations'] + ' : ' +stanox_map_data['StationName'],
        mode = 'markers',
        ))

fig.update_layout(
        title = 'Some Public Transport Stops UK<br>(Hover for names)',
        geo_scope='europe',
    )
fig.show()


# The above visualisation isn't perfect, but it serves its purpose. You can zoom into the UK and see roughly where each station is on the map and that they are all in the area west of London.

# In[7]:


# store variables for next notebook
get_ipython().run_line_magic('store', 'train_timings')

