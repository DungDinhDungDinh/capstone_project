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
        try:
            file_name = './changi/' + date + '/changi_' + date + '_' + hour + '.csv'
            data = pd.read_csv(file_name)
            
            
            data_groupby = data.groupby(['time']).count()
            
            if len(data_groupby) != 0:
                avg_taxi_drivers = round(sum(data['cluster_size'])/len(data_groupby), 2)
                
                max_cluster_size = data['cluster_size'].max()
                
                data_rows.append([date, hour, avg_taxi_drivers, max_cluster_size])
            else:
                data_rows.append([date, hour, 0, 0])
        except FileNotFoundError:
            data_rows.append([date, hour, 0, 0])
        
    return data_rows


def writingToSentosaStatisticsCSVFile():
    fields = ['date', 'hour', 'avg_taxi_drivers', 'max_cluster_size']
    
    save_path = 'changi'
    
    # dates = ['2018-12-23']
    # dates = ['2023-07-29', '2023-07-09', '2023-03-14', '2023-02-25', '2023-01-24', '2021-12-24']
    dates = ['2018-11-25', '2019-12-19', '2019-12-20', '2019-12-21', '2019-12-25', '2022-12-22', '2023-04-11',
             '2023-05-01', '2023-06-02', '2023-06-18', '2023-06-29', '2023-08-09', '2023-09-10', '2023-10-02', '2018-11-25']
    
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
        try:
            file_name = './changi/' + date +'/changi_' + date + '_' + i + '.csv'
            
            data = pd.read_csv(file_name)
            
            data_groupby_address = data.groupby(['address']).count()['date'].nlargest(5).reset_index()
            
            addresses = data_groupby_address['address'].values
            frequency = data_groupby_address['date'].values
            
            j=0
            while j < len(addresses):
                data_rows.append([date, i, addresses[j], frequency[j]])
                j = j+1
        except FileNotFoundError:
            data_rows.append([date, i, "", ""])
    
    return data_rows

def writingToFrequencyCSVFile():
    fields = ['date', 'time', 'address', 'frequency']
    
    save_path = 'changi'
    
    # dates = ['2018-12-23']
    dates = ['2023-07-29', '2023-07-09', '2023-03-14', '2023-02-25', '2023-01-24', '2021-12-24', '2018-11-25', 
             '2019-12-19', '2019-12-20', '2019-12-21', '2019-12-25', '2022-12-22', '2023-04-11', '2023-05-01', 
             '2023-06-02', '2023-06-18', '2023-06-29', '2023-08-09', '2023-09-10', '2023-10-02', '2018-11-25']
    
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
        try:
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
        except FileNotFoundError:
            res = res
    # print(res)
    return res
                

def writingCongestionToCSVFile():
    fields = ['date', 'time', 'address', 'congestion_minutes', 'congestion_minute_counts']
    
    save_path = 'changi'
    
    # date = '2018-12-23'  
    
    dates = ['2023-07-29', '2023-07-09', '2023-03-14', '2023-02-25', '2023-01-24', '2021-12-24', '2018-11-25', 
             '2019-12-19', '2019-12-20', '2019-12-21', '2019-12-25', '2022-12-22', '2023-04-11', '2023-05-01', 
             '2023-06-02', '2023-06-18', '2023-06-29', '2023-08-09', '2023-09-10', '2023-10-02', '2018-11-25']
    
    for date in dates:
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

