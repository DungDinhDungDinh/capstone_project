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
import plotly.express as px

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
        print('"{}, {}"'.format(y.iloc[0], x.iloc[0]))
    
    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()

# clusters = get_all_taxi_clusters('2024-01-02', '09%3A24%3A00')
# plotting_clusters(clusters)

def coordinates_on_map_base():
    gmap1 = gmplot.GoogleMapPlotter(1.3521, 103.8198, 13, apikey='AIzaSyCWSsxr7oe7Xf11wFI_sUCMTxQRmJAzuuc') 
    
    coordinates = getTaxiCoordinatesByTime('2024-01-30', '00%3A31%3A00')    
    
    
    gmap1.scatter(coordinates['lats'], coordinates['lons'], '#ff0ebb',size = 1, marker = False)
  
    # Pass the absolute path 
    gmap1.draw( "./map18.html" ) 

# coordinates_on_map_base()

def time_creation_with_param(start, end):
    minutes = range(start, end)
    res = []
    for minute in minutes:
        res.append(f"{minute:02}")
    return res

def draw_seemless_lanes():    
    one_hour = time_creation_with_param(00, 60)
    hours = time_creation_with_param(12, 15)
    date = '2023-08-08'
    coordinates = pd.DataFrame()
    for hour in hours: 
        for minute in one_hour:
            time = hour + '%3A' + minute + '%3A00'
            new_coordinates = getTaxiCoordinatesByTime(date, time)  
            coordinates = pd.concat([coordinates, new_coordinates])
    
    fig = px.scatter_mapbox(coordinates, lat="lats", lon="lons",
                        color_discrete_sequence=["fuchsia"], zoom=1, opacity=0.1)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_html('eda.html', auto_open=True)

# draw_seemless_lanes()

def mapbox_show():
    coordinates = getTaxiCoordinatesByTime('2023-11-07', '00%3A58%3A00') 
    fig = px.scatter_mapbox(coordinates, lat="lats", lon="lons",
                        color_discrete_sequence=["fuchsia"], zoom=3)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.write_html('eda1.html', auto_open=True)
    
# mapbox_show()

def get_address():
    geoLoc = Nominatim(user_agent="GetLoc", timeout=15)
    locname = geoLoc.reverse("1.35943, 103.9888")
    address = locname.address
    print(address)
    
# get_address()
    


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

