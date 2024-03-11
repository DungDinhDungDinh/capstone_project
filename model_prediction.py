#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 13:58:40 2024

@author: dungdinh
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import datetime
import geopy.distance
import requests
import numpy as np

should_go_predictors = ['day_of_week', 'month', 'hour', 'taxi_count_minute0', 'taxi_length_minute0', 
                                                     'taxi_count_minute-1', 'taxi_length_minute-1', 'taxi_count_minute-2', 'taxi_length_minute-2', 
                                                     'taxi_count_minute-3', 'taxi_length_minute-3', 'taxi_count_minute-4', 'taxi_length_minute-4', 
                                                     'taxi_count_minute-5', 'taxi_length_minute-5']
heavy_congestion_predictors = ['day_of_week', 'month', 'hour', 'taxi_count_minute-1', 'taxi_length_minute-1', 
              'taxi_count_minute-2', 'taxi_length_minute-2', 'taxi_count_minute-3', 'taxi_length_minute-3',
              'taxi_count_minute-4', 'taxi_length_minute-4', 'taxi_count_minute-5', 'taxi_length_minute-5',
              'taxi_count_minute0', 'taxi_length_minute0', 'taxi_count_minute1', 'taxi_length_minute1',
              'taxi_count_minute2', 'taxi_length_minute2', 'taxi_count_minute3', 'taxi_length_minute3',
              'taxi_count_minute4', 'taxi_length_minute4', 'taxi_count_minute5', 'taxi_length_minute5']

should_go_type = 1
heavy_congestion_type = 0


def import_and_preprocess_should_go(terminal):
    data = pd.read_csv('./training_datasets/' + terminal + '_queue_all_days_avg_combined_5m.csv')
    
    
    data['month'] = [i[5:7] for i in data['date']]
    
    # Split the data into features (X) and target (y)
    data.loc[(data['sum'] >= 5) & (data['sum'] <= 20), 'should_go'] = '1'
    data.loc[(data['sum'] < 5) | (data['sum'] > 20), 'should_go'] = '0'
    
    X = data.drop('should_go', axis=1)
    y = data['should_go']
    

    #Data preprocessing
    X = X[should_go_predictors]
        
    X = pd.get_dummies(X, columns = ['day_of_week', 'hour', 'month'])

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

    return X_train, X_test, y_train, y_test

def import_and_preprocess_heavy_congestion(terminal):
    data = pd.read_csv('./training_datasets/' + terminal + '_queue_all_days_avg_combined_5m.csv')
    data['month'] = [i[5:7] for i in data['date']]
    
    # Split the data into features (X) and target (y)
    data.loc[data['sum'] >= 12, 'heavy_congestion'] = '1'
    data.loc[data['sum'] < 12, 'heavy_congestion'] = '0'
    
    X = data.drop('heavy_congestion', axis=1)
    y = data['heavy_congestion']

    #Data preprocessing
    X = X.loc[:, heavy_congestion_predictors]
    
    X = pd.get_dummies(X, columns = ['day_of_week', 'month', 'hour'])

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.20,random_state=42)

    return X_train, X_test, y_train, y_test

def decision_tree_training(X_train, y_train): 
    clf = DecisionTreeClassifier(max_depth=4, random_state=42)
    
    # Train Decision Tree Classifer
    clf = clf.fit(X_train, y_train)
    return clf

#Function to invert longtitiude and latitude
def invertLongtitudeLatitude(coordinates):
    inverted_coordinates = []
    for x in coordinates:
        latitude = x[1]
        longtitude =  x[0]
        inverted_coordinate = (latitude, longtitude)
        inverted_coordinates.append(inverted_coordinate)
    return inverted_coordinates

def terminal_one_congestion_by_minute(df, terminal):
    if terminal == 't1':
        terminal_one = df[(df['lats'] <= 1.36185) & 
                          (df['lons'] >= 103.9877) & (df['lons'] <= 103.98896)]
    elif terminal == 't2':
        terminal_one = df[(df['lats'] <= 1.3588) & 
                          (df['lons'] >= 103.9892) & (df['lons'] <= 103.9903)]
    elif terminal == 't3':
        terminal_one = df[(df['lats'] >= 1.35231) & (df['lats'] <= 1.35415) &
                          (df['lons'] >= 103.9856) & (df['lons'] <= 103.9864)]
    else:
        terminal_one = df[(df['lats'] <= 1.3409) &
                          (df['lons'] >= 103.9826) & (df['lons'] <= 103.9833)]
            
    terminal_one_inverted = invertLongtitudeLatitude(terminal_one.values.tolist())
    
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
                if var in clusters[j]:
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
        return [taxi_count, 0]
    
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
         
        return [taxi_count, queue_length]
    

