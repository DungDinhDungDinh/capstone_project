#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 10:17:23 2023

@author: dungdinh
"""

import geopandas as gpd
import pandas as pd 
# import matplotlib.pyplot as plt
from fiona.drvsupport import supported_drivers
# import contextily as cx
# import geoplot as gplt
import matplotlib.pyplot as plt
import requests
import geopy.distance
import datetime as dt
import csv
import geoplot as gplt
import geoplot.crs as gcrs
import seaborn as sns
from shapely.geometry import Point
from geopy.geocoders import Nominatim
# import plotly.express as px
import os

supported_drivers['KML'] = 'rw'


# gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
# gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
hawker_geo_df = gpd.read_file('./hawker-centres/hawker-centres-kml.kml',driver='KML')
taxi_stop_geo_df = gpd.read_file('./lta-taxi-stop/lta-taxi-stop-kml.kml', driver='KML')
singapore_subzones = gpd.GeoDataFrame.from_file('./singapore_subzones.kml', driver='KML')
hawker_geodataframe = gpd.GeoDataFrame.from_file('./hawker-centres/hawker-centres-kml.kml', driver='KML')
taxistand_geodataframe = gpd.GeoDataFrame.from_file('./lta-taxi-stop/lta-taxi-stop-kml.kml', driver='KML')


#Import data
parse_dates = ['date_time']
one_week_dinner = pd.read_csv('./one_week_dinner-2.csv', parse_dates=parse_dates)
one_month_dinner = pd.read_csv('./one_month_dinner-2.csv', parse_dates=parse_dates)
three_month_dinner = pd.read_csv('./three_month_dinner.csv', parse_dates=parse_dates)
six_month_dinner = pd.read_csv('./six_month_dinner.csv', parse_dates=parse_dates)
one_month_lunch = pd.read_csv('./one_month_lunch.csv', parse_dates=parse_dates)
three_month_lunch = pd.read_csv('./three_month_lunch.csv', parse_dates=parse_dates)
six_month_lunch = pd.read_csv('./six_month_lunch.csv', parse_dates=parse_dates)
six_month_data = pd.read_csv('./six_month_data.csv', parse_dates=parse_dates)



# extracting time from timestamp
one_week_dinner['time'] = [dt.datetime.time(d) for d in one_week_dinner['date_time']] 
one_month_dinner['time'] = [dt.datetime.time(d) for d in one_month_dinner['date_time']]
three_month_dinner['time'] = [dt.datetime.time(d) for d in three_month_dinner['date_time']]  
six_month_dinner['time'] = [dt.datetime.time(d) for d in six_month_dinner['date_time']] 
one_month_lunch['time'] = [dt.datetime.time(d) for d in one_month_lunch['date_time']] 
three_month_lunch['time'] = [dt.datetime.time(d) for d in three_month_lunch['date_time']] 
six_month_lunch['time'] = [dt.datetime.time(d) for d in six_month_lunch['date_time']] 

# extracting month from timestamp
six_month_data['month'] = six_month_data['date_time'].dt.month


# extracting weekday from timestamp
six_month_data['day_of_week'] = [d.weekday() for d in six_month_data['date_time']] 
# print(six_month_data['day_of_week'])

def even_days_creation():
    days = range(1, 31)
    res = []
    for day in days:
        res.append(f"{day:02}")
    return res

def odd_days_creation():
    days = range(1, 32)
    res = []
    for day in days:
        res.append(f"{day:02}")
    return res

def minute_creation():
    minutes = range(0, 60)
    res = []
    for minute in minutes:
        res.append(f"{minute:02}")
    return res

#Function to get taxi_count of June 2023
def getTaxiCountsByHour():
    hours = ['00','01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
    minutes = minute_creation()
    results = []
    days = odd_days_creation()
    
    for hour in hours:
        counts = 0
        for day in days:
            for minute in minutes:
                request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-05-' + day + 'T' + hour + '%3A' + minute + '%3A00'
                response = requests.get(request)
                data = response.json()
                taxi_counts = data['features'][0]['properties']['taxi_count']
                counts = counts + taxi_counts
        results.append([hour, counts])
    return results
        
def writingTaxiCountsByHourToCSVFile():
    fields = ['hour', 'taxi_counts']
    
    data_rows = getTaxiCountsByHour()
    
    # name of csv file 
    filename = "taxi_counts_by_hour_05-2023.csv"
            
    # writing to csv file 
    with open(filename, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(data_rows)

# writingTaxiCountsByHourToCSVFile()

#Function to invert longtitiude and latitude
def invertLongtitudeLatitude(coordinates):
    inverted_coordinates = []
    for x in coordinates:
        latitude = x[1]
        longtitude =  x[0]
        inverted_coordinate = (latitude, longtitude)
        inverted_coordinates.append(inverted_coordinate)
    return inverted_coordinates

# print(invertLongtitudeLatitude([[103.6237, 1.29071], [100, 1]]))

def getMaxHawkerInMinutes():
    hawker_geodataframe['lon'] = hawker_geodataframe['geometry'].apply(lambda p: p.x)
    hawker_geodataframe['lat'] = hawker_geodataframe['geometry'].apply(lambda p: p.y)
    dataframe = pd.DataFrame(data=hawker_geodataframe, columns=['lat','lon']) 
    dataframe['combined'] = dataframe.values.tolist()
    hawker_coordinates = dataframe['combined'].values.tolist()
    
    day = '01'
    
    hour = '18'
    
    minutes = ['00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55']
    
    for minute in minutes:
        request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-06-' + day +'T' + hour + '%3A' + minute +'%3A00'
        response = requests.get(request)
        data = response.json()
        taxi_driver_coordinates = data['features'][0]['geometry']['coordinates']
        taxi_driver_coordinates_inverted = invertLongtitudeLatitude(taxi_driver_coordinates)
        
        taxis_near_hawker = []
        
        for hawker in hawker_coordinates:
            count = 0
            for taxi_driver in taxi_driver_coordinates_inverted:
                distance = geopy.distance.geodesic(hawker, taxi_driver).km
                if distance <= 1.0:
                    count = count + 1
            taxis_near_hawker.append([hawker, count])
        
        # taxis_near_hawker['count'] = taxis_near_hawker.apply(lambda x: x[1])
        df = pd.DataFrame(taxis_near_hawker)
        # df['count'] = df.apply(lambda x: x[1])
        count_list = df.loc[:,1]
        hawker_list = df.loc[:,0]
        max_count = max(count_list)
        max_index = count_list[count_list == max_count].index[0]
        hawker_max = hawker_list[max_index]
        print(hawker_max)
    
# getMaxHawkerInMinutes()


def getMaxTaxiStand(time):
    # print(len(taxistand_geodataframe))
    taxistand_geodataframe['lon'] = taxistand_geodataframe['geometry'].apply(lambda p: p.x)
    taxistand_geodataframe['lat'] = taxistand_geodataframe['geometry'].apply(lambda p: p.y)
    dataframe = pd.DataFrame(data=taxistand_geodataframe, columns=['lat','lon']) 
    dataframe['combined'] = dataframe.values.tolist()
    taxistand_coordinates = dataframe['combined'].values.tolist()
    
    even_days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']
    for day in even_days:
        request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-06-' + day +'T' + time + '%3A00%3A00'
        response = requests.get(request)
        data = response.json()
        taxi_driver_coordinates = data['features'][0]['geometry']['coordinates']
        taxi_driver_coordinates_inverted = invertLongtitudeLatitude(taxi_driver_coordinates)
        
        taxis_near_taxistand = []
        
        for stand in taxistand_coordinates:
            count = 0
            for taxi_driver in taxi_driver_coordinates_inverted:
                distance = geopy.distance.geodesic(stand, taxi_driver).km
                if distance <= 3.0:
                    count = count + 1
            taxis_near_taxistand.append([stand, count])
        
        df = pd.DataFrame(taxis_near_taxistand)
        # df['count'] = df.apply(lambda x: x[1])
        count_list = df.loc[:,1]
        stand_list = df.loc[:,0]
        max_count = max(count_list)
        max_index = count_list[count_list == max_count].index[0]
        stand_max = stand_list[max_index]
        print(stand_max)
        # print(max_count)

# print(getMaxTaxiStand('24'))
        
def findLunchTime():
    # print(hawker_geodataframe)
    hawker_geodataframe['lon'] = hawker_geodataframe['geometry'].apply(lambda p: p.x)
    hawker_geodataframe['lat'] = hawker_geodataframe['geometry'].apply(lambda p: p.y)
    dataframe = pd.DataFrame(data=hawker_geodataframe, columns=['lat','lon']) 
    dataframe['combined'] = dataframe.values.tolist()
    hawker_coordinates = dataframe['combined'].values.tolist()
    
    #get taxi drivers
    day = '18'
    time = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    for x in time:
        request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-06-' + day +'T' + x + '%3A00%3A00'
        response = requests.get(request)
        data = response.json()
        taxi_driver_coordinates = data['features'][0]['geometry']['coordinates']
        taxi_driver_coordinates_inverted = invertLongtitudeLatitude(taxi_driver_coordinates)
        
        taxis_near_hawker = []
        
        for hawker in hawker_coordinates:
            count = 0
            for taxi_driver in taxi_driver_coordinates_inverted:
                distance = geopy.distance.geodesic(hawker, taxi_driver).km
                if distance <= 1.0:
                    count = count + 1
            taxis_near_hawker.append([hawker, count])
        
        # taxis_near_hawker['count'] = taxis_near_hawker.apply(lambda x: x[1])
        df = pd.DataFrame(taxis_near_hawker)
        # df['count'] = df.apply(lambda x: x[1])
        count_list = df.loc[:,1]
        hawker_list = df.loc[:,0]
        sum_taxi_near_hawkers = sum(count_list)
        # max_index = count_list[count_list == max_count].index[0]
        # hawker_max = hawker_list[max_index]
        print(sum_taxi_near_hawkers)
        # print(max_count)
    

    # print(taxis_near_hawker['count'])
    # max_index = taxis_near_hawker.index(max_value)
    # print(max_index)


#Function to get taxi_count around a point
def getTaxiCountsAroundPoint():
    Maxwell = (1.2805077172124257, 103.84478845262983)
    HongLim = (1.2854511122136445, 103.84582854110447)
    ABCBrickworks = (1.287432663819198, 103.80806370014119)
    
    lunch_time = ['10', '11', '12', '13', '14']
    dinner_time = ['16', '17', '18', '19', '20']
    
    odd_days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    
    even_days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']
    
    january = ['11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
               '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    
    february = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28']
    
    # open the file in the write mode
    f = open('./test.csv', 'w')
    
    # create the csv writer
    writer = csv.writer(f)  
    
    
    for day in odd_days:
        for x in lunch_time:
            request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-03-' + day +'T' + x + '%3A00%3A00'
            response = requests.get(request)
            data = response.json()
            taxi_driver_coordinates = data['features'][0]['geometry']['coordinates']
            taxi_driver_coordinates_inverted = invertLongtitudeLatitude(taxi_driver_coordinates)
            
            count = 0
            for taxi_driver in taxi_driver_coordinates_inverted:
                distance = geopy.distance.geodesic(ABCBrickworks, taxi_driver).km
                if distance <= 3.0:
                    count = count + 1
            # print('Day {} - {}:00 has {} drivers'.format(day, x, count))
            # print(count)
            
            # write a row to the csv file
            writer.writerow('count')
            
    # close the file
    f.close()

# print(getTaxiCountsAroundPoint())

def extractTaxiCountsByHour():
    even_days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']
    
    odd_days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    january = ['11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
               '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    
    february = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28']
    
    time = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    
    # taxi_count_dataset = pd.DataFrame([], columns=['date', 'time', 'taxi_counts'])
    # taxi_count_dataset = pd.DataFrame({
    #                         'date': [],
    #                         'time': [],
    #                         'taxi_counts': []
    #                         }, index=['date', 'time', 'taxi_counts'])
    taxi_count_frame = {'date': [],
                        'time': [],
                        'taxi_counts': []}
    taxi_count_dataset = pd.DataFrame(taxi_count_frame)
     
    for day in january:
        for x in time:
            request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-01-' + day +'T' + x + '%3A00%3A00'
            response = requests.get(request)
            data = response.json()
            taxi_count = data['features'][0]['properties']['taxi_count']
            # df1 = pd.DataFrame({
            #                        'date': [day],
            #                        'time': [x],
            #                        'taxi_counts': [taxi_count]
            #                     })
            
            # print(df1)
            
            # taxi_count_dataset.append(df1)
            taxi_count_dataset.loc[len(taxi_count_dataset.index)] = [day, x, taxi_count]
            # print(taxi_count_dataset)
    
    # taxi_count_dataset = pd.DataFrame({'date': even_days, 'time': time, 'taxi_counts': taxi_counts}, columns=['date', 'time', 'taxi_counts'])
    # print(taxi_count_dataset)
    return taxi_count_dataset

def getTaxiCountsByHour():
    even_days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14']
    
    odd_days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    january = ['11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
               '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
    
    february = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26', '27', '28']
    
    time = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    
     
    for day in even_days:
        for x in time:
            request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-06-' + day +'T' + x + '%3A00%3A00'
            response = requests.get(request)
            data = response.json()
            taxi_count = data['features'][0]['properties']['taxi_count']
            print(taxi_count)
            
# print(getTaxiCountsByHour())


# return taxi_counts in console
# def extractTaxiCountsByTime():
#     even_days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
#             '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
#             '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']
#     time = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24']
    
#     for day in even_days:
#         for x in time:
#             request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-06-' + day +'T' + x + '%3A00%3A00'
#             response = requests.get(request)
#             data = response.json()
#             taxi_count = data['features'][0]['properties']['taxi_count']
#             print(taxi_count)

# extractTaxiCountsByTime()

#Return taxi counts by area
def taxiCountsByArea(day, time):
    singapore_subzones['lon'] = singapore_subzones.centroid.x
    singapore_subzones['lat'] = singapore_subzones.centroid.y
    dataframe = pd.DataFrame(data=singapore_subzones, columns=['lat','lon']) 
    dataframe['combined'] = dataframe.values.tolist()
    subzone_coordinates = dataframe['combined'].values.tolist()
    
    
    request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-05-' + day +'T' + time + '%3A00%3A00'
    response = requests.get(request)
    data = response.json()
    taxi_driver_coordinates = data['features'][0]['geometry']['coordinates']
    taxi_driver_coordinates_inverted = invertLongtitudeLatitude(taxi_driver_coordinates)
    
    taxis_near_centroid = []
    
    for centroid in subzone_coordinates:
        count = 0
        for taxi_driver in taxi_driver_coordinates_inverted:
            distance = geopy.distance.geodesic(centroid, taxi_driver).km
            if distance <= 5.0:
                count = count + 1
        taxis_near_centroid.append([centroid, count])
    
    df = pd.DataFrame(taxis_near_centroid)
    count_list = df.loc[:,1]
    max_count = max(count_list)
    max_index = count_list[count_list == max_count].index[0]
    area = singapore_subzones.Description[max_index]
    # centroid_max = centroid_list[max_index]
    print(time)
    print(max_count)
    print(area)
    
# taxiCountsByArea('27','23')


#Measure the change on taxi drivers after 1 minute
def measureTaxiMovementByMinute(day, time1, time2):
    request1 = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-05-' + day + 'T' + time1
    request2 = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-05-' + day + 'T' + time2
    
    response1 = requests.get(request1)
    data1 = response1.json()
    taxi_driver_coordinates1 = data1['features'][0]['geometry']['coordinates']
    taxi_driver_coordinates_inverted1 = invertLongtitudeLatitude(taxi_driver_coordinates1)
    
    response2 = requests.get(request2)
    data2 = response2.json()
    taxi_driver_coordinates2 = data2['features'][0]['geometry']['coordinates']
    taxi_driver_coordinates_inverted2 = invertLongtitudeLatitude(taxi_driver_coordinates2)
    
    taxi1_changes = []
    taxi2_changes = []
    
    for taxi1 in taxi_driver_coordinates_inverted1:
        for taxi2 in taxi_driver_coordinates_inverted2:
            distance = geopy.distance.geodesic(taxi1, taxi2).km
            if distance <= 0.5:
                taxi1_changes.append(taxi1)
                taxi2_changes.append(taxi2)
    
    return taxi1_changes, taxi2_changes
    
def convertFromCoordinatestoDataframe(coordinates):
    lats = []
    longs = []
    for coordinate in coordinates:
        lat = coordinate[0]
        long = coordinate[1]
        lats.append(lat)
        longs.append(long)
    
    df = pd.DataFrame({'lat': lats, 'long': longs})
    return df

#GENERATING SENTOSA DATASETS
def getSentosaTaxiClusters(date, time):
    request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=' + date + 'T' + time
    response = requests.get(request)
    data = response.json()
    coordinates = data['features'][0]['geometry']['coordinates']
    lons = [x[0] for x in coordinates]
    lats = [x[1] for x in coordinates]
    df = pd.DataFrame({'lons': lons, 'lats': lats})
    
    sentosa_gdf_1 = df[(df['lats'] <= 1.2631) & (df['lons'] >= 103.80) & (df['lons'] <= 103.85)]
    sentosa_gdf_2 = df[(df['lats'] <= 1.2655) & ((df['lats'] > 1.2631)) & (df['lons'] > 103.82373) & (df['lons'] <= 103.8246)]
    sentosa_gdf = pd.concat([sentosa_gdf_1, sentosa_gdf_2])
    sentosa_gdf_inverted = invertLongtitudeLatitude(sentosa_gdf.values.tolist())
    
    clusters = []
    sentosa_length = len(sentosa_gdf_inverted)
    
    for i in range(0, sentosa_length):
        for j in range(0, sentosa_length):
            distance = geopy.distance.geodesic(sentosa_gdf_inverted[i], sentosa_gdf_inverted[j]).m
            #distance by bird flight
            if distance <= 26.62:
                if sentosa_gdf_inverted[i] == sentosa_gdf_inverted[j]:
                    string_i = str(sentosa_gdf_inverted[i])
                    clusters.append([string_i[1:-1]])
                else:
                    string_i = str(sentosa_gdf_inverted[i])
                    string_j = str(sentosa_gdf_inverted[j])
                    clusters.append([string_i[1:-1], string_j[1:-1]])   
                    
    # clusters = [["A", "B"], ["C", "D"], ["B", "D"], ["F", "H"], ["F", "K"]]
    i = 0
    while i < len(clusters):
        j = i+1
        found = False
        while j < len(clusters):
            for var in clusters[i]:
                # print("clusters[i]=", clusters[i])
                if var in clusters[j]:
                    # print(test[j])
                    found = True
                    clusters[i] = clusters[i] + clusters[j]
                    clusters.pop(j)
                    break
            j = j+1
        if found == False: 
            i=i+1

    # print(clusters)
                    
                    
            
    
    merged_clusters_set = []
    for e in clusters:
        merged_clusters_set.append(set(e))
        
    # print(merged_clusters_set)
    # print(get_all_elements_in_list_of_lists(merged_clusters_set))
    # print(geopy.distance.geodesic((1.25, 103.82569), (1.25, 103.82548)).m)
    return merged_clusters_set

def matchingClusterNames(clusters):
    capella_hotel = ['1.25, 103.82285', '1.25, 103.82569', '1.25, 103.82539', '1.25, 103.82548', '1.25003, 103.82554',
                     '1.2511, 103.82391', '1.25, 103.82545', '1.25, 103.82551', '1.25, 103.8249', '1.25, 103.82553', 
                     '1.25, 103.82424', '1.25, 103.82464', '1.25, 103.82505', '1.25, 103.82554', '1.25053, 103.82561',
                     '1.25, 103.82568', '1.25, 103.82563', '1.25, 103.82543', '1.25, 103.82513', '1.25008, 103.82395', 
                     '1.25151, 103.82363']
    resorts_world_sentosa = ['1.25594, 103.82321', '1.25607, 103.82342', '1.25383, 103.82534', '1.25268, 103.82216',
                             '1.25505408333333, 103.824558116667', '1.25495, 103.82464', '1.25608865, 103.823412416667',
                             '1.25530748333333, 103.824460866667', '1.2561, 103.82332', '1.2559, 103.82325', '1.25492, 103.82478',
                             '1.25616, 103.82312', '1.25455, 103.81957', '1.25293, 103.82168', '1.25587, 103.82316', 
                             '1.25422, 103.82499', '1.25517938333333, 103.819011383333', '1.2558, 103.82415', 
                             '1.25493908333333, 103.824152033333', '1.25698, 103.81845', '1.25752, 103.81676', '1.25756, 103.81684',
                             '1.25761, 103.81689', '1.25767, 103.81694', '1.25758, 103.81683', '1.25763, 103.81687', 
                             '1.25606, 103.82328', '1.25761, 103.81687', '1.25759, 103.81685', '1.2576, 103.81685', 
                             '1.25765, 103.81693', '1.25756, 103.81685', '1.2576, 103.8169', '1.25765, 103.81696', 
                             '1.25761, 103.8169', '1.25761, 103.81692', '1.25685, 103.81739', '1.2576, 103.81691', 
                             '1.25476, 103.82469', '1.25761, 103.81691', '1.2576, 103.81692', '1.25675, 103.81867', 
                             '1.25536215, 103.824336833333', '1.25763, 103.81697', '1.25672, 103.81869', '1.25675, 103.81868',
                             '1.25673, 103.81871', '1.25675, 103.81869', '1.2541, 103.82518', '1.25675, 103.81871', 
                             '1.25675, 103.81872', '1.25677, 103.81867', '1.25391883333333, 103.8254395']
    straits_of_singapore = ['1.26281, 103.82372', '1.26189, 103.82366', '1.26, 103.82389', 
                            '1.26100515, 103.823901833333', '1.26, 103.82404', '1.26014, 103.82401', 
                            '1.26029635, 103.824052033333', '1.25712, 103.82374', '1.26101296666667, 103.823662166667',
                            '1.25927, 103.82374', '1.259073, 103.824064', '1.26, 103.82383', '1.26038, 103.82403',
                            '1.25965, 103.82403', '1.25788, 103.8241', '1.26013, 103.82401', '1.25942, 103.82376',
                            '1.26123876666667, 103.823866866667', '1.25768, 103.82369', '1.259613, 103.823789', 
                            '1.26134, 103.82364', '1.262, 103.82387', '1.25917, 103.82401', '1.26, 103.82368', 
                            '1.26115, 103.82366', '1.25889, 103.82375', '1.259363, 103.823717', '1.26105056666667, 103.82387275',
                            '1.25771806666667, 103.823986333333', '1.2591806, 103.824083666667', '1.25699261666667, 103.823705583333',
                            '1.26127133333333, 103.823851666667', '1.2569, 103.82396', '1.25989883333333, 103.823807683333',
                            '1.25826966666667, 103.823990333333', '1.26, 103.82402', '1.26, 103.824', '1.2601255, 103.8240085',
                            '1.25756, 103.82397', '1.25773, 103.824', '1.25647, 103.82394', '1.26271, 103.82387', 
                            '1.26, 103.82401', '1.26222, 103.82385', '1.26, 103.82399', '1.25842, 103.82403', '1.25899, 103.82378',
                            '1.25984, 103.82378', '1.25682, 103.82372', '1.262085, 103.823734', '1.25765, 103.82399', 
                            '1.25966, 103.82405', '1.2602, 103.82406', '1.26208701666667, 103.82365575', '1.25946395, 103.8240396',
                            '1.25681, 103.8237', '1.26, 103.82388', '1.26053, 103.824', '1.26, 103.82403', 
                            '1.26087183333333, 103.823924666667', '1.26, 103.82408', '1.26084, 103.82392', 
                            '1.26075791666667, 103.823999166667', '1.25969, 103.82379', '1.25704, 103.82397', 
                            '1.26255693333333, 103.823726066667', '1.25936883333333, 103.824049', 
                            '1.25649583333333, 103.823978666667', '1.25962, 103.82405', '1.26138, 103.82382', '1.26, 103.82386']
    southern_islands = ['1.254618, 103.825437', '1.25521, 103.82503', '1.25428, 103.82566', '1.2544, 103.82552', 
                        '1.25428, 103.82562', '1.25458, 103.82549', '1.255981, 103.824202', '1.25511, 103.82494',
                        '1.254151, 103.825795583333', '1.254666, 103.825392', '1.254149, 103.825775583333', 
                        '1.254157, 103.825855583333', '1.2544, 103.82554', '1.25511508333333, 103.825168116667',
                        '1.254144, 103.825725583333', '1.25445, 103.82557', '1.25411033333333, 103.825718866667',
                        '1.25429806666667, 103.8256622', '1.254519, 103.825433', '1.25416, 103.82574', 
                        '1.2544, 103.82562', '1.25413633333333, 103.825978866667', '1.254595, 103.825396', '1.254151, 103.8258',
                        '1.25438091666667, 103.8254599', '1.25440791666667, 103.8257299', '1.25412233333333, 103.825838866667',
                        '1.254159, 103.825875583333', '1.25485, 103.82529', '1.25464, 103.82539', '1.254163, 103.825915583333', 
                        '1.254327, 103.825535', '1.25559, 103.8246', '1.25437, 103.82551', '1.25500093333333, 103.824947283333',
                        '1.25461943333333, 103.825611583333', '1.254169, 103.825975583333', '1.254153, 103.825815583333',
                        '1.25445, 103.82553', '1.254166, 103.825945583333', '1.25461343333333, 103.825551583333',
                        '1.25497833333333, 103.825240166667', '1.25628, 103.824', '1.25437, 103.82547', '1.25626, 103.82401', 
                        '1.255373, 103.824824', '1.25462143333333, 103.825631583333', '1.25573, 103.82446', '1.254589, 103.825426',
                        '1.25431, 103.82548', '1.25435, 103.82545', '1.254147, 103.825755583333', '1.25579075, 103.824412616667',
                        '1.254156, 103.825845583333', '1.25553, 103.82464', '1.25464221666667, 103.825392833333', 
                        '1.25416, 103.825885583333', '1.254167, 103.825955583333', '1.25542416666667, 103.824856566667', 
                        '1.25434, 103.82545', '1.254662, 103.8256', '1.254161, 103.825895583333', '1.25446, 103.82554', 
                        '1.25445, 103.8254', '1.254143, 103.825715583333', '1.25423, 103.82556', '1.25529, 103.82491', 
                        '1.25438, 103.82554', '1.25485, 103.82533', '1.25451, 103.82556', '1.25451666666667, 103.825581833333',
                        '1.25456256666667, 103.825588566667', '1.25435471666667, 103.825701783333', '1.256026, 103.824222',
                        '1.25436371666667, 103.825791783333', '1.25436771666667, 103.825831783333', '1.25418, 103.82557',
                        '1.25434171666667, 103.825571783333', '1.25526, 103.8249', '1.25435871666667, 103.825741783333', 
                        '1.25436671666667, 103.825821783333', '1.25425, 103.82556', '1.25439, 103.82558']
    sentosa_gateway = ['1.26337, 103.82375', '1.26339, 103.82372', '1.26423, 103.82406', '1.26422, 103.82406',
                       '1.26473, 103.82388', '1.26356, 103.82368', '1.2557, 103.82405', '1.2646335, 103.82401', 
                       '1.26542766666667, 103.824308666667', '1.263414, 103.823979', '1.26346, 103.8237', '1.26328, 103.82369',
                       '1.264306, 103.823865', '1.2634298, 103.823728516667', '1.26447, 103.82396', '1.26526, 103.8237', 
                       '1.26503743333333, 103.8237048', '1.26507786666667, 103.823781733333', '1.26432, 103.82406', 
                       '1.26542, 103.82405', '1.26443, 103.82375', '1.26431, 103.82401', '1.26518996666667, 103.82424935',
                       '1.26401, 103.82391', '1.26465425, 103.82416865', '1.26464325, 103.82405865', '1.2563, 103.823655',
                       '1.26519268333333, 103.824010066667', '1.26548, 103.82375', '1.265, 103.8241', '1.26549, 103.82377',
                       '1.26491, 103.82382', '1.26519, 103.82401', '1.25514, 103.81916', '1.263798, 103.824', '1.264, 103.82384',
                       '1.26436, 103.82406', '1.25598, 103.8232', '1.2638, 103.82401', '1.26434, 103.82408', '1.26436, 103.82409',
                       '1.26434, 103.8241', '1.26434, 103.82409', '1.26362493333333, 103.8237967', '1.2639, 103.82382',
                       '1.2636, 103.82401', '1.26384, 103.82381', '1.26497, 103.82381', '1.26405, 103.82401']
    gateway_avenue = ['1.25409, 103.82571', '1.25408, 103.82567', '1.25404, 103.82536', '1.25239, 103.82534', 
                      '1.254126, 103.825545583333', '1.254135, 103.825635583333', '1.25507108333333, 103.824728116667',
                      '1.25413, 103.82548', '1.25413, 103.825585583333', '1.25415, 103.82563', '1.25502, 103.82482',
                      '1.25433, 103.8254', '1.254133, 103.825615583333', '1.25406, 103.82567', '1.254, 103.82567', 
                      '1.254137, 103.825655583333', '1.25403, 103.82545', '1.25248, 103.82563', '1.25362, 103.8261',
                      '1.25153, 103.82486', '1.2524, 103.82536', '1.25229688333333, 103.825233416667', '1.25437, 103.82531',
                      '1.25189536666667, 103.82485545', '1.25413, 103.82553', '1.254975, 103.824841', 
                      '1.25192436666667, 103.82514545', '1.25409, 103.82561', '1.25261, 103.82562', '1.25476, 103.82487',
                      '1.254132, 103.825605583333', '1.254127, 103.825555583333', '1.25414, 103.825685583333', 
                      '1.25392583333333, 103.8255095', '1.25396683333333, 103.8259195']
    pavilion_carpark = ['1.24982, 103.82784', '1.2497, 103.82795', '1.2498, 103.82782', '1.24972, 103.82795',
                        '1.24979, 103.82784', '1.24976, 103.82782', '1.24975, 103.82791', '1.2497, 103.82794',
                        '1.24978, 103.82782', '1.24975, 103.82795', '1.24974, 103.82795', '1.24972, 103.82794',
                        '1.24974, 103.82794', '1.24973, 103.82794', '1.24938, 103.82788', '1.25407, 103.82569']
    opp_amara_sanctuary_resort = ['1.25259798333333, 103.822876733333', '1.25259898333333, 103.822886733333'] 
    amara_sanctuary_resort = ['1.25258098333333, 103.822706733333', '1.25258598333333, 103.822756733333', '1.25274, 103.82257']
    cove_drive_station = ['1.24706, 103.83924', '1.24706, 103.83926', '1.24692, 103.83919', '1.24694, 103.83922']
    sentosa_cove = ['1.24364, 103.8404']
    sofitel_hotel = ['1.24525, 103.82764', '1.24519, 103.82763', '1.24452, 103.8284', '1.2453, 103.82764', 
                     '1.245, 103.82794', '1.24530328333333, 103.828256183333']
    artillery_avenue = ['1.25262198333333, 103.823116733333', '1.25265698333333, 103.823466733333', 
                        '1.24939, 103.82692', '1.25262698333333, 103.823166733333', '1.25264198333333, 103.823316733333',
                        '1.25363316666667, 103.82063275', '1.25064, 103.82551', '1.2537063, 103.820152216667', 
                        '1.25386, 103.82014', '1.25254, 103.82361', '1.25197811666667, 103.824353416667', 
                        '1.25267268333333, 103.823127883333', '1.250238, 103.825934', '1.24946, 103.8269', '1.25244, 103.82356',
                        '1.2507, 103.82547', '1.25314, 103.82133']
    shangri_la = ['1.25805333333333, 103.810172833333', '1.25805, 103.80976', '1.25816, 103.80991', '1.25818, 103.80995',
                  '1.25802821666667, 103.810325233333', '1.25783, 103.8104', '1.2579, 103.81042']
    the_coast_sentosa_cove = ['1.246073, 103.84428175', '1.24604, 103.84387']
    beach_view_road = ['1.25295, 103.81896', '1.25087, 103.81924', '1.25392, 103.82003', '1.25213, 103.81888']
    sentosa_golf_club = ['1.24469883333333, 103.829094466667', '1.24766, 103.83823']
    allanbrooke_road = ['1.24647228333333, 103.837132366667', '1.24788068333333, 103.832285316667', '1.24613, 103.836',
                        '1.248, 103.82983', '1.24729, 103.83366', '1.24856, 103.82869', '1.24898, 103.82843', 
                        '1.24726, 103.83382', '1.2483, 103.82893', '1.24776, 103.83245', '1.24643, 103.83449', '1.24863, 103.82865']
    beach_station = ['1.25144, 103.81926', '1.24634255, 103.83484255', '1.24903743333333, 103.827350783333', 
                     '1.247897, 103.831292', '1.25168, 103.81878']
    bukit_manis_road = ['1.24771483333333, 103.828131966667']
    oasia_resort_sentosa = ['1.25344, 103.81945', '1.2536653, 103.819742216667', '1.25308, 103.81984', '1.25302, 103.82',
                            '1.25304, 103.81999']
    cove_grove = ['1.24, 103.83638']
    allanbrooke_road_2227 = ['1.24722, 103.83727']
    siloso_road = ['1.2577, 103.81094', '1.25609083333333, 103.816764683333', '1.25556, 103.81842', '1.25753, 103.81151']
    opp_village_hotel = ['1.25330703333333, 103.821127233333', '1.25331138333333, 103.8211381']
    adventure_cove_water_park = ['1.25686251666667, 103.817676916667']
    ocean_drive = ['1.25256, 103.8454', '1.25262, 103.84567', '1.25167, 103.84385', '1.24929, 103.84118', 
                   '1.25193471666667, 103.8446535', '1.25177, 103.8441', '1.25200671666667, 103.8453735', '1.25263, 103.8464', 
                   '1.2497, 103.84698', '1.24972045, 103.841862816667', '1.25094, 103.84254', '1.2522, 103.84504', 
                   '1.2498, 103.84703', '1.24861733333333, 103.840040183333', '1.2459, 103.8445', '1.2443, 103.84273',
                   '1.251613, 103.843203', '1.248952, 103.841127', '1.24356, 103.84197', '1.24834, 103.84572', 
                   '1.24558, 103.84428', '1.2522, 103.84714', '1.25161, 103.84325', '1.24909, 103.84665', '1.24966, 103.84165',
                   '1.25265, 103.84577', '1.24852, 103.83994', '1.25162, 103.84356', '1.24743, 103.83918', '1.24866, 103.84007']
    w_hotel = ['1.24699, 103.84255', '1.24647, 103.84226', '1.24646, 103.84226', '1.24644, 103.84224', '1.24638, 103.84231',
               '1.24649, 103.84224', '1.24654, 103.84212', '1.24654, 103.84215']
    universal_studios = ['1.25489508333333, 103.823712033333', '1.254896, 103.8237']
    cove_way = ['1.24165, 103.83945', '1.24838, 103.84161', '1.24857, 103.84121']
    cove_avenue = ['1.24781, 103.8383', '1.247403, 103.837404']
    equarius_hotel = ['1.25747, 103.81672']
    paradise_island = ['1.249153, 103.844579', '1.249808, 103.843928']
    sentosa_cove = ['1.24414, 103.84161']
    palawan_beach = ['1.25, 103.82054']
    
    cluster_list = list(clusters)
    
    for cluster in cluster_list:
        for coordinate in cluster:       
            if coordinate in capella_hotel:
                print('Capella Hotel')
                # print(len(cluster))
                break
            elif coordinate in resorts_world_sentosa:
                print('Resorts World Sentosa')
                # print(len(cluster))
                break
            elif coordinate in straits_of_singapore:
                print('Straits of Singapore')
                # print(len(cluster))
                break
            elif coordinate in southern_islands:
                print('Southern Islands')
                # print(len(cluster))
                break
            elif coordinate in sentosa_gateway:
                print('Sentosa Gateway')
                # print(len(cluster))
                break
            elif coordinate in gateway_avenue:
                print('Gateway Avenue')
                # print(len(cluster))
                break
            elif coordinate in pavilion_carpark:
                print('Carpark (1.249570, 103.827800)')
                # print(len(cluster))
                break
            elif coordinate in opp_amara_sanctuary_resort:
                print('Opp Amara Sanctuary')
                # print(len(cluster))
                break
            elif coordinate in cove_drive_station:
                print('Cove Drive Station')
                # print(len(cluster))
                break
            elif coordinate in sentosa_cove:
                print('Sentosa Cove')
                # print(len(cluster))
                break
            elif coordinate in sofitel_hotel:
                print('Sofitel Singapore Sentosa Resort & Spa')
                # print(len(cluster))
                break
            elif coordinate in amara_sanctuary_resort:
                print('Amara Sanctuary Resort')
                # print(len(cluster))
                break
            elif coordinate in artillery_avenue:
                print('Artillery Avenue')
                # print(len(cluster))
                break
            elif coordinate in shangri_la:
                print('Shangri-La Rasa')
                # print(len(cluster))
                break
            elif coordinate in the_coast_sentosa_cove:
                print('The Coast at Sentosa Cove')
                # print(len(cluster))
                break
            elif coordinate in beach_view_road:
                print('Beach View Road')
                # print(len(cluster))
                break
            elif coordinate in sentosa_golf_club:
                print('Sentosa Golf Club')
                # print(len(cluster))
                break
            elif coordinate in allanbrooke_road:
                print('Allanbrooke Road')
                # print(len(cluster))
                break
            elif coordinate in beach_station:
                print('Beach Station')
                # print(len(cluster))
                break
            elif coordinate in bukit_manis_road:
                print('Bukit Manis Road')
                # print(len(cluster))
                break
            elif coordinate in oasia_resort_sentosa:
                print('Oasia Resort Sentosa')
                # print(len(cluster))
                break
            elif coordinate in cove_grove:
                print('Cove Grove')
                # print(len(cluster))
                break
            elif coordinate in allanbrooke_road_2227:
                print('1.24722, 103.83727')
            elif coordinate in siloso_road:
                print('Siloso Road')
            elif coordinate in opp_village_hotel:
                print('Opp Village Hotel')
            elif coordinate in adventure_cove_water_park:
                print('Adventure Cove Waterpark')
            elif coordinate in ocean_drive:
                print('Ocean Drive')
            elif coordinate in w_hotel:
                print('W Hotel/Quayside Isle')  
            elif coordinate in universal_studios:
                print('Universal Studios') 
            elif coordinate in cove_way:
                print('Cove Way')
            elif coordinate in cove_avenue:
                print('Cove Avenue')
            elif coordinate in equarius_hotel:
                print('Equarius Hotel and Villas')
            elif coordinate in paradise_island:
                print('Paradise Island')
            elif coordinate in sentosa_cove:
                print('Sentosa Cove')
            elif coordinate in palawan_beach:
                print('Palawan Beach')
            else:
                print(coordinate)
                # print(len(cluster))
                break

def get_all_elements_in_list_of_lists(list_e):
    for element in list_e:
        print(len(element))

minutes = minute_creation()

def getSentosaAddresses(date, hour, day_type):
    geoLoc = Nominatim(user_agent="GetLoc")
    
    
    data_rows = []

    
    for minute in minutes:
        time_input = hour + '%3A' + minute + '%3A00'
        
        time = time_input.replace('%3A', ':')
        
        clusters = getSentosaTaxiClusters(date, time_input)
        
        cluster_list = list(clusters)
        
        for cluster in cluster_list:
            try:
                locname = geoLoc.reverse(list(cluster)[0])
                address = locname.address
                if address.partition(',')[0].isnumeric():
                    first_two = address.split(',',9)[1:2]
                    address_name = ','.join(first_two).strip(' ')
                    data_rows.append([date, time, len(cluster), address_name, day_type])
                else:
                   address_name = address.partition(',')[0] 
                   data_rows.append([date, time, len(cluster), address_name, day_type])
            except:
                data_rows.append([date, time, len(cluster), "", day_type])
            
    return(data_rows)
    
# start = time.time()

# end = time.time()
# print(end - start)
# getSentosaAddresses('2023-05-29', '02', 'weekday')   

# getSentosaAddresses(sentosa_clusters, date, time, day_type)
# get_all_elements_in_list_of_lists(sentosa_clusters)

distance = geopy.distance.geodesic((1.35121, 103.9843), (1.35145, 103.98443)).m
print(distance)


def writingToCSVFile():
    fields = ['date', 'time', 'cluster_size', 'address', 'day_type']
    
    save_path = 'sentosa'
    
    #EDIT 2 PLACES !!!!
    date = '2023-06-29'
    day_type = 'holiday'
    
    hours = ['00','01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
    
    for hour in hours:
        #creating rows
        data_rows = getSentosaAddresses(date, hour, day_type)
        
        # name of csv file 
        filename = "sentosa_" + date + "_" + hour + ".csv"
        
        completeName = os.path.join(save_path, date, filename)
            
        # writing to csv file 
        with open(completeName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(fields) 
                
            # writing the data rows 
            csvwriter.writerows(data_rows)

# writingToCSVFile()

# print(geopy.distance.geodesic((1.25415, 103.82563), (1.25439891666667, 103.8256399)).m)



#Visualize
# fig, ax = plt.subplots()

# singapore_subzones.plot(ax=ax, color='black')

# def getTaxiCoordinatesByTime(date, time):
#     request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-' + date + 'T' + time
#     response = requests.get(request)
#     data = response.json()
#     coordinates = data['features'][0]['geometry']['coordinates']
#     lons = [x[0] for x in coordinates]
#     lats = [x[1] for x in coordinates]
#     df = pd.DataFrame({'lons': lons, 'lats': lats})
#     gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lons, df.lats), crs="EPSG:4326")
#     return gdf

# taxi1_changes_df = getTaxiCoordinatesByTime('01-19', '06%3A03%3A00')

# #SCATTER
# ax.scatter(taxi1_changes_df['lons'], taxi1_changes_df['lats'], s=2, picker=True)

# def onpick(event):
#     ind = event.ind
#     data = taxi1_changes_df.iloc[ind]
#     x = data['lons']
#     y = data['lats']
#     print(data)
#     # print('%f, %f'%(y,x))

# fig.canvas.mpl_connect('pick_event', onpick)
# plt.show()

# cid = fig.canvas.mpl_connect('button_press_event', onclick)
# fig.canvas.callbacks.connect('pick_event', on_pick)

# gplt.kdeplot(taxi1_changes_df, ax=ax)
# print(taxi1_changes_df)
# sns.displot(taxi1_changes_df, x='lon', y='lat', kind='kde')


# gplt.polyplot(Polygons, ax=ax)
# kde = sns.kdeplot(
#     ax=ax,
#     levels=10,
#     x=taxi1_changes_df['geometry'].x,
#     y= taxi1_changes_df['geometry'].y,
#     fill=True,
#     cmap='Reds'
# )

# gplt.pointplot(
#     taxi1_changes_df,
#     ax=ax
#     )
# taxi2_changes_df = getTaxiCoordinatesByHour('28', '00%3A05%3A00')


# taxi1_changes_df.plot.scatter(x='long', y='lat', ax=ax, s=2, color='yellow', marker='*')
# taxi2_changes_df.plot.scatter(x='long', y='lat', ax=ax, s=2, color='blue')


# taxi2_changes_df.plot(
#             figsize=(10, 6),
#             markersize=2,
#             color='blue',
#             ax=ax)


    
    

# taxi_stop_geo_df.plot(
#             figsize=(10, 6),
#             markersize=10,
#             color='black',
#             ax=ax)

# taxi_available_df.plot(ax=ax)

# plt.axis('off')
# plt.show()

#Visualize 1 week dinner
# time_groupby = one_week_dinner.groupby(['time']).sum().reset_index()
# print(time_groupby['time'])
# time_groupby.plot.bar()

#Visualize 1 month dinner
# time_groupby = six_month_dinner.groupby(['time']).sum().reset_index()
# print(time_groupby['time'])
# time_groupby.plot.bar()

#Visualize 1 month lunch
# time_groupby = one_month_lunch.groupby(['time']).sum().reset_index()
# print(time_groupby['time'])
# time_groupby.plot.bar()

#Visualize 1 week lunch
# one_week_lunch = one_month_lunch.iloc[0:105]
# time_groupby = one_week_lunch.groupby(['time']).sum().reset_index()
# time_groupby.plot.bar()

#Visualize 3 months lunch
# time_groupby = three_month_lunch.groupby(['time']).sum().reset_index()
# time_groupby.plot.bar()

#Visualize 6 months lunch
# time_groupby = six_month_lunch.groupby(['time']).sum().reset_index()
# time_groupby.plot.bar()

#Visualize 6 months taxi counts
# time_groupby = six_month_data.groupby(['month']).sum().reset_index()
# time_groupby.plot.bar()

#Visualize 6 months day of a week taxi counts
# time_groupby = six_month_data.groupby(['day_of_week']).sum().reset_index()
# time_groupby.plot.bar(x='day_of_week', y='taxi_counts')

#Visualize by day type
# time_groupby = six_month_data.groupby(['day_type']).sum().reset_index()
# time_groupby.plot.bar(x='day_type', y='taxi_counts')

#Visualize 1 day taxi_counts
# one_day_taxi_counts = extractTaxiCountsByHour()
# one_day_taxi_counts.plot.bar(x='time', y='taxi_counts')


#Visualize 1 month taxi_counts by time
# one_moth_taxi_count = extractTaxiCountsByHour()
# one_moth_taxi_count_groupby = one_moth_taxi_count.groupby(['time']).sum().reset_index()
# # print(one_moth_taxi_count_groupby)
# one_moth_taxi_count_groupby_sorted = one_moth_taxi_count_groupby.sort_values(['taxi_counts'])
# print(one_moth_taxi_count_groupby_sorted)
# top5 = one_moth_taxi_count_groupby.sort_values(['taxi_counts']).tail(5)
# print(top5)
# one_moth_taxi_count_groupby.plot.bar(x='time', y='taxi_counts')

def getMaxHawker(time):
    hawker_geodataframe['lon'] = hawker_geodataframe['geometry'].apply(lambda p: p.x)
    hawker_geodataframe['lat'] = hawker_geodataframe['geometry'].apply(lambda p: p.y)
    dataframe = pd.DataFrame(data=hawker_geodataframe, columns=['lat','lon']) 
    dataframe['combined'] = dataframe.values.tolist()
    hawker_coordinates = dataframe['combined'].values.tolist()
    
    even_days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                '21', '22', '23', '24', '25', '26', '27', '28', '29', '30']
    for day in even_days:
        request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=2023-06-' + day +'T' + time + '%3A00%3A00'
        response = requests.get(request)
        data = response.json()
        taxi_driver_coordinates = data['features'][0]['geometry']['coordinates']
        taxi_driver_coordinates_inverted = invertLongtitudeLatitude(taxi_driver_coordinates)
        
        taxis_near_hawker = []
        
        for hawker in hawker_coordinates:
            count = 0
            for taxi_driver in taxi_driver_coordinates_inverted:
                distance = geopy.distance.geodesic(hawker, taxi_driver).km
                if distance <= 1.0:
                    count = count + 1
            taxis_near_hawker.append([hawker, count])
        
        df = pd.DataFrame(taxis_near_hawker)
        count_list = df.loc[:,1]
        hawker_list = df.loc[:,0]
        max_count = max(count_list)
        max_index = count_list[count_list == max_count].index[0]
        hawker_max = hawker_list[max_index]
        print(hawker_max)
        print(max_count)

