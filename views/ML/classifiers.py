import numpy as numpy

from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier


def useKNC(X,y,x):
    model = KNeighborsClassifier()

    model.fit(X,y)
    
    prediction = model.predict(x)
    prediction = prediction[0]
    
    return prediction

def useDTC(X,y,x):
    model = DecisionTreeClassifier()

    model.fit(X,y)

    prediction = model.predict(x)
    prediction = prediction[0]

    return prediction




    