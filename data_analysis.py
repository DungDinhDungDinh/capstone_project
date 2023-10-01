#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 14:21:06 2023

@author: dungdinh
"""

import pandas as pd 
import csv
import os


def hour_creation():
    hour_list = []
    for num in range(0,24):
        hour_list.append(f'{num:02}')
    return hour_list

hour_list = hour_creation()
        
def sentosa_statistics_by_hour(date):
    data_rows = []
    for hour in hour_list:
        file_name = './sentosa/' + date + '/sentosa_' + date + '_' + hour + '.csv'
        data = pd.read_csv(file_name)
        
        data_groupby = data.groupby(['time']).count()
        avg_taxi_drivers = round(sum(data['cluster_size'])/len(data_groupby), 2)
        
        max_cluster_size = data['cluster_size'].max()
        
        data_rows.append([date, hour, avg_taxi_drivers, max_cluster_size])
        
    return data_rows


def writingToSentosaStatisticsCSVFile():
    fields = ['date', 'hour', 'avg_taxi_drivers', 'max_cluster_size']
    
    save_path = 'sentosa'
    
    dates = ['2021-04-02', '2021-07-14', '2021-09-01', '2021-10-23', '2022-02-01', '2022-11-13', 
            '2022-12-03', '2023-01-19', '2023-01-22', '2023-01-24', '2023-02-01', '2023-03-06',
            '2023-03-18', '2023-04-11', '2023-05-28', '2023-06-02', '2023-06-08', '2023-06-29',
            '2023-07-29']
    
    for date in dates:
        data_rows = sentosa_statistics_by_hour(date)
        
        # name of csv file 
        filename = "sentosa_statistics_by_hour_" + date + ".csv"
        
        completeName = os.path.join(save_path, filename)
            
        # writing to csv file 
        with open(completeName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(fields) 
                
            # writing the data rows 
            csvwriter.writerows(data_rows)
        
# writingToSentosaStatisticsCSVFile()
        
def top_addresses_by_hour(date):
    data_rows = []
    
    for i in hour_list:
        file_name = './sentosa/' + date +'/sentosa_' + date + '_' + i + '.csv'
        
        data = pd.read_csv(file_name)
        
        data_groupby_address = data.groupby(['address']).count()['date'].nlargest(5).reset_index()
        
        addresses = data_groupby_address['address'].values
        frequency = data_groupby_address['date'].values
        
        j=0
        while j < len(addresses):
            data_rows.append([date, i, addresses[j], frequency[j]])
            j = j+1
    
    return data_rows

def writingToFrequencyCSVFile():
    fields = ['date', 'time', 'address', 'frequency']
    
    save_path = 'sentosa'
    
    dates = ['2021-04-02', '2021-07-14', '2021-09-01', '2021-10-23', '2022-02-01', '2022-11-13', 
            '2022-12-03', '2023-01-19', '2023-01-22', '2023-01-24', '2023-02-01', '2023-03-06',
            '2023-03-18', '2023-04-11', '2023-05-28', '2023-06-02', '2023-06-08', '2023-06-29',
            '2023-07-29']
    
    for date in dates:
        data_rows = top_addresses_by_hour(date)
        
        # name of csv file 
        filename = "top5_addresses_by_hour_" + date + ".csv"
        
        completeName = os.path.join(save_path, filename)
            
        # writing to csv file 
        with open(completeName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(fields) 
                
            # writing the data rows 
            csvwriter.writerows(data_rows)
            
writingToFrequencyCSVFile()
        

        



