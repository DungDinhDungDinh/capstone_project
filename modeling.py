#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 10:27:03 2024

@author: dungdinh
"""

# Data Processing
import pandas as pd
import numpy as np

# Modelling
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, ConfusionMatrixDisplay
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from scipy.stats import randint

# Tree Visualisation
from sklearn.tree import export_graphviz
from IPython.display import display

# import graphviz
from subprocess import call
from IPython.display import Image
from sklearn import preprocessing
from sklearn.feature_selection import mutual_info_classif
import matplotlib.pyplot as plt
from sklearn.tree import export_text
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.impute import SimpleImputer
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from sklearn import linear_model
from sklearn import svm

from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


terminal = 't2'
is_should_go = True
one_date = '2023-11-12'

# def sum_congestion_minutes_by_hour():

def import_and_preprocess_should_go():
    data = pd.read_csv('./' + terminal + '_congestion/' + terminal + '_queue_all_days_avg_combined_5m.csv')
    
    data['month'] = [i[5:7] for i in data['date']]
    
    # Split the data into features (X) and target (y)
    data.loc[(data['sum'] >= 5) & (data['sum'] <= 20), 'should_go'] = '1'
    data.loc[(data['sum'] < 5) | (data['sum'] > 20), 'should_go'] = '0'
    
    X = data.drop('should_go', axis=1)
    y = data['should_go']

    

    #Data preprocessing
    # X = X.drop(['date', 'sum', 'minutes', 'taxi_count_avg'], axis=1)
    X = X.loc[:, ['day_of_week', 'month', 'hour', 'taxi_count_minute-1', 'taxi_length_minute-1', 
                  'taxi_count_minute-2', 'taxi_length_minute-2', 'taxi_count_minute-3', 'taxi_length_minute-3',
                  'taxi_count_minute-4', 'taxi_length_minute-4', 'taxi_count_minute-5', 'taxi_length_minute-5',
                  'taxi_count_minute0', 'taxi_length_minute0']]
    # X = X.loc[:, ['day_of_week', 'hour']]
    
    X = pd.get_dummies(X, columns = ['day_of_week', 'hour', 'month'])

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

    return X_train, X_test, y_train, y_test

def import_and_preprocess_heavy_congestion():
    data = pd.read_csv('./' + terminal + '_congestion/' + terminal + '_queue_all_days_avg_combined_5m.csv')
    data['month'] = [i[5:7] for i in data['date']]
    
    # Split the data into features (X) and target (y)
    data.loc[data['sum'] >= 12, 'heavy_congestion'] = '1'
    data.loc[data['sum'] < 12, 'heavy_congestion'] = '0'
    
    X = data.drop('heavy_congestion', axis=1)
    y = data['heavy_congestion']


    #Data preprocessing
    # X = X = X.drop(['date', 'sum', 'minutes', 'taxi_count_avg'], axis=1)
    X = X.loc[:, ['day_of_week', 'month', 'hour', 'taxi_count_minute-1', 'taxi_length_minute-1', 
                  'taxi_count_minute-2', 'taxi_length_minute-2', 'taxi_count_minute-3', 'taxi_length_minute-3',
                  'taxi_count_minute-4', 'taxi_length_minute-4', 'taxi_count_minute-5', 'taxi_length_minute-5',
                  'taxi_count_minute0', 'taxi_length_minute0', 'taxi_count_minute1', 'taxi_length_minute1',
                  'taxi_count_minute2', 'taxi_length_minute2', 'taxi_count_minute3', 'taxi_length_minute3',
                  'taxi_count_minute4', 'taxi_length_minute4', 'taxi_count_minute5', 'taxi_length_minute5']]
    
    X = pd.get_dummies(X, columns = ['day_of_week', 'month', 'hour'])

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.20,random_state=42)

    return X_train, X_test, y_train, y_test

#HEAVY OR SHOULD GO TRAINING
if is_should_go:
    X_train, X_test, y_train, y_test = import_and_preprocess_should_go()
    # fixed_columns = ['day_of_week_Friday', 'day_of_week_Monday',
    # 'day_of_week_Saturday', 'day_of_week_Sunday', 'day_of_week_Thursday',
    # 'day_of_week_Tuesday', 'day_of_week_Wednesday', 'hour_0', 'hour_1', 'hour_2',
    # 'hour_3', 'hour_4', 'hour_5', 'hour_6', 'hour_7', 'hour_8', 'hour_9',
    # 'hour_10', 'hour_11', 'hour_12', 'hour_13', 'hour_14', 'hour_15',
    # 'hour_16', 'hour_17', 'hour_18', 'hour_19', 'hour_20', 'hour_21',
    # 'hour_22', 'hour_23', 'month']
    # print(X_test.iloc[0])
    # for col in fixed_columns:
    #     if col not in X_test.columns:
    #       X_test[col] = np.nan
    
    # X_test = X_test.loc[:, [fixed_columns]]
else:
    X_train, X_test, y_train, y_test = import_and_preprocess_heavy_congestion()


#test data preprocessing
one_day = pd.read_csv('./' + terminal + '_congestion/' + terminal + '_queue_' + one_date + '_avg_combined_5m.csv')
def test_data_preprocessing(one_day):
    one_day['month'] = [i[5:7] for i in one_day['date']]
    if is_should_go:
        one_day = one_day.loc[:, ['day_of_week', 'month', 'hour', 'taxi_count_minute-1', 'taxi_length_minute-1', 
                      'taxi_count_minute-2', 'taxi_length_minute-2', 'taxi_count_minute-3', 'taxi_length_minute-3',
                      'taxi_count_minute-4', 'taxi_length_minute-4', 'taxi_count_minute-5', 'taxi_length_minute-5',
                      'taxi_count_minute0', 'taxi_length_minute0']]
    else:
        one_day = one_day.loc[:, ['day_of_week', 'hour', 'month', 'taxi_count_minute-1', 'taxi_length_minute-1', 
                      'taxi_count_minute-2', 'taxi_length_minute-2', 'taxi_count_minute-3', 'taxi_length_minute-3',
                      'taxi_count_minute-4', 'taxi_length_minute-4', 'taxi_count_minute-5', 'taxi_length_minute-5',
                      'taxi_count_minute0', 'taxi_length_minute0', 'taxi_count_minute1', 'taxi_length_minute1',
                      'taxi_count_minute2', 'taxi_length_minute2', 'taxi_count_minute3', 'taxi_length_minute3',
                      'taxi_count_minute4', 'taxi_length_minute4', 'taxi_count_minute5', 'taxi_length_minute5']]
                              
    one_day = pd.get_dummies(one_day, columns = ['day_of_week', 'hour', 'month'])
    
    
    for col in X_train.columns:
        if col not in one_day.columns:
            one_day[col] = 0

          
    #Arrange test data
    one_day = one_day[X_train.columns]
    return one_day

one_day = test_data_preprocessing(one_day)

def decision_tree_training(): 
    # imputer = SimpleImputer(strategy='mean')
    # X_train_transformed = imputer.fit_transform(X_train)
    # X_test_transformed = imputer.fit_transform(X_test)
    
    clf = DecisionTreeClassifier(max_depth=4, random_state=42)
    
    # Train Decision Tree Classifer
    clf = clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    
    if len(one_day) > 0:
        y_pred = clf.predict(one_day)
        print(y_pred)
        
        indexes = []
        for index, element in enumerate(y_pred):
            if element == '1':
                indexes.append(index)
        print(indexes)
    
    #Finding indexes of '1'
    # value = '1'
    # indexes = [index for index, element in enumerate(y_pred) if element == value]
    # print(indexes)
    
    #Predict the response for test dataset
    # day_of_week = 'Tuesday'
    # month = '01'
    # test_data = {'day_of_week': [day_of_week, day_of_week, day_of_week, day_of_week, day_of_week,
    #                              day_of_week, day_of_week, day_of_week, day_of_week, day_of_week,
    #                              day_of_week, day_of_week, day_of_week, day_of_week, day_of_week,
    #                              day_of_week, day_of_week, day_of_week, day_of_week, day_of_week,
    #                              day_of_week, day_of_week, day_of_week, day_of_week],
    #         'hour': [0, 1, 2, 3, 4, 
    #                  5, 6, 7, 8, 9, 
    #                  10, 11, 12, 13, 14, 
    #                  15, 16, 17, 18, 19,
    #                  20, 21, 22, 23],
    #         'month': [month, month, month, month, month,
    #                   month, month, month, month, month,
    #                   month, month, month, month, month,
    #                   month, month, month, month, month,
    #                   month, month, month, month
    #                   ]}
    # test_df = pd.DataFrame(test_data)
    # test_df = pd.get_dummies(test_df, columns = ['day_of_week', 'hour', 'month'])
    # for col in X_train.columns:
    #     if col not in test_df.columns:
    #         test_df[col] = np.nan

          
    # #Arrange test data
    # test_df = test_df[X_train.columns]
    
    # print(X_test.iloc[6]['taxi_count_minute4'])
    # print(X_test.iloc[6]['taxi_length_minute4'])
    
    # print('index: ', list(y_pred).index('1'))
    
    
    # Print tree by words in console
    # r = export_text(clf)
    # print(r)
    
    # if is_should_go:
    #     dot_name = terminal + '_should_go.dot'
    #     png_name = terminal + '_should_go.png'
    # else:
    #     dot_name = terminal + '_heavy_congestion.dot'
    #     png_name = terminal + '_heavy_congestion.png'
        
    # export_graphviz(clf, out_file= dot_name, 
    #                 feature_names = X_train.columns,
    #                 class_names = ["no", "yes"],
    #                 rounded = True, proportion = False, 
    #                 precision = 2, filled = True)
    
    # call(['dot', '-Tpng', dot_name, '-o', png_name, '-Gdpi=600'])
    
    # Image(filename = png_name)
# decision_tree_training()

def linear_regression_model():
    reg = linear_model.Ridge(alpha=0.5).fit(X_train, y_train)
    print(reg.score(X_test, y_test))
# linear_regression_model()
    
def logistic_regression_training():
    logisticRegr = LogisticRegression(random_state=42)
    logisticRegr.fit(X_train, y_train)
    y_pred = logisticRegr.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
# logistic_regression_training()  

def svm_training():
    #Create a svm Classifier
    clf = svm.SVC(kernel='linear') # Linear Kernel
    
    #Train the model using the training sets
    clf.fit(X_train, y_train)
    
    #Predict the response for test dataset
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
# svm_training()
    
    