def congestion_analysis():
    weekdays = ['2023-12-05', '2023-11-07', '2023-10-17', '2023-09-26', '2023-08-01',
             '2023-07-04', '2023-06-13', '2023-05-23', '2023-04-11', '2023-03-14',
             '2023-02-07', '2022-12-20', '2022-11-08', '2022-10-11', '2022-09-06',
             '2022-08-16', '2022-07-19', '2022-06-14', '2022-05-10', '2022-04-19',
             '2022-03-15', '2022-02-22', '2022-01-04', '2019-01-08', '2019-02-12',
             '2019-03-19', '2019-04-23', '2019-05-14', '2019-06-04', '2019-07-02',
             '2019-08-27', '2019-09-17', '2019-10-15', '2019-12-17', '2019-12-24',
             '2019-01-09', '2019-02-13', '2019-03-20', '2019-04-03', '2019-05-22',
             '2019-06-12', '2019-07-10', '2019-08-21', '2019-09-18', '2019-10-23',
             '2019-11-27', '2019-12-18', '2022-01-12', '2022-02-09', '2022-03-16',
             '2022-04-27', '2022-05-18', '2022-06-01', '2022-07-13', '2022-08-24',
             '2022-09-28', '2022-10-05', '2022-11-02', '2022-12-21', '2023-02-08',
             '2023-03-22', '2023-04-19', '2023-05-31', '2023-06-21', '2023-07-12',
             '2023-08-16', '2023-09-20', '2023-10-25', '2023-11-22', '2023-12-06',
             '2023-02-09', '2023-03-16', '2023-04-13', '2023-05-25', '2023-06-15',
             '2023-07-27', '2023-08-24', '2023-09-21', '2023-10-19', '2023-11-09',
             '2023-12-28', '2022-01-06', '2022-02-10', '2022-03-31', '2022-04-21',
             '2022-05-26', '2022-06-16', '2022-07-29', '2022-08-18', '2022-09-08',
             '2022-10-21', '2022-11-04', '2022-12-23', '2019-01-03', '2019-02-14',
             '2019-03-21', '2019-04-18', '2019-05-23', '2019-06-20', '2019-07-11',
             '2019-08-22', '2019-09-12', '2019-10-31', '2019-11-28', '2019-12-05',
             '2019-01-04', '2019-02-22', '2019-03-15', '2019-04-26', '2019-06-28',
             '2019-05-24', '2019-07-19', '2019-08-16', '2019-09-06', '2019-10-04',
             '2019-11-29', '2019-12-13', '2022-01-07', '2022-02-18', '2022-03-25',
             '2022-04-22', '2022-05-13', '2022-06-03', '2022-07-29', '2022-08-12',
             '2022-09-30', '2022-10-07', '2022-11-25', '2022-12-23', '2023-01-27',
             '2023-02-24', '2023-03-31', '2023-04-14', '2023-05-19', '2023-06-09',
             '2023-07-07', '2023-08-11', '2023-09-08', '2023-10-27', '2023-11-10',
             '2023-12-15', '2023-11-07', '2024-01-30', '2024-02-01', '2024-02-16', 
             '2024-02-19']
    weekends = ['2023-01-14', '2023-02-18', '2023-03-25', '2023-04-01','2023-05-20', 
                '2023-06-24', '2023-07-29', '2023-08-12', '2023-09-16',
             '2023-10-21', '2023-11-18', '2023-12-30', '2023-01-29', '2023-02-26',
             '2023-03-12', '2023-04-02', '2023-05-21', '2023-06-11', '2023-07-09',
             '2023-08-06', '2023-09-24', '2023-10-08', '2023-11-12', '2023-12-31',
             '2022-01-21', '2022-01-30', '2022-02-12', '2022-02-27', '2022-03-26',
             '2022-03-13', '2022-04-30', '2022-04-10', '2022-05-14', '2022-05-15',
             '2022-06-18', '2022-06-05', '2022-07-23', '2022-07-17', '2022-08-20',
             '2022-08-21', '2022-09-24', '2022-09-04', '2022-10-22', '2022-10-16',
             '2022-11-26', '2022-11-27', '2022-12-31', '2022-12-11', '2019-01-26',
             '2019-01-06', '2019-02-23', '2019-02-24', '2019-03-09', '2019-03-17',
             '2019-04-06', '2019-04-07', '2019-05-11', '2019-05-26', '2019-06-01',
             '2019-06-30', '2019-07-13', '2019-07-28', '2019-08-24', '2019-08-25',
             '2019-09-21', '2019-09-01', '2019-10-12', '2019-10-20', '2019-11-09',
             '2019-11-10', '2019-12-07', '2019-12-15', '2024-02-18']
    holidays = ['2024-01-01', '2023-12-31', '2023-12-30', '2023-12-25', '2023-12-24', '2023-12-16',				
                '2023-11-11', '2023-10-21', '2023-08-09', '2023-08-08', '2023-06-29', '2023-06-28',				
                '2023-06-02', '2023-06-01', '2023-12-28', '2019-10-27', '2019-10-26', '2019-10-28',				
                '2019-12-24', '2019-12-25', '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24',				
                '2023-04-21', '2023-04-22', '2023-04-30', '2023-05-01', '2023-05-02']
    all_days = weekdays + weekends + holidays
    terminal = 't4'
    days_running = '2023-11-07'
    one_day = [days_running]
    
    duration_list = []
    
    for date in one_day:
        d = pd.Timestamp(date)
        file_name = './' + terminal + '_congestion/' + terminal + '_' + date +'.csv'
        
        data = pd.read_csv(file_name)
    
        
        queues = data[(data['taxi_count'] >= 10) & (data['queue_length'] >= 100)]
            
        i = 0
        count = 0
        minutes = []
        taxi_count_list = []
        queues_len = len(queues)
        queue_length_list = []
        max_minute = 300
        
        while i < queues_len - 2:
                
            j = i + 1
            
            if (queues.iloc[j]['id']-queues.iloc[i]['id']) == 1:
                if j == queues_len - 1:
                    if count != 0:
                        append_list = [date, d.day_name(), data['day_type'][0], minutes[0].split('.')[0], minutes]
                        minute_count = 0
                        while minute_count < len(taxi_count_list) and minute_count < max_minute:
                            if taxi_count_list[minute_count]:
                                append_list.append(taxi_count_list[minute_count])
                                append_list.append(queue_length_list[minute_count])
                            else:
                                append_list.append(None)
                                append_list.append(None)
                            minute_count += 1
                        append_list.extend([round((sum(taxi_count_list) / len(taxi_count_list)), 2),count + 1])
                        duration_list.append(append_list)
                else:
                    if count != 0:
                        count = count + 1
                        minutes.append(queues.iloc[j]['time'])
                        taxi_count_list.append(queues.iloc[j]['taxi_count'])
                        queue_length_list.append(queues.iloc[j]['queue_length'])
                    else:
                        count = count + 1
                        minutes.append(queues.iloc[i]['time'])
                        taxi_count_list.append(queues.iloc[i]['taxi_count'])
                        queue_length_list.append(queues.iloc[i]['queue_length'])
                        minutes.append(queues.iloc[j]['time'])
                        taxi_count_list.append(queues.iloc[j]['taxi_count'])
                        queue_length_list.append(queues.iloc[j]['queue_length'])
            else:
                if minutes:
                    append_list = [date, d.day_name(), data['day_type'][0], minutes[0].split('.')[0], minutes]
                    minute_count = 0
                    while minute_count < max_minute:
                        if minute_count < len(taxi_count_list) and taxi_count_list[minute_count]:
                            append_list.append(taxi_count_list[minute_count])
                            append_list.append(queue_length_list[minute_count])
                        else:
                            append_list.append(None)
                            append_list.append(None)
                        minute_count += 1
                    append_list.extend([round((sum(taxi_count_list) / len(taxi_count_list)), 2),count + 1])
                    duration_list.append(append_list)
                    count = 0 
                    minutes = []
                    taxi_count_list = []
                    queue_length_list = []
            
            i = i + 1
        
    save_path = terminal + '_congestion'
    
    # name of csv file
    filename = terminal + "_queue_" + days_running + "_avg_combined" + ".csv"
    
    fields = ['date', 'day_of_week', 'day_type','hour','minutes'] 
    field_count = 0
    while field_count < max_minute:
        taxi_count_name = 'taxi_count_minute' + str(field_count)
        taxi_length_name = 'taxi_length_minute' + str(field_count)
        fields.append(taxi_count_name)
        fields.append(taxi_length_name)
        field_count += 1
    
    fields.extend(['taxi_count_avg', 'sum'])
    
    completeName = os.path.join(save_path, filename)
    
    # writing to csv file 
    with open(completeName, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(duration_list)
    
congestion_analysis()

def t1_one_day_analysis():
    date = '2024-01-03'

    d = pd.Timestamp(date)
    file_name = './t1_congestion/t1_' + date +'.csv'
    
    data = pd.read_csv(file_name)
    
    queues = data[(data['taxi_count'] >= 10) & (data['queue_length'] >= 100)]
        
    i = 0
    count = 0
    minutes = []
    taxi_count_list = []
    queues_len = len(queues)
    
    duration_list = []
    while i < queues_len - 1:
        j = i + 1
        
        if (queues.iloc[j]['id']-queues.iloc[i]['id']) == 1:
            if j == queues_len - 1:
                if count != 0:
                    duration_list.append([date, d.day_name(), data['day_type'][0], minutes[0].split('.')[0], minutes, taxi_count_list, count + 1])
            else:
                if count != 0:
                    count = count + 1
                    minutes.append(queues.iloc[j]['time'])
                    taxi_count_list.append(queues.iloc[j]['taxi_count'])
                else:
                    count = count + 1
                    minutes.append(queues.iloc[i]['time'])
                    taxi_count_list.append(queues.iloc[i]['taxi_count'])
                    minutes.append(queues.iloc[j]['time'])
                    taxi_count_list.append(queues.iloc[j]['taxi_count'])
        else:
            if minutes:
                duration_list.append([date, d.day_name(), data['day_type'][0], minutes[0].split('.')[0], minutes, taxi_count_list, count + 1])
                count = 0 
                minutes = []
                taxi_count_list = []
        
        i = i + 1
    
    save_path = 't1_congestion'
    # name of csv file 
    filename = "t1_queue_" + date + ".csv"
    
    fields = ['date', 'day_of_week', 'day_type','hour', 'minutes', 'taxi_count', 'sum']
    
    completeName = os.path.join(save_path, filename)
    
    # writing to csv file 
    with open(completeName, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(duration_list)
        
# t1_one_day_analysis()
    

            



