
import os
import numpy as np
import sys

from flask import request, render_template, redirect
from werkzeug.utils import secure_filename
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier


from .ML.classifiers import useKNC, useDTC


UPLOADS_DIRECTORY_PATH = "../uploads" 
DOWNLOADS_DIRECTORY_PATH = "../downloads"




def evaluation_view():

    X = np.load( DOWNLOADS_DIRECTORY_PATH + "/" + "4.15" + "/X.npy")
    y = np.load( DOWNLOADS_DIRECTORY_PATH + "/" + "4.15" + "/y.npy")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    train_set = X_train.shape
    test_set = X_test.shape


    #KNeighborsClassifier
    modelKNC = KNeighborsClassifier()
    modelKNC.fit(X_train, y_train)

    KNC_train_score = modelKNC.score(X_train, y_train)
    KNC_test_score = modelKNC.score(X_test, y_test)

    #DecisionTreeClassifier
    modelDTC = DecisionTreeClassifier()
    modelDTC.fit(X_train, y_train)

    DTC_train_score = modelDTC.score(X_train, y_train)
    DTC_test_score = modelDTC.score(X_test, y_test)


    return render_template('evaluation.html', train_set=train_set, test_set=test_set, KNC_train_score=KNC_train_score, KNC_test_score=KNC_test_score, DTC_train_score=DTC_train_score, DTC_test_score=DTC_test_score)

