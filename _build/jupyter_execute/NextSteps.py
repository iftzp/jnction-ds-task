#!/usr/bin/env python
# coding: utf-8

# # Next Steps

# Overall, there is a wide scope for further analysis if required by c2c. The data provided is of a high quality. Compared to many other data sources, the cleaning required is minimal and overall the data is reasonably tidy.  
#   
# If coupled with other datasets and more extensive technologies, the information which can be taken from this dataset could be visualised and digested in a much more appealing and easy-to-read way.

# ## Time Series Analysis & Forecasting
# 
# The most appropriate application for data tied to time such as this is to use time series analysis and forecasting. This would allow c2c to know when a delay is most likely to occur and know where resources should be allocated.
# 
# Another application could be to predict when a signal is going to fail.

# ## Signal Clustering and Monitoring
# 
# If the sequences in which signals are triggered were analysed and grouped into clusters, the clusters could be used for monitoring purposes. If a signal within a cluster did not trigger when all other signals in the same clusters did, this would indicate that there is an issue. 
# 
# This would also require less work as each signal could be checked against the associated cluster, instead of monitoring each signal individually.

# ## Optimise Route Endings
# 
# There seems to be a lot of activity showing trains moving during off peak hours, during times where there are very few planned events.
# 
# If this is because trains need to be relocated for some reason, for example:
# - starting a journey at another station the following day
# - cleaning or servicing required which can only be carried out at a different station
# 
# Maybe route allocation can be optimised so that trains don't have to be moved as much during off peak hours, saving resources.