def termianl_one_congestion_analysis(count, date, time, day_type):
    request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=' + date + 'T' + time
    response = requests.get(request)
    data = response.json()
    coordinates = data['features'][0]['geometry']['coordinates']
    lons = [x[0] for x in coordinates]
    lats = [x[1] for x in coordinates]
    df = pd.DataFrame({'lons': lons, 'lats': lats})
    
    terminal_one = df[(df['lats'] <= 1.36185) & 
                      (df['lons'] >= 103.9877) & (df['lons'] <= 103.98896)]
    
    # print(terminal_one)
        
    terminal_one_inverted = invertLongtitudeLatitude(terminal_one.values.tolist())
    # fig, ax = plt.subplots()
    # ax.scatter(terminal_one['lons'], terminal_one['lats'], s=2, picker=True)
    # plt.show()
    
    clusters = []
    terminal_one_length = len(terminal_one_inverted)
    
    for i in range(0, terminal_one_length):
        for j in range(0, terminal_one_length):
            distance = geopy.distance.geodesic(terminal_one_inverted[i], terminal_one_inverted[j]).m
            # distance by bird flight
            if distance <= 16:
                if terminal_one_inverted[i] == terminal_one_inverted[j]:
                    string_i = str(terminal_one_inverted[i])
                    clusters.append([string_i[1:-1]])
                else:
                    string_i = str(terminal_one_inverted[i])
                    string_j = str(terminal_one_inverted[j])
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
    
    clusters = list(merged_clusters_set)
    
    cluster_list = []
    for set_items in clusters:
        set_items_list = list(set_items)
        if len(set_items_list) > 6:
            cluster_list.append(set_items_list)
    
    # print(cluster_list)
    
    # #COUNT NUMBER OF TAXI DRIVERS
    taxi_count = 0
    for cluster in cluster_list:
        taxi_count += len(cluster)
    
    # #MEASURE THE LENGTH OF THE QUEUE
    unlist = []
    for cluster in cluster_list:
        unlist += cluster
            
    lat_list = [ x.split(',')[0] for x in unlist]
    
    if not lat_list:
        return [count, time.replace('%3A', '.'), taxi_count, 0, 0, 0, day_type]
    
    else:
        min_coordinate = min(lat_list) 
        max_coordinate = max(lat_list) 
        
        #LENGTH OF THE QUEUE
        min_index = lat_list.index(min_coordinate)
        max_index = lat_list.index(max_coordinate)
        
        min_coordinate = unlist[min_index]
        max_coordinate = unlist[max_index]
        
        
        queue_length = min_coordinate and max_coordinate and geopy.distance.geodesic(min_coordinate, max_coordinate).m
        
        queue_length = ((not queue_length) and 0) or queue_length
         
        return [count, time.replace('%3A', '.'), taxi_count, queue_length, min_coordinate, max_coordinate, day_type]
 
    
    #VISUALIZE TO CHECK THE RESULTS
    # x = []
    # y = []
    # for cluster_set in cluster_list:
    #     cluster_set_list = list(cluster_set)
    #     lats = []
    #     lons = []
    #     for coordinate in cluster_set_list:
    #         string_split = coordinate.split(',')
    #         lons.append(float(string_split[1]))
    #         lats.append(float(string_split[0]))
    #     x.append(lats)
    #     y.append(lons)
    
    # clustering_result = []
    # count = 0
    # for cluster in x:
    #     for element in list(cluster):
    #         clustering_result.append(count)
    #     count = count + 1
    # x_merged = sum(x, [])
    # y_merged = sum(y, [])
        
    # fig, ax = plt.subplots()
    # df = pd.DataFrame({'lons': y_merged, 'lats': x_merged})
    # gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lons, df.lats), crs="EPSG:4326")
    # ax.scatter(gdf['lons'], gdf['lats'], s=3, picker=True, c = clustering_result, cmap='prism')
    
    # def onpick(event):
    #     ind = event.ind
    #     data = df.iloc[ind]
    #     x = data['lons']
    #     y = data['lats']
    #     print('"{}, {}"'.format(y.iloc[0], x.iloc[0]))
    
    # fig.canvas.mpl_connect('pick_event', onpick)
    # plt.show()
    
    # changi_area_inverted = invertLongtitudeLatitude(terminal_one.values.tolist()) 
# termianl_one_congestion_analysis(1,'2024-01-02', '03%3A24%3A00', 'weekday')

