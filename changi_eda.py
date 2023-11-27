#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 12:40:09 2023

@author: dungdinh
"""
#Importing libraries
import matplotlib.pyplot as plt
import geopandas as gpd
import requests
import pandas as pd 
from fiona.drvsupport import supported_drivers
from geopy.geocoders import Nominatim
import os
import csv
import geopy.distance
import time as t
import gmplot 

#Import datasets
supported_drivers['KML'] = 'rw'
singapore_subzones = gpd.GeoDataFrame.from_file('./singapore_subzones.kml', driver='KML')

def getTaxiCoordinatesByTime(date, time):
    request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=' + date + 'T' + time
    response = requests.get(request)
    data = response.json()
    coordinates = data['features'][0]['geometry']['coordinates']
    lons = [x[0] for x in coordinates]
    lats = [x[1] for x in coordinates]
    df = pd.DataFrame({'lons': lons, 'lats': lats})
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lons, df.lats), crs="EPSG:4326")
    return gdf

#Function to invert longtitiude and latitude
def invertLongtitudeLatitude(coordinates):
    inverted_coordinates = []
    for x in coordinates:
        latitude = x[1]
        longtitude =  x[0]
        inverted_coordinate = (latitude, longtitude)
        inverted_coordinates.append(inverted_coordinate)
    return inverted_coordinates

def get_all_taxi_clusters(date, time):
    request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=' + date + 'T' + time
    response = requests.get(request)
    data = response.json()
    coordinates = data['features'][0]['geometry']['coordinates']
    lons = [x[0] for x in coordinates]
    lats = [x[1] for x in coordinates]
    df = pd.DataFrame({'lons': lons, 'lats': lats})
    
    changi_area = df[(df['lats'] >= 1.336) & (df['lats'] <= 1.3622) &  (df['lons'] >= 103.97897) & (df['lons'] <= 103.9918)]
    # plt.scatter(changi_area['lons'], changi_area['lats'], s=2, picker=True, color='red')
    changi_area_inverted = invertLongtitudeLatitude(changi_area.values.tolist()) 
    
    clusters = []
    changi_length = len(changi_area_inverted)
    
    for i in range(0, changi_length):
        for j in range(0, changi_length):
            distance = geopy.distance.geodesic(changi_area_inverted[i], changi_area_inverted[j]).m
            #distance by bird flight
            if distance <= 8.009:
                if changi_area_inverted[i] == changi_area_inverted[j]:
                    string_i = str(changi_area_inverted[i])
                    clusters.append([string_i[1:-1]])
                else:
                    string_i = str(changi_area_inverted[i])
                    string_j = str(changi_area_inverted[j])
                    clusters.append([string_i[1:-1], string_j[1:-1]]) 
                    
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

    merged_clusters_set = []
    for e in clusters:
        merged_clusters_set.append(set(e))

    return merged_clusters_set

#Plotting taxi_availability 
def plot_taxi_availability():
    fig, ax = plt.subplots()
    
    singapore_subzones.plot(ax=ax, color='black')
    
    taxi1_changes_df = getTaxiCoordinatesByTime('2018-12-25', '21%3A00%3A00')
    
    #SCATTER
    ax.scatter(taxi1_changes_df['lons'], taxi1_changes_df['lats'], s=2, picker=True)
    
    clusters = get_all_taxi_clusters('2018-12-25', '16%3A00%3A00')
    cluster_list = list(clusters)
    
    x = []
    y = []

    for cluster_set in cluster_list:
        cluster_set_list = list(cluster_set)
        lats = []
        lons = []
        for coordinate in cluster_set_list:
            string_split = coordinate.split(',')
            lons.append(float(string_split[1]))
            lats.append(float(string_split[0]))
        x.append(lats)
        y.append(lons)
    
    clustering_result = []
    count = 0
    for cluster in x:
        for element in list(cluster):
            clustering_result.append(count)
        count = count + 1
    x_merged = sum(x, [])
    y_merged = sum(y, [])
        
    df = pd.DataFrame({'lons': y_merged, 'lats': x_merged})
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lons, df.lats), crs="EPSG:4326")
    ax.scatter(gdf['lons'], gdf['lats'], s=3, picker=True, c = 'red')
    
    def onpick(event):
        ind = event.ind
        data = taxi1_changes_df.iloc[ind]
        x = data['lons']
        y = data['lats']
        comment = '{}, {}'
        print(comment.format(y.iloc[0], x.iloc[0]))
    
    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()
    
# plot_taxi_availability()


def plotting_clusters(clusters):
    cluster_list = list(clusters)
    
    x = []
    y = []

    for cluster_set in cluster_list:
        cluster_set_list = list(cluster_set)
        lats = []
        lons = []
        for coordinate in cluster_set_list:
            string_split = coordinate.split(',')
            lons.append(float(string_split[1]))
            lats.append(float(string_split[0]))
        x.append(lats)
        y.append(lons)
    
    clustering_result = []
    count = 0
    for cluster in x:
        for element in list(cluster):
            clustering_result.append(count)
        count = count + 1
    x_merged = sum(x, [])
    y_merged = sum(y, [])
        
    fig, ax = plt.subplots()
    df = pd.DataFrame({'lons': y_merged, 'lats': x_merged})
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lons, df.lats), crs="EPSG:4326")
    ax.scatter(gdf['lons'], gdf['lats'], s=3, picker=True, c = clustering_result, cmap='prism')
    # print(clustering_result)
    
    def onpick(event):
        ind = event.ind
        data = df.iloc[ind]
        x = data['lons']
        y = data['lats']
        comment = '{}, {}'
        print(comment.format(y.iloc[0], x.iloc[0]))
    
    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()

clusters = get_all_taxi_clusters('2018-12-23', '07%3A21%3A00')
# plotting_clusters(clusters)

def coordinates_on_map_base():
    gmap1 = gmplot.GoogleMapPlotter(1.3521, 103.8198, 15) 
    
    coordinates = getTaxiCoordinatesByTime('2018-12-23', '07%3A21%3A00')    
    
    # latitude_list = []
    # longitude_list = []
    # for coordinate in clusters:
    #     coordinate_list = list(coordinate)
    #     print(coordinate_list)
    #     latitude_list.append(coordinate_list[0])
    #     longitude_list.append(coordinate_list[1])
    # print(latitude_list)
    
    # print(coordinates['lats'])
    
    gmap1.scatter(coordinates['lats'], coordinates['lons'], '#FF0000',size = 2, marker = False)
  
    # Pass the absolute path 
    gmap1.draw( "./map11.html" ) 

coordinates_on_map_base()


def minute_creation():
    minutes = range(0, 60)
    res = []
    for minute in minutes:
        res.append(f"{minute:02}")
    return res

minutes = minute_creation()

def getChangiAddresses(date, hour, day_type):
    geoLoc = Nominatim(user_agent="GetLoc", timeout=15)
    
    
    data_rows = []

    
    for minute in minutes:  
        print('minute: ', minute)          
        time_input = hour + '%3A' + minute + '%3A00'
        
        time = time_input.replace('%3A', ':')
        
        clusters = get_all_taxi_clusters(date, time_input)
        
        cluster_list = list(clusters)
        
        for cluster in cluster_list:
            try:
                start = t.time()
                locname = geoLoc.reverse(list(cluster)[0])
                address = locname.address
                end = t.time()
                print(end-start)
                data_rows.append([date, time, len(cluster), address, day_type])
            except:
                print('geo catch errors')
                data_rows.append([date, time, len(cluster), "", day_type])
            
    return(data_rows)

def hour_creation():
    hours = range(0, 24)
    res = []
    for hour in hours:
        res.append(f"{hour:02}")
    return res

def writingTaxiAddressesToCSV():
    fields = ['date', 'time', 'cluster_size', 'address', 'day_type']
    
    save_path = 'changi'
    
    #EDIT 2 PLACES !!!!
    date = '2018-12-23'
    day_type = 'weekend'
    
    # hours = hour_creation()
    
    four_hours = ['20']
    
    #RUNNING 04
    # one_hours = ['10']
    
    for hour in four_hours:
        #creating rows
        data_rows = getChangiAddresses(date, hour, day_type)
        
        # name of csv file 
        filename = "changi_" + date + "_" + hour + ".csv"
        
        completeName = os.path.join(save_path, date, filename)
            
        # writing to csv file 
        with open(completeName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(fields) 
                
            # writing the data rows 
            csvwriter.writerows(data_rows)
        
# writingTaxiAddressesToCSV()
    