def all_terminals_prediction(current_time, should_go):
    date = current_time.date()
    hour = current_time.hour
    month = str(date)[5:7]
    d = pd.Timestamp(date)
    day_of_week = d.day_name()
    current_minute = current_time.minute
    
    df_for_prediction_t1 = pd.DataFrame()
    df_for_prediction_t2 = pd.DataFrame()
    df_for_prediction_t3 = pd.DataFrame()
    df_for_prediction_t4 = pd.DataFrame()
    
    if should_go == True:
        minutes_to_get = 6
        predictor_columns = should_go_predictors
    else:
        minutes_to_get = 11
        predictor_columns = heavy_congestion_predictors
        
    for terminal in ['t1', 't2', 't3', 't4']:
        try:
            count = 0
            count_name = 0
            taxi_count_length_data = []
            while count < minutes_to_get:
                minute = "{0:0=2d}".format(current_minute - count)
                time = str(hour) + '%3A' + str(minute) + '%3A00'
                request = 'https://api.data.gov.sg/v1/transport/taxi-availability?date_time=' + str(date) + 'T' + time
                response = requests.get(request)
                data = response.json()
                coordinates = data['features'][0]['geometry']['coordinates']
                lons = [x[0] for x in coordinates]
                lats = [x[1] for x in coordinates]
                df = pd.DataFrame({'lons': lons, 'lats': lats})
            
                
                taxi_count_length_data += terminal_one_congestion_by_minute(df, terminal)
                count += 1
                count_name -= 1
            data = [[day_of_week, month, hour] + taxi_count_length_data]
            
            if terminal == 't1':
                df_for_prediction_t1 = pd.DataFrame(data, columns = predictor_columns)
            elif terminal == 't2':
                df_for_prediction_t2 = pd.DataFrame(data, columns = predictor_columns)
            elif terminal == 't3':
                df_for_prediction_t3 = pd.DataFrame(data, columns = predictor_columns)
            else:
                df_for_prediction_t4 = pd.DataFrame(data, columns = predictor_columns)
        except:
            print("Calling api failed")
    
    if should_go == True:
        X_train_sg_t1, X_test_sg_t1, y_train_sg_t1, y_test_sg_t1 = import_and_preprocess_should_go('t1')
        X_train_sg_t2, X_test_sg_t2, y_train_sg_t2, y_test_sg_t2 = import_and_preprocess_should_go('t2')
        X_train_sg_t3, X_test_sg_t3, y_train_sg_t3, y_test_sg_t3 = import_and_preprocess_should_go('t3')
        X_train_sg_t4, X_test_sg_t4, y_train_sg_t4, y_test_sg_t4 = import_and_preprocess_should_go('t4')
    else:
        X_train_sg_t1, X_test_sg_t1, y_train_sg_t1, y_test_sg_t1 = import_and_preprocess_heavy_congestion('t1')
        X_train_sg_t2, X_test_sg_t2, y_train_sg_t2, y_test_sg_t2 = import_and_preprocess_heavy_congestion('t2')
        X_train_sg_t3, X_test_sg_t3, y_train_sg_t3, y_test_sg_t3 = import_and_preprocess_heavy_congestion('t3')
        X_train_sg_t4, X_test_sg_t4, y_train_sg_t4, y_test_sg_t4 = import_and_preprocess_heavy_congestion('t4')
        
    
    clf_t1 = decision_tree_training(X_train_sg_t1, y_train_sg_t1)
    clf_t2 = decision_tree_training(X_train_sg_t2, y_train_sg_t2)
    clf_t3 = decision_tree_training(X_train_sg_t3, y_train_sg_t3)
    clf_t4 = decision_tree_training(X_train_sg_t4, y_train_sg_t4)
    
    def should_go_checking(df_for_prediction, X_train, clf):
        if len(df_for_prediction) > 0:
            df_for_prediction = pd.get_dummies(df_for_prediction, columns = ['day_of_week', 'month', 'hour'])
            for col in X_train.columns:
                if col not in df_for_prediction.columns:
                    df_for_prediction[col] = np.nan
            df_for_prediction = df_for_prediction[X_train.columns]
            
            return list(clf.predict(df_for_prediction))[0]
    
    t1_shouldgo_check = should_go_checking(df_for_prediction_t1, X_train_sg_t1, clf_t1)
    t2_shouldgo_check = should_go_checking(df_for_prediction_t2, X_train_sg_t2, clf_t2)
    t3_shouldgo_check = should_go_checking(df_for_prediction_t3, X_train_sg_t3, clf_t3)
    t4_shouldgo_check = should_go_checking(df_for_prediction_t4, X_train_sg_t4, clf_t4)
    
    return [t1_shouldgo_check, t2_shouldgo_check, t3_shouldgo_check, t4_shouldgo_check]

def return_realtime_predictions():
    current_time = datetime.datetime.now()
    should_go_predictions = all_terminals_prediction(current_time, should_go = True)
    heavy_congestion_predictions = all_terminals_prediction(current_time, should_go = False)
    
    terminal_no = 4
    result = []
    index = 0 
    while index < terminal_no:
        if heavy_congestion_predictions[index] == 1:
            if index == 0: result.append({'lat': 1.361527,
                                      'lng': 103.989,
                                      'type': heavy_congestion_type})
            elif index == 1: result.append({'lat': 1.35741,
                                       'lng': 103.9899,
                                       'type': heavy_congestion_type}) 
            elif index == 2: result.append({'lat': 1.35401,
                                       'lng': 103.9864,
                                       'type': heavy_congestion_type}) 
            else: result.append({'lat': 1.33895,
                                       'lng': 103.9825,
                                       'type': heavy_congestion_type})
        elif should_go_predictions[index] == 1:
            if index == 0: result.append({'lat': 1.361527,
                                      'lng': 103.989,
                                      'type': should_go_type})
            elif index == 1: result.append({'lat': 1.35741,
                                       'lng': 103.9899,
                                       'type': should_go_type}) 
            elif index == 2: result.append({'lat': 1.35401,
                                       'lng': 103.9864,
                                       'type': should_go_type}) 
            else: result.append({'lat': 1.33895,
                                       'lng': 103.9825,
                                       'type': should_go_type})
        index += 1
    return result

return_realtime_predictions()
