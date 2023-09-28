#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 14:21:06 2023

@author: dungdinh
"""

import pandas as pd 
import numpy as np



def hour_creation():
    hour_list = []
    for num in range(0,24):
        hour_list.append(f'{num:02}')
    return hour_list

hour_list = hour_creation()

def return_avg_taxi_drivers_by_hour():
    for hour in hour_list:
        file_name = './sentosa/29_05_2023/sentosa_2023-05-29_' + hour + '.csv'
        data = pd.read_csv(file_name)
        data_groupby = data.groupby(['time']).count()
        print(round(sum(data_groupby['date'])/len(data_groupby), 2))
    
def return_max_cluster_size_by_hour():
    for hour in hour_list:
        file_name = './sentosa/29_05_2023/sentosa_2023-05-29_' + hour + '.csv'
        data = pd.read_csv(file_name)
        cluster_size_max = data['cluster_size'].max()
        print(cluster_size_max)
        
def top_addresses_by_hour():
    data = pd.read_csv('./sentosa/29_05_2023/sentosa_2023-05-29_04.csv')
    
    data_groupby_address = data.groupby(['time','address'])['date'].count()
    
    index = data_groupby_address.index.tolist()
    
    time = []
    address = []
    for i in index:
        time_, address_ = i
        time.append(time_)
        address.append(address_)
    
        
    values = data_groupby_address.values.tolist()
    
    groupby_df = pd.DataFrame({'time': time, 'address': address, 'count': values})
    
    groupby_df_groupby_time = groupby_df.groupby('time').apply(lambda x: x.nlargest(1, 'count')).reset_index(drop = True)
    
    for i in groupby_df_groupby_time['address']:
        print(i)   
top_addresses_by_hour()
