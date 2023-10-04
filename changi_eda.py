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

#Plotting taxi_availability 
def plot_taxi_availability():
    fig, ax = plt.subplots()
    
    singapore_subzones.plot(ax=ax, color='black')
    
    taxi1_changes_df = getTaxiCoordinatesByTime('2018-12-25', '21%3A00%3A00')
    
    #SCATTER
    ax.scatter(taxi1_changes_df['lons'], taxi1_changes_df['lats'], s=2, picker=True)
    
    def onpick(event):
        ind = event.ind
        data = taxi1_changes_df.iloc[ind]
        x = data['lons']
        y = data['lats']
        print(y.iloc[0],x.iloc[0])
    
    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()
    
# plot_taxi_availability()

#Function to invert longtitiude and latitude
def invertLongtitudeLatitude(coordinates):
    inverted_coordinates = []
    for x in coordinates:
        latitude = x[1]
        longtitude =  x[0]
        inverted_coordinate = (latitude, longtitude)
        inverted_coordinates.append(inverted_coordinate)
    return inverted_coordinates

def get_all_taxi_addresses(date, time):
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
    # print(changi_area_inverted)
    
    #Getting locations of taxi drivers
    addresses = []
    for taxi in changi_area_inverted:
        print(taxi)
        try:
            geoLoc = Nominatim(user_agent="GetLoc")
            locname = geoLoc.reverse(taxi)
            address = locname.address
            print(address)
            addresses.append([taxi,address])
        except:
            addresses.append([taxi,'none'])
    print(address)
    return addresses    

def writingTaxiAddressesToCSV():
    fields = ['coordinate', 'address']
    
    save_path = 'changi'
    
    #creating rows
    data_rows = get_all_taxi_addresses('2018-12-25', '21%3A00%3A00')
    
    # name of csv file 
    filename = 'address.csv'
    
    completeName = os.path.join(save_path, filename)
        
    # writing to csv file 
    with open(completeName, 'w') as csvfile: 
        # creating a csv writer object 
        csvwriter = csv.writer(csvfile) 
            
        # writing the fields 
        csvwriter.writerow(fields) 
            
        # writing the data rows 
        csvwriter.writerows(data_rows)
        
writingTaxiAddressesToCSV()
    
