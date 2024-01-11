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
from sklearn import svm

holidays = pd.read_csv('./t1_congestion/t1_queue_holiday_avg_combined.csv')
weekends = pd.read_csv('./t1_congestion/t1_queue_weekend_avg_combined.csv')
weekdays = pd.read_csv('./t1_congestion/t1_queue_weekday_avg_combined.csv')
data = pd.concat([holidays, weekends, weekdays], axis=0, ignore_index=True)

# Split the data into features (X) and target (y)
data.loc[data['sum'] >= 10, 'heavy_congestion'] = '1'
data.loc[data['sum'] < 10, 'heavy_congestion'] = '0'

X = data.drop('heavy_congestion', axis=1)
y = data['heavy_congestion']


#Data preprocessing
X = X.drop('date', axis=1)
X = X.drop('sum', axis=1)
X = X.drop(['minutes', 'taxi_count'], axis=1)


X = pd.get_dummies(X, columns = ['day_of_week', 'day_type', 'hour'])

# X = X[['taxi_count_start', 'queue_start']]

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.25,random_state=42)

def decision_tree_training():
    # parameters = {'max_depth':range(3,20)}
    # clf = GridSearchCV(tree.DecisionTreeClassifier(), parameters, n_jobs=4)
    # clf.fit(X, y)
    # tree_model = clf.best_estimator_
    # print (clf.best_score_, clf.best_params_)
    # classifier_rf = RandomForestClassifier(random_state=42, n_jobs=-1, max_depth=3,
    #                                    n_estimators=100, oob_score=True)

    # classifier_rf.fit(X_train, y_train)
    
    # print('oob', classifier_rf.oob_score_)
    
    
    # y_pred = classifier_rf.predict(X_test)
    
    # accuracy = accuracy_score(y_test, y_pred)
    # print("Accuracy:", accuracy)
    
    #Export decision tree
    # r = export_text(classifier_rf)
    # print(r)
    
    # rf = RandomForestClassifier(random_state=42, n_jobs=-1)

    # params = {
    #     'max_depth': [2,3,5,10,20],
    #     'min_samples_leaf': [5,10,20,50,100,200],
    #     'n_estimators': [10,25,30,50,100,200]
    # }
    
    
    # # Instantiate the grid search model
    # grid_search = GridSearchCV(estimator=rf,
    #                            param_grid=params,
    #                            cv = 4,
    #                            n_jobs=-1, verbose=1, scoring="accuracy")
    
    # grid_search.fit(X_train, y_train)
    
    # grid_search.best_score_
    
    # rf_best = grid_search.best_estimator_
    
    # r = export_text(rf_best[5])
    # print(r)
    
    # imp_df = pd.DataFrame({
    # "Varname": X_train.columns,
    # "Imp": rf_best.feature_importances_
    # })
    
    # imp_df.sort_values(by="Imp", ascending=False)
    # print(imp_df)
    
    # Create Decision Tree classifer object
    clf = DecisionTreeClassifier(max_depth=4, random_state=42)
    
    # Train Decision Tree Classifer
    clf = clf.fit(X_train,y_train)
    
    #Predict the response for test dataset
    y_pred = clf.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    
    r = export_text(clf)
    print(r)
    
    
    export_graphviz(clf, out_file='tree.dot', 
                    feature_names = X_train.columns,
                    class_names = ["no", "yes"],
                    rounded = True, proportion = False, 
                    precision = 2, filled = True)
    
    call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png', '-Gdpi=600'])
    
    Image(filename = 'tree.png')
# decision_tree_training()
    
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
    
    