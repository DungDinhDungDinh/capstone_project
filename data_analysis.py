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
        file_name = './changi/' + date + '/changi_' + date + '_' + hour + '.csv'
        data = pd.read_csv(file_name)
        
        data_groupby = data.groupby(['time']).count()
        
        if len(data_groupby) != 0:
            avg_taxi_drivers = round(sum(data['cluster_size'])/len(data_groupby), 2)
            
            max_cluster_size = data['cluster_size'].max()
            
            data_rows.append([date, hour, avg_taxi_drivers, max_cluster_size])
        else:
            data_rows.append([date, hour, 0, 0])
        
    return data_rows


def writingToSentosaStatisticsCSVFile():
    fields = ['date', 'hour', 'avg_taxi_drivers', 'max_cluster_size']
    
    save_path = 'changi'
    
    dates = ['2018-12-23']
    
    for date in dates:
        data_rows = sentosa_statistics_by_hour(date)
        
        # name of csv file 
        filename = "changi_statistics_by_hour_" + date + ".csv"
        
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
        file_name = './changi/' + date +'/changi_' + date + '_' + i + '.csv'
        
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
    
    dates = ['2018-12-23']
    
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
            
# writingToFrequencyCSVFile()

def hour_creation():
    hours = range(0, 24)
    res = []
    for hour in hours:
        res.append(f"{hour:02}")
    return res

def finding_congestion_at_changi(date):
    hours = hour_creation()
    
    res = []
    for hour in hours:
        file_name = './changi/' + date + '/changi_' + date + '_' + hour +'.csv'
        
        data = pd.read_csv(file_name)
        
        big_clusters = data[data['cluster_size'] >= 20]
        
        big_clusters['time'] = big_clusters['time'].apply(lambda x: int(x.split(':')[1]))
        
        big_clusters.sort_values("time", ascending=True)
        
        
        big_clusters_len = len(big_clusters)
        congestion_location = {}
        
        for i in range(0, big_clusters_len):
            for j in range(i+1, big_clusters_len):
                if big_clusters.iloc[i]['address'] ==  big_clusters.iloc[j]['address']:
                    if ((big_clusters.iloc[j]['time'] - big_clusters.iloc[i]['time']) == 1):
                        key = big_clusters.iloc[j]['address']
                        value = congestion_location.get(key)
                        if value:
                            congestion_location[key].append(big_clusters.iloc[i]['time'])
                            congestion_location[key].append(big_clusters.iloc[j]['time'])
                        else:
                            congestion_location[key] = [big_clusters.iloc[i]['time']]
                            congestion_location[key].append(big_clusters.iloc[j]['time'])
        
        
        
        for x in congestion_location:
            minute_sorted = list(set(congestion_location[x]))
            minute_sorted.sort()
            congestion_location[x] = minute_sorted
            
        
        #counting congestion minutes
        congestion_minutes = [] 
        for address in congestion_location:
            minute_list = congestion_location[address]
            
            # minutes_set_list = list(set(minutes))
            
            
            i = 0
            count = 0
            minutes = []
            minutes_set_list_len = len(minute_list)
            while i < minutes_set_list_len - 1:
                j = i + 1
    
                if (minute_list[j] - minute_list[i]) == 1:
                    if j == minutes_set_list_len - 1:
                        if count != 0:
                            count = count + 1
                            minutes.append(minute_list[j])
                            congestion_minutes.append([date, hour, address, minutes, count + 1])
                    else:
                        count = count + 1
                        minutes.append(minute_list[j])

                else:
                    congestion_minutes.append([date, hour, address, minutes, count + 1])
                    count = 0 
                    minutes = []
                
                i = i + 1
        
        for location in congestion_minutes:
            minute_list = location[3]
            added = minute_list[0] - 1
            # print(added)
            location[3].insert(0, added)
            
        res = res + congestion_minutes
    
    # print(res)
    return res
                

def writingCongestionToCSVFile():
    fields = ['date', 'time', 'address', 'congestion_minutes', 'congestion_minute_counts']
    
    save_path = 'changi'
    
    date = '2018-12-23'    
    
    data_rows = finding_congestion_at_changi(date)
    
    # name of csv file 
    filename = "congestion_" + date + ".csv"
    
    completeName = os.path.join(save_path, filename)
        
    # writing to csv file 
    with open(completeName, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(data_rows)

# writingCongestionToCSVFile()

def test_congestion():
    congestion_location = {'Changi Airport Terminal 2, 60, T1 Boulevard, Changi, Singapore, Southeast, 819643, Singapore': [22, 23, 35, 36, 37, 38, 45, 46, 47, 48, 54, 55, 56, 57, 58, 59]}
    
    congestion_minutes = []   
           
    for address in congestion_location:
        minute_list = congestion_location[address]
        
        # minutes_set_list = list(set(minutes))
        
        # print(minute_list)
        
        
        i = 0
        count = 0
        minutes = []
        minute_list_len = len(minute_list)

        while i < minute_list_len - 1:
            j = i + 1
            if (minute_list[j] - minute_list[i]) == 1:
                print(j)
                if j == minute_list_len - 1:
                    if count != 0:
                        print(j)
                        congestion_minutes.append([address, minutes, count + 1])
                # print(minute_list[j])
                # print(minute_list[i])
                else:
                    count = count + 1
                    minutes.append(minute_list[j])
            else:
                # print(minute_list[j])
                # print(minute_list[i])
                congestion_minutes.append([address, minutes, count + 1])
                count = 0 
                minutes = []
            
            i = i + 1
    
    print(congestion_minutes) 

# test_congestion()

            