#WRITE TERMINAL ONE TAXI QUEING INTO FILES
def write_taxi_queue_of_t1():
    fields = ['id', 'time', 'taxi_count', 'queue_length', 'min_coordinate', 'max_coordinate', 'day_type']
    
    save_path = 't1_congestion'
    
    weekdays = ['2024-01-30']
    
    
    day_type = 'weekday'
    
    
    one_hour = time_creation_with_param(0,60)
    
    hours = time_creation_with_param(0,24)
    
    for date in weekdays:
        print(date)
        data_rows = []
        count = 0
        for hour in hours:
            print(hour)
            for minute in one_hour:
                time = hour + '%3A' + minute + '%3A00'
                
                count += 1
                
                data_rows.append(termianl_one_congestion_analysis(count, date, time, day_type))
        
        # name of csv file 
        filename = "t1_" + date + ".csv"
        
        completeName = os.path.join(save_path, filename)
            
        # writing to csv file 
        with open(completeName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(fields) 
                
            # writing the data rows 
            csvwriter.writerows(data_rows)
            
        print('DONE')

# start = t.time()
# write_taxi_queue_of_t1()
# end = t.time()
# print(end-start)

def termianl_two_congestion_analysis(count, date, time, day_type):
    request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=' + date + 'T' + time
    response = requests.get(request)
    data = response.json()
    coordinates = data['features'][0]['geometry']['coordinates']
    lons = [x[0] for x in coordinates]
    lats = [x[1] for x in coordinates]
    df = pd.DataFrame({'lons': lons, 'lats': lats})
    
    terminal_one = df[(df['lats'] <= 1.3588) & 
                      (df['lons'] >= 103.9892) & (df['lons'] <= 103.9903)]
    
    # print(terminal_one)
        
    terminal_one_inverted = invertLongtitudeLatitude(terminal_one.values.tolist())
    # fig, ax = plt.subplots()
    # ax.scatter(terminal_one['lons'], terminal_one['lats'], s=2, picker=True)
    # plt.show()
    
    clusters = []
    terminal_one_length = len(terminal_one_inverted)
    
    for i in range(0, terminal_one_length):
        for j in range(0, terminal_one_length):
            distance = geopy.distance.geodesic(terminal_one_inverted[i], terminal_one_inverted[j]).m
            # distance by bird flight
            if distance <= 16:
                if terminal_one_inverted[i] == terminal_one_inverted[j]:
                    string_i = str(terminal_one_inverted[i])
                    clusters.append([string_i[1:-1]])
                else:
                    string_i = str(terminal_one_inverted[i])
                    string_j = str(terminal_one_inverted[j])
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
    
    clusters = list(merged_clusters_set)
    
    cluster_list = []
    for set_items in clusters:
        set_items_list = list(set_items)
        if len(set_items_list) > 6:
            cluster_list.append(set_items_list)
    
    # print(cluster_list)
    
    # #COUNT NUMBER OF TAXI DRIVERS
    taxi_count = 0
    for cluster in cluster_list:
        taxi_count += len(cluster)
    
    # #MEASURE THE LENGTH OF THE QUEUE
    unlist = []
    for cluster in cluster_list:
        unlist += cluster
            
    lat_list = [ x.split(',')[0] for x in unlist]
    
    if not lat_list:
        return [count, time.replace('%3A', '.'), taxi_count, 0, 0, 0, day_type]
    
    else:
        min_coordinate = min(lat_list) 
        max_coordinate = max(lat_list) 
        
        #LENGTH OF THE QUEUE
        min_index = lat_list.index(min_coordinate)
        max_index = lat_list.index(max_coordinate)
        
        min_coordinate = unlist[min_index]
        max_coordinate = unlist[max_index]
        
        
        queue_length = min_coordinate and max_coordinate and geopy.distance.geodesic(min_coordinate, max_coordinate).m
        
        queue_length = ((not queue_length) and 0) or queue_length
         
        return [count, time.replace('%3A', '.'), taxi_count, queue_length, min_coordinate, max_coordinate, day_type]
 
    
    #VISUALIZE TO CHECK THE RESULTS
    # x = []
    # y = []
    # for cluster_set in cluster_list:
    #     cluster_set_list = list(cluster_set)
    #     lats = []
    #     lons = []
    #     for coordinate in cluster_set_list:
    #         string_split = coordinate.split(',')
    #         lons.append(float(string_split[1]))
    #         lats.append(float(string_split[0]))
    #     x.append(lats)
    #     y.append(lons)
    
    # clustering_result = []
    # count = 0
    # for cluster in x:
    #     for element in list(cluster):
    #         clustering_result.append(count)
    #     count = count + 1
    # x_merged = sum(x, [])
    # y_merged = sum(y, [])
        
    # fig, ax = plt.subplots()
    # df = pd.DataFrame({'lons': y_merged, 'lats': x_merged})
    # gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lons, df.lats), crs="EPSG:4326")
    # ax.scatter(gdf['lons'], gdf['lats'], s=3, picker=True, c = clustering_result, cmap='prism')
    
    # def onpick(event):
    #     ind = event.ind
    #     data = df.iloc[ind]
    #     x = data['lons']
    #     y = data['lats']
    #     print('"{}, {}"'.format(y.iloc[0], x.iloc[0]))
    
    # fig.canvas.mpl_connect('pick_event', onpick)
    # plt.show()
    
    # changi_area_inverted = invertLongtitudeLatitude(terminal_one.values.tolist()) 
# termianl_two_congestion_analysis(1,'2023-12-16', '20%3A43%3A00', 'weekday')

#WRITE TERMINAL TWO TAXI QUEING INTO FILES
def write_taxi_queue_of_t2():
    fields = ['id', 'time', 'taxi_count', 'queue_length', 'min_coordinate', 'max_coordinate', 'day_type']
    
    save_path = 't2_congestion'
    
    # weekends = ['2019-07-13', '2019-07-28', '2019-08-24', '2019-08-25',
    # '2019-09-21', '2019-09-01', '2019-10-12', '2019-10-20', '2019-11-09',
    # '2019-11-10', '2019-12-07', '2019-12-15']
    
    # weekdays = ['2023-09-08', '2023-10-27', '2023-11-10','2023-12-15']
    # weekdays = ['2023-07-07', '2023-08-11', '2023-09-08', '2023-10-27', '2023-11-10',
    # '2023-12-15']
    weekdays = ['2024-01-30']
    
    
    day_type = 'weekday'
    
    
    one_hour = time_creation_with_param(0,60)
    
    hours = time_creation_with_param(0,24)
    
    for date in weekdays:
        print(date)
        data_rows = []
        count = 0
        for hour in hours:
            print(hour)
            for minute in one_hour:
                time = hour + '%3A' + minute + '%3A00'
                
                count += 1
                
                data_rows.append(termianl_two_congestion_analysis(count, date, time, day_type))
        
        # name of csv file 
        filename = "t2_" + date + ".csv"
        
        completeName = os.path.join(save_path, filename)
            
        # writing to csv file 
        with open(completeName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(fields) 
                
            # writing the data rows 
            csvwriter.writerows(data_rows)
            
        print('DONE')

# start = t.time()
# write_taxi_queue_of_t2()
# end = t.time()
# print(end-start)

def termianl_three_congestion_analysis(count, date, time, day_type):
    request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=' + date + 'T' + time
    response = requests.get(request)
    data = response.json()
    coordinates = data['features'][0]['geometry']['coordinates']
    lons = [x[0] for x in coordinates]
    lats = [x[1] for x in coordinates]
    df = pd.DataFrame({'lons': lons, 'lats': lats})
    
    terminal_one = df[(df['lats'] >= 1.35231) & (df['lats'] <= 1.35415) &
                      (df['lons'] >= 103.9856) & (df['lons'] <= 103.9864)]
    
    # print(terminal_one)
        
    terminal_one_inverted = invertLongtitudeLatitude(terminal_one.values.tolist())
    # fig, ax = plt.subplots()
    # ax.scatter(terminal_one['lons'], terminal_one['lats'], s=2, picker=True)
    # plt.show()
    
    clusters = []
    terminal_one_length = len(terminal_one_inverted)
    
    for i in range(0, terminal_one_length):
        for j in range(0, terminal_one_length):
            distance = geopy.distance.geodesic(terminal_one_inverted[i], terminal_one_inverted[j]).m
            # distance by bird flight
            if distance <= 16:
                if terminal_one_inverted[i] == terminal_one_inverted[j]:
                    string_i = str(terminal_one_inverted[i])
                    clusters.append([string_i[1:-1]])
                else:
                    string_i = str(terminal_one_inverted[i])
                    string_j = str(terminal_one_inverted[j])
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
    
    clusters = list(merged_clusters_set)
    
    cluster_list = []
    for set_items in clusters:
        set_items_list = list(set_items)
        if len(set_items_list) > 6:
            cluster_list.append(set_items_list)
    
    # print(cluster_list)
    
    # #COUNT NUMBER OF TAXI DRIVERS
    taxi_count = 0
    for cluster in cluster_list:
        taxi_count += len(cluster)
    
    # #MEASURE THE LENGTH OF THE QUEUE
    unlist = []
    for cluster in cluster_list:
        unlist += cluster
            
    lat_list = [ x.split(',')[0] for x in unlist]
    
    if not lat_list:
        return [count, time.replace('%3A', '.'), taxi_count, 0, 0, 0, day_type]
    
    else:
        min_coordinate = min(lat_list) 
        max_coordinate = max(lat_list) 
        
        #LENGTH OF THE QUEUE
        min_index = lat_list.index(min_coordinate)
        max_index = lat_list.index(max_coordinate)
        
        min_coordinate = unlist[min_index]
        max_coordinate = unlist[max_index]
        
        
        queue_length = min_coordinate and max_coordinate and geopy.distance.geodesic(min_coordinate, max_coordinate).m
        
        queue_length = ((not queue_length) and 0) or queue_length
         
        return [count, time.replace('%3A', '.'), taxi_count, queue_length, min_coordinate, max_coordinate, day_type]
 
    
    #VISUALIZE TO CHECK THE RESULTS
    # x = []
    # y = []
    # for cluster_set in cluster_list:
    #     cluster_set_list = list(cluster_set)
    #     lats = []
    #     lons = []
    #     for coordinate in cluster_set_list:
    #         string_split = coordinate.split(',')
    #         lons.append(float(string_split[1]))
    #         lats.append(float(string_split[0]))
    #     x.append(lats)
    #     y.append(lons)
    
    # clustering_result = []
    # count = 0
    # for cluster in x:
    #     for element in list(cluster):
    #         clustering_result.append(count)
    #     count = count + 1
    # x_merged = sum(x, [])
    # y_merged = sum(y, [])
        
    # fig, ax = plt.subplots()
    # df = pd.DataFrame({'lons': y_merged, 'lats': x_merged})
    # gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lons, df.lats), crs="EPSG:4326")
    # ax.scatter(gdf['lons'], gdf['lats'], s=3, picker=True, c = clustering_result, cmap='prism')
    
    # def onpick(event):
    #     ind = event.ind
    #     data = df.iloc[ind]
    #     x = data['lons']
    #     y = data['lats']
    #     print('"{}, {}"'.format(y.iloc[0], x.iloc[0]))
    
    # fig.canvas.mpl_connect('pick_event', onpick)
    # plt.show()
    
    # changi_area_inverted = invertLongtitudeLatitude(terminal_one.values.tolist()) 
# termianl_three_congestion_analysis(1,'2024-02-01', '08%3A30%3A00', 'weekday')

#WRITE TERMINAL TWO TAXI QUEING INTO FILES
def write_taxi_queue_of_t3():
    fields = ['id', 'time', 'taxi_count', 'queue_length', 'min_coordinate', 'max_coordinate', 'day_type']
    
    save_path = 't3_congestion'
        
    
    # weekdays = ['2022-10-21', '2022-11-04', '2022-12-23', '2019-01-03', '2019-02-14',
    # '2019-03-21', '2019-04-18', '2019-05-23', '2019-06-20', '2019-07-11',
    # '2019-08-22', '2019-09-12', '2019-10-31', '2019-11-28', '2019-12-05']
    
    
    # weekends = ['2023-07-09', '2023-08-06', '2023-09-24', '2023-10-08', '2023-11-12', '2023-12-31',
    # '2022-01-21', '2022-01-30', '2022-02-12', '2022-02-27', '2022-03-26']
    
    
    # weekends = ['2022-11-26', '2022-11-27', '2022-12-31', '2022-12-11', '2019-01-26',
    # '2019-01-06', '2019-02-23', '2019-02-24', '2019-03-09', '2019-03-17',
    # '2019-04-06', '2019-04-07', '2019-05-11', '2019-05-26', '2019-06-01']
    
    # weekends = ['2019-07-13', '2019-07-28', '2019-08-24', '2019-08-25',
    # '2019-09-21', '2019-09-01', '2019-10-12', '2019-10-20', '2019-11-09',
    # '2019-11-10', '2019-12-07', '2019-12-15']
    
    # holidays = ['2024-01-01', '2023-12-31', '2023-12-30', '2023-12-25', '2023-12-24', '2023-12-16',				
    #             '2023-11-11', '2023-10-21', '2023-08-09', '2023-08-08', '2023-06-29', '2023-06-28',				
    #             '2023-06-02', '2023-06-01', '2023-12-28', '2019-10-27', '2019-10-26', '2019-10-28']
    
    # holidays = ['2019-12-24', '2019-12-25', '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24',				
    # '2023-04-21', '2023-04-22', '2023-04-30', '2023-05-01', '2023-05-02']
    
    weekdays = ['2023-11-07']
    
    
    day_type = 'weekday'
    
    
    one_hour = time_creation_with_param(0,60)
    
    hours = time_creation_with_param(0,24)
    
    for date in weekdays:
        print(date)
        data_rows = []
        count = 0
        for hour in hours:
            print(hour)
            for minute in one_hour:
                time = hour + '%3A' + minute + '%3A00'
                
                count += 1
                
                data_rows.append(termianl_three_congestion_analysis(count, date, time, day_type))
        
        # name of csv file 
        filename = "t3_" + date + ".csv"
        
        completeName = os.path.join(save_path, filename)
            
        # writing to csv file 
        with open(completeName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(fields) 
                
            # writing the data rows 
            csvwriter.writerows(data_rows)
            
        print('DONE')

# start = t.time()
# write_taxi_queue_of_t3()
# end = t.time()
# print(end-start)
    
def termianl_four_congestion_analysis(count, date, time, day_type):
    request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=' + date + 'T' + time
    response = requests.get(request)
    data = response.json()
    coordinates = data['features'][0]['geometry']['coordinates']
    lons = [x[0] for x in coordinates]
    lats = [x[1] for x in coordinates]
    df = pd.DataFrame({'lons': lons, 'lats': lats})
    
    terminal_one = df[(df['lats'] <= 1.3409) &
                      (df['lons'] >= 103.9826) & (df['lons'] <= 103.9833)]
    
    # print(terminal_one)
        
    terminal_one_inverted = invertLongtitudeLatitude(terminal_one.values.tolist())
    # fig, ax = plt.subplots()
    # ax.scatter(terminal_one['lons'], terminal_one['lats'], s=2, picker=True)
    # plt.show()
    
    clusters = []
    terminal_one_length = len(terminal_one_inverted)
    
    for i in range(0, terminal_one_length):
        for j in range(0, terminal_one_length):
            distance = geopy.distance.geodesic(terminal_one_inverted[i], terminal_one_inverted[j]).m
            # distance by bird flight
            if distance <= 16:
                if terminal_one_inverted[i] == terminal_one_inverted[j]:
                    string_i = str(terminal_one_inverted[i])
                    clusters.append([string_i[1:-1]])
                else:
                    string_i = str(terminal_one_inverted[i])
                    string_j = str(terminal_one_inverted[j])
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
    
    clusters = list(merged_clusters_set)
    
    cluster_list = []
    for set_items in clusters:
        set_items_list = list(set_items)
        if len(set_items_list) > 6:
            cluster_list.append(set_items_list)
    
    # print(cluster_list)
    
    # #COUNT NUMBER OF TAXI DRIVERS
    taxi_count = 0
    for cluster in cluster_list:
        taxi_count += len(cluster)
    
    # #MEASURE THE LENGTH OF THE QUEUE
    unlist = []
    for cluster in cluster_list:
        unlist += cluster
            
    lat_list = [ x.split(',')[0] for x in unlist]
    
    if not lat_list:
        return [count, time.replace('%3A', '.'), taxi_count, 0, 0, 0, day_type]
    
    else:
        min_coordinate = min(lat_list) 
        max_coordinate = max(lat_list) 
        
        #LENGTH OF THE QUEUE
        min_index = lat_list.index(min_coordinate)
        max_index = lat_list.index(max_coordinate)
        
        min_coordinate = unlist[min_index]
        max_coordinate = unlist[max_index]
        
        
        queue_length = min_coordinate and max_coordinate and geopy.distance.geodesic(min_coordinate, max_coordinate).m
        
        queue_length = ((not queue_length) and 0) or queue_length
         
        return [count, time.replace('%3A', '.'), taxi_count, queue_length, min_coordinate, max_coordinate, day_type]
 
    
    #VISUALIZE TO CHECK THE RESULTS
    # x = []
    # y = []
    # for cluster_set in cluster_list:
    #     cluster_set_list = list(cluster_set)
    #     lats = []
    #     lons = []
    #     for coordinate in cluster_set_list:
    #         string_split = coordinate.split(',')
    #         lons.append(float(string_split[1]))
    #         lats.append(float(string_split[0]))
    #     x.append(lats)
    #     y.append(lons)
    
    # clustering_result = []
    # count = 0
    # for cluster in x:
    #     for element in list(cluster):
    #         clustering_result.append(count)
    #     count = count + 1
    # x_merged = sum(x, [])
    # y_merged = sum(y, [])
        
    # fig, ax = plt.subplots()
    # df = pd.DataFrame({'lons': y_merged, 'lats': x_merged})
    # gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lons, df.lats), crs="EPSG:4326")
    # ax.scatter(gdf['lons'], gdf['lats'], s=3, picker=True, c = clustering_result, cmap='prism')
    
    # def onpick(event):
    #     ind = event.ind
    #     data = df.iloc[ind]
    #     x = data['lons']
    #     y = data['lats']
    #     print('"{}, {}"'.format(y.iloc[0], x.iloc[0]))
    
    # fig.canvas.mpl_connect('pick_event', onpick)
    # plt.show()
    
    # changi_area_inverted = invertLongtitudeLatitude(terminal_one.values.tolist()) 
# termianl_four_congestion_analysis(1,'2019-11-27', '00%3A14%3A00', 'weekday')

#WRITE TERMINAL TWO TAXI QUEING INTO FILES
def write_taxi_queue_of_t4():
    fields = ['id', 'time', 'taxi_count', 'queue_length', 'min_coordinate', 'max_coordinate', 'day_type']
    
    save_path = 't4_congestion'
    
    
    # weekdays = ['2022-10-21', '2022-11-04', '2022-12-23', '2019-01-03', '2019-02-14',
    # '2019-03-21', '2019-04-18', '2019-05-23', '2019-06-20', '2019-07-11',
    # '2019-08-22', '2019-09-12', '2019-10-31', '2019-11-28', '2019-12-05']

    
    # weekends = ['2019-07-13', '2019-07-28', '2019-08-24', '2019-08-25',
    # '2019-09-21', '2019-09-01', '2019-10-12', '2019-10-20', '2019-11-09',
    # '2019-11-10', '2019-12-07', '2019-12-15']
    
    # weekends = ['2019-09-21', '2019-09-01', '2019-10-12', '2019-10-20', '2019-11-09']
    
    # weekends = ['2019-11-10', '2019-12-07', '2019-12-15']
    
    # holidays = ['2019-12-24', '2019-12-25', '2023-01-21', '2023-01-22', '2023-01-23', '2023-01-24',				
    # '2023-04-21', '2023-04-22', '2023-04-30', '2023-05-01', '2023-05-02']
    
    weekdays = ['2024-01-30']
    
    
    day_type = 'weekday'
    
    
    one_hour = time_creation_with_param(0,60)
    
    hours = time_creation_with_param(0,24)
    
    for date in weekdays:
        print(date)
        data_rows = []
        count = 0
        for hour in hours:
            print(hour)
            for minute in one_hour:
                time = hour + '%3A' + minute + '%3A00'
                
                count += 1
                
                data_rows.append(termianl_four_congestion_analysis(count, date, time, day_type))
        
        # name of csv file 
        filename = "t4_" + date + ".csv"
        
        completeName = os.path.join(save_path, filename)
            
        # writing to csv file 
        with open(completeName, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(fields) 
                
            # writing the data rows 
            csvwriter.writerows(data_rows)
            
        print('DONE')

# start = t.time()
write_taxi_queue_of_t4()
# end = t.time()
# print(end-start)    

    
