#!/usr/bin/env python
# coding: utf-8

# # Data Cleaning

# In[1]:


# Import pandas and read data
import pandas as pd
import numpy as np

# load data from previous notebook.
get_ipython().run_line_magic('store', '-r train_timings')


# ## Feature Engineering
# 
# We should probably engineer some features first and add them to the dataframe so that we can get a better understanding of the data.
# 
# - day of week
# - hour of day
# - signal date
# - difference between planned event time and actual event time
# - previous signal as it might be useful later
# 
# We don't need origin date. It is not relevant to our analysis.

# In[2]:


# create new features
train_timings['event_diff_seconds'] = (train_timings['planned_event_time'] - train_timings['actual_event_time']).dt.total_seconds()
train_timings['signal_date'] = train_timings['signal_passing_time'].dt.floor('d')
train_timings['day_of_week'] = train_timings['signal_date'].dt.day_name()
train_timings['hour_of_day'] = train_timings['signal_passing_time'].dt.hour

train_timings['previous_signal'] = train_timings['signal'].shift(+1)
train_timings['previous_train_id'] = train_timings['train_id'].shift(+1)
train_timings['previous_signal'] = np.where((train_timings['train_id'] == train_timings['previous_train_id']), train_timings['previous_signal'], np.nan)

# drop origin date
train_timings.drop(['origin_date', 'dataset_stations'], axis=1, inplace=True)

# sort the dataframe to help us to understand how the data works.
train_timings.sort_values(['signal_date', 'hour_of_day', 'train_id', 'signal_passing_time'], inplace=True, ignore_index=True)

# drop duplicate rows
train_timings.drop_duplicates(inplace=True)


# In[3]:


# store variables for next notebook
get_ipython().run_line_magic('store', 'train_timings')

