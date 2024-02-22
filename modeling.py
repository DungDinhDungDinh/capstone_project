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
from sklearn import linear_model
from sklearn import svm
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


terminal = 't4'
is_should_go = False
one_date = '2023-11-07'

def import_and_preprocess_should_go():
    data = pd.read_csv('./' + terminal + '_congestion/' + terminal + '_queue_all_days_avg_combined.csv')
        
    # Split the data into features (X) and target (y)
    data.loc[(data['sum'] > 5) & (data['sum'] < 15), 'should_go'] = '1'
    data.loc[(data['sum'] <= 5) | (data['sum'] >= 15), 'should_go'] = '0'
    
    X = data.drop('should_go', axis=1)
    y = data['should_go']


    #Data preprocessing
    # X = X.drop(['date', 'sum', 'minutes', 'taxi_count_avg'], axis=1)
    X = X.loc[:, ['day_of_week', 'day_type', 'hour', 'taxi_count_minute0', 'taxi_length_minute0', 
                  'taxi_count_minute1', 'taxi_length_minute1', 'taxi_count_minute2', 'taxi_length_minute2',
                  'taxi_count_minute3', 'taxi_length_minute3']]
    
    X = pd.get_dummies(X, columns = ['day_of_week', 'day_type', 'hour'])

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

    return X_train, X_test, y_train, y_test

def import_and_preprocess_heavy_congestion():
    
    data = pd.read_csv('./' + terminal + '_congestion/' + terminal + '_queue_all_days_avg_combined.csv')
    
    # Split the data into features (X) and target (y)
    data.loc[data['sum'] >= 10, 'heavy_congestion'] = '1'
    data.loc[data['sum'] < 10, 'heavy_congestion'] = '0'
    
    X = data.drop('heavy_congestion', axis=1)
    y = data['heavy_congestion']


    #Data preprocessing
    # X = X = X.drop(['date', 'sum', 'minutes', 'taxi_count_avg'], axis=1)
    X = X.loc[:, ['day_of_week', 'day_type', 'hour', 'taxi_count_minute0', 'taxi_length_minute0', 
                  'taxi_count_minute1', 'taxi_length_minute1', 'taxi_count_minute2', 'taxi_length_minute2', 
                  'taxi_count_minute3', 'taxi_length_minute3', 'taxi_count_minute4', 'taxi_length_minute4']]
    
    X = pd.get_dummies(X, columns = ['day_of_week', 'day_type', 'hour'])

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.20,random_state=42)

    return X_train, X_test, y_train, y_test

#HEAVY OR SHOULD GO TRAINING
if is_should_go:
    X_train, X_test, y_train, y_test = import_and_preprocess_should_go()
else:
    X_train, X_test, y_train, y_test = import_and_preprocess_heavy_congestion()


#test data preprocessing
one_day = pd.read_csv('./' + terminal + '_congestion/' + terminal + '_queue_' + one_date + '_avg_combined.csv')
def test_data_preprocessing(one_day):
    if is_should_go:
        one_day = one_day.loc[:, ['day_of_week', 'day_type', 'hour', 'taxi_count_minute0', 'taxi_length_minute0', 'taxi_count_minute1', 'taxi_length_minute1', 
                              'taxi_count_minute2', 'taxi_length_minute2', 'taxi_count_minute3', 'taxi_length_minute3']]
    else:
        one_day = one_day.loc[:, ['day_of_week', 'day_type', 'hour', 'taxi_count_minute0', 'taxi_length_minute0', 'taxi_count_minute1', 'taxi_length_minute1', 
                              'taxi_count_minute2', 'taxi_length_minute2', 'taxi_count_minute3', 'taxi_count_minute4', 'taxi_length_minute4']]
                              
    one_day = pd.get_dummies(one_day, columns = ['day_of_week', 'day_type', 'hour'])
    
    for col in X_train.columns:
        if col not in one_day.columns:
          one_day[col] = np.NaN
          
    #Arrange test data
    one_day = one_day[X_train.columns]
    return one_day

one_day = test_data_preprocessing(one_day)

def decision_tree_training():
    
    # Create Decision Tree classifer object
    clf = DecisionTreeClassifier(max_depth=4, random_state=42)
    
    # Train Decision Tree Classifer
    clf = clf.fit(X_train,y_train)
    
    #PREDICTING AND ACCURACY
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    
    #Predict the response for test dataset
    # y_pred = clf.predict(one_day)
    
    # print(y_pred)
    
    
    # #Print tree by words in console
    # # r = export_text(clf)
    # # print(r)
    
    if is_should_go:
        dot_name = terminal + '_should_go.dot'
        png_name = terminal + '_should_go.png'
    else:
        dot_name = terminal + '_heavy_congestion.dot'
        png_name = terminal + '_heavy_congestion.png'
        
    export_graphviz(clf, out_file= dot_name, 
                    feature_names = X_train.columns,
                    class_names = ["no", "yes"],
                    rounded = True, proportion = False, 
                    precision = 2, filled = True)
    
    call(['dot', '-Tpng', dot_name, '-o', png_name, '-Gdpi=600'])
    
    Image(filename = png_name)
decision_tree_training()

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
    
    