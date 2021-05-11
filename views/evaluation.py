
import os
import numpy as np
import sys

from flask import request, render_template, redirect, request
from werkzeug.utils import secure_filename
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier



DOWNLOADS_DIRECTORY_PATH = "../downloads"




def evaluation_view():


    list_version = os.listdir(DOWNLOADS_DIRECTORY_PATH)  # Get all the files in that directory


    version = request.args.get('version')



    if version is not None :

        X = np.load( DOWNLOADS_DIRECTORY_PATH + "/" + version + "/X.npy")
        y = np.load( DOWNLOADS_DIRECTORY_PATH + "/" + version + "/y.npy")


        shape = X.shape

        #we check if there is enough data
        if shape[0] > 5 :

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

        else:

            train_set = "not enough data"
            test_set = "not enough data"

            KNC_train_score = "not enough data"
            KNC_test_score = "not enough data"

            DTC_train_score = "not enough data"
            DTC_test_score = "not enough data"


        return render_template('evaluation.html', list_version=list_version, train_set=train_set, test_set=test_set, KNC_train_score=KNC_train_score, KNC_test_score=KNC_test_score, DTC_train_score=DTC_train_score, DTC_test_score=DTC_test_score, version=version)



    return render_template('evaluation.html', list_version=list_version)